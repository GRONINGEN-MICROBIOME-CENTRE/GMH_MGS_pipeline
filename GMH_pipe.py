# ===================================
# MG data analysis pipeline
# by R.Gacesa, UMCG (2022, Dec)
#  Version GMH pipeline v0.9 (beta)
# ===================================
# UPDATES (GMH 0.9.0):
#  > fixed bugs with humann3.6 checkjobs
#  > fixed bugs with sorting strainphlan4 jobs
#  > added support for GTDBTK, CheckM
#  > misc other minor changes
#  > renamed the version to Groningen Microbiome Hub (GMH pipeline)
#    > codes are now on github
# UPDATES (03/h):
#  > added support for node tmp for jobs 0,1a,1b
#  > moved merging to tmp nodes [if usetmp != 0]
# UPDATES (03/g):
#  > added support for Panphlan, Metawrap binning, Metawrap refining
# UPDATES (03/f):
#  > added supprot for Metaphlan4
# UPDATES (03/e):
#  > updated support for SVFINDER to two-step job
#    for improved parallelization and job management
# UPDATES (03/d):
#  > added support for SVFINDER (experimental)
# UPDATES (03/c):
#  > added support for BBduk
#
# includes:
# -> raw data qc (fastQC -> kneaddata -> fastQC)
# -> profiling (metaphlan3, humann3, kraken2)
# -> targeted analysis:
#       - virulence factors (VFDB)
#       - resistance genes (CARD (WIP), ResFinder DB)
#       - strain profiling (strainphlan)
# -> assembly:
#       - metaspades
#       - megahit
#
# -> job management:
#       - job writing
#       - result collection
#
# ==================================

# helper functions
# ==================================
# buffered counter for read number
def bufcount(filename):
    f = open(filename)                  
    lines = 0
    buf_size = 1024 * 1024
    read_f = f.read
    buf = read_f(buf_size)
    while buf:
        lines += buf.count('\n')
        buf = read_f(buf_size)
    return lines

# config loader
# ================================
def loadConfig():
    print ('  --> loading config file',args.jobConfig)
    if not os.path.isfile(args.jobConfig):
        print (" ERROR: config file not found! make sure --jobConfig points to config file")
        exit(1)
    else:
        cfg = configparser.RawConfigParser()
        cfg.read(args.jobConfig)
    return cfg

# job writer modules
# ================================
# next job writer

def writeNextJob(pipeSection, jobID):
   jT = cfg.get(pipeSection,'time').split(':')
   # print('<'+cfg.get('PIPELINE','usePeregrineJobQueues')+'>',cfg.get('PIPELINE','usePeregrineJobQueues')=="1")
   # print('<'+cfg.get('PIPELINE','useSlurm')+'>',cfg.get('PIPELINE','useSlurm')=="1")
   # print(jT[-3],int(jT[-3]),int(jT[-3])==0)
   # print(jT[-2],int(jT[-2])<=30)
   oF.write('# --- SUBMIT '+pipeSection+' (job '+jobID+') ---- \n')
   oF.write('# echo "Submitting '+pipeSection+' (job '+jobID+')" \n')
   if '-' in cfg.get(pipeSection,'time'):      
      nJ = nextjob+' '+smpl+'_'+jobID+'.sh \n'
   elif int(jT[-3]) == 0 and int(jT[-2]) <= 30 and cfg.get('PIPELINE','usePeregrineJobQueues') == "1" and cfg.get('PIPELINE','useSlurm') == "1":
      nJ = nextjob+' --partition=short '+smpl+'_'+jobID+'.sh \n'
   else:
      nJ = nextjob+' '+smpl+'_'+jobID+'.sh \n'
   oF.write(nJ)

# basic job parameters writer:
# > writes basic part of SLURM job (memory,cpus,time...)
# > also adds module loading, paths and conda
def writeBasics(mdlName,jobName,purgeConda=True,purgeModsAfterConda=False,writeSBATCH=True):
    if writeSBATCH:
       oF.write('#!/bin/bash\n')
       oF.write('#SBATCH --job-name='+jobName+'_'+smpl+'\n')
       oF.write('#SBATCH --error='+cfg.get('PIPELINE','jobOut')+'/'+'__'+smpl+'_'+jobName+'.err\n')
       oF.write('#SBATCH --output='+cfg.get('PIPELINE','jobOut')+'/'+'__'+smpl+'_'+jobName+'.out\n')
       oF.write('#SBATCH --mem='+cfg.get(mdlName,'memory')+'\n')
       oF.write('#SBATCH --time='+cfg.get(mdlName,'time')+'\n')
       oF.write('#SBATCH --cpus-per-task='+cfg.get(mdlName,'cpus')+'\n')
       oF.write('#SBATCH --open-mode=truncate\n')
       if cfg.get('PIPELINE','doProfiling',fallback='0') == '1':
          oF.write('#SBATCH --profile=task'+'\n')
    oF.write('# ==== JOB '+mdlName+' ('+jobName+')'+' ==== \n')
    oF.write('echo "========================================== " \n')
    oF.write('echo "> STARTING JOB '+mdlName+' (job '+jobName+')"'+' \n')
    oF.write('echo "========================================== " \n')
    # purge existing stuff to avoid weird roll-overs and bugs
    oF.write('# PURGING ENVIRUMENT \n')
    oF.write('echo "> purging environment "\n')
    oF.write('module purge \n')
    # load modules
    if not cfg.get(mdlName,'modules').strip() == '':
       oF.write('echo "> loading modules "\n')
       oF.write('# --- LOAD MODULES --- \n')
       for m in cfg.get(mdlName,'modules').split(','): 
          oF.write('module load '+m+'\n')
    # load CONDA                
    if not cfg.get(mdlName,'condaEnv').strip() == '':
       oF.write('# --- CLEAN CONDA  --- \n')
       oF.write('echo "> cleaning conda env. "\n')
       if purgeConda:
          oF.write('conda deactivate\n')
       oF.write('# --- LOAD CONDA --- \n')
       oF.write('echo "> loading conda env. "\n')
        #oF.write('conda init bash \n')
       oF.write('conda activate '+cfg.get(mdlName,'condaEnv').strip()+'\n')
       if purgeModsAfterConda:
          oF.write('module purge'+'\n')
    # add paths
    if not cfg.get(mdlName,'paths').strip() == '':
       oF.write('echo "> loading sys paths "\n')
       oF.write('# --- LOAD PATHS --- \n')
       for p in cfg.get(mdlName,'paths').split(','): 
          #oF.write('export PATH="$PATH":'+p+'\n')
          oF.write('PATH=${PATH}:'+p+'\n')

# imports
# =================================
import copy
import argparse
import os
import csv
import shutil
import glob
import configparser
import subprocess
import random

# ============================================================
# ============================================================
#              MAIN 
# ============================================================
# ============================================================

# process CL args
parser = argparse.ArgumentParser()
parser.add_argument("cmd",
   help=''' command for pipeline, as follows:
    checkjobs   : checks which input files in _datalist.tsv are done by checking (--tgt) for results
    writejobs   : prepares jobs for _datalist.tsv
    sortresults : sorts results and moves them to new location; has to be used with --outPath <target location>
    runjobs     : runs all samples (sbatch queues *_p1.sh jobs)
    ''')
parser.add_argument('tgt',help='where [def= current folder (".") ]',default='.',nargs='?')
parser.add_argument('--outPath',help='where to put results',default='.')
parser.add_argument('--inPath',help='where are results',default='.')
parser.add_argument('--jobConfig',help='master config for making jobs',default='GMH_pipe.cfg')
parser.add_argument('--version', action='version', version='GMH pipeline v.0.9.0 (15/02/2023)')
args = parser.parse_args()
# set-up and define allowed commands
cmd = args.cmd
tgt = args.tgt
cmdlist = ['runjobs',
           'writejobs',
           'checkjobs',
           'sortresults',
           'mergeresults']

# ================= START THE PIPELINE =======================
print (' ----------------------------------------')
print ('        DAG3 pipeline V3 invoked  ')
print (' ----------------------------------------')
print (' >>> running command <',cmd,'> on target <',tgt,'>')
# check if command is actually allowed

if args.cmd in cmdlist:
   print ('  --> Executing',args.cmd,'command!')
else:
   print ('  --> ERROR: command',args.cmd,'not recognized!') 
   print ('    --> NOTE: run --help to see supported commands')  
   exit(1)

# ============================================================
# runjobs command:
# ============================================================
#
# > runs all startup jobs (<xyz>_p1.sh in tgt folder)
# ============================================================
if args.cmd == 'runjobs':
   print ('  --> starting pipeline for all samples in ',tgt)
   torun = set()
   for l in os.listdir(tgt):
      if os.path.isfile(l) and l.endswith('_p0.sh'):
         torun.add(l)
   if len(torun) == 0:
      print('    --> WARNING: No jobs to run (jobs should end in _p0.sh)')
      print('        Check if writejobs was run or <tgt> is set properly')
   else:
      print('    --> Submitting',len(torun),'jobs!')
      for j in torun:
         os.system('sbatch '+j)

# ============================================================
# cleantmp command:
#
# > goes through <tgt> and cleans stuff
# -> does not clean tmp files of jobs in progress
# -> otherwise:
# --> cleans humann temp
# --> cleans clean_reads
# --> cleans filtered reads
# ============================================================
if args.cmd == 'cleantmp':
    print ('  --> Performing cleanup of temporary files in ',tgt)
    print ('    --> looking for jobs in progress')
    jlist = subprocess.check_output('sacct --format="JobName%30" -n --allusers', shell=True)
    jhesh = set()
    for j in jlist.split('\n'):
        j = j.strip()
        if not j == '': jhesh.add(j)
    for l in os.listdir(tgt):
        if os.path.isdir(l):
            runna = False
            for j in jhesh:
                if l.strip() in j:
                    print (' W: ',l,'is running (',j,')')
                    runna = True
                    break
            if not runna:
                print (' > ',l,'not running, cleaning')
                if os.path.isdir(l+'/clean_reads'): os.system('rm -r '+l+'/clean_reads')
                if os.path.isdir(l+'/filtering_data'): os.system('rm -r '+l+'/filtering_data')
                if os.path.isdir(l+'/humann3'):
                    for hl in os.listdir(l+'/humann3'):
                        if 'temp' in hl:
                            os.system('rm -r '+l+'/humann3/'+hl)

