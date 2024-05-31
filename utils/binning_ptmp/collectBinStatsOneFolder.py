# =============================================================================
# bin stat collector script
# > collects stats of all bins in the given folder
# =============================================================================
import argparse
import csv
import os

# args
parser = argparse.ArgumentParser()
parser.add_argument("-I","--infolder", help="folder with samples (each sample folder has bins)", default = '.', required=False)
parser.add_argument("-O","--out", help="output file [Def: bin_stats.csv]", default='bin_stats.csv',required=False)
args = parser.parse_args()

res = [] # filled with oneRes lists
res.append(['Sample','Bin.ID','GTDBK.taxonomy','GTDBK.GenSpec','CheckM.Completeness','CheckM.Contamination','CheckM.Strain.Heterogenuity']) # header
smpl = args.infolder
if smpl.endswith('/'): smpl = smpl.removesuffix('/')
print(smpl)
gtdbk = os.path.join(smpl,'bins_GTDBK',smpl+'.gtdbk.bac120.summary.tsv')
gtdbk2 = os.path.join(smpl,'bins_GTDBK',smpl+'.gtdbtk.bac120.summary.tsv')
checkm = os.path.join(smpl,'bins_checkM',smpl+'_checkM_results_parsed.csv')
binabundance = os.path.join(smpl,'bins_quantification',smpl+'_bin_abundances.txt')
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
   # parse bin abundance table (if it exists)
   abundtbl = None
   if os.path.isfile(binabundance):
      print(' >> parsing Bin quantification table')
      res[0].append('Bin.Abundance')
      res[0].append('Bin.Rel.Abundance')
      abundtbl = {} 
      with open(binabundance) as iF:
         rdr = csv.reader(iF,delimiter='\t')
         for l in rdr:
            if l[0] == 'Genomic bins': continue
            abundtbl[l[0]] = float(l[1])
            #print(l[0],abundtbl[l[0]])

   # merge them
   if abundtbl != None:
      totab = 0
      for (k,v) in abundtbl.items():
         if k in gtdbktbl.keys(): totab += v  
   for k in gtdbktbl.keys():
#      print(k)
      oneL = [smpl,k]
      oneL.append(gtdbktbl[k])
      oneL.append(';'.join(gtdbktbl[k].split(';')[-2:]))
      oneL = oneL + checkmtbl[k]
      if abundtbl != None:
          oneL = oneL + [abundtbl[k],abundtbl[k]/totab]
#         print(oneL)
      res.append(oneL)
# save it
with open(args.out,'w') as oF:
   writ = csv.writer(oF)
   for oneL in res:
      writ.writerow(oneL)
