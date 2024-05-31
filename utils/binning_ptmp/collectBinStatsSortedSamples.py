# =============================================================================
# bin stat collector script
# > collects stats of all bins in the given sorted results folder
# > IT MUST be run from root folder of where results were sorted to [using GMPpipe sortresults]
# =============================================================================
import argparse
import csv
import os

# args
parser = argparse.ArgumentParser()
parser.add_argument("-I","--infolder", help="folder with samples (each sample folder has bins)", default = '.', required=False)
parser.add_argument("-O","--out", help="output file [Def: bin_stats.csv]", default='bin_stats.csv',required=False)
parser.add_argument("--addpaths", help="if Y, collects paths to bins as well", default='Y',required=False)
args = parser.parse_args()

res = [] # filled with oneRes lists
reshdr = ['Sample','Bin.ID','GTDBK.taxonomy','GTDBK.GenSpec','CheckM.Completeness','CheckM.Contamination','CheckM.Strain.Heterogenuity','Bin.Abundance','Bin.Rel.Abundance']
addPaths = False
if args.addpaths == 'Y': 
    addPaths = True
    reshdr.append('Bin.File.Path')

# parse bins_refined_GTDBK
print (' >> parsing GTDBK files')
gtdbktbl = {}
for smpl in os.listdir(os.path.join(args.infolder,'bins_refined_GTDBK')):
    if not smpl.endswith('.gtdbk.bac120.summary.tsv'): continue
    #print(' >> parsing taxonomy table [gtdbk]')
    with open(os.path.join(args.infolder,'bins_refined_GTDBK',smpl)) as iF:         
       rdr = csv.reader(iF, delimiter='\t')
       for l in rdr:
          if l[0] != 'user_genome':
              #print(l)
              gtdbktbl[l[0]] = l[1]
# parse CheckM
print (' >> parsing CheckM files')
checkmtbl = {}      
for smpl in os.listdir(os.path.join(args.infolder,'bins_refined_checkM')):
    if not smpl.endswith('_checkM_results_parsed.csv'): continue
    #print(' >> parsing QC table [checkM]')
    with open(os.path.join(args.infolder,'bins_refined_checkM',smpl)) as iF:         
        rdr = csv.reader(iF, delimiter='\t')
        for l in rdr:
           if l[0] != 'Bin Id':
              checkmtbl[l[0]] = l[-3:]
# parse abundance
print (' >> parsing Bin Abundance files')
abundtbl = {}
spath = os.path.join(args.infolder,'bins_refined_quantified')
#print(spath)
if os.path.isdir(spath):
   for smpl in os.listdir( os.path.join(spath)):
      #print(smpl)
      if not smpl.endswith('_bin_abundances.txt'): continue
      ll = []
      with open(os.path.join(spath,smpl)) as iF:
         rdr = csv.reader(iF,delimiter='\t')
         relab = 0
         for l in rdr:
            if l[0] == 'Genomic bins': continue
            abundtbl[l[0]] = [float(l[1])]
            relab += float(l[1])
            ll.append(l[0])
#         print(ll)
         for l in ll:
#             print(abundtbl[l])
             abundtbl[l].append(abundtbl[l][0]/relab)             
#for (k,v) in abundtbl.items():
#    print(k,' -> ',v)

# add header
print (' >> Merging tables')
res.append(reshdr)
# merge tables
#reshdr = ['Sample','Bin.ID','GTDBK.taxonomy','GTDBK.GenSpec','CheckM.Completeness','CheckM.Contamination','CheckM.Strain.Heterogenuity']
for k in checkmtbl.keys():
   # basics
   oneL = [k.split('.bin')[0],k]
   # add gtdbtk
   try:
      oneL.append(gtdbktbl[k])
      oneL.append(';'.join(gtdbktbl[k].split(';')[-2:]))
   except:
      oneL = oneL + ['NA','NA']
   # add checkM
   oneL = oneL + checkmtbl[k]
   # add Abundance
   if abundtbl != None:
      try:
          oneL = oneL + abundtbl[k]
      except:
          oneL = oneL + ["NA","NA"]
   # add bin path (if requested)
   if addPaths:
       # for TR_2103_Week50 & TR_2103_Week50.bin.17.fa : 
       # $PWD/bins_refined/TR_2103_Week50/TR_2103_Week50.bin.17.fa
       binPath = os.path.join(os.getcwd(),'bins_refined',oneL[0],oneL[1]+'.fa').strip()
       oneL.append(binPath)
   # add data
   res.append(oneL)
# save it
print(' >> saving results to ',args.out)
with open(args.out,'w') as oF:
   writ = csv.writer(oF)
   for oneL in res:
      writ.writerow(oneL)