# ============================================================
# checkjobs command:
# ============================================================
# - takes target (either folder or datafile) and compares to target folder(s) to identify
# a) which samples have been processed [def output: _done_mp.tsv, _done_hu.tsv]
# b) which samples have not been processed [def output: _ndone_mp.tsv,ndone_hu.tsv']
# NYI: b) which step was done for which sample
# ===========================================================
if args.cmd == 'checkjobs':     
    print (' > Executing "',args.cmd,'" command!')
    inPath = args.inPath
    # load config
    cfg = loadConfig()
    print (' --> identifying which samples in <',inPath,'> have results in <',tgt,'>')
    # find samples
    smpls = set()
    smpls_all = {}
    dFileIn = False
    if os.path.isdir(inPath):
        for l in os.listdir(inPath):
            if os.path.isdir(l) and not l == cfg.get('PIPELINE','jobOut'):
                smpls.add(l) 

    if len(smpls) == 0:
        print (' ERROR: no samples found!')
        exit(1)
    print ('   --> found',len(smpls),'samples in',inPath)
    print (' --> scanning ',tgt)
    # done
    kneadDone = set()
    humann3Done = set()
    humann36Done = set()
    metaPhlan3Done = set()
    strainPhlan3Done = set()
    strainPhlan4Done = set()
    sbVFDB_done = set()
    sbCARD_done = set()
    assMetaDone = set()
    assMegaDone = set()
    kraken2Done = set()
    metaPhlan4Done = set()
    svDone = set()
    binMwRefDone = set()
    binAnnotCmDone = set()
    binAnnotGtDone = set()
    binQuantifyDone = set()
    # not done
    kneadND = set()
    metaPhlan3ND = set()
    metaPhlan4ND = set()
    strainPhlan3ND = set()
    strainPhlan4ND = set()
    humann3ND = set()
    humann36ND = set()
    sbVFDB_ND = set()
    sbCARD_ND = set()
    assMetaND = set()
    assMegaND = set()
    kraken2ND = set()
    svND = set()
    binMwRefND = set()
    binAnnotCmND = set()
    binAnnotGtND = set()
    binQuantifyND = set()

    for root, dirpath, files in os.walk(tgt):
        for fl in files:
            #print (fl)
            aPathFl = os.path.abspath(root)+'/'+fl
            # find kneaddata results
            if cfg.get('PIPELINE','doKnead') == '1':
                if cfg.get('KNEAD','mergeResults') == '1':
                    if fl.endswith('_kneaddata_cleaned_paired_merged.fastq'):
                        if fl.replace('_kneaddata_cleaned_paired_merged.fastq','') in smpls:
                            if os.path.getsize(aPathFl) > 10000:
                                kneadDone.add(fl.replace('_kneaddata_cleaned_paired_merged.fastq',''))
                else:
                    if fl.endswith('_kneaddata_cleaned_pair_2.fastq'):
                        if fl.replace('_kneaddata_cleaned_pair_2.fastq','') in smpls:
                            if os.path.getsize(aPathFl) > 10000:
                                kneadDone.add(fl.replace('_kneaddata_cleaned_pair_2.fastq',''))
            # find humann results [H3]
            if cfg.get('PIPELINE','doHumann3') == '1':                
                if fl.endswith('pathabundance.tsv') and root.endswith('humann3'):
                    if fl.replace('_kneaddata_cleaned_paired_merged_pathabundance.tsv','') in smpls:
                        #print (fl)
                        #print (dirs)                        
                        humann3Done.add(fl.replace('_kneaddata_cleaned_paired_merged_pathabundance.tsv',''))
            # find humann results [H3.6]
            if cfg.get('PIPELINE','doHumann3.6') == '1' and root.endswith('humann3.6'):
                if fl.endswith('pathabundance.tsv'):
                    if fl.replace('_kneaddata_cleaned_paired_merged_pathabundance.tsv','') in smpls:
                        humann36Done.add(fl.replace('_kneaddata_cleaned_paired_merged_pathabundance.tsv',''))
            # find metaphlan
            if cfg.get('PIPELINE','doMeta3') == '1':
                if fl.endswith('_metaphlan.txt') and 'metaphlan3' in root:
                    if fl.replace('_metaphlan.txt','') in smpls:
                        if os.path.getsize(aPathFl) > 100:
                            metaPhlan3Done.add(fl.replace('_metaphlan.txt',''))
            # find metaphlan
            if cfg.get('PIPELINE','doMeta4') == '1':
                if fl.endswith('_metaphlan.txt') and 'metaphlan4' in root:
                    if fl.replace('_metaphlan.txt','') in smpls:
                        if os.path.getsize(aPathFl) > 100:
                            metaPhlan4Done.add(fl.replace('_metaphlan.txt',''))
            # find strainphlan markers
            if cfg.get('PIPELINE','doStrainPhlan3') == '1':
                if fl.endswith('_metaphlan3.pkl'):
                    if fl.replace('_metaphlan3.pkl','') in smpls:
                        if os.path.getsize(aPathFl) > 0:
                            strainPhlan3Done.add(fl.replace('_metaphlan3.pkl',''))
            # find strainphlan markers
            if cfg.get('PIPELINE','doStrainPhlan4') == '1':
                if fl.endswith('_metaphlan4.pkl'):
                    if fl.replace('_metaphlan4.pkl','') in smpls:
                        if os.path.getsize(aPathFl) > 0:
                            strainPhlan4Done.add(fl.replace('_metaphlan4.pkl',''))
            # find CARD
            if cfg.get('PIPELINE','doCARD_SB') == '1':
                if fl.endswith('_CARD_sb.txt'):
                    if fl.replace('_CARD_sb.txt','') in smpls:
                        if os.path.getsize(aPathFl) > 0:
                            sbCARD_done.add(fl.replace('_CARD_sb.txt',''))
            # find VFDB
            if cfg.get('PIPELINE','doVFDB_SB') == '1':
                if fl.endswith('_vfdb_sb.txt'):
                    if fl.replace('_vfdb_sb.txt','') in smpls:
                        if os.path.getsize(aPathFl) > 0:
                            sbVFDB_done.add(fl.replace('_vfdb_sb.txt',''))
            # find MEGAHIT
            if cfg.get('PIPELINE','doAssemblyMegaHit') == '1':
                if fl.endswith('_megahit_contigs.fa'):
                    if fl.replace('_megahit_contigs.fa','') in smpls:
                        if os.path.getsize(aPathFl) > 0:
                            assMegaDone.add(fl.replace('_megahit_contigs.fa',''))
            # find META-SPADES            
            if cfg.get('PIPELINE','doAssemblyMetaSpades') == '1':
                if fl.endswith('_metaspades_scaffolds.fa'):
                    if fl.replace('_metaspades_scaffolds.fa','') in smpls:
                        if os.path.getsize(aPathFl) > 0:
                            assMetaDone.add(fl.replace('_metaspades_scaffolds.fa',''))
            # find KRAKEN
            if cfg.get('PIPELINE','doKraken2') == '1':
                if fl.endswith('.bracken.result.kr'):
                    if fl.replace('.bracken.result.kr','') in smpls:
                        if os.path.getsize(aPathFl) > 0:
                            kraken2Done.add(fl.replace('.bracken.result.kr',''))
            # find SVs
            if cfg.get('PIPELINE','doSVFinder',fallback='0') == '1':
                if fl.endswith('_SVs.mapped.jsdel'):
                    if fl.replace('_SVs.mapped.jsdel','') in smpls:
                        if os.path.getsize(aPathFl) > 0:
                            svDone.add(fl.replace('_SVs.mapped.jsdel',''))

            # find quantified bins
            if cfg.get('PIPELINE','doBinQuantification',fallback='0') == '1':                 
                if fl.endswith('_bin_abundances.txt') and 'bins_quantification' in root:
                    if os.path.getsize(aPathFl) > 50:
                        binQuantifyDone.add(fl.replace('_bin_abundances.txt',''))                   
            # find annotation (checkM)
            if cfg.get('PIPELINE','doBinAnnotationCheckM',fallback='0') == '1':                 
                if fl.endswith('_checkM_results_parsed.csv') and 'bins_checkM' in root:
                    if os.path.getsize(aPathFl) > 50:
                        binAnnotCmDone.add(fl.replace('_checkM_results_parsed.csv',''))
            # find annotation (GTDBK)
            if cfg.get('PIPELINE','doBinAnnotationGTDBK',fallback='0') == '1':                 
                if fl.endswith('.gtdbk.bac120.summary.tsv') and 'bins_GTDBK' in root:
                    if os.path.getsize(aPathFl) > 50:
                        binAnnotGtDone.add(fl.replace('.gtdbk.bac120.summary.tsv',''))
            # find refined Bins
            if cfg.get('PIPELINE','doBinRefiningMWrap',fallback='0') == '1':                 
                if 'bins_metawrap_refined' in root and len(files) > 0:
                    fldr = root.split('/')[-2]
                    binMwRefDone.add(fldr)

    # get failed samples
    humann3ND = smpls - humann3Done 
    humann36ND = smpls - humann36Done 
    kneadND = smpls - kneadDone 
    metaPhlan3ND = smpls - metaPhlan3Done 
    metaPhlan4ND = smpls - metaPhlan4Done 
    strainPhlan3ND = smpls - strainPhlan3Done
    strainPhlan4ND = smpls - strainPhlan4Done
    sbVFDB_ND = smpls - sbVFDB_done
    sbCARD_ND = smpls - sbCARD_done
    assMegaND = smpls - assMegaDone
    assMetaND = smpls - assMetaDone
    kraken2ND = smpls - kraken2Done
    svND = smpls - svDone
    binMwRefND = smpls - binMwRefDone
    binAnnotCmND = smpls - binAnnotCmDone
    binAnnotGtND = smpls - binAnnotGtDone
    binQuantifyND = smpls - binQuantifyDone

    # output
    # > Knead
    if cfg.get('PIPELINE','doKnead') == '1':
        print ('  -> KneadData DONE :',len(kneadDone),'samples [saving to _done_kn.tsv]')
        print ('               NOT  :',len(kneadND),'samples [saving to _ndone_kn.tsv]')
        with open('_done_kn.tsv','w') as oF:
            for s in kneadDone: oF.write(s+'\n')
        with open('_ndone_kn.tsv','w') as oF:
            for s in kneadND: oF.write(s+'\n')
    # > Humann3
    if cfg.get('PIPELINE','doHumann3') == '1':
        print ('  -> Humann3 DONE   :',len(humann3Done),'samples [saving to _done_hum3.tsv]')
        print ('              NOT   :',len(humann3ND),'samples [saving to _ndone_hum3.tsv]')
        with open('_done_hum3.tsv','w') as oF:
            for s in humann3Done: oF.write(s+'\n')
        with open('_ndone_hum3.tsv','w') as oF:
            for s in humann3ND:  oF.write(s+'\n')
    # > Humann3.6
    if cfg.get('PIPELINE','doHumann3.6') == '1':
        print ('  -> Humann3.6 DONE :',len(humann36Done),'samples [saving to _done_hum36.tsv]')
        print ('                NOT :',len(humann36ND),'samples [saving to _ndone_hum36.tsv]')
        with open('_done_hum36.tsv','w') as oF:
            for s in humann36Done: oF.write(s+'\n')
        with open('_ndone_hum36.tsv','w') as oF:
            for s in humann36ND:  oF.write(s+'\n')
    if cfg.get('PIPELINE','doMeta3') == '1':
        print ('  -> Metaphlan3 DONE :',len(metaPhlan3Done),'samples [saving to _done_mph3.tsv]')
        print ('                 NOT :',len(metaPhlan3ND),'samples [saving to _ndone_mph3.tsv]')
        with open('_done_mph3.tsv','w') as oF:
            for s in metaPhlan3Done:  oF.write(s+'\n')
        with open('_ndone_mph3.tsv','w') as oF:
            for s in metaPhlan3ND:  oF.write(s+'\n')
    # >> metaphlan 4
    if cfg.get('PIPELINE','doMeta4') == '1':
        print ('  -> Metaphlan4 DONE :',len(metaPhlan4Done),'samples [saving to _done_mph4.tsv]')
        print ('                 NOT :',len(metaPhlan4ND),'samples [saving to _ndone_mph4.tsv]')
        with open('_done_mph4.tsv','w') as oF:
            for s in metaPhlan4Done:  oF.write(s+'\n')
        with open('_ndone_mph4.tsv','w') as oF:
            for s in metaPhlan4ND:  oF.write(s+'\n')
    # >> strainphlan 3
    if cfg.get('PIPELINE','doStrainPhlan3') == '1':
        print ('  -> Strainphlan3 markers DONE :',len(strainPhlan3Done),'samples [saving to _done_sph3.tsv]')
        print ('                           NOT :',len(strainPhlan3ND),'samples [saving to _ndone_sph3.tsv]')
        with open('_done_sph3.tsv','w') as oF:
            for s in strainPhlan3Done: oF.write(s+'\n')
        with open('_ndone_sph3.tsv','w') as oF:
            for s in strainPhlan3ND:  oF.write(s+'\n')
    # >> strainphlan 4
    if cfg.get('PIPELINE','doStrainPhlan4') == '1':
        print ('  -> Strainphlan4 markers DONE :',len(strainPhlan4Done),'samples [saving to _done_sph4.tsv]')
        print ('                          NOT  :',len(strainPhlan4ND),'samples [saving to _ndone_sph4.tsv]')
        with open('_done_sph4.tsv','w') as oF:
            for s in strainPhlan4Done: oF.write(s+'\n')
        with open('_ndone_sph4.tsv','w') as oF:
            for s in strainPhlan4ND:  oF.write(s+'\n')
    # >> VFDB
    if cfg.get('PIPELINE','doVFDB_SB') == '1':
        print ('  -> ShortBRED VFDB DONE :',len(sbVFDB_done),'samples [saving to _done_vfdb.tsv]')
        print ('                    NOT  :',len(sbVFDB_ND),'samples [saving to _ndone_vfdb.tsv]')
        with open('_done_vfdb.tsv','w') as oF:
            for s in sbVFDB_done: oF.write(s+'\n')
        with open('_ndone_vfdb.tsv','w') as oF:
            for s in sbVFDB_ND:  oF.write(s+'\n')
    if cfg.get('PIPELINE','doCARD_SB') == '1':
        print ('  -> ShortBRED CARD DONE :',len(sbCARD_done),'samples [saving to _done_card.tsv]')
        print ('                    NOT  :',len(sbCARD_ND),'samples [saving to _ndone_card.tsv]')
        with open('_done_card.tsv','w') as oF:
            for s in sbCARD_done: oF.write(s+'\n')
        with open('_ndone_card.tsv','w') as oF:
            for s in sbCARD_ND:  oF.write(s+'\n')
    if cfg.get('PIPELINE','doAssemblyMegaHit',fallback=0) == '1':
        print ('  -> MetaHIT Assembly DONE :',len(assMegaDone),'samples [saving to _done_mega.tsv]')
        print ('                      NOT  :',len(assMegaND),'samples [saving to _ndone_mega.tsv]')
        with open('_done_mega.tsv','w') as oF:
            for s in assMegaDone: oF.write(s+'\n')
        with open('_ndone_mega.tsv','w') as oF:
            for s in assMegaND:  oF.write(s+'\n')
    if cfg.get('PIPELINE','doAssemblyMetaSpades',fallback=0) == '1':
        print ('  -> MetaSPADES       DONE :',len(assMetaDone),'samples [saving to _done_mspades.tsv]')
        print ('                      NOT  :',len(assMetaND),'samples [saving to _ndone_mspades.tsv]')
        with open('_done_mspades.tsv','w') as oF:
            for s in assMetaDone: oF.write(s+'\n')
        with open('_ndone_mspades.tsv','w') as oF:
            for s in assMetaND:  oF.write(s+'\n')
    if cfg.get('PIPELINE','doKraken2',fallback=0) == '1':
        print ('  -> KRAKEN2          DONE :',len(kraken2Done),'samples [saving to _done_kraken2.tsv]')
        print ('                      NOT  :',len(kraken2ND),'samples [saving to _ndone_kraken2.tsv]')
        with open('_done_kraken2.tsv','w') as oF:
            for s in kraken2Done: oF.write(s+'\n')
        with open('_ndone_kraken2.tsv','w') as oF:
            for s in kraken2ND:  oF.write(s+'\n')
    if cfg.get('PIPELINE','doSVFinder',fallback=0) == '1':
        print ('  -> SV FINDER        DONE :',len(svDone),'samples [saving to _done_sv.tsv]')
        print ('                      NOT  :',len(svND),'samples [saving to _ndone_sv.tsv]')
        with open('_done_sv.tsv','w') as oF:
            for s in svDone: oF.write(s+'\n')
        with open('_ndone_sv.tsv','w') as oF:
            for s in svND:  oF.write(s+'\n')

    # > Binning Metawrap
    if cfg.get('PIPELINE','doBinRefiningMWrap',fallback=0) == '1':
        print ('  -> BIN refining DONE :',len(binMwRefDone),'samples [saving to _done_bin_ref.tsv]')
        print ('                  NOT  :',len(binMwRefND),'samples [saving to _ndone_bin_ref.tsv]')
        with open('_done_bin_ref.tsv','w') as oF:
            for s in binMwRefDone: oF.write(s+'\n')
        with open('_ndone_bin_ref.tsv','w') as oF:
            for s in binMwRefND: oF.write(s+'\n')
    # > Bin checkM
    if cfg.get('PIPELINE','doBinAnnotationCheckM',fallback=0) == '1':
        print ('  -> BIN QC       DONE :',len(binAnnotCmDone),'samples [saving to _done_bin_checkm.tsv]')
        print ('                  NOT  :',len(binAnnotCmND),'samples [saving to _ndone_bin_checkm.tsv]')
        with open('_done_bin_checkm.tsv','w') as oF:
            for s in binAnnotCmDone: oF.write(s+'\n')
        with open('_ndone_bin_checkm.tsv','w') as oF:
            for s in binAnnotCmND: oF.write(s+'\n')
    # > Bin GTDBTK
    if cfg.get('PIPELINE','doBinAnnotationGTDBK',fallback=0) == '1':
        print ('  -> BIN TAXONOMY DONE :',len(binAnnotGtDone),'samples [saving to _done_bin_gtdbtk.tsv]')
        print ('                  NOT  :',len(binAnnotGtND),'samples [saving to _ndone_bin_gtdbtk.tsv]')
        with open('_done_bin_gtdbtk.tsv','w') as oF:
            for s in binAnnotGtDone: oF.write(s+'\n')
        with open('_ndone_bin_gtdbtk.tsv','w') as oF:
            for s in binAnnotGtND: oF.write(s+'\n')
    # > Bin QUANTIFICATION
    if cfg.get('PIPELINE','doBinQuantification',fallback=0) == '1':
        print ('  -> BIN ABUNDANCE DONE:',len(binQuantifyDone),'samples [saving to _done_bin_abundance.tsv]')
        print ('                   NOT :',len(binQuantifyND),'samples [saving to _ndone_bin_abundance.tsv]')
        with open('_done_bin_abundance.tsv','w') as oF:
            for s in binQuantifyDone: oF.write(s+'\n')
        with open('_ndone_bin_abundance.tsv','w') as oF:
            for s in binQuantifyND: oF.write(s+'\n')


# ================== END OF CHECKJOBS ========================


