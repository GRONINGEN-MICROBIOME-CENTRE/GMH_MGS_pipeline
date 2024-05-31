# ============================
# 
# ============================
import sys
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-S","--samples",required=True,help="input folder with samples [_1.fq.gz]")
parser.add_argument("-A","--assemblies",required=True,help="input folder with assemblies [.fa]")
args = parser.parse_args()

# collect assemblies into hash
assdic={} # sample => assembly file 
for f in os.listdir(args.assemblies):
   if f.endswith('.fa') and '_metaspades_scaffolds' in f:
      sn = f.strip().replace('_metaspades_scaffolds.fa','')
      assdic[sn] = f.strip()
     
#for (k,v) in assdic.items():
#   print(k,'->',v)

# go over samples and put assemblies into right places
for f in os.listdir(args.samples):
   if not f.endswith('_1.fq.gz'): continue
   sn = f.strip().replace('_1.fq.gz','')
   if sn in assdic.keys():
      assLoc = args.assemblies+'/'+assdic[sn]
      if '_metaspades_scaffolds.fa' in assLoc:
         toLoc = args.samples+'/'+sn+'/assembly_metaspades/'
#      else:
#         toLoc = args.samples+'/'+sn+'/assembly_metaspades'
         cmd = 'mv '+assLoc+' '+toLoc
         print(cmd)
         os.system('mkdir -p '+toLoc)
         os.system(cmd)
         
   
