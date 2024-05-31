# Helper script for merging results of VFDB / shortBRED analysis
# =====================================================================
import os
import sys
import csv
import copy
import argparse

parser = argparse.ArgumentParser(description='Merged SHORTBRED VFDB output')
parser.add_argument('--infolder', help='input folder [def="VFDB_SB"]',default='VFDB_SB')
parser.add_argument('--out', help='output file [def="shortbred_VFDB_merged.csv"]',default='shortbred_VFDB_merged.csv')
args = parser.parse_args()

inFolder = args.infolder
outFile = args.out

res = {} # VFs -> NR

# first pass: get all VFs
print ('> doing 1st pass: finding all VFs')
c = 0
for i in os.listdir(inFolder):
   if '_vfdb_sb.txt' not in inFolder+'/'+i: continue
   with open(inFolder+'/'+i) as iF:
      rdr = csv.reader(iF,delimiter='\t')
      for r in rdr:
         res[r[0]] = 0.0
   c+=1
   #print ('  >> ',c,'files done')

print ('> ',len(res.keys()),' VFs found')

c = 0
arse = sorted(res.keys())
with open(outFile,'w') as oF:   
   writ = csv.writer(oF,delimiter='\t')
   arseT = copy.copy(arse)
   arseT[0] = "Sample"
   writ.writerow(arseT)
   for i in os.listdir(inFolder):
      if '_vfdb_sb.txt' not in inFolder+'/'+i: continue
      with open(inFolder+'/'+i) as iF:
         resOne = res
         rdr = csv.reader(iF,delimiter='\t')      
         for r in rdr:
#            print (i)
#            print (r)
            res[r[0]] = r[1]
      c+=1
      oR = []
      for a in arse:
         oR.append(res[a])
         oR[0] = i.strip().replace('_vfdb_sb.txt','')
      writ.writerow(oR)
   print ('  >> ',c,'files parsed and merged')

