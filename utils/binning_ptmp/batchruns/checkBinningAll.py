# ===================================
# R. Gacesa (UMCG, 2022)
#
# > checks binning steps for samples
#   in current folder
#
# ===================================
import os
# CONFIG
fbinner = 'DAS'

# ===============
#   all samples
allS = set()
#   preppers
prepCoverM = set()
prepMetabinnerCov = set()
prepBAM = set()
prepMinimapBAM = set()
#   bins
binsMaxbin2 = set()
binsMetabat2 = set()
binsConcoct = set()
binsVAMB = set()
binsSemibin = set()
binsGraphbin = set()
binsMetaWrap = set()
binsDAS = set()
binsMetaCOAG = set()
#    >  reassembled
binsReassembled = set()
#   checkM
checkmConcoct = set()
checkmMetabat2 = set()
checkmMaxbin2 = set()
checkmMetaCOAG = set()
checkmVAMB = set()
checkmSemibin = set()
checkmGraphbin = set()
checkmDAS = set()
checkmMetaWrap = set()
checkmReassembled = set()
#   GTDBK
gtdbkMetabat2 = set()
gtdbkMaxbin2 = set()
gtdbkConcoct = set()
gtdbkMetaCOAG = set()
gtdbkVAMB = set()
gtdbkSemibin = set()
gtdbkGraphbin = set()
gtdbkDAS = set()
gtdbkMetaWrap = set()
gtdbkReassembled = set()
#   QUANTIFIED
binsQuantified = set()

# iterate over samples in "."
print(' > checking status of BINNING in .')
for f in os.listdir('.'):
   if f == 'JOB_OUT': continue
   if os.path.isdir(f):
      print(' >> checking ',f)
      allS.add(f)
      # drill into folder, check for binning steps:
      for ff in os.listdir(os.path.join('.',f)):
         #print('   >>> ',ff)
         # binning preppers
