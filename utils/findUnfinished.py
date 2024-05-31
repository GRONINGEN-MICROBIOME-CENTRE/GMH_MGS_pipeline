# script which checks which jobs were successfully completed (and sorted):
# params:
# --samples [-S] : where samples to be checked are
# --samplelist [-L] : OR a list of sample names (text file, one name per line)
# --results [-R] : where sorted results are

# output:
# __nd_<data layer> : list of samples which were not done for the given data layer
# __alldone : list of samples for which all data layers were done

import os
import argparse
import csv

# set up argument parser:
parser = argparse.ArgumentParser()
parser.add_argument("-S","--samples",help="location of samples [samples must end in _1.fq.gz]",required=False)
parser.add_argument("-R","--results",help="location of sorted results (root folder) [must include subfolders, e.g. humann3, metaphlan3, kraken2 ...",required=True)
parser.add_argument("-L","--samplelist",help="sample list file (text file, one name per line)",required=False)
args = parser.parse_args()

# check for input params
print (args.samples)
print (args.samplelist)
if (args.samples == None and args.samplelist == None) or (args.samples != None and args.samplelist != None):
   print('ERROR: --samples OR --samplelist [but not both] have to be provided')
   exit()

# collectors
dnHum3 = set()
dnMP3 = set()
dnVFDB = set()
dnCARD = set()
dnKrak2 = set()
dnSP3 = set()
res = set()

# paths:
pHum3 = args.results+'/humann3.6/path_abundances/'
pMP3 = args.results+'/metaphlan4'
pVFDB = args.results+'/VFDB_SB'
pCARD =  args.results+'/CARD_SB'
pKrak2 = args.results+'/kraken2'
pSP3 = args.results+'/strainphlan4'

# collect results'
# =============================
print(' > collecting processed samples in ',args.results,'')
#  > humann3
if os.path.isdir(pHum3):
   for f in os.listdir(pHum3):
      if not f.endswith('.tsv'): continue
      if os.path.getsize(pHum3+'/'+f) < 10: continue
      #ff = '_'.join(f.split('_')[0:3])  
      ff = f.strip().replace('_kneaddata_cleaned_paired_merged_pathabundance.tsv','')
      dnHum3.add(ff)

#  > metaphlan3
if os.path.isdir(pMP3):
   for f in os.listdir(pMP3):
      if not f.endswith('.txt'): continue
      if os.path.getsize(pMP3+'/'+f) < 10: continue
      #ff = '_'.join(f.split('_')[0:3])  
      ff = f.strip().replace('_metaphlan.txt','')
      dnMP3.add(ff)

#  > strainphlan3
if os.path.isdir(pSP3):
   for f in os.listdir(pSP3):
      if not f.endswith('.pkl'): continue
      if os.path.getsize(pSP3+'/'+f) < 10: continue
      #ff = '_'.join(f.split('_')[0:3])  
      ff = f.strip().replace('_metaphlan3.pkl','')
      dnSP3.add(ff)

# > VFDB
if os.path.isdir(pVFDB):
   for f in os.listdir(pVFDB):
      if not f.endswith('.txt'): continue
      if os.path.getsize(pVFDB+'/'+f) < 10: continue
      #ff = '_'.join(f.split('_')[0:3])  
      ff = f.strip().replace('_vfdb_sb.txt','')
      dnVFDB.add(ff)

# > CARD
if os.path.isdir(pCARD):
   for f in os.listdir(pCARD):
      if not f.endswith('.txt'): continue
      if os.path.getsize(pCARD+'/'+f) < 10: continue
      #ff = '_'.join(f.split('_')[0:3])  
      ff = f.strip().replace('_CARD_sb.txt','')
      dnCARD.add(ff)

# > Kraken2
if os.path.isdir(pKrak2):
   for f in os.listdir(pKrak2):
      if not f.endswith('.bracken.result.mp3.txt'): continue
      if os.path.getsize(pKrak2+'/'+f) < 10: continue
      ff = f.strip().replace('.bracken.result.mp3.txt','')
      #ff = '_'.join(f.split('_')[0:3])  
      dnKrak2.add(ff)
print (' >> done collecting results')

# collect samples
# =============================
#  > from folder (if --samples is given)
if args.samples != None:
   if not os.path.isdir(args.samples):
      print ('ERROR: samples folder [',args.samples,'] does not exist')
   for f in os.listdir(args.samples):
      if not (f.endswith('_1.fq.gz') or f.endswith('_1.fastq.gz')): continue
      #ff = '_'.join(f.split('_')[0:3])     
      ff = f.strip().replace('_1.fq.gz','').replace('_1.fastq.gz','')
      res.add(ff)

#  > from file (if --samplelist is given)
if args.samplelist != None:
   #print (args.samplelist)
   with open(args.samplelist) as inF:
      for f in inF:
         #print(f)
         #print(str(f))
         ff = f.strip().replace('_1.fq.gz','').replace('_2.fq.gz','').replace('_1.fastq.gz','').replace('_2.fastq.gz','')
         res.add(ff)
   print ('>> sample list loaded [',args.samplelist,'=',len(list(res)),'] samples')

# compare samples to results
# =============================
ndoneHum3 = res - dnHum3
ndoneMP3 = res - dnMP3
ndoneSP3 = res - dnSP3
#ndoneKrak2 = res - dnKrak2
ndoneCARD = res - dnCARD
ndoneVFDB = res - dnVFDB
#dnAll = set.intersection(dnHum3,dnMP3,dnSP3,dnKrak2,dnCARD,dnVFDB,res)
dnAll = set.intersection(dnHum3,dnMP3,dnSP3,dnCARD,dnVFDB,res)
#print(dnAll)
#print(res)
#print(res - dnAll)
ndoneAll = res - dnAll
print (' Total samples:',len(res))
print ('  Metaphlan3  : DONE:',len(dnMP3),'; NOT DONE:',len(ndoneMP3))
#print ('  Metaphlan4  : DONE:',len(dnMP4),'; NOT DONE:',len(ndoneMP4))
print ('  Strainphlan3: DONE:',len(dnSP3),'; NOT DONE:',len(ndoneSP3))
print ('  Humann3     : DONE:',len(dnHum3),'; NOT DONE:',len(ndoneHum3))
#print ('  Kraken2     : DONE:',len(dnKrak2),'; NOT DONE:',len(ndoneKrak2))
print ('  CARD        : DONE:',len(dnCARD),'; NOT DONE:',len(ndoneCARD))
print ('  VFDB        : DONE:',len(dnVFDB),'; NOT DONE:',len(ndoneVFDB))
print ('  ALL TOOLS   : DONE:',len(dnAll),'; NOT DONE:',len(ndoneAll))

# === make happy table ===
# ===============================
with open('results.csv','w') as oF:
   writ = csv.writer(oF)
   tt = ['Sample','Metaphlan3','Strainphlan3','Humann3','Kraken2','CARD','VFDB','ALL']
   writ.writerow(tt)
   for s in res:
      oneLine = [s]
      oneLine.append('Y' if s in dnMP3 else 'N')
      oneLine.append('Y' if s in dnSP3 else 'N')
      oneLine.append('Y' if s in dnHum3 else 'N')
      oneLine.append('Y' if s in dnKrak2 else 'N')
      oneLine.append('Y' if s in dnVFDB else 'N')
      oneLine.append('Y' if s in dnCARD else 'N')
      oneLine.append('Y' if s in dnAll else 'N')
#      print(oneLine)
      writ.writerow(oneLine)

