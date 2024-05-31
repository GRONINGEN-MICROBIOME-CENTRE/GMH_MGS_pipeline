# =============================================================================
# BAKTA TAXONOMY SORTER
# > sorts bins by taxonomy
# > run AFTER sortBinsBAKTAOneFolder.py
# > used to prepare for building of pangenomes using ROARY
# example: runs with TR_2101_Week8Q3
# =============================================================================
import argparse
import csv
import os

# args
parser = argparse.ArgumentParser()
parser.add_argument("-I","--infolder", help="folder with samples (each sample folder has bins)", required=True)
parser.add_argument("-O","--outfolder", help="output folder [Def: bins_metawrap_refined_BAKTA_taxsorted]", default='bins_metawrap_refined_BAKTA_taxsorted',required=False)
parser.add_argument("--maxcont", help="maximum contamination [Def: 10]", default='10',required=False)
parser.add_argument("--mincomp", help="min completeness [Def: 70]", default='70',required=False)
parser.add_argument("--gff", help="if not 0, collects gff files", default='1',required=False)
parser.add_argument("--mag", help="if not 0, collects raw mags", default='1',required=False)
args = parser.parse_args()

print ('===========================================')
print (' PROCESSING ',args.infolder)
print ('===========================================')


# === load taxonomy table ====
taxTblF = os.path.join(args.infolder,'bins_metawrap_refined_BAKTA','bin_taxonomy_stats.csv')
if not os.path.exists(taxTblF): 
   print('ERROR: taxonomy table for bins [',taxTbl,'] does not exist')
   exit()

taxTbl = []
#print(taxTblF)
with open(taxTblF) as iF:
   rdr = csv.reader(iF,delimiter=',')
   for r in rdr:
      #print(r)
      taxTbl.append(r)

if len(taxTbl) <= 1:
   print('ERROR: no entries in taxonomy table, quitting!')
   exit()

# === make output folder ===
# make folder (if needed)
outPath = os.path.join(args.infolder,args.outfolder)
if not os.path.exists(outPath):
   os.makedirs(outPath)

# === go through taxonomy table, sort BAKTAS ===
#['TR_2103_Week27', 'TR_2103_Week27.bin.14', 'd__Bacteria;p__Firmicutes;c__Bacilli;o__Lactobacillales;f__Enterococcaceae;g__Enterococcus_B;s__Enterococcus_B faecium', 'g__Enterococcus_B;s__Enterococcus_B faecium', '99.63', '0.12', '0.00']
#print(taxTbl)
cnt = 0
for oneR in taxTbl:
   cnt += 1
   if cnt == 1: continue
   #print(oneR)
   comp = float(oneR[4])
   cont = float(oneR[5])
   good = False
   if comp >= float(args.mincomp) and cont <= float(args.maxcont): good = True
   species = oneR[3].strip().split(';')[1]
   speciesF = species.replace('s__','').replace(' ','_')
   # if species is unknown / nothing, add genus instead
   genus = oneR[3].strip().split(';')[0]
   genusF = genus.replace('g__','').replace(' ','_')+'_sp'
   if speciesF == '': speciesF = genusF
   # genus is unknown / nothing, add family instead
   familyF = oneR[2].strip().split(';')[4].strip()+'_unknown'
   if genusF == '_sp': speciesF = familyF
   # genus is unknown / nothing, add family instead
   orderF = oneR[2].strip().split(';')[3].strip()+'_unknown'
   if familyF == 'f___unknown': speciesF = orderF

   print(genusF,speciesF,'-> comp:',comp,'cont:',cont,'good:',good)

   # make output folder for species [convention of name = <genus>_<species>; e.g. Escherichia_coli or Tannerella_sp_oral_taxon_HOT_286
   # move stuff to it and rename to <sample_species>.gff3
   #   > make folder if needed
   outPathSp = os.path.join(outPath,speciesF)
   if not os.path.exists(outPathSp):
      os.makedirs(outPathSp)
   # copy
   if (args.gff != '0'):
      getPath = os.path.join(args.infolder,'bins_metawrap_refined_BAKTA',oneR[1],oneR[1]+'.gff3')
      outFile = outPathSp+'/'+oneR[0]+'.'+speciesF+'.gff3'
      osCmd = 'cp '+getPath+' '+outFile
      #print(osCmd)
      os.system(osCmd)
   if (args.mag != '0'):
      getPath = os.path.join(args.infolder,'bins_metawrap_refined_BAKTA',oneR[1],oneR[1]+'.fna')
      outFile = outPathSp+'/'+oneR[0]+'.'+speciesF+'.fna'      
      osCmd = 'cp '+getPath+' '+outFile
      #print(osCmd)
      os.system(osCmd)