# ============================================================
# Result merger command:
# ============================================================
# - looks for sorted results in <tgt> [def = .]
# - merges data layers using appropriate tools 
#    (e.g. merge tables for metaphlan)
# =============================================================
if args.cmd == 'mergeresults':
    inFolder = tgt
    print (' > Executing "mergeresults" command')
    print (' ==============================================================')
    print (' WARNING: THIS COMMAND IS UNDER DEVELOPMENT AND MIGHT NOT WORK!')
    print (' ==============================================================')
    # load config
    cfg = loadConfig()
    
    with open('mergercommand.sh','w') as oF:
        oF.write('#!/bin/bash\n')
        oF.write('echo "MERGING RESULTS"\n')
        oF.write('echo "==============="\n')
        oF.write('echo ""\n')
        # merge metaphlan 3
        if cfg.get('PIPELINE','doMeta3') == '1':
            if (os.path.isdir(tgt+'/metaphlan3')):
                print ('prepping code for merging metaphlan3 results in '+tgt+'/metaphlan3')
                oF.write('echo "MERGING METAPHLAN3 RESULTS"\n')
                oF.write('echo "==========================================="\n')
                oF.write('mkdir -p '+tgt+'/results_merged\n')
                oF.write('echo "> initializing conda module"\n')
                oF.write('module purge\n')
                oF.write('module load '+cfg.get('MERGE_RESULTS','condaModule').strip()+' \n')
                oF.write('echo  "> cleaning conda env"\n')
                oF.write('conda deactivate\n')
                oF.write('echo  "> loading biobakery conda"\n')
                oF.write('conda activate '+cfg.get('MERGE_RESULTS','condaBiobakery').strip()+'\n')
                oF.write('echo  "> merging tables... "\n')
                oF.write('merge_metaphlan_tables.py '+tgt+'/metaphlan3/*.txt > '+tgt+'/results_merged/results_metaphlan3.txt\n')
                oF.write('conda deactivate\n')
                oF.write('echo "================ DONE ====================="\n')
                oF.write('echo ""\n')
            else:
                print ('WARNING: metaphlan3 results are not in '+tgt)
        # merge metaphlan 4
        if cfg.get('PIPELINE','doMeta4') == '1':
            if (os.path.isdir(tgt+'/metaphlan4')):
                print ('prepping code for merging metaphlan4 results in '+tgt+'/metaphlan4')
                oF.write('echo "MERGING METAPHLAN4 RESULTS"\n')
                oF.write('echo "==========================================="\n')
                oF.write('mkdir -p '+tgt+'/results_merged\n')
                oF.write('echo "> initializing conda module"\n')
                oF.write('module purge\n')
                oF.write('module load '+cfg.get('MERGE_RESULTS','condaModule').strip()+' \n')
                oF.write('echo  "> cleaning conda env"\n')
                oF.write('conda deactivate\n')
                oF.write('echo  "> loading biobakery conda"\n')
                oF.write('conda activate '+cfg.get('MERGE_RESULTS','condaBiobakery').strip()+'\n')
                oF.write('echo  "> merging tables... "\n')
                oF.write('merge_metaphlan_tables.py '+tgt+'/metaphlan4/*.txt > '+tgt+'/results_merged/results_metaphlan4.txt\n')
                oF.write('conda deactivate\n')
                oF.write('echo "================ DONE ====================="\n')
                oF.write('echo ""\n')
            else:
                print ('WARNING: metaphlan4 results are not in '+tgt)
        # merge humann 3
        # ===================================
        if cfg.get('PIPELINE','doHumann3') == '1':
            if (os.path.isdir(tgt+'/humann3')):
                print ('prepping code for merging humann3 results in '+tgt+'/humann3')
                oF.write('echo "MERGING HUMANN3 RESULTS"\n')
                oF.write('echo "==========================================="\n')
                oF.write('mkdir -p '+tgt+'/results_merged\n')
                oF.write('echo "> initializing conda module"\n')
                oF.write('module purge\n')
                oF.write('module load '+cfg.get('MERGE_RESULTS','condaModule').strip()+' \n')
                oF.write('echo  "> cleaning conda env"\n')
                oF.write('conda deactivate\n')
                oF.write('echo  "> loading biobakery conda"\n')
                oF.write('conda activate '+cfg.get('MERGE_RESULTS','condaBiobakery').strip()+'\n')
                oF.write('echo  "> merging tables (gene families)... "\n')
                oF.write('humann_join_tables -i '+tgt+'/humann3/gene_families/ -o '+tgt+'/results_merged/results_humann3_genefamilies.txt\n')
                oF.write('echo  "> merging tables (pathway abundances)... "\n')
                oF.write('humann_join_tables -i '+tgt+'/humann3/path_abundances/ -o '+tgt+'/results_merged/results_humann3_pathway_abundances_metacyc.txt\n')
                oF.write('echo  "> merging tables (pathway coverage)... "\n')
                oF.write('humann_join_tables -i '+tgt+'/humann3/path_coverage/ -o '+tgt+'/results_merged/results_humann3_pathway_coverages_metacyc.txt\n')
                oF.write('conda deactivate\n')
                oF.write('echo "================ DONE ====================="\n')
                oF.write('echo ""\n')
            else:
                print ('WARNING: humann3 results are not in '+tgt)
        
        # merge humann 3.6
        # =============================================
        if cfg.get('PIPELINE','doHumann3.6') == '1':
            if (os.path.isdir(tgt+'/humann3.6')):
                print ('prepping code for merging humann3.6 results in '+tgt+'/humann3.6')
                oF.write('echo "MERGING HUMANN3.6 RESULTS"\n')
                oF.write('echo "==========================================="\n')
                oF.write('mkdir -p '+tgt+'/results_merged\n')
                oF.write('echo "> initializing conda module"\n')
                oF.write('module purge\n')
                oF.write('module load '+cfg.get('MERGE_RESULTS','condaModule').strip()+' \n')
                oF.write('echo  "> cleaning conda env"\n')
                oF.write('conda deactivate\n')
                oF.write('echo  "> loading biobakery conda"\n')
                oF.write('conda activate '+cfg.get('MERGE_RESULTS','condaBiobakery').strip()+'\n')
                oF.write('echo  "> merging tables (gene families)... "\n')
                oF.write('humann_join_tables -i '+tgt+'/humann3.6/gene_families/ -o '+tgt+'/results_merged/results_humann3.6_genefamilies.txt\n')
                oF.write('echo  "> merging tables (pathway abundances)... "\n')
                oF.write('humann_join_tables -i '+tgt+'/humann3.6/path_abundances/ -o '+tgt+'/results_merged/results_humann3.6_pathway_abundances_metacyc.txt\n')
                oF.write('echo  "> merging tables (pathway coverage)... "\n')
                oF.write('humann_join_tables -i '+tgt+'/humann3.6/path_coverage/ -o '+tgt+'/results_merged/results_humann3.6_pathway_coverages_metacyc.txt\n')
                oF.write('conda deactivate\n')
                oF.write('echo "================ DONE ====================="\n')
                oF.write('echo ""\n')
            else:
                print ('WARNING: humann3.6 results are not in '+tgt)


        # merge CARDs
        if cfg.get('PIPELINE','doCARD_SB') == '1':
            if (os.path.isdir(tgt+'/CARD_SB')):
                print ('prepping code for merging shortbred (CARD) results in '+tgt+'/CARD_SB')
                oF.write('echo "MERGING shortBRED CARD RESULTS"\n')
                oF.write('echo "==========================================="\n')
                oF.write('mkdir -p '+tgt+'/results_merged\n')
                oF.write('echo "> initializing conda module"\n')
                oF.write('module purge\n')
                oF.write('module load '+cfg.get('MERGE_RESULTS','condaModule').strip()+' \n')
                oF.write('echo  "> cleaning conda env"\n')
                oF.write('conda deactivate\n')
                oF.write('echo  "> loading biobakery conda"\n')
                oF.write('conda activate '+cfg.get('MERGE_RESULTS','condaBiobakery').strip()+'\n')
                oF.write('echo  "> merging shortbred results... "\n')
                oF.write('python '+cfg.get('MERGE_RESULTS','cardSbMerger')+' --infolder '+tgt+'/CARD_SB'+' --out '+tgt+'/results_merged/results_card_shortbred.txt'+'\n')
                oF.write('conda deactivate\n')
                oF.write('echo "================ DONE ====================="\n')
                oF.write('echo ""\n')
            else:
                print ('WARNING: CARD shortbred results are not in '+tgt)

        # merge VFs
        if cfg.get('PIPELINE','doVFDB_SB') == '1':
            if (os.path.isdir(tgt+'/VFDB_SB')):
                print ('prepping code for merging shortbred (VFDB) results in '+tgt+'/VFDB_SB')
                oF.write('echo "MERGING shortBRED VFDB RESULTS"\n')
                oF.write('echo "==========================================="\n')
                oF.write('mkdir -p '+tgt+'/results_merged\n')
                oF.write('echo "> initializing conda module"\n')
                oF.write('module purge\n')
                oF.write('module load '+cfg.get('MERGE_RESULTS','condaModule').strip()+' \n')
                oF.write('echo  "> cleaning conda env"\n')
                oF.write('conda deactivate\n')
                oF.write('echo  "> loading biobakery conda"\n')
                oF.write('conda activate '+cfg.get('MERGE_RESULTS','condaBiobakery').strip()+'\n')
                oF.write('echo  "> merging shortbred results... "\n')
                oF.write('python '+cfg.get('MERGE_RESULTS','vfdbSbMerger')+' --infolder '+tgt+'/VFDB_SB'+' --out '+tgt+'/results_merged/results_vfdb_shortbred.txt'+'\n')
                oF.write('conda deactivate\n')
                oF.write('echo "================ DONE ====================="\n')
                oF.write('echo ""\n')
            else:
                print ('WARNING: VFDB shortbred results are not in '+tgt)

        # merge kraken2
        if cfg.get('PIPELINE','doKraken2') == '1':
            if (os.path.isdir(tgt+'/kraken2')):
                print ('prepping code for merging kraken2 results in '+tgt+'/kraken2')
                oF.write('echo "MERGING KRAKEN2 and KRAKEN2-BRACKEN RESULTS"\n')
                oF.write('echo "==========================================="\n')
                oF.write('mkdir -p '+tgt+'/results_merged\n')
                oF.write('echo "> initializing conda module"\n')
                oF.write('module purge\n')
                oF.write('module load '+cfg.get('MERGE_RESULTS','condaModule').strip()+' \n')
                oF.write('echo  "> cleaning conda env"\n')
                oF.write('conda deactivate\n')
                oF.write('echo  "> loading biobakery conda"\n')
                oF.write('conda activate '+cfg.get('MERGE_RESULTS','condaBiobakery').strip()+'\n')
                oF.write('echo  "> merging Kraken-Bracken results... "\n')
                oF.write('merge_metaphlan_tables.py '+tgt+'/kraken2/*bracken.result.mp3.txt > '+tgt+'/results_merged/results_kraken2_bracken.txt\n')
                #oF.write('echo  "> merging Kraken-only results... "\n')
                #oF.write('merge_metaphlan_tables.py '+tgt+'/kraken2/*.kreport.bc.mp3.txt > '+tgt+'/results_merged/results_kraken2.txt\n')
                oF.write('conda deactivate\n')
                oF.write('echo "================ DONE ====================="\n')
                oF.write('echo ""\n')
            else:
                print ('WARNING: kraken2 results are not in '+tgt)

        # merge kneaddata stats
        if cfg.get('PIPELINE','doKnead') == '1':
            if (os.path.isdir(tgt+'/kneaddata')):
                print ('prepping code for merging kneaddata read statistics in '+tgt+'/kneaddata')
                oF.write('echo "MERGING KNEADDATA REPORTS"\n')
                oF.write('echo "==========================================="\n')
                oF.write('mkdir -p '+tgt+'/results_merged\n')
                oF.write('echo "> initializing conda module"\n')
                oF.write('module purge\n')
                oF.write('module load '+cfg.get('MERGE_RESULTS','condaModule').strip()+' \n')
                oF.write('echo  "> cleaning conda env"\n')
                oF.write('conda deactivate\n')
                oF.write('echo  "> loading biobakery conda"\n')
                oF.write('conda activate '+cfg.get('MERGE_RESULTS','condaBiobakery').strip()+'\n')
                oF.write('echo  "> merging tables... "\n')
                oF.write('python '+cfg.get('MERGE_RESULTS','kneaddataMerger')+' --infolder '+tgt+'/kneaddata'+' --out '+tgt+'/results_merged/results_kneaddata_readdepth.csv'+'\n')
                oF.write('conda deactivate\n')
                oF.write('echo "================ DONE ====================="\n')
                oF.write('echo ""\n')
            else:
                print ('WARNING: kneaddata results are not in '+tgt)

        print (' code prep done, run: "bash ./mergercommand.sh" to start result merge')

