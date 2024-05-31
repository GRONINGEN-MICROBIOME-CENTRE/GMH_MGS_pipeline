# Helper script for merging results of CARD / shortbred analysis
# ===================================================================

import os
import sys
import csv
import copy

import argparse

parser = argparse.ArgumentParser(description='Merged SHORTBRED CARD output')
parser.add_argument('--infolder', help='input folder [def="CARD_SB"]',default='CARD_SB')
parser.add_argument('--out', help='output file [def="shortbred_CARD_merged.csv"]',default='shortbred_CARD_merged.csv')
args = parser.parse_args()

inFolder = args.infolder
outFile = args.out

res = {} # CARD -> NR

# first pass: get all CARDs
print ('> doing 1st pass: finding all ARs')
c = 0
for i in os.listdir(inFolder):
   if '_CARD_sb.txt' not in inFolder+'/'+i: continue
   with open(inFolder+'/'+i) as iF:
      rdr = csv.reader(iF,delimiter='\t')
      for r in rdr:
         res[r[0]] = 0.0
   c+=1
   #print ('  >> ',c,'files done')

print ('> ',len(res.keys()),' ARs found')

c = 0
arse = sorted(res.keys())
with open(outFile,'w') as oF:   
   writ = csv.writer(oF,delimiter='\t')
   arseT = copy.copy(arse)
   arseT[0] = "Sample"
   writ.writerow(arseT)
   for i in os.listdir(inFolder):
      if '_CARD_sb.txt' not in inFolder+'/'+i: continue
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
         oR[0] = i.strip().replace('_CARD_sb.txt','')
      writ.writerow(oR)
   print ('  >> ',c,'files parsed and merged')