#         print(os.path.join(f,ff,'abundance.tsv'))
         if ff == 'assembly_coverage_coverm' and os.path.isfile(os.path.join(f,ff,'abundance.tsv')):
             #print('    >>> coverM: ',f)
             prepCoverM.add(f)
         if ff == 'assembly_coverage_metabinner' and os.path.isfile(os.path.join(f,ff,'coverage_profile_f1k.tsv')):
             #print('    >>> metabinner coverage: ',f)
             prepMetabinnerCov.add(f)
         if ff == 'assembly_coverage_metabinner' and os.path.isfile(os.path.join(f,ff,f+'_kneaddata_cleaned_repaired.bam')):
             #print('    >>> metabinner bam: ',f)
             prepBAM.add(f)
         if ff == 'assembly_coverage_minimap2' and os.path.isfile(os.path.join(f,ff,'sample_cov_minimap2.bam')):
             #print('    >>> minimap2 bam: ',f)
             prepMinimapBAM.add(f)
         # binners
         try: 
            if ff == 'bins_concoct' and len(os.listdir(os.path.join(f,ff))) > 0:
                binsConcoct.add(f)
         except: 
            pass
         try: 
            if ff == 'bins_maxbin2' and len(os.listdir(os.path.join(f,ff))) > 0:
                binsMaxbin2.add(f)
         except: 
            pass
         try:
            if ff == 'bins_metabat2' and len(os.listdir(os.path.join(f,ff))) > 0:
                binsMetabat2.add(f)
         except:
            pass
         try:
            if ff == 'bins_semibin' and len(os.listdir(os.path.join(f,ff))) > 0:
                binsSemibin.add(f)
         except:
            pass
         try:
            if ff == 'bins_vamb' and len(os.listdir(os.path.join(f,ff))) > 0:
                binsVAMB.add(f)
         except:
            pass
         try:
            if ff == 'bins_metaCOAG' and len(os.listdir(os.path.join(f,ff))) > 0:
                binsMetaCOAG.add(f)
         except:
            pass
         try:
            if ff == 'bins_graphBin' and len(os.listdir(os.path.join(f,ff))) > 0:
                binsGraphbin.add(f)
         except:
            pass
         try:
            if ff == 'bins_DAS' and len(os.listdir(os.path.join(f,ff))) > 0:
                binsDAS.add(f)
         except:
            pass
         try:
            if ff == 'bins_metawrap_refined' and len(os.listdir(os.path.join(f,ff))) > 0:
                binsMetaWrap.add(f)
         except:
            pass
         try:
            if ff == 'bins_reassembled' and len(os.listdir(os.path.join(f,ff))) > 0:
                binsReassembled.add(f)
         except:
            pass
         # checkM
         if ff == 'checkM_all' and os.path.isfile(os.path.join(f,ff,'bins_maxbin2_checkM_results_parsed.csv')):
            if os.path.getsize(os.path.join(f,ff,'bins_maxbin2_checkM_results_parsed.csv')) > 150:
                checkmMaxbin2.add(f)
         if ff == 'checkM_all' and os.path.isfile(os.path.join(f,ff,'bins_metabat2_checkM_results_parsed.csv')):
            if os.path.getsize(os.path.join(f,ff,'bins_metabat2_checkM_results_parsed.csv')) > 150:
                checkmMetabat2.add(f)
         if ff == 'checkM_all' and os.path.isfile(os.path.join(f,ff,'bins_concoct_checkM_results_parsed.csv')):
            if os.path.getsize(os.path.join(f,ff,'bins_concoct_checkM_results_parsed.csv')) > 150:
                checkmConcoct.add(f)
         if ff == 'checkM_all' and os.path.isfile(os.path.join(f,ff,'bins_DAS_checkM_results_parsed.csv')):
            if os.path.getsize(os.path.join(f,ff,'bins_DAS_checkM_results_parsed.csv')) > 150:
                checkmDAS.add(f)
         if ff == 'checkM_all' and os.path.isfile(os.path.join(f,ff,'bins_graphBin_checkM_results_parsed.csv')):
            if os.path.getsize(os.path.join(f,ff,'bins_graphBin_checkM_results_parsed.csv')) > 150:
                checkmGraphbin.add(f)
         if ff == 'checkM_all' and os.path.isfile(os.path.join(f,ff,'bins_metaCOAG_checkM_results_parsed.csv')):
            if os.path.getsize(os.path.join(f,ff,'bins_metaCOAG_checkM_results_parsed.csv')) > 150:
                checkmMetaCOAG.add(f)
         if ff == 'checkM_all' and os.path.isfile(os.path.join(f,ff,'bins_metawrap_refined_checkM_results_parsed.csv')):
            if os.path.getsize(os.path.join(f,ff,'bins_metawrap_refined_checkM_results_parsed.csv')) > 150:
                checkmMetaWrap.add(f)
         if ff == 'checkM_all' and os.path.isfile(os.path.join(f,ff,'bins_semibin_checkM_results_parsed.csv')):
            if os.path.getsize(os.path.join(f,ff,'bins_semibin_checkM_results_parsed.csv')) > 150:
                checkmSemibin.add(f)
         if ff == 'checkM_all' and os.path.isfile(os.path.join(f,ff,'bins_vamb_checkM_results_parsed.csv')):
            if os.path.getsize(os.path.join(f,ff,'bins_vamb_checkM_results_parsed.csv')) > 150:
                checkmVAMB.add(f)
         # reassmbled
         if ff == 'checkM_all' and os.path.isfile(os.path.join(f,ff,'reassembled_bins_checkM_results_parsed.csv')):
            if os.path.getsize(os.path.join(f,ff,'reassembled_bins_checkM_results_parsed.csv')) > 150:
                checkmReassembled.add(f)
         # bin quantification
         if ff == 'bins_quantified':
            #print(ff)
            #print(os.path.join(f,ff,'bins_'+fbinner+'_quantified_ab_table.tab'))
            if os.path.isfile(os.path.join(f,ff,'bins_'+fbinner+'_quantified_ab_table.tab')):
                if os.path.getsize(os.path.join(f,ff,'bins_'+fbinner+'_quantified_ab_table.tab')) > 100:
                    binsQuantified.add(f)
         # GTDBK
         gtdbkp = os.path.join(f,ff,'bins_maxbin2','gtdbtk.bac120.summary.tsv')
         if ff == 'GTDBTK_all' and os.path.isfile(gtdbkp):
            if os.path.getsize(gtdbkp) > 500:
                gtdbkMaxbin2.add(f)
         gtdbkp = os.path.join(f,ff,'bins_metabat2','gtdbtk.bac120.summary.tsv')
         if ff == 'GTDBTK_all' and os.path.isfile(gtdbkp):
            if os.path.getsize(gtdbkp) > 500:
                gtdbkMetabat2.add(f)
         gtdbkp = os.path.join(f,ff,'bins_vamb','gtdbtk.bac120.summary.tsv')
         if ff == 'GTDBTK_all' and os.path.isfile(gtdbkp):
            if os.path.getsize(gtdbkp) > 500:
                gtdbkVAMB.add(f)
         gtdbkp = os.path.join(f,ff,'bins_semibin','gtdbtk.bac120.summary.tsv')
         if ff == 'GTDBTK_all' and os.path.isfile(gtdbkp):
            if os.path.getsize(gtdbkp) > 500:
                gtdbkSemibin.add(f)
         gtdbkp = os.path.join(f,ff,'bins_metaCOAG','gtdbtk.bac120.summary.tsv')
         if ff == 'GTDBTK_all' and os.path.isfile(gtdbkp):
            if os.path.getsize(gtdbkp) > 500:
                gtdbkMetaCOAG.add(f)
         gtdbkp = os.path.join(f,ff,'bins_concoct','gtdbtk.bac120.summary.tsv')
         if ff == 'GTDBTK_all' and os.path.isfile(gtdbkp):
            if os.path.getsize(gtdbkp) > 500:
                gtdbkConcoct.add(f)
         gtdbkp = os.path.join(f,ff,'bins_metawrap_refined','gtdbtk.bac120.summary.tsv')
         if ff == 'GTDBTK_all' and os.path.isfile(gtdbkp):
            if os.path.getsize(gtdbkp) > 500:
                gtdbkMetaWrap.add(f)
         gtdbkp = os.path.join(f,ff,'bins_reassembled','gtdbtk.bac120.summary.tsv')
         if ff == 'GTDBTK_all' and os.path.isfile(gtdbkp):
            if os.path.getsize(gtdbkp) > 500:
                gtdbkReassembled.add(f)
         gtdbkp = os.path.join(f,ff,'bins_DAS','gtdbtk.bac120.summary.tsv')
         if ff == 'GTDBTK_all' and os.path.isfile(gtdbkp):
            if os.path.getsize(gtdbkp) > 500:
                gtdbkDAS.add(f)
         gtdbkp = os.path.join(f,ff,'bins_graphBin','gtdbtk.bac120.summary.tsv')
         if ff == 'GTDBTK_all' and os.path.isfile(gtdbkp):
            if os.path.getsize(gtdbkp) > 500:
                gtdbkGraphbin.add(f)