# ============================================================
# Result sorter command:
# ============================================================
# - looks for pieces of completed jobs in <tgt> [def = .]
# - puts results into appropriate subfolders under --outPath
# example: all metaphlan results are put into outPath/metaphlan
# =============================================================
if args.cmd == 'sortresults':
    outPath = args.outPath
    outFolder = outPath
    inFolder = tgt
    print (' > Executing "sortresults" command')
    if outPath == '.':
        print ('ERROR: incorrect parameters: call with <tgt> --outPath; <tgt> = where to find results, --outPath = where to put results')
        exit(1)
    if not os.path.isdir(outPath):
        print ('NOTE: folder',outPath,'does not exist, making it!')
        try:
            os.mkdir(outPath)
        except:
            print ('ERROR: making folder failed! Quitting!')
    print (' --> output folders, making new ones as necessary')
    # load config
    cfg = loadConfig()
    if cfg.get('PIPELINE','doHumann3',fallback=0) == '1':
        if not os.path.isdir(outFolder+'/humann3'):
            os.mkdir(outFolder+'/humann3')
        if not os.path.isdir(outFolder+'/humann3/gene_families'):
            os.mkdir(outFolder+'/humann3/gene_families')
        if not os.path.isdir(outFolder+'/humann3/path_abundances'):
            os.mkdir(outFolder+'/humann3/path_abundances')
        if not os.path.isdir(outFolder+'/humann3/path_coverage'):
            os.mkdir(outFolder+'/humann3/path_coverage')
    if cfg.get('PIPELINE','doHumann3.6',fallback=0) == '1':
        if not os.path.isdir(outFolder+'/humann3.6'):
            os.mkdir(outFolder+'/humann3.6')
        if not os.path.isdir(outFolder+'/humann3.6/gene_families'):
            os.mkdir(outFolder+'/humann3.6/gene_families')
        if not os.path.isdir(outFolder+'/humann3.6/path_abundances'):
            os.mkdir(outFolder+'/humann3.6/path_abundances')
        if not os.path.isdir(outFolder+'/humann3.6/path_coverage'):
            os.mkdir(outFolder+'/humann3.6/path_coverage')
    if cfg.get('PIPELINE','doQC',fallback=0) == '1':
        if not os.path.isdir(outFolder+'/qc_preclean'):
            os.mkdir(outFolder+'/qc_preclean')
        if not os.path.isdir(outFolder+'/qc_postclean'):
            os.mkdir(outFolder+'/qc_postclean')
    if cfg.get('PIPELINE','doMeta3',fallback=0) == '1':
        if not os.path.isdir(outFolder+'/metaphlan3'):
            os.mkdir(outFolder+'/metaphlan3')
    if cfg.get('PIPELINE','doMeta4',fallback=0) == '1':
        if not os.path.isdir(outFolder+'/metaphlan4'):
            os.mkdir(outFolder+'/metaphlan4')
    if cfg.get('PIPELINE','doStrainPhlan3',fallback=0) == '1':
        if not os.path.isdir(outFolder+'/strainphlan3'):
            os.mkdir(outFolder+'/strainphlan3')
    if cfg.get('PIPELINE','doStrainPhlan4',fallback=0) == '1':
        if not os.path.isdir(outFolder+'/strainphlan4'):
            os.mkdir(outFolder+'/strainphlan4')
    if not os.path.isdir(outFolder+'/logs'):
        os.mkdir(outFolder+'/logs')
    if cfg.get('PIPELINE','doCARD_SB',fallback=0) == '1':
        if not os.path.isdir(outFolder+'/CARD_SB'):
            os.mkdir(outFolder+'/CARD_SB')
    if cfg.get('PIPELINE','doVFDB_SB',fallback=0) == '1':
        if not os.path.isdir(outFolder+'/VFDB_SB'):
            os.mkdir(outFolder+'/VFDB_SB')
    if cfg.get('PIPELINE','doKraken2',fallback=0) == '1':
        if not os.path.isdir(outFolder+'/kraken2'):
            os.mkdir(outFolder+'/kraken2')
    if cfg.get('PIPELINE','doAssemblyMetaSpades',fallback=0) == '1':
        if not os.path.isdir(outFolder+'/assembly_metaspades'):
            os.mkdir(outFolder+'/assembly_metaspades')
    if cfg.get('PIPELINE','doAssemblyMegaHit',fallback=0) == '1':
        if not os.path.isdir(outFolder+'/assembly_megahit'):
            os.mkdir(outFolder+'/assembly_megahit')        
    if cfg.get('PIPELINE','doKnead',fallback=0) == '1':
        if not os.path.isdir(outFolder+'/kneaddata'):
            os.mkdir(outFolder+'/kneaddata')        
    if cfg.get('PIPELINE','doSVFinder',fallback=0) == '1':
        if not os.path.isdir(outFolder+'/SVfinder'):
            os.mkdir(outFolder+'/SVfinder')      
    if cfg.get('PIPELINE','doBinRefiningMWrap',fallback=0) == '1' :
        if not os.path.isdir(outFolder+'/bins_refined'):
            os.mkdir(outFolder+'/bins_refined')
    if cfg.get('PIPELINE','doBinAnnotationGTDBK',fallback=0) == '1':
        if not os.path.isdir(outFolder+'/bins_refined_GTDBK'):
            os.mkdir(outFolder+'/bins_refined_GTDBK')
    if cfg.get('PIPELINE','doBinAnnotationCheckM',fallback=0) == '1':
        if not os.path.isdir(outFolder+'/bins_refined_checkM'):
            os.mkdir(outFolder+'/bins_refined_checkM')
    if cfg.get('PIPELINE','doBinQuantification',fallback=0) == '1':
        if not os.path.isdir(outFolder+'/bins_refined_quantified'):
            os.mkdir(outFolder+'/bins_refined_quantified')

    print (' --> Preparing to copy files')
    c = 0
    for l in os.listdir(inFolder):
        if os.path.isdir(l) and not l == cfg.get('PIPELINE','jobOut'):
           c+=1
           print ('   --> sorting ',l)
           # sort metaphlan results
           if cfg.get('PIPELINE','doMeta3',fallback=0) == '1':
               for f in glob.glob(inFolder+'/'+l+'/metaphlan3/*metaphlan.txt'):
                   shutil.copy2(f, outFolder+'/metaphlan3')
           if cfg.get('PIPELINE','doMeta4',fallback=0) == '1':
               for f in glob.glob(inFolder+'/'+l+'/metaphlan4/*metaphlan.txt'):
                   shutil.copy2(f, outFolder+'/metaphlan4')
           # sort strainphlan 3 results
           if cfg.get('PIPELINE','doStrainPhlan3',fallback=0) == '1':
               for f in glob.glob(inFolder+'/'+l+'/strainphlan3/*.pkl'):
                   shutil.copy2(f, outFolder+'/strainphlan3')
           # sort strainphlan 4 results
           if cfg.get('PIPELINE','doStrainPhlan4',fallback=0) == '1':
               for f in glob.glob(inFolder+'/'+l+'/strainphlan4/*.pkl'):
                   shutil.copy2(f, outFolder+'/strainphlan4')
           # sort QC
           if cfg.get('PIPELINE','doQC',fallback=0) == '1':
               for f in glob.glob(inFolder+'/'+l+'/qc_preclean/*'):
                   shutil.copy2(f, outFolder+'/qc_preclean')
               for f in glob.glob(inFolder+'/'+l+'/qc_postclean/*'):
                   shutil.copy2(f, outFolder+'/qc_postclean')
           # sort HUMANN3:
           if cfg.get('PIPELINE','doHumann3',fallback=0) == '1':
               # sort humann gene families
               for f in glob.glob(inFolder+'/'+l+'/humann3/*_genefamilies.tsv'):
                   shutil.copy2(f, outFolder+'/humann3/gene_families')
               # sort humann gene pathway abundances
               for f in glob.glob(inFolder+'/'+l+'/humann3/*_pathabundance.tsv'):
                   shutil.copy2(f, outFolder+'/humann3/path_abundances')
               # sort humann gene pathway coverage
               for f in glob.glob(inFolder+'/'+l+'/humann3/*_pathcoverage.tsv'):
                   shutil.copy2(f, outFolder+'/humann3/path_coverage')
           if cfg.get('PIPELINE','doHumann3.6',fallback=0) == '1':
               # sort humann gene families
               for f in glob.glob(inFolder+'/'+l+'/humann3.6/*_genefamilies.tsv'):
                   shutil.copy2(f, outFolder+'/humann3.6/gene_families')
               # sort humann gene pathway abundances
               for f in glob.glob(inFolder+'/'+l+'/humann3.6/*_pathabundance.tsv'):
                   shutil.copy2(f, outFolder+'/humann3.6/path_abundances')
               # sort humann gene pathway coverage
               for f in glob.glob(inFolder+'/'+l+'/humann3.6/*_pathcoverage.tsv'):
                   shutil.copy2(f, outFolder+'/humann3.6/path_coverage')
           # sort logs
           for f in glob.glob(inFolder+'/'+l+'/*.log'):
               shutil.copy2(f, outFolder+'/logs')
           # kneaddata stats
           if cfg.get('PIPELINE','doKnead',fallback=0) == '1':
               for f in glob.glob(inFolder+'/'+l+'/*_kneaddata_reads_stats.csv'):
                   shutil.copy2(f, outFolder+'/kneaddata')
           # assembly [metaspades]
           if cfg.get('PIPELINE','doAssemblyMetaSpades',fallback=0) == '1':
               for f in glob.glob(inFolder+'/'+l+'/assembly_metaspades/*scaffolds.fa'):
                   shutil.copy2(f, outFolder+'/assembly_metaspades') 
           # assembly [megahit]
           if cfg.get('PIPELINE','doAssemblyMegaHit',fallback=0) == '1':
               for f in glob.glob(inFolder+'/'+l+'/assembly_megahit/*.fa'):
                   shutil.copy2(f, outFolder+'/assembly_megahit') 
           # VFs
           if cfg.get('PIPELINE','doVFDB_SB',fallback=0) == '1':
               for f in glob.glob(inFolder+'/'+l+'/VFDB_SB/*.txt'):
                   shutil.copy2(f, outFolder+'/VFDB_SB')
           # CARDs
           if cfg.get('PIPELINE','doCARD_SB',fallback=0) == '1':
               for f in glob.glob(inFolder+'/'+l+'/CARD_SB/*.txt'):
                   shutil.copy2(f, outFolder+'/CARD_SB')
           # KRAKEN2
           if cfg.get('PIPELINE','doKraken2',fallback=0) == '1':
               for f in glob.glob(inFolder+'/'+l+'/kraken2/'+l+'*'):
                   shutil.copy2(f, outFolder+'/kraken2')
           # SVs
           if cfg.get('PIPELINE','doSVFinder',fallback=0) == '1':
               for f in glob.glob(inFolder+'/'+l+'/SVs/*.mapped.jsdel'):
                   shutil.copy2(f, outFolder+'/SVfinder')
           # bins [refined]
           if cfg.get('PIPELINE','doBinRefiningMWrap',fallback=0) == '1':
               for f in glob.glob(inFolder+'/'+l+'/bins_metawrap_refined/*.fa'):
                   if not os.path.isdir(outFolder+'/bins_refined/'+l):
                       os.mkdir(outFolder+'/bins_refined/'+l)
                   shutil.copy2(f, outFolder+'/bins_refined/'+l+'/')
           # bins [quantification, GTDBK, checkM)
           if cfg.get('PIPELINE','doBinAnnotationGTDBK',fallback=0) == '1':
               for f in glob.glob(inFolder+'/'+l+'/bins_GTDBK/'+l+'.gtdbk.bac120.summary.tsv'):
                   shutil.copy2(f, outFolder+'/bins_refined_GTDBK')
           if cfg.get('PIPELINE','doBinAnnotationCheckM',fallback=0) == '1':
               for f in glob.glob(inFolder+'/'+l+'/bins_checkM/'+l+'*'):
                   shutil.copy2(f, outFolder+'/bins_refined_checkM')
           if cfg.get('PIPELINE','doBinQuantification',fallback=0) == '1':
               for f in glob.glob(inFolder+'/'+l+'/bins_quantification/'+l+'*'):
                   shutil.copy2(f, outFolder+'/bins_refined_quantified')
           

    print ('ALL DONE, sorted through',c,'results!')

# =============================================================================================================
# =============================================================================================================
# MASTER JOB WRITER FUNCTION:
#
# - writes slurm jobs for each input file in --inPath which might have output files in --outPath
#    -> if --inPath points to file, then it parses through this as if it was _datafile.tsv
#    -> if it points to folder, then it makes jobs for fastq/fq OR fastq.gz/fq.gz OR .bam (pairs) in folder
# =============================================================================================================
# =============================================================================================================
if args.cmd == 'writejobs':    
    print ('   >>> Executing "writejobs" command')
# check for config
    cfg = loadConfig()
# BASIC PARAMETERS
# ============================
# slurm or bash for next job?
    if cfg.get('PIPELINE','useSlurm',fallback=0) == '0':
        nextjob = 'bash'
    else:
        nextjob = 'sbatch'
# === END OF BASIC PARAMS ====

# list of samples
    dataFnd = [] # each entry will be [name,absolute path & name, type, paired ]     
# check if jobout folder exists, if not, make it
    jOutF = cfg.get('PIPELINE','jobOut')
    if not os.path.isdir(jOutF):
        print ('    --> WARNING: job output folder [',jOutF,'] does not exist')
        print ('       --> running mkdir',jOutF)
        os.system('mkdir -p '+jOutF)
        if not os.path.isdir(jOutF):             
            print ('       --> ERROR: mkdir',jOutF,'FAILED! Check cfg file and folders!')
        else:
            print ('       --> SUCCESS, jobs outputs will go into',jOutF)
    else:
        print ('    --> NOTE: jobs outputs will go into',jOutF,'folder!')

