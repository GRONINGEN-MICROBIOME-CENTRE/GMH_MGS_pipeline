# DAG3 pipeline helper utils,
# Script for merging kneaddata read reports

import argparse
import csv
import os

# =========================== MAIN ===================
# ===================================================
parser = argparse.ArgumentParser()
parser.add_argument("--infolder", help="Folder with kneaddata reports",required=True)
parser.add_argument("--out", help="output file",required=True)
args = parser.parse_args()

# result accumulator
res = []
hdrWritten = False
# iterate over input folder
for f in os.listdir(args.infolder):
   if not f.endswith('.csv'): continue
   # parse .csv files
   with open(args.infolder+'/'+f) as iF:
      rdr = csv.reader(iF,delimiter=',')      
      ln = 0
      for l in rdr:
         ln += 1
         if not hdrWritten and ln == 1:
            res.append(l)
            hdrWritten = True
         elif ln > 1:
            res.append(l)
with open(args.out,'w') as oF:
   writ = csv.writer(oF,delimiter=',')
   for r in res:
      writ.writerow(r)    