print(' > checking done, writing outline per job type:')
print('--- PRE-PROCESSING ---')
print('CoverM coverage:     ',len(prepCoverM))
print('Metabinner coverage: ',len(prepMetabinnerCov))
print('Coverage BAM: done:  ',len(prepBAM))
print('Minimap BAM: done:   ',len(prepMinimapBAM))
print('--- BINNING ---')
print('Metabat2: done:',len(binsMetabat2))
print('Maxbin2:  done:',len(binsMaxbin2))
print('Concoct:  done:',len(binsConcoct))
print('MetaCOAG: done:',len(binsMetaCOAG))
print('VAMB:     done:',len(binsVAMB))
print('SemiBIN:  done:',len(binsSemibin))
print('--- BIN REFINING ---')
print('GraphBin: done:',len(binsGraphbin))
print('DAS:      done:',len(binsDAS))
print('MetaWrap  done:',len(binsMetaWrap))
print('--- BIN RE-ASSEMBLY ---')
print('          done:',len(binsReassembled))
print('--- BIN QUANTIFICATION ---')
print('  ['+fbinner+'] done:',len(binsQuantified))
print('--- CHECKM ---')
print('Metabat2: done:',len(checkmMetabat2))
print('Maxbin2:  done:',len(checkmMaxbin2))
print('Concoct:  done:',len(checkmConcoct))
print('MetaCOAG: done:',len(checkmMetaCOAG))
print('VAMB:     done:',len(checkmVAMB))
print('SemiBIN:  done:',len(checkmSemibin))
print('GraphBin: done:',len(checkmGraphbin))
print('DAS:      done:',len(checkmDAS))
print('MetaWrap  done:',len(checkmMetaWrap))
print('Reassembled   :',len(checkmReassembled))
print('--- GTDBK ---')
print('Metabat2: done:',len(gtdbkMetabat2))
print('Maxbin2:  done:',len(gtdbkMaxbin2))
print('Concoct:  done:',len(gtdbkConcoct))
print('MetaCOAG: done:',len(gtdbkMetaCOAG))
print('VAMB:     done:',len(gtdbkVAMB))
print('SemiBIN:  done:',len(gtdbkSemibin))
print('GraphBin: done:',len(gtdbkGraphbin))
print('DAS:      done:',len(gtdbkDAS))
print('MetaWrap  done:',len(gtdbkMetaWrap))
print('Reassembled   :',len(gtdbkReassembled))
print()

print(' >> listing samples NOT DONE into files:')
#   bins
binsMaxbin2Nd = allS - binsMaxbin2
binsMetabat2Nd = allS - binsMetabat2
binsConcoctNd = allS - binsConcoct
binsVAMBNd = allS - binsVAMB
binsSemibinNd = allS - binsSemibin
binsGraphbinNd = allS - binsGraphbin
binsMetaWrapNd = allS - binsMetaWrap
binsDASNd = allS - binsDAS
binsMetaCOAGNd = allS - binsMetaCOAG