# input is folder instead: make jobs for all samples in folder
    if os.path.isdir(tgt): 
        print ('  --> searching for samples in input folder ',tgt)
        for fl in os.listdir(tgt):
            aPathFl = os.path.abspath(fl)
            # zipped fastq
            if fl.endswith('.fq.gz'):
                if fl.endswith('.fq.gz'): fl = fl[:-6]
                dataFnd.append( [fl,aPathFl,"fq.gz",None] )
            elif fl.endswith('.fastq.gz'):
                if fl.endswith('.fastq.gz'): fl=fl[:-9]
                dataFnd.append( [fl,aPathFl,"fastq.gz",None] )
            # fastq
            elif fl.endswith('.fastq'):
                fl=fl[:-6]
                dataFnd.append( [fl,aPathFl,"fastq",None] )
            elif fl.endswith('.fq'):
                fl = fl[:-3]
                dataFnd.append( [fl,aPathFl,"fq",None] )
            # bam
            elif fl.endswith('.bam'):           
                fl = fl[:-4]
                dataFnd.append( [fl,aPathFl,"bam",None] )

        if len(dataFnd) > 0:
            #print (' --> identifying paired samples')
            dataFnd = sorted(dataFnd)
            dic = {}
            for l in dataFnd:
                lN = l[0]
                if lN.endswith('_1') or lN.endswith('_2'):
                    try: dic[lN[:-2]] += 1
                    except: dic[lN[:-2]] = 1
            for l in dataFnd:
                lN = l[0]
                if (lN.endswith('_1') or lN.endswith('_2')) and dic[lN[:-2]] == 2:
                    l[3] = True
                    l[0] = l[0][:-2]
                else:
                    l[3] = False
    else:
        print (' ERROR: input (<tgt> parameter) should be folder with samples')
        exit()

    # sample list is ready, bit of cleaning
    dataUn = {} # job -> paired or not
    dataFmt = {} # job -> format
    nrPairs = 0.0
    for s in dataFnd: 
        dataUn[s[0]] = False
        dataFmt[s[0]] = s[2]
        if s[3]: 
            nrPairs+=0.5
            dataUn[s[0]] = True
    print ('    --> found',len(dataFnd),'files [',len(dataUn),'unique samples / ',nrPairs,'pairs]')
    #print ('---------------------------------')
    # iterate over unique samples and write jobs:
    for smpl,paired in dataUn.items():
        fmt = dataFmt[smpl]
        print ('      --> Writing jobs for sample',smpl,'[paired:',paired,'; format',fmt,']')
        # if sample is paired, extract pairs
        if paired or fmt == 'bam':
            if dataFmt[smpl] == 'bam':
                bamFile = smpl+'.bam' 
                pair1 = smpl+'_1.fastq'
                pair2 = smpl+'_2.fastq'            
            elif dataFmt[smpl] == 'fq.gz':
                pair1 = smpl+'_1.fq.gz'
                pair2 = smpl+'_2.fq.gz'                
            elif dataFmt[smpl] == 'fastq.gz':
                pair1 = smpl+'_1.fastq.gz'
                pair2 = smpl+'_2.fastq.gz'                
            elif dataFmt[smpl] == 'fastq':
                pair1 = smpl+'_1.fastq'
                pair2 = smpl+'_2.fastq'                
            elif dataFmt[smpl] == 'fq':
                pair1 = smpl+'_1.fq'
                pair2 = smpl+'_2.fq'
               
            #debug print (smpl,pair1,pair2)

            # PART 0: Initialization & QC
            # =============================================================


            # PART 0-1b: Initialization & QC
            # =============================================================
            with open(smpl+'_p0.sh','w') as oF:                
                writeBasics('INIT','i')
                # set up paths
                sampleDataF = smpl
                # folder making
                oF.write('# --- MAKE FOLDERS ---- \n')
                oF.write('mkdir -p '+smpl+'\n')               
                oF.write('mkdir -p '+sampleDataF+'/clean_reads/'+'\n')
                # do not use node tmp:               
                if cfg.get('PIPELINE','useNodeTMP',fallback=0) == '0':
                   filteringDataF = smpl+'/filtering_data/'
                # use node tmp
                elif cfg.get('PIPELINE','useNodeTMP',fallback=0) == '1':
                   filteringDataF = '${TMPDIR}'+'/'+smpl+'/filtering_Data/'
                oF.write('mkdir -p '+filteringDataF+'\n')                     
                rawDataF = smpl
                # == PREP DATA FOR FURTHER PROCESSING ==
                # > we always want to end with .fastq extension
                # i) input is bam:
                if fmt == 'bam': 
                    oF.write('# --- BAM to FastQ conversion ---- \n')
                    oF.write('picard SamToFastq I='+bamFile+' F='+filteringDataF+'/'+pair1+' F2='+filteringDataF+'/'+pair2+'\n')
                # not bam:
                elif not fmt == 'bam': 
                    if pair1.endswith('.fq.gz'):
                       oF.write('echo " > copying files"'+'\n')
                       oF.write('cp '+pair1+' '+filteringDataF+'/'+pair1.replace('.fq.gz','.fastq.gz')+'\n')
                       oF.write('cp '+pair2+' '+filteringDataF+'/'+pair2.replace('.fq.gz','.fastq.gz')+'\n')
                       oF.write('echo " > unzipping files"'+'\n')
                       oF.write('gunzip '+filteringDataF+'/'+pair1.replace('.fq.gz','.fastq.gz')+'\n')
                       oF.write('gunzip '+filteringDataF+'/'+pair2.replace('.fq.gz','.fastq.gz')+'\n')
                    elif (pair1.endswith('.fastq.gz')):
                       oF.write('echo " > copying files"'+'\n')
                       oF.write('cp '+pair1+' '+filteringDataF+'\n')
                       oF.write('cp '+pair2+' '+filteringDataF+'\n')
                       oF.write('echo " > unzipping files"'+'\n')
                       oF.write('gunzip '+filteringDataF+'/'+pair1+'\n')
                       oF.write('gunzip '+filteringDataF+'/'+pair2+'\n')
                    elif pair1.endswith('.fastq'):
                       oF.write('echo " > copying files"'+'\n')
                       oF.write('cp '+pair1+' '+filteringDataF+'\n')
                       oF.write('cp '+pair2+' '+filteringDataF+'\n')
                    elif pair1.endswith('.fq'):
                       oF.write('echo " > copying files"'+'\n')
                       oF.write('cp '+pair1+' '+filteringDataF+'/'+pair1.replace('.fq','.fastq')+'\n')
                       oF.write('cp '+pair2+' '+filteringDataF+'/'+pair2.replace('.fq','.fastq')+'\n')
                    else:
                       print(' ERROR: CANNOT RECOGNIZE DATA TYPE FOR ',pair1,', ABORTING!')
                       quit(1)
                else: 
                    print(' ERROR: CANNOT RECOGNIZE DATA TYPE FOR ',pair1,', ABORTING!')
                    quit(1)                                     
                in1 = filteringDataF+'/'+smpl+'_1.fastq'
                in2 = filteringDataF+'/'+smpl+'_2.fastq'
                # INITIAL QC
                if cfg.get('PIPELINE','doQC',fallback=0) == '1':                           
                    # write QC runner 
                    oF.write('# --- RUN QC --- \n')
                    oF.write('echo "Running FastQC on unclean reads" \n')
                    oF.write('mkdir -p '+smpl+'/qc_preclean'+'\n')
                    oF.write('fastqc -t '+cfg.get('QC','threads')+' -q -o '+smpl+'/qc_preclean'+' '+in1+'\n')
                    oF.write('fastqc -t '+cfg.get('QC','threads')+' -q -o '+smpl+'/qc_preclean'+' '+in2+'\n')                    
                # PART 1/a: BBduk
                # =============================================================
                if cfg.get('PIPELINE','doBBduk',fallback=0) == '1':
                   writeBasics('BBDUK','p1a',writeSBATCH=False)
                   in1 = filteringDataF+'/'+smpl+'_1.fastq'
                   in2 = filteringDataF+'/'+smpl+'_2.fastq'
                   out1 = filteringDataF+'/'+smpl+'_bbdukout_1.fastq'
                   out2 = filteringDataF+'/'+smpl+'_bbdukout_2.fastq'                   
                   oF.write('echo " > running BBDUK"'+'\n')
                   oF.write('bbduk.sh in1='+in1+' in2='+in2+' out1='+out1+' out2='+out2+' ref='+cfg.get('BBDUK','adapters')+' '+cfg.get('BBDUK','bbdukParams')+ ' 2>&1 | tee '+smpl+'/'+smpl+'_bbduk.log'+'\n')
                   # replace original filtering data with bbdukked one
                   oF.write('rm '+in1+'\n')
                   oF.write('rm '+in2+'\n')
                   oF.write('mv '+out1+' '+in1+'\n')
                   oF.write('mv '+out2+' '+in2+'\n')

            # PART 1/b: Kneaddata
            # =============================================================
                writeBasics('KNEAD','kn',writeSBATCH=False)
                if cfg.get('PIPELINE','doKnead',fallback=0) == '1':
                   oF.write('# --- RUN KNEADDATA ---- \n')  # PAIRED END KNEAD
                   oF.write('echo " > running Kneaddata" \n')
                   # set trimming options
                   if (cfg.get('KNEAD','doTrimIfUsingBBduk',fallback='0') == '1') or (cfg.get('PIPELINE','doBBduk',fallback=0) == '0'):
                      trimstr = ' --trimmomatic '+cfg.get('KNEAD','trimmomatic',fallback='trimmomatic') + ' '+ cfg.get('KNEAD','trimmomaticOptions',fallback='')
                   else:
                      trimstr = ' --bypass-trim'                                     
                   # === KNEADDATA (normal) ===
                   # kneaddata job
                   if cfg.get('PIPELINE','useNodeTMP',fallback=0) != 'X':
                       # run kneaddata {biobakery4}
                       if cfg.get('KNEAD','kneadversion',fallback='') == 'biobakery4':
                           oF.write('kneaddata --input1 '+in1+' --input2 '+in2+' --threads '+cfg.get('KNEAD','threads',fallback='1')+' --processes '+cfg.get('KNEAD','threads',fallback='1')+' --output '+filteringDataF+' --log '+smpl+'/'+smpl+'_kneaddata.log -db '+cfg.get('KNEAD','db')+' '+trimstr+' '+cfg.get('KNEAD','options',fallback='')+'\n')
                       else:
                           oF.write('kneaddata --input '+in1+' --input '+in2+' --threads '+cfg.get('KNEAD','threads',fallback='1')+' --processes '+cfg.get('KNEAD','threads',fallback='1')+' --output '+filteringDataF+' --log '+smpl+'/'+smpl+'_kneaddata.log -db '+cfg.get('KNEAD','db')+' '+trimstr+' '+cfg.get('KNEAD','options',fallback='')+'\n')
                       # merge & move stuff, remove contaminants and unpaired reads, rename for clarity
                       #oF.write('mkdir -p '+sampleDataF+'/clean_reads/'+'\n')
                       oF.write('mv '+filteringDataF+'/'+smpl+'_1_kneaddata_paired_1.fastq '+sampleDataF+'/clean_reads/'+smpl+'_kneaddata_cleaned_pair_1.fastq'+'\n')
                       oF.write('mv '+filteringDataF+'/'+smpl+'_1_kneaddata_paired_2.fastq '+sampleDataF+'/clean_reads/'+smpl+'_kneaddata_cleaned_pair_2.fastq'+'\n')
                       if cfg.get('PIPELINE','useNodeTMP',fallback='0') == '0':
                         oF.write('cat '+sampleDataF+'/clean_reads/'+smpl+'_kneaddata_cleaned_pair_1.fastq > '+sampleDataF+'/clean_reads/'+smpl+'_kneaddata_cleaned_paired_merged.fastq\n')
                         oF.write('cat '+sampleDataF+'/clean_reads/'+smpl+'_kneaddata_cleaned_pair_2.fastq >> '+sampleDataF+'/clean_reads/'+smpl+'_kneaddata_cleaned_paired_merged.fastq\n')
                       # keep contaminants (if Y)
                       if cfg.get('KNEAD','keepHumanReads',fallback='0') == '1':
                          oF.write('cat '+filteringDataF+'/*paired_contam_1.fastq >> '+sampleDataF+'/clean_reads/'+smpl+'_kneaddata_contaminants_pair_1.fastq\n')
                          oF.write('cat '+filteringDataF+'/*paired_contam_2.fastq >> '+sampleDataF+'/clean_reads/'+smpl+'_kneaddata_contaminants_pair_2.fastq\n')                         
                       if cfg.get('PIPELINE','useNodeTMP',fallback='0') == '0':
                          oF.write('cat '+sampleDataF+'/clean_reads/*contaminants_pair_[12].fastq >> '+sampleDataF+'/clean_reads/'+smpl+'_kneaddata_contaminants_paired_merged.fastq\n')
                       # clean stuff
                       if cfg.get('KNEAD','cleanTmp',fallback='0') == '1':
                          oF.write('#   -->  clean kneaddata results: \n')                          
                          if cfg.get('PIPELINE','useNodeTMP',fallback='0') == '1':
                             oF.write('rm -r ${TMPDIR}'+'/'+smpl+'\n')
                          else:
                             oF.write('rm -r '+smpl+'/filtering_data\n')

                   # PARSE KNEADDATA RESULTS
                   oF.write('# -- PARSING KNEADDATA RESULTS --\n')
                   oF.write('echo " > parsing kneaddata logs"\n')
                   oF.write('python '+cfg.get('KNEAD','knead3parser')+' --infile '+smpl+'/'+smpl+'_kneaddata.log'+' --outfile '+smpl+'/'+smpl+'_kneaddata_reads_stats.csv'+'\n')
                   # DONE WITH PARSING KNEADDATA
                   oF.write('# -- DONE PARSING -- \n')
                   # ===============================================================

                # NO KNEADDATA:
                # ==============================================================
                elif cfg.get('PIPELINE','doKnead',fallback='0') == '0':
                   oF.write('# -- NO KneadData, copies files to clean_reads instead -- \n')
                   # not bam:
                   oF.write('echo " > copying files"'+'\n')
                   oF.write('cp '+in1+' '+smpl+'/clean_reads/'+smpl+'_kneaddata_cleaned_pair_1.fastq\n')
                   oF.write('cp '+in2+' '+smpl+'/clean_reads/'+smpl+'_kneaddata_cleaned_pair_2.fastq\n')
                   if cfg.get('PIPELINE','useNodeTMP',fallback='0') == '0':
                       oF.write('cat '+smpl+'/clean_reads/'+smpl+'_kneaddata_cleaned_pair_1.fastq > '+smpl+'/clean_reads/'+smpl+'_kneaddata_cleaned_paired_merged.fastq\n')
                       oF.write('cat '+smpl+'/clean_reads/'+smpl+'_kneaddata_cleaned_pair_2.fastq >> '+smpl+'/clean_reads/'+smpl+'_kneaddata_cleaned_paired_merged.fastq\n')

                # POST-QC JOB
                if cfg.get('PIPELINE','doQC',fallback='0') == '1':
                   oF.write('# --- RUN QC --- \n')
                   oF.write('echo "Running FastQC on cleaned reads" \n')
                   oF.write('mkdir -p '+smpl+'/qc_postclean'+'\n')
                   #oF.write('fastqc -t '+cfg.get('QC','threads')+' -q -o '+smpl+'/qc_postclean '+smpl+'/clean_reads/'+smpl+'_kneaddata_cleaned_paired_merged.fastq'+'\n')
                   oF.write('fastqc -t '+cfg.get('QC','threads')+' -q -o '+smpl+'/qc_postclean '+smpl+'/clean_reads/'+smpl+'_kneaddata_cleaned_pair_1.fastq'+'\n')
                   oF.write('fastqc -t '+cfg.get('QC','threads')+' -q -o '+smpl+'/qc_postclean '+smpl+'/clean_reads/'+smpl+'_kneaddata_cleaned_pair_2.fastq'+'\n')

                # ======= DONE WITH QC steps, submit jobs ========
                # SUBMIT Virulence factor finder (shortBRED) (if required)
                if cfg.get('PIPELINE','doVFDB_SB',fallback='0') == '1':
                   writeNextJob('VFDB_SB','vs')
                # SUBMIT CARD antibiotic resistance (shortBRED) (if required)
                if cfg.get('PIPELINE','doCARD_SB',fallback='0') == '1':
                   writeNextJob('CARD_SB','ac')
                # SUBMIT METAPHLAN (if required)
                if cfg.get('PIPELINE','doMeta3',fallback='0') == '1':
                   writeNextJob('METAPHLAN3','p2')
               # SUBMIT METAPHLAN4 (if required)
                if cfg.get('PIPELINE','doMeta4',fallback='0') == '1':
                   writeNextJob('METAPHLAN4','pM4')
                # SUBMIT ASSEMBLY (METASPADES)
                if cfg.get('PIPELINE','doAssemblyMetaSpades',fallback='0') == '1':
                   writeNextJob('ASSEMBLY_METASPADES','aMS')
                # SUBMIT ASSEMBLY (MEGAHIT)
                if cfg.get('PIPELINE','doAssemblyMegaHit',fallback='0') == '1':
                   writeNextJob('ASSEMBLY_MEGAHIT','aMH')
                # SUBMIT KRAKEN2
                if cfg.get('PIPELINE','doKraken2',fallback='0') == '1':
                   writeNextJob('KRAKEN2','pK2')
                # SUBMIT SVFINDER
                if cfg.get('PIPELINE','doSVFinder',fallback='0') == '1':
                   writeNextJob('SVFINDER','pSV')
               # END OF PART 1                  

            # WRITE METAPHLAN4
            # =======================================================
            if cfg.get('PIPELINE','doMeta4',fallback='0') == '1':
                with open(smpl+'_pM4.sh','w') as oF:
                    vscout = ''
                    writeBasics('METAPHLAN4','m4')
                    # prep strainphlan options (if any)
                    if cfg.get('PIPELINE','doStrainPhlan4',fallback='0') == '0':
                        strainPhlanOpts = ''
                    if cfg.get('PIPELINE','doStrainPhlan4',fallback='0') == '1' :
                        strainPhlanOpts = ' --bowtie2out ' +smpl+'/metaphlan4/'+smpl+'_metaphlan4_bowtie2.txt' + ' --samout ' +smpl+'/metaphlan4/'+smpl+'_metaphlan4.sam.bz2'
                    # write metaphlan4 runner
                    oF.write('# --- RUN METAPHLAN4 --- \n')
                    # write virus profiling stuff
                    if '--profile_vsc' in cfg.get('METAPHLAN4','metaphlanOptions', fallback=''):
                        vscout = ' --vsc_out '+sampleDataF+'/metaphlan4/'+smpl+'_metaphlan_vscout.txt '
                    # make folder if it does not exist
                    oF.write('mkdir -p ./'+smpl+'/metaphlan4 \n') 
                    # local node temp use:
                    useLS = False;
                    if cfg.get('PIPELINE','useNodeTMP',fallback='0') == '1' and cfg.get('PIPELINE','useSlurm') == '1':
                        useLS = True;          
                    if useLS:
                        # METAPHLAN RUN WITH LOCAL NODE TMP
                        # ====================================
                        sampleDataF = '${TMPDIR}'+'/'+smpl
                        # prep node TMP
                        oF.write('# prep node temp folders\n')
                        oF.write('mkdir -p '+sampleDataF+'\n') 
                        oF.write('mkdir -p '+sampleDataF+'/metaphlan4'+'\n')                         
                        oF.write('mkdir -p '+sampleDataF+'/clean_reads'+'\n')
                        oF.write('mkdir -p '+sampleDataF+'/metaphlan4_tmp'+'\n')
                        # run it [MP3 & 4 can swallow metaphlan metagenome_1.fastq,metagenome_2.fastq] 
                        # TMP NODE merge (to save space, adds a bit of write time)
                        smplCleanMrgd = sampleDataF+'/clean_reads/'+smpl+'_kneaddata_cleaned_paired_merged.fastq'
                        oF.write('cat '+smpl+'/clean_reads/'+smpl+'_kneaddata_cleaned_pair_1.fastq > '+smplCleanMrgd+'\n')
                        oF.write('cat '+smpl+'/clean_reads/'+smpl+'_kneaddata_cleaned_pair_2.fastq >> '+smplCleanMrgd+'\n')
                        # run it   
                        oF.write(cfg.get('METAPHLAN4','metaphlan')+' '+smplCleanMrgd+' --input_type fastq --nproc '+cfg.get('METAPHLAN4','threads') + vscout + ' -o '+sampleDataF+'/metaphlan4/'+smpl+'_metaphlan.txt'+' --tmp_dir '+sampleDataF+'/metaphlan4_tmp' + ' --bowtie2db '+cfg.get('METAPHLAN4','metaphlanDB') + ' ' + cfg.get('METAPHLAN4','metaphlanOptions')+strainPhlanOpts+' 2>&1 | tee '+smpl+'/'+smpl+'_metaphlan4.log'+'\n')
                        # collect data
                        oF.write('cp '+sampleDataF+'/metaphlan4/* '+smpl+'/metaphlan4/\n')
                        # clean node
                        oF.write('rm -r '+sampleDataF+'\n')
                    else:                   
                        # METAPHLAN RUN WITHOUT LOCAL NODE TMP
                        # ====================================
                        oF.write('mkdir -p '+smpl+'/metaphlan4_tmp'+'\n')

                        oF.write(cfg.get('METAPHLAN4','metaphlan')+' '+smpl+'/clean_reads/'+smpl+'_kneaddata_cleaned_paired_merged.fastq'+' --input_type fastq --nproc '+cfg.get('METAPHLAN4','threads') + vscout + ' -o '+smpl+'/metaphlan4/'+smpl+'_metaphlan.txt'+' --tmp_dir '+smpl+'/metaphlan4_tmp' + ' --bowtie2db '+cfg.get('METAPHLAN4','metaphlanDB') + ' ' + cfg.get('METAPHLAN4','metaphlanOptions')+strainPhlanOpts+' 2>&1 | tee '+smpl+'/'+smpl+'_metaphlan4.log'+'\n')

                    #SUBMIT STRAINPLHAN (if required)
                    if cfg.get('PIPELINE','doStrainPhlan4') == '1' :
                        writeNextJob('STRAINPHLAN4','p2sp4') 
                    # SUBMIT HUMANN3.6 (if required)
                    if cfg.get('PIPELINE','doHumann3.6') == '1':
                        writeNextJob('HUMANN3.6','pH36')
            # =============================================================
            # END OF METAPHLAN4

            # WRITE PART 2 (METAPHLAN3)
            # =============================================================
            if cfg.get('PIPELINE','doMeta3',fallback='0') == '1':
                with open(smpl+'_p2.sh','w') as oF:                    
                    writeBasics('METAPHLAN3','m')
                    # prep strainphlan options (if any)
                    if cfg.get('PIPELINE','doStrainPhlan3') == '0':
                        strainPhlanOpts = ''
                    if cfg.get('PIPELINE','doStrainPhlan3') == '1' :
                        strainPhlanOpts = ' --bowtie2out ' +smpl+'/metaphlan3/'+smpl+'_metaphlan3_bowtie2.txt' + ' --samout ' +smpl+'/metaphlan3/'+smpl+'_metaphlan3.sam.bz2'
                    # write metaphlan3 runner
                    oF.write('# --- RUN METAPHLAN3 --- \n')
                    # make folder if it does not exist
                    oF.write('mkdir -p ./'+smpl+'/metaphlan3 \n') 
                    # local node temp use:
                    useLS = False;
                    if cfg.get('PIPELINE','useNodeTMP',fallback='0') == '1' and cfg.get('PIPELINE','useSlurm',fallback='0') == '1':
                        useLS = True;          
                    if useLS:
                        # METAPHLAN RUN WITH LOCAL NODE TMP
                        # ====================================
                        sampleDataF = '${TMPDIR}'+'/'+smpl
                        # prep node TMP
                        oF.write('# prep node temp folders\n')
                        oF.write('mkdir -p '+sampleDataF+'\n') 
                        oF.write('mkdir -p '+sampleDataF+'/metaphlan3'+'\n')
                        oF.write('mkdir -p '+sampleDataF+'/clean_reads'+'\n')
                        # TMP NODE merge (to save space, adds a bit of write time)
                        smplCleanMrgd = sampleDataF+'/clean_reads/'+smpl+'_kneaddata_cleaned_paired_merged.fastq'
                        oF.write('cat '+smpl+'/clean_reads/'+smpl+'_kneaddata_cleaned_pair_1.fastq > '+smplCleanMrgd+'\n')
                        oF.write('cat '+smpl+'/clean_reads/'+smpl+'_kneaddata_cleaned_pair_2.fastq >> '+smplCleanMrgd+'\n')
                        # run it
                        oF.write(cfg.get('METAPHLAN3','metaphlan')+' '+smplCleanMrgd+' --input_type fastq --nproc '+cfg.get('METAPHLAN3','threads') + ' -o '+sampleDataF+'/metaphlan3/'+smpl+'_metaphlan.txt'+' --tmp_dir '+sampleDataF+'/metaphlan3_tmp' + ' --bowtie2db '+cfg.get('METAPHLAN3','metaphlanDB') + ' ' + cfg.get('METAPHLAN3','metaphlanOptions')+strainPhlanOpts+' 2>&1 | tee '+smpl+'/'+smpl+'_metaphlan3.log'+'\n')
                        # collect data
                        oF.write('cp '+sampleDataF+'/metaphlan3/* '+smpl+'/metaphlan3/\n')
                        # clean node
                        oF.write('rm -r '+sampleDataF+'\n')
                    else:                   
                        # METAPHLAN RUN WITHOUT LOCAL NODE TMP
                        # ====================================
                        oF.write(cfg.get('METAPHLAN3','metaphlan')+' '+smpl+'/clean_reads/'+smpl+'_kneaddata_cleaned_paired_merged.fastq'+' --input_type fastq --nproc '+cfg.get('METAPHLAN3','threads') + ' -o '+smpl+'/metaphlan3/'+smpl+'_metaphlan.txt'+' --tmp_dir '+smpl+'/metaphlan3_tmp' + ' --bowtie2db '+cfg.get('METAPHLAN3','metaphlanDB') + ' ' + cfg.get('METAPHLAN3','metaphlanOptions')+strainPhlanOpts+' 2>&1 | tee '+smpl+'/'+smpl+'_metaphlan3.log'+'\n')

                    # SUBMIT STRAINPLHAN (if required)
                    if cfg.get('PIPELINE','doStrainPhlan3') == '1' :
                        writeNextJob('STRAINPHLAN3','p2sp') 
                    # SUBMIT HUMANN3 (if required)
                    if cfg.get('PIPELINE','doHumann3') == '1':
                        writeNextJob('HUMANN3','p3')
            # =============================================================
            # END OF PART 2

            # WRITE PART 2/b (STRAINPHLAN 3) 
            # =============================================================
            if cfg.get('PIPELINE','doStrainPhlan3',fallback='0') == '1' :
                # STRAINPHLAN
                with open(smpl+'_p2sp.sh','w') as oF:
                    writeBasics('STRAINPHLAN3','sp3');
                    oF.write('echo "Running Strainphlan 3 marker generation" \n')
                    # make folder if it does not exist
                    oF.write('mkdir -p ./'+smpl+'/strainphlan3 \n') 
                    # run strainphlan
                    oF.write('# --- RUN STRAINPHLAN 3 --- \n')                  
                    oF.write(cfg.get('STRAINPHLAN3','samples2markers')+' --nprocs '+cfg.get('STRAINPHLAN3','threads')+' --input '+smpl+'/metaphlan3/'+smpl+'_metaphlan3.sam.bz2'+ ' --output_dir '+smpl+'/strainphlan3'+' 2>&1 | tee '+smpl+'/'+smpl+'_strainphlan3.log'+'\n')
            # =============================================================

            # WRITE PART 2/b (STRAINPHLAN 4) 
            # =============================================================
            if cfg.get('PIPELINE','doStrainPhlan4',fallback='0') == '1' :
                # STRAINPHLAN
                with open(smpl+'_p2sp4.sh','w') as oF:
                    writeBasics('STRAINPHLAN4','sp4');
                    oF.write('echo "Running Strainphlan 4 marker generation" \n')
                    # make folder if it does not exist
                    oF.write('mkdir -p ./'+smpl+'/strainphlan4 \n') 
                    # run strainphlan
                    oF.write('# --- RUN STRAINPHLAN 4 --- \n')                  
                    # -- node TMP --
                    if cfg.get('PIPELINE','useNodeTMP') == '1' and cfg.get('PIPELINE','useSlurm') == '1':
                       tmpSmplF = '${TMPDIR}'+'/'+smpl
                       tmpInput = tmpSmplF+'/metaphlan4/'
                       tmpOut = tmpSmplF+'/strainphlan4/'
                       oF.write('mkdir -p '+tmpInput+'\n')
                       oF.write('mkdir -p '+tmpOut+'\n')
                       oF.write('cp -r '+smpl+'/metaphlan4/*.sam.bz2 '+tmpInput+'\n')
                       oF.write(cfg.get('STRAINPHLAN4','samples2markers')+' --nprocs '+cfg.get('STRAINPHLAN4','threads')+' --input '+tmpInput+smpl+'_metaphlan4.sam.bz2'+ ' --output_dir '+tmpOut+' 2>&1 | tee '+smpl+'/'+smpl+'_strainphlan4.log'+'\n')
                       oF.write('cp '+tmpOut+'/*.pkl '+smpl+'/strainphlan4/'+'\n')
                    # -- no node TMP --
                    else:
                       oF.write(cfg.get('STRAINPHLAN4','samples2markers')+' --nprocs '+cfg.get('STRAINPHLAN4','threads')+' --input '+smpl+'/metaphlan4/'+smpl+'_metaphlan4.sam.bz2'+ ' --output_dir '+smpl+'/strainphlan4'+' 2>&1 | tee '+smpl+'/'+smpl+'_strainphlan4.log'+'\n')
            # =============================================================

            # WRITE PART 3 (HUMANN3) (if required):
            # =============================================================
            if cfg.get('PIPELINE','doHumann3',fallback='0') == '1':
                with open(smpl+'_p3.sh','w') as oF:                    
                    writeBasics('HUMANN3','h')
                    oF.write('echo "Running Humann3" \n')
                    oF.write('# --- RUN HUMANN3 --- \n')
                    # local node temp use:
                    useLS = False;
                    # make folder if it does not eixt
                    oF.write('mkdir -p ./'+smpl+'/humann3 \n') 
                    # node TMP use
                    if cfg.get('PIPELINE','useNodeTMP') == '1' and cfg.get('PIPELINE','useSlurm') == '1':
                        useLS = True;          
                    if useLS:
                        # HUMANN RUN WITH LOCAL NODE TMP
                        sampleDataF = '${TMPDIR}'+'/'+smpl
                        oF.write('# prep node temp folders\n')
                        oF.write('mkdir -p '+sampleDataF+'\n') 
                        oF.write('mkdir -p '+sampleDataF+'/humann3'+'\n')
                        # TMP NODE merge (to save space, adds a bit of write time)
                        oF.write('mkdir -p '+sampleDataF+'/clean_reads'+'\n')                     
                        smplCleanMrgd = sampleDataF+'/clean_reads/'+smpl+'_kneaddata_cleaned_paired_merged.fastq'
                        oF.write('cat '+smpl+'/clean_reads/'+smpl+'_kneaddata_cleaned_pair_1.fastq > '+smplCleanMrgd+'\n')
                        oF.write('cat '+smpl+'/clean_reads/'+smpl+'_kneaddata_cleaned_pair_2.fastq >> '+smplCleanMrgd+'\n')
                        # run it
                        oF.write(cfg.get('HUMANN3','humann')+' --input '+smplCleanMrgd+' --output '+sampleDataF+'/humann3/ --taxonomic-profile '+smpl+'/metaphlan3/'+smpl+'_metaphlan.txt --threads '+cfg.get('HUMANN3','threads')+' --o-log '+smpl+'/'+smpl+'_humann3.log --remove-temp-output'+'\n')
                        # collect data
                        oF.write('cp '+sampleDataF+'/humann3/* '+smpl+'/humann3/\n')
                        # clean node
                        oF.write('rm -r '+sampleDataF+'\n')
                    else:
                        # HUMANN RUN WITHOUT LOCAL NODE TMP
                        oF.write(cfg.get('HUMANN3','humann')+' --input '+smpl+'/clean_reads/'+smpl+'_kneaddata_cleaned_paired_merged.fastq --output '+smpl+'/humann3/ --taxonomic-profile '+smpl+'/metaphlan3/'+smpl+'_metaphlan.txt --threads '+cfg.get('HUMANN3','threads')+' --o-log '+smpl+'/'+smpl+'_humann3.log --remove-temp-output'+'\n')
                    #oF.write('# --- CLEANUP --- \n')
                    #oF.write('echo "Cleaning redundant data"\n')
                    #oF.write('rm -r '+smpl+'/clean_reads/\n')
                    #oF.write('rm -r '+smpl+'/filtering_data/\n')

                    oF.write('echo " --> HUMANN3 DONE !!! <-- "\n')
            # =============================================================
            # END OF PART 3

            # WRITE HUMANN3.6 (if required):
            # =============================================================
            if cfg.get('PIPELINE','doHumann3.6',fallback='0') == '1':
                with open(smpl+'_pH36.sh','w') as oF:                    
                    writeBasics('HUMANN3.6','h36')
                    oF.write('echo "Running Humann3.6 using MP4" \n')
                    oF.write('# --- RUN HUMANN3.6 --- \n')
                    # local node temp use:
                    useLS = False;
                    # make folder if it does not eixt
                    oF.write('mkdir -p ./'+smpl+'/humann3.6 \n') 
                    # node TMP use
                    if cfg.get('PIPELINE','useNodeTMP') == '1' and cfg.get('PIPELINE','useSlurm') == '1':
                        useLS = True;          
                    if useLS:
                        # HUMANN RUN WITH LOCAL NODE TMP
                        sampleDataF = '${TMPDIR}'+'/'+smpl
                        oF.write('# prep node temp folders\n')
                        oF.write('mkdir -p '+sampleDataF+'\n') 
                        oF.write('mkdir -p '+sampleDataF+'/humann3.6'+'\n')                     
                        # TMP NODE merge (to save space, adds a bit of write time)
                        oF.write('mkdir -p '+sampleDataF+'/clean_reads'+'\n')                     
                        smplCleanMrgd = sampleDataF+'/clean_reads/'+smpl+'_kneaddata_cleaned_paired_merged.fastq'
                        oF.write('cat '+smpl+'/clean_reads/'+smpl+'_kneaddata_cleaned_pair_1.fastq > '+smplCleanMrgd+'\n')
                        oF.write('cat '+smpl+'/clean_reads/'+smpl+'_kneaddata_cleaned_pair_2.fastq >> '+smplCleanMrgd+'\n')
                        # run it
                        oF.write(cfg.get('HUMANN3.6','humann')+' --input '+smplCleanMrgd+' --output '+sampleDataF+'/humann3.6/ --taxonomic-profile '+smpl+'/metaphlan4/'+smpl+'_metaphlan.txt --threads '+cfg.get('HUMANN3.6','threads')+' --o-log '+smpl+'/'+smpl+'_humann3.6.log --remove-temp-output'+'\n')
                        # collect data
                        oF.write('cp '+sampleDataF+'/humann3.6/* '+smpl+'/humann3.6/\n')
                        # clean node
                        oF.write('rm -r '+sampleDataF+'\n')
                    else:
                        # HUMANN RUN WITHOUT LOCAL NODE TMP
                        oF.write(cfg.get('HUMANN3.6','humann')+' --input '+smpl+'/clean_reads/'+smpl+'_kneaddata_cleaned_paired_merged.fastq --output '+smpl+'/humann3.6/ --taxonomic-profile '+smpl+'/metaphlan4/'+smpl+'_metaphlan.txt --threads '+cfg.get('HUMANN3.6','threads')+' --o-log '+smpl+'/'+smpl+'_humann3.6.log --remove-temp-output'+'\n')
                    #oF.write('# --- CLEANUP --- \n')
                    #oF.write('echo "Cleaning redundant data"\n')
                    #oF.write('rm -r '+smpl+'/clean_reads/\n')
                    #oF.write('rm -r '+smpl+'/filtering_data/\n')

                    oF.write('echo " --> HUMANN3.6 DONE !!! <-- "\n')
            # =============================================================
            # END OF PART 3

            # WRITE PART AC (CARD shortBRED) (if required):            
            # =============================================================
            if cfg.get('PIPELINE','doCARD_SB',fallback='0') == '1':
                with open(smpl+'_ac.sh','w') as oF:
                    writeBasics('CARD_SB','cs')
                    oF.write('mkdir -p ./'+smpl+'/CARD_SB \n') 
                    oF.write('echo "Running CARD/SB analysis"\n')
                    oF.write('# --- RUN shortBRED vs CARD DB Markers --- \n')
                    # TMP NODE merge (to save space, adds a bit of write time)
                    if cfg.get('PIPELINE','useNodeTMP') == '1':
                       sampleDataF = '${TMPDIR}'+'/'+smpl
                       oF.write('# prep node temp folders\n')
                       oF.write('mkdir -p '+sampleDataF+'\n') 
                       oF.write('mkdir -p '+sampleDataF+'/CARD_SB'+'\n')                     
                       # TMP NODE merge (to save space, adds a bit of write time)
                       oF.write('mkdir -p '+sampleDataF+'/clean_reads'+'\n')                     
                       smplCleanMrgd = sampleDataF+'/clean_reads/'+smpl+'_kneaddata_cleaned_paired_merged.fastq'
                       oF.write('cat '+smpl+'/clean_reads/'+smpl+'_kneaddata_cleaned_pair_1.fastq > '+smplCleanMrgd+'\n')
                       oF.write('cat '+smpl+'/clean_reads/'+smpl+'_kneaddata_cleaned_pair_2.fastq >> '+smplCleanMrgd+'\n')
                    else:
                       sampleDataF = smpl
                       smplCleanMrgd = smpl+'/clean_reads/'+smpl+'_kneaddata_cleaned_paired_merged.fastq'
                    # run it
                    oF.write(cfg.get('CARD_SB','shortbred')+ ' --markers '+cfg.get('CARD_SB','markers')+' --wgs '+smplCleanMrgd+' --threads '+cfg.get('CARD_SB','threads')+' --results '+smpl+'/CARD_SB/'+smpl+'_CARD_sb.txt'+' --tmp '+sampleDataF+'/CARD_SB_tmp'+' --usearch '+cfg.get('CARD_SB','usearch')+'\n')
                    # CLEANUP
                    oF.write('rm -r '+sampleDataF+'/CARD_SB_tmp'+'\n')
            # =============================================================
            # ---- END OF CARD/SB (part AC) ----
 
            # WRITE PART VS (VFDB shortBRED) (if required):
            # =============================================================
            if cfg.get('PIPELINE','doVFDB_SB',fallback='0') == '1':
                with open(smpl+'_vs.sh','w') as oF:
                    writeBasics('VFDB_SB','vs')
                    oF.write('mkdir -p ./'+smpl+'/VFDB_SB \n') 
                    oF.write('echo "Running VFDB_SB analysis"\n')
                    oF.write('# --- RUN shortBRED vs VFDB DB Markers --- \n')
                    if cfg.get('PIPELINE','useNodeTMP') == '1':
                       sampleDataF = '${TMPDIR}'+'/'+smpl
                       oF.write('# prep node temp folders\n')
                       oF.write('mkdir -p '+sampleDataF+'\n') 
                       oF.write('mkdir -p '+sampleDataF+'/VFDB_SB'+'\n')                     
                       # TMP NODE merge (to save space, adds a bit of write time)
                       oF.write('mkdir -p '+sampleDataF+'/clean_reads'+'\n')                     
                       smplCleanMrgd = sampleDataF+'/clean_reads/'+smpl+'_kneaddata_cleaned_paired_merged.fastq'
                       oF.write('cat '+smpl+'/clean_reads/'+smpl+'_kneaddata_cleaned_pair_1.fastq > '+smplCleanMrgd+'\n')
                       oF.write('cat '+smpl+'/clean_reads/'+smpl+'_kneaddata_cleaned_pair_2.fastq >> '+smplCleanMrgd+'\n')
                   
                    else:
                       sampleDataF = smpl
                       smplCleanMrgd = smpl+'/clean_reads/'+smpl+'_kneaddata_cleaned_paired_merged.fastq'
                    # run it
                    oF.write(cfg.get('VFDB_SB','shortbred')+ ' --markers '+cfg.get('VFDB_SB','markers')+' --wgs '+smplCleanMrgd+' --threads '+cfg.get('VFDB_SB','threads')+' --results '+smpl+'/VFDB_SB/'+smpl+'_vfdb_sb.txt'+' --tmp '+sampleDataF+'/VFDB_SB_tmp'+' --usearch '+cfg.get('VFDB_SB','usearch')+'\n')
                    # CLEANUP
                    oF.write('rm -r '+sampleDataF+'/VFDB_SB_tmp'+'\n')
            # =============================================================
            # ---- END OF VFDB/SB (part VS) ----

            # WRITE ASSEMBLY JOB (metaspades)
            # =============================================================
            if cfg.get('PIPELINE','doAssemblyMetaSpades',fallback='0') == '1':
                with open(smpl+'_aMS.sh','w') as oF:
                    writeBasics('ASSEMBLY_METASPADES','aMS')
                    oF.write('echo "Running METASPADES Assembly"\n')
                    oF.write('# --- RUN MetaSpades Assembly --- \n')                                        
                    outFolder = smpl+'/assembly_metaspades'
                    oF.write('mkdir -p '+outFolder+'\n')
                    if cfg.get('PIPELINE','useNodeTMP') == '1' and cfg.get('PIPELINE','useSlurm') == '1':
                        outFolderTmp = '${TMPDIR}/'+smpl+'/assembly_metaspades/tmp'
                        oF.write('# prep Node TMP\n')
                        oF.write('mkdir -p ${TMPDIR}/'+smpl+'\n')
                        oF.write('mkdir -p ${TMPDIR}/'+smpl+'/assembly_metaspades'+'\n')
                        oF.write('mkdir -p '+outFolderTmp+'\n')
                    else:
                        outFolderTmp = outFolder+'/tmp'
                    # prep job                         
                    oF.write(cfg.get('ASSEMBLY_METASPADES','assemblerPath')+ ' -1 '+smpl+'/clean_reads/'+smpl+'_kneaddata_cleaned_pair_1.fastq'+' -2 '+smpl+'/clean_reads/'+smpl+'_kneaddata_cleaned_pair_2.fastq'+' -o '+outFolderTmp+' -m '+cfg.get('ASSEMBLY_METASPADES','memory').replace('gb','')+' -t '+cfg.get('ASSEMBLY_METASPADES','threads')+' '+cfg.get('ASSEMBLY_METASPADES','extraparams')+ '\n')
                    # copy data
                    oF.write('mv '+outFolderTmp+'/scaffolds.fasta '+outFolder+'/'+smpl+'_metaspades_scaffolds.fa'+'\n')
                    oF.write('mv '+outFolderTmp+'/contigs.fasta '+outFolder+'/'+smpl+'_metaspades_contigs.fa'+'\n')
                    oF.write('mv '+outFolderTmp+'/spades.log '+outFolder+'/'+smpl+'_metaspades_log.log'+'\n')
                    # remove tmp
                    oF.write('rm -r '+outFolderTmp+'\n')                              
                    # run quast
            # ========= END OF ASSEMBLY JOB (metaspades) ==================
            # =============================================================

            # WRITE ASSEMBLY JOB (megahit)
            # =============================================================
            if cfg.get('PIPELINE','doAssemblyMegaHit',fallback='0') == '1':
                with open(smpl+'_aMH.sh','w') as oF:
                    writeBasics('ASSEMBLY_MEGAHIT','aMH')
                    oF.write('echo "Running MEGAHIT Assembly"\n')
                    oF.write('# --- RUN MegaHit Assembly --- \n')                    
                    outFolder = smpl+'/assembly_megahit'
                    oF.write('mkdir -p '+outFolder+'\n')

                    if cfg.get('PIPELINE','useNodeTMP') == '1' and cfg.get('PIPELINE','useSlurm') == '1':
                        outFolderTmp = '${TMPDIR}/'+smpl+'/assembly_megahit/tmp'
                        outFolderTmp2 = '${TMPDIR}/'+smpl+'/assembly_megahit/tmp2'
                        oF.write('# prep Node TMP\n')
                        oF.write('mkdir -p ${TMPDIR}/'+smpl+'\n')
                        oF.write('mkdir -p ${TMPDIR}/'+smpl+'/assembly_megahit'+'\n')
                        #oF.write('mkdir -p '+outFolderTmp+'\n')
                        oF.write('mkdir -p '+outFolderTmp2+'\n')
                    else:
                        outFolderTmp = outFolder+'/tmp'
                        outFolderTmp2 = outFolder+'/tmp2'
                        oF.write('mkdir -p '+outFolderTmp2+'\n')
                    # prep job                         
                    oF.write(cfg.get('ASSEMBLY_MEGAHIT','assemblerPath')+ ' -1 '+smpl+'/clean_reads/'+smpl+'_kneaddata_cleaned_pair_1.fastq'+' -2 '+smpl+'/clean_reads/'+smpl+'_kneaddata_cleaned_pair_2.fastq'+' -o '+outFolderTmp+' -m '+cfg.get('ASSEMBLY_MEGAHIT','memory').replace('gb','')+' -t '+cfg.get('ASSEMBLY_MEGAHIT','threads')+' --tmp-dir '+outFolderTmp2+'\n')
                    # copy data
                    oF.write('mv '+outFolderTmp+'/final.contigs.fa '+outFolder+'/'+smpl+'_megahit_contigs.fa'+'\n')
                    oF.write('mv '+outFolderTmp+'/log '+outFolder+'/'+smpl+'_megahit_log.log'+'\n')
                    # remove tmp
                    oF.write('rm -r '+outFolderTmp+'\n')                              
                    oF.write('rm -r '+outFolderTmp2+'\n')                              
                    # run binning (if required)
                    if cfg.get('PIPELINE','doBinningMWrap',fallback=0) == '1':
                        writeNextJob('BINNING_METAWRAP','bMW') 
            # ========= END OF ASSEMBLY JOB (megahit)  ====================
            # =============================================================

            # WRITE BINNING JOB (metawrap binners)
            # =============================================================
            if cfg.get('PIPELINE','doBinningMWrap',fallback=0) == '1':
                with open(smpl+'_bMW.sh','w') as oF:
                    writeBasics('BINNING_METAWRAP','bMW')
                    # fix reads to avoid binner problems (repair.sh from BBMap)
                    oF.write('# --- FIX / PREP CLEAN READS FOR BINNING --- "\n')
                    oF.write('echo "Prepping cleaned reads for binners"\n')
                    readsTmpF = '${TMPDIR}/'+smpl+'/reads_fixed'
                    oF.write('mkdir -p '+readsTmpF+'\n')                    
                    cleanReads1 = smpl+'/clean_reads/'+smpl+'_kneaddata_cleaned_pair_1.fastq'
                    cleanReads2 = smpl+'/clean_reads/'+smpl+'_kneaddata_cleaned_pair_2.fastq'
                    fixedReads1 = readsTmpF+'/'+smpl+'_rdy_1.fastq'
                    fixedReads2 = readsTmpF+'/'+smpl+'_rdy_2.fastq'
                    fixedReadsS = readsTmpF+'/'+smpl+'_s.fastq'
                    oF.write('repair.sh in='+cleanReads1+' in2='+cleanReads2+' out='+fixedReads1+' out2='+fixedReads2+' outs='+fixedReadsS+'\n')
                    # run metawrap binners
                    oF.write('# --- RUN MetaWrap Binners --- \n')                    
                    oF.write('echo "Running MetaWrap Binners"\n')
                    # define which contigs to use   
                    if cfg.get('BINNING_METAWRAP','assembler') == 'MEGAHIT':    
                       contigs = smpl+'/assembly_megahit/'+smpl+'_megahit_contigs.fa'
                    elif cfg.get('BINNING_METAWRAP','assembler') == 'METASPADES':
                       contigs = smpl+'/assembly_metaspades/'+smpl+'_metaspades_scaffolds.fa'
                    else: 
                       print('ERROR: [BINNING_METAWRAP] assembler has to be "MEGAHIT" or "METASPADES"!!')
                       exit(1)
                    tmpOutF='${TMPDIR}/'+smpl+'/bins_metawrap'
                    contigLt = cfg.get('BINNING_METAWRAP','minContigLength')
                    # prep tmp folder
                    oF.write('mkdir -p '+tmpOutF+'\n')
                    # run metawrap binners
                    oF.write('metawrap binning -m '+cfg.get('BINNING_METAWRAP','memory').replace('gb','')+' -t '+cfg.get('BINNING_METAWRAP','threads')+' -a '+contigs+' -o '+tmpOutF+' --metabat2 --maxbin2 --concoct -l '+contigLt+' '+fixedReads1+' '+fixedReads2+'\n')
                    # collect results
                    oF.write('echo " collecting results! "\n')
                    outFolder = smpl+'/bins_metawrap'
                    oF.write('mkdir -p '+outFolder+'\n')
                    oF.write('mv '+tmpOutF+'/concoct_bins/'+' '+outFolder+'\n')
                    oF.write('mv '+tmpOutF+'/maxbin2_bins/'+' '+outFolder+'\n')
                    oF.write('mv '+tmpOutF+'/metabat2_bins/'+' '+outFolder+'\n')
                    oF.write('rm '+outFolder+'/metabat2_bins/bin.unbinned.fa'+'\n')
                    oF.write('rm '+outFolder+'/concoct_bins/unbinned.fa'+'\n')
                    # clean tmp
                    oF.write('rm -r '+tmpOutF+'\n')
                    oF.write('rm -r '+readsTmpF+'\n')
                    # run BIN REFINING (if required)
                    if cfg.get('PIPELINE','doBinRefiningMWrap',fallback=0) == '1':
                        writeNextJob('BIN_REFINING_METAWRAP','bMWr') 
            # ========= END OF METAWRAP BINNING JOB ====================
            # =============================================================

            # WRITE BIN REFINING JOB (metawrap bins)
            # =============================================================
            if cfg.get('PIPELINE','doBinRefiningMWrap',fallback=0) == '1':
                with open(smpl+'_bMWr.sh','w') as oF:
                    writeBasics('BIN_REFINING_METAWRAP','bMWr')
                    tmpInputF='${TMPDIR}/'+smpl
                    tmpOutputF=tmpInputF+'/bins_metawrap_refined'
                    outFolder=smpl+'/bins_metawrap_refined'
                    cont=cfg.get('BIN_REFINING_METAWRAP','CONTAMINATION_MAX')
                    comp=cfg.get('BIN_REFINING_METAWRAP','COMPLETENESS_MIN')
                    memGB=cfg.get('BIN_REFINING_METAWRAP','memory').replace('gb','')
                    nrThreads=cfg.get('BIN_REFINING_METAWRAP','threads').replace('gb','')
                    # prep TMP folders
                    oF.write('mkdir -p '+tmpInputF+'\n')
                    oF.write('mkdir -p '+tmpInputF+'/bins_maxbin2'+'\n')
                    oF.write('mkdir -p '+tmpInputF+'/bins_concoct'+'\n')
                    oF.write('mkdir -p '+tmpInputF+'/bins_metabat2'+'\n')
                    oF.write('mkdir -p '+tmpOutputF+'\n')
                    # copy data to TMP [concoct_bins/  maxbin2_bins/  metabat2_bins/]
                    oF.write('cp -r '+smpl+'/bins_metawrap/maxbin2_bins/*.fa '+tmpInputF+'/bins_maxbin2'+'\n')
                    oF.write('cp -r '+smpl+'/bins_metawrap/metabat2_bins/*.fa '+tmpInputF+'/bins_metabat2'+'\n')
                    oF.write('cp -r '+smpl+'/bins_metawrap/concoct_bins/*.fa '+tmpInputF+'/bins_concoct'+'\n')
                    # run metawrap refining  [using node tmp]
                    oF.write('metawrap bin_refinement -t '+nrThreads+' -m '+memGB+' --quick -c '+comp+' -x '+cont+' -o '+tmpOutputF+' -A '+tmpInputF+'/bins_maxbin2 -B '+tmpInputF+'/bins_metabat2 -C '+tmpInputF+'/bins_concoct'+'\n')
                    # collect data
                    oF.write('mkdir -p '+outFolder+'\n')
                    oF.write('rm -r '+tmpOutputF+'/bins_maxbin2/'+'\n')
                    oF.write('rm -r '+tmpOutputF+'/bins_metabat2/'+'\n')
                    oF.write('rm -r '+tmpOutputF+'/bins_concoct/'+'\n')
                    oF.write('rm -r '+tmpOutputF+'/work_files/'+'\n')
                    oF.write('rm '+tmpOutputF+'/*'+'\n')
                    oF.write('cp -r '+tmpOutputF+'/metawrap_'+comp+'_'+cont+'_bins/*.fa '+outFolder+'/'+'\n')
                    # cleanup
                    oF.write('rm -r '+tmpInputF+'\n')
                    oF.write('rm -r '+tmpOutputF+'\n')                
                    # rename bins
                    oF.write('for b in '+outFolder+'/bin*.fa; do mv ${b} ${b/bin./'+smpl+'.bin.}; done\n')
                    # run annotation
                    if cfg.get('PIPELINE','doBinAnnotationCheckM',fallback=0) == '1':
                        writeNextJob('BIN_ANNOTATION_CHECKM','bACh')
                    if cfg.get('PIPELINE','doBinAnnotationGTDBK',fallback=0) == '1':
                        writeNextJob('BIN_ANNOTATION_GTDBK','bAgt')
                    if cfg.get('PIPELINE','doBinQuantification',fallback=0) == '1':
                        writeNextJob('BIN_QUANTIFICATION','bQ')

            # ========= END OF METAWRAP REFINING JOB ====================
            # =============================================================


            # WRITE BIN QUANTIFICATION JOB (metaWrap)
            # =============================================================
            if cfg.get('PIPELINE','doBinQuantification',fallback=0) == '1':
                with open(smpl+'_bQ.sh','w') as oF:
                    writeBasics('BIN_QUANTIFICATION','bQ')
                    inputF=smpl+'/'+cfg.get('BIN_QUANTIFICATION','input').strip()
                    tmpInputF='${TMPDIR}/'+smpl+'/'+cfg.get('BIN_QUANTIFICATION','input').strip()
                    tmpOutputF='${TMPDIR}/'+smpl+'/bins_quantification'
                    outFolder=smpl+'/bins_quantification'
                    nrThreads=cfg.get('BIN_QUANTIFICATION','threads').strip()
                    cleanReads1 = smpl+'/clean_reads/'+smpl+'_kneaddata_cleaned_pair_1.fastq'
                    cleanReads2 = smpl+'/clean_reads/'+smpl+'_kneaddata_cleaned_pair_2.fastq'
                    # prep TMP folders
                    oF.write('mkdir -p '+tmpInputF+'\n')
                    oF.write('mkdir -p '+tmpOutputF+'\n')
                    # copy data to TMP
                    oF.write('cp '+inputF+'/*.fa '+tmpInputF+'\n')
                    # run bin quantification
                    #oF.write('checkm lineage_wf -t 8 -f '+tmpInputF+'/'+smpl+'_checkM_results_parsed.csv -x fa '+tmpInputF+' '+tmpOutputF+' --tab_table --pplacer_threads 8'+'\n')
                    oF.write('metawrap quant_bins'+' -t '+nrThreads+' -b '+tmpInputF+' -o '+tmpOutputF+' '+cleanReads1+' '+cleanReads2+'\n') 
                    # collect data
                    oF.write('mkdir -p '+outFolder+'\n')
                    oF.write('cp '+tmpOutputF+'/bin_abundance_table.tab '+outFolder+'/'+smpl+'_bin_abundances.txt'+'\n')
                    # cleanup
                    oF.write('rm -r '+tmpInputF+'\n')
                    oF.write('rm -r '+tmpOutputF+'\n')                
            # ========= END OF BIN ANNOTATION (CHECKM) ====================
            # =============================================================

            # WRITE BIN ANNOTATION JOB (checkM)
            # =============================================================
            if cfg.get('PIPELINE','doBinAnnotationCheckM',fallback=0) == '1':
                with open(smpl+'_bACh.sh','w') as oF:
                    writeBasics('BIN_ANNOTATION_CHECKM','bACh')
                    inputF=smpl+'/'+cfg.get('BIN_ANNOTATION_CHECKM','input').strip()
                    tmpInputF='${TMPDIR}/'+smpl+'/'+cfg.get('BIN_ANNOTATION_CHECKM','input').strip()
                    tmpOutputF=tmpInputF+'/bins_checkM'
                    outFolder=smpl+'/bins_checkM'
                    nrThreads=cfg.get('BIN_ANNOTATION_CHECKM','threads').strip()
                    # prep TMP folders
                    oF.write('mkdir -p '+tmpInputF+'\n')
                    oF.write('mkdir -p '+tmpOutputF+'\n')
                    # copy data to TMP
                    oF.write('cp '+inputF+'/*.fa '+tmpInputF+'\n')
                    # run checkM
                    oF.write('checkm lineage_wf -t 8 -f '+tmpInputF+'/'+smpl+'_checkM_results_parsed.csv -x fa '+tmpInputF+' '+tmpOutputF+' --tab_table --pplacer_threads 8'+'\n')
                    # collect data
                    oF.write('mkdir -p '+outFolder+'\n')
                    oF.write('mv '+tmpInputF+'/'+smpl+'_checkM_results_parsed.csv '+outFolder+'\n')
                    # cleanup
                    oF.write('rm -r '+tmpInputF+'\n')
                    oF.write('rm -r '+tmpOutputF+'\n')                
            # ========= END OF BIN ANNOTATION (CHECKM) ====================
            # =============================================================

            # WRITE BIN ANNOTATION JOB (gtdbtk)
            # =============================================================
            if cfg.get('PIPELINE','doBinAnnotationGTDBK',fallback=0) == '1':
                with open(smpl+'_bAgt.sh','w') as oF:
                    writeBasics('BIN_ANNOTATION_GTDBK','bAgt')
                    inputF=smpl+'/'+cfg.get('BIN_ANNOTATION_GTDBK','input').strip()
                    tmpInputF='${TMPDIR}/'+smpl+'/'+cfg.get('BIN_ANNOTATION_GTDBK','input').strip()
                    tmpOutputF=tmpInputF+'/bins_GTDBK'
                    outFolder=smpl+'/bins_GTDBK'
                    nrThreads=cfg.get('BIN_ANNOTATION_GTDBK','threads').strip()
                    mashDB=cfg.get('BIN_ANNOTATION_GTDBK','mashDB',fallback='')
                    
                    # set path
                    oF.write('GTDBTK_DATA_PATH='+cfg.get('BIN_ANNOTATION_GTDBK','GTDBK_DB').strip()+'\n')
                    # prep TMP folders
                    oF.write('mkdir -p '+tmpInputF+'\n')
                    oF.write('mkdir -p '+tmpOutputF+'\n')
                    # copy data to TMP
                    oF.write('cp '+inputF+'/*.fa '+tmpInputF+'\n')
                    # run GTDBK
                    if not mashDB == '':
                       oF.write('gtdbtk classify_wf --mash_db '+mashDB+' --genome_dir '+tmpInputF+' --out_dir '+tmpOutputF+' --extension .fa --cpus '+nrThreads+'\n')                     
                    else: 
                       oF.write('gtdbtk classify_wf --skip_ani_screen '+mashDB+' --genome_dir '+tmpInputF+' --out_dir '+tmpOutputF+' --extension .fa --cpus '+nrThreads+'\n')                     
                    # collect data
                    oF.write('mkdir -p '+outFolder+'\n')
                    oF.write('cp '+tmpOutputF+'/identify/* '+outFolder+'\n')
                    oF.write('cp '+tmpOutputF+'/classify/*.tsv '+outFolder+'\n')
                    # cleanup
                    oF.write('rm -r '+tmpInputF+'\n')
                    oF.write('rm -r '+tmpOutputF+'\n')
                    # rename
                    oF.write('for F in '+outFolder+'/gtdbtk*.tsv'+'\n')
                    oF.write('do mv ${F} ${F/gtdbtk/'+smpl+'.gtdbk}\n')
                    oF.write('done')                  
            # ========= END OF BIN ANNOTATION (GTDBK) ====================
            # =============================================================


            # WRITE KRAKEN2 JOB
            # =============================================================
            if cfg.get('PIPELINE','doKraken2',fallback='0') == '1':
                with open(smpl+'_pK2.sh','w') as oF:
                    writeBasics('KRAKEN2','aK2')
                    oF.write('echo "Running KRAKEN2 profiling"\n')
                    oF.write('# --- RUN KRAKEN2 --- \n')                    
                    outFolder = smpl+'/kraken2'
                    oF.write('mkdir -p '+outFolder+'\n')
                    # kraken2 run
                    oF.write('# >> RUN KRAKEN2\n')  
                    oF.write(cfg.get('KRAKEN2','krakenPath')+ ' --db '+cfg.get('KRAKEN2','krakenDB')+' --threads '+cfg.get('KRAKEN2','threads')+' --output - --paired '+ ' --report '+outFolder+'/'+smpl+'.kreport '+ cfg.get('KRAKEN2','krakenExtraParams') +' '+ smpl+'/clean_reads/'+smpl+'_kneaddata_cleaned_pair_1.fastq'+' '+smpl+'/clean_reads/'+smpl+'_kneaddata_cleaned_pair_2.fastq' +'\n')
                    # kraken2 report fixer (makes UHGG kraken2 database report compatible with bracken)
                    oF.write('# >> RUN KRAKEN2 report fixed script (makes K2 UHGG DB report BRACKEN compatible)\n')  
                    oF.write('python '+cfg.get('KRAKEN2','krakenReportFixer')+' '+outFolder+'/'+smpl+'.kreport '+'\n')
                    # convert KRAKEN2 results into Metaphlan3-compatible format
                    #oF.write('python '+cfg.get('KRAKEN2','krakenToMP3')+' --infile '+outFolder+'/'+smpl+'.kreport.bc'+' --out '+outFolder+'/'+smpl+'.kreport.bc.mp3.txt'+ '\n')
                    # BRACKEN run
                    oF.write('# >> RUN BRACKEN \n')
                    oF.write(cfg.get('KRAKEN2','brackenPath')+' -d '+cfg.get('KRAKEN2','krakenDB')+' -i '+outFolder+'/'+smpl+'.kreport.bc '+' -w '+outFolder+'/'+smpl+'.bracken.result.kr'+' -o '+outFolder+'/'+smpl+'.bracken.result.kr -t '+cfg.get('KRAKEN2','brackenReadThreshold')+' -l '+cfg.get('KRAKEN2','brackenLevel')+' -r '+cfg.get('KRAKEN2','brackenReadLt')+' '+cfg.get('KRAKEN2','brackenExtraParams')+'\n')
                    # convert BRACKEN results into Metaphlan3-compatible format
                    oF.write('python '+cfg.get('KRAKEN2','krakenToMP3')+' --infile '+outFolder+'/'+smpl+'.bracken.result.kr'+' --out '+outFolder+'/'+smpl+'.bracken.result.mp3.txt'+ '\n')
            # ========= END OF CLASSIFICATION JOB (KRAKEN2)  ==============
            # =============================================================

            # WRITE SVFINDER JOB (part I)
            # =============================================================
            if cfg.get('PIPELINE','doSVFinder',fallback=0) == '1':
                with open(smpl+'_pSV.sh','w') as oF:
                    writeBasics('SVFINDER','aSV',purgeConda=False,purgeModsAfterConda=False)
                    oF.write('echo "Running SVFINDER"\n')
                    oF.write('# --- do read pairing / sorting --- \n')                    
                    outFolder = smpl+'/SVs'
                    oF.write('mkdir -p '+outFolder+'\n')

                    
                    # sort the data
                    oF.write('echo "RUNNING fastq_pair!" \n')
                    oF.write(cfg.get('SVFINDER','fastq_pair')+' '+smpl+'/clean_reads/'+smpl+'_kneaddata_cleaned_pair_1.fastq'+' '+smpl+'/clean_reads/'+smpl+'_kneaddata_cleaned_pair_2.fastq' +'\n')
                    oF.write('echo   ">> done!" \n')
                    oF.write('echo "Renaming and moving files" \n')
                    # rename sorted data
                    oF.write('mv '+smpl+'/clean_reads/'+smpl+'_kneaddata_cleaned_pair_1.fastq.paired.fq'+' '+outFolder+'/'+smpl+'_SVready_1.fastq' +'\n')
                    oF.write('mv '+smpl+'/clean_reads/'+smpl+'_kneaddata_cleaned_pair_2.fastq.paired.fq'+' '+outFolder+'/'+smpl+'_SVready_2.fastq' +'\n')
                    oF.write('echo   ">> done!" \n')
                    # run ICRA
                    oF.write('echo "Running ICRA" \n')
                    oF.write('python '+cfg.get('SVFINDER','ICRA')+' '+outFolder+' '+outFolder+'/'+smpl+'_SVready '+'--pe '+' --threads '+cfg.get('SVFINDER','threads')+'\n')
                    oF.write('echo   ">> done!" \n')
                    # run SVfinder
                    oF.write('echo "Submitting SVfinder" \n')
                    writeNextJob('SVFINDER2','pSV2')
                    oF.write('echo   ">> done!" \n')
            # ========= END OF SVFINDER part I ===========================
            # =============================================================

            # WRITE SVFINDER JOB (part II)
            # =============================================================
            if cfg.get('PIPELINE','doSVFinder',fallback=0) == '1':
                with open(smpl+'_pSV2.sh','w') as oF:
                    writeBasics('SVFINDER2','aSV2',purgeConda=False,purgeModsAfterConda=True)
                    oF.write('echo "Running SVFINDER (part II)"\n')
                    # run SVfinder
                    oF.write('echo "Running SVfinder" \n')
                    oF.write('python '+cfg.get('SVFINDER2','SGVF')+' '+outFolder+'/'+smpl+'_SVready.jsdel '+outFolder+'/'+smpl+'_SVs.mapped.jsdel ' +cfg.get('SVFINDER2','SGVF_READL')+' --x_coverage '+cfg.get('SVFINDER2','SGVF_COV')+' --rate_param '+cfg.get('SVFINDER2','SGVF_RATEPARAM')+'\n')
                    # cleanup
                    if cfg.get('SVFINDER2','CLEANUP') == '1':
                       oF.write('rm '+outFolder+'/'+smpl+'_SVready.jsdel'+'\n')
                       oF.write('rm '+outFolder+'/'+smpl+'_SVready_1.fastq'+'\n')
                       oF.write('rm '+outFolder+'/'+smpl+'_SVready_2.fastq'+'\n')
                       oF.write('rm '+outFolder+'/'+smpl+'_SVready.pmp'+'\n')                    
                    oF.write('echo   ">> done!" \n')
            # ========= END OF SVFINDER part 1 ===========================
            # =============================================================

            # WRITE PANPHLAN (part I, mapping)
            # =============================================================
            if cfg.get('PIPELINE','doPanphlan',fallback=0) == '1':
                clades = cfg.get('PANPHLAN','clades').strip().split(',')
                if cfg.get('PANPHLAN','domulticlades') == '0':
                    clades = clades[0]
                #oneclade = clades[0]
                jobnr = 0
                for oneclade in clades:
                    jobnr += 1
                    jobnrs = 'pp'+str(jobnr).zfill(2)
                    with open(smpl+'_'+jobnrs+'.sh','w') as oF:
                        writeBasics('PANPHLAN',jobnrs,purgeConda=False,purgeModsAfterConda=True)
                        outFolder = smpl+'/Panphlan/'+oneclade
                        if cfg.get('PIPELINE','useNodeTMP') == '1' and cfg.get('PIPELINE','useSlurm') == '1':
                            tmpFolder = '${TMPDIR}/'+smpl+'/Panphlan/'+oneclade+'/tmp'
                        else:
                            tmpFolder = smpl+'/Panphlan/'+oneclade+'/tmp' 
                        oF.write('echo "Running Panphlan mapping"\n')
                        oF.write('mkdir -p '+outFolder+'\n')
                        oF.write('mkdir -p '+tmpFolder+'\n')
                        # panphlan map
                        #   prep files
                        # TMP NODE merge (to save space, adds a bit of write time)
                        if cfg.get('PIPELINE','useNodeTMP') == '1':
                           oF.write('mkdir -p '+sampleDataF+'/clean_reads'+'\n')                     
                           inFile = sampleDataF+'/clean_reads/'+smpl+'_kneaddata_cleaned_paired_merged.fastq'
                           oF.write('cat '+smpl+'/clean_reads/'+smpl+'_kneaddata_cleaned_pair_1.fastq > '+inFile+'\n')
                           oF.write('cat '+smpl+'/clean_reads/'+smpl+'_kneaddata_cleaned_pair_2.fastq >> '+inFile+'\n')
                        else:
                           inFile = smpl+'/clean_reads/'+smpl+'_kneaddata_cleaned_paired_merged.fastq'
                        # run it
                        panGenome = cfg.get('PANPHLAN','panphlan_DBs')+'/'+oneclade+'/'+oneclade+'_pangenome.tsv'
                        pangIndex = cfg.get('PANPHLAN','panphlan_DBs')+'/'+oneclade+'/'+oneclade
                        outFile = smpl+'_'+oneclade+'_pp.csv'
                        #   write command
                        oF.write(cfg.get('PANPHLAN','panphlan_map')+' -i '+inFile+' -p '+panGenome+' --indexes '+pangIndex+' -o '+outFolder+'/'+outFile+' --nproc '+cfg.get('PANPHLAN','threads')+' -m '+cfg.get('PANPHLAN','memory').replace('gb','').replace('GB','')+' --tmp '+tmpFolder+'\n')
                        # sort the data                    
                        oF.write('echo ">> done!" \n')
            # ========= END OF PANPHLAN MAP     ===========================
            # =============================================================

        # if sample is unpaired, find it
        else:            
            unpaired = False
            for d in dataFnd:
                if d[0] == smpl: unpaired = d; break
            # ready for job writing
            print (unpaired)
        
