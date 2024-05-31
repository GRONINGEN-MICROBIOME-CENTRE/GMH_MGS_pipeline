# =============================================================================
# bin stat collector script
# > collects stats of all bins in the given folder
# =============================================================================
import argparse
import csv
import os

# args
parser = argparse.ArgumentParser()
parser.add_argument("-I","--infolder", help="folder with samples (each sample folder has bins)", required=True)
parser.add_argument("-O","--outfolder", help="output folder [Def: bins_metawrap_refined_BAKTA]", default='bins_metawrap_refined_BAKTA',required=False)
parser.add_argument("-T","--outtable", help="output table [Def: bin_taxonomy_stats.csv]", default='bin_taxonomy_stats.csv',required=False)
args = parser.parse_args()

res = [] # filled with oneRes lists
res.append(['Sample','Bin.ID','GTDBK.taxonomy','GTDBK.GenSpec','CheckM.Completeness','CheckM.Contamination','CheckM.Strain.Heterogenuity']) # header
smpl = args.infolder.replace('/','')
print('====================================')
print(' processing folder',smpl)
print('====================================')
gtdbk = os.path.join(smpl,'bins_GTDBK',smpl+'.gtdbk.bac120.summary.tsv')
gtdbk2 = os.path.join(smpl,'bins_GTDBK',smpl+'.gtdbtk.bac120.summary.tsv')
checkm = os.path.join(smpl,'bins_checkM',smpl+'_checkM_results_parsed.csv')
print (gtdbk)
print (checkm)
if os.path.isfile(gtdbk2) and not os.path.isfile(gtdbk):
   gtdbk = gtdbk2
if os.path.isfile(gtdbk) and os.path.isfile(checkm):
   print(' > parsing ',smpl,'[',gtdbk,'&',checkm,']')
   # parse gtdbk
   gtdbktbl = {}
   checkmtbl = {}      
   print(' >> parsing taxonomy table [gtdbk]')
   with open(gtdbk) as iF:         
      rdr = csv.reader(iF, delimiter='\t')
      for l in rdr:
         if l[0] != 'user_genome':
            gtdbktbl[l[0]] = l[1]
   print(' >> parsing QC table [checkM]')
   with open(checkm) as iF:         
      rdr = csv.reader(iF, delimiter='\t')
      for l in rdr:
         if l[0] != 'Bin Id':
#            print(l)
            checkmtbl[l[0]] = l[-3:]
   # merge them
   for k in gtdbktbl.keys():
#      print(k)
      oneL = [smpl,k]
      oneL.append(gtdbktbl[k])
      oneL.append(';'.join(gtdbktbl[k].split(';')[-2:]))
      oneL = oneL + checkmtbl[k]
#         print(oneL)
      res.append(oneL)

# === make output folder ===
# make folder (if needed)
outPath = os.path.join(args.infolder,args.outfolder)
if not os.path.exists(outPath):
   os.makedirs(outPath)

# save taxonomy table
outPathTbl = os.path.join(outPath,args.outtable)
with open(outPathTbl,'w') as oF:
   writ = csv.writer(oF)
   for oneL in res:
      writ.writerow(oneL)

# find BAKTA RESULTS
binsFolder = os.path.join(args.infolder,'bins_metawrap_refined')
# sort them
for f in os.listdir(binsFolder):
   #print(f)
   onef = os.path.join(binsFolder,f)
   if os.path.isdir(onef):
      print(onef,'is bin folder, sorting!')
      scmd = 'mv '+onef+'/ '+outPath+'/'
      #print(' > ',scmd)
      os.system(scmd)
