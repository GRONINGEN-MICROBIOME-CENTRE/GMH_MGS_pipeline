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
#   bins
binsMaxbin2 = set()
binsMetabat2 = set()
binsConcoct = set()
binsMetaWrap = set()
#   checkM
checkmMetaWrap = set()
#   GTDBK
gtdbkMetaWrap = set()
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
         # binners
         try: 
            if ff == 'bins_metawrap' and len(os.listdir(os.path.join(f,ff))) > 0:
                try:
                   if len(os.listdir(os.path.join(f,ff,'concoct_bins'))) > 0:
                       binsConcoct.add(f)
                except: pass
                try: 
                   if len(os.listdir(os.path.join(f,ff,'maxbin2_bins'))) > 0:
                       binsMaxbin2.add(f)
                except: pass
                try:
                   if len(os.listdir(os.path.join(f,ff,'metabat2_bins'))) > 0:
                       binsMetabat2.add(f)
                except: pass
         except: pass
         try:
            if ff == 'bins_metawrap_refined' and len(os.listdir(os.path.join(f,ff))) > 0:
                binsMetaWrap.add(f)
         except: pass
         # checkM
         if ff == 'bins_checkM':
            if len(os.listdir(os.path.join(f,ff))) > 0:
                checkmMetaWrap.add(f)

         # bin quantification
         if ff == 'bins_quantification':
            #print(ff)
            #print(os.path.join(f,ff,'bins_'+fbinner+'_quantified_ab_table.tab'))
            if os.path.isfile(os.path.join(f,ff,f+'_bin_abundances.txt')):
                if os.path.getsize(os.path.join(f,ff,f+'_bin_abundances.txt')) > 100:
                    binsQuantified.add(f)
         # GTDBK       
         # TR_2101_Week18.gtdbtk.bac120.summary.tsv
         gtdbkp = os.path.join(f,ff,f+'.gtdbk.bac120.summary.tsv')
         #print(gtdbkp)
         if ff == 'bins_GTDBK' and os.path.isfile(gtdbkp):
            if os.path.getsize(gtdbkp) > 500:
                gtdbkMetaWrap.add(f)

print(' > checking done, writing outline per job type:')
print('--- BINNING ---')
print('Metabat2: done:',len(binsMetabat2))
print('Maxbin2:  done:',len(binsMaxbin2))
print('Concoct:  done:',len(binsConcoct))
print('--- BIN REFINING ---')
print('MetaWrap  done:',len(binsMetaWrap))
print('--- BIN QUANTIFICATION ---')
print('Bins quantified:',len(binsQuantified))
print('--- CHECKM ---')
print('MetaWrap  done:',len(checkmMetaWrap))
print('--- GTDBK ---')
print('MetaWrap  done:',len(gtdbkMetaWrap))
print()

print(' >> listing samples NOT DONE into files:')
#   bins
binsMetaWrapND = allS - binsMetaWrap
with open('__binning_notdone_mw.txt','w') as oF:
   for f in binsMetaWrapND:
      oF.write(f+'\n')
checkmMetaWrapND = allS - checkmMetaWrap
with open('__binning_notdone_checkm.txt','w') as oF:
   for f in checkmMetaWrapND:
      oF.write(f+'\n')
gtdbkMetaWrapND = allS - gtdbkMetaWrap
with open('__binning_notdone_gtdbk.txt','w') as oF:
   for f in gtdbkMetaWrapND:
      oF.write(f+'\n')
