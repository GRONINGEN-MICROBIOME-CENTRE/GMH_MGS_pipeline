# ==========================================================
# == script for making pretty contig names after binning ===
# ==========================================================
# args
# > --binfolder <folder with bins>
# > --outfolder <output folder>
# > --taxtable <taxonomy table> : csv [<bin name>,<taxonomy assignment>]
# output
# > bins_annotated folder:
#  file names are the same, contig headers are renamed to
#  ><sample_name>|<bin_name> <contig_name> <taxonomy annotation>
#    where <contig_name> is just contig.<number> [starting with 001]

import csv
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-I","--binfolder", help="folder with bins", required=True)
parser.add_argument("-O","--outfolder", help="output folder [Def: bins_renamed]", default='bins_renamed',required=False)
parser.add_argument("-T","--taxtable", help="taxonomy table [tsv, col1=bin,col2=taxonomy, can use GTDBK output]", required=False, default="")
parser.add_argument("-S","--samplename",help="name of the sample [req]",required=True)
parser.add_argument("--renamefiles",help="if Y, renames bins to include sample name [e.g. bin.1.fa => sample.bin.1.fa][def=Y]",required=False,default="Y")
args = parser.parse_args()

# iterate over fasta files in the input folder
# load file, prep output file
# go through it, rename headers
print('> Startig bin contig renaming')
if not args.taxtable == '':
   taxtbl = {}
   print(' >> parsing taxonomy table')
   with open(args.taxtable) as iF:
      rdr = csv.reader(iF, delimiter='\t')
      for l in rdr:
         taxtbl[l[0]] = l[1]
 
print(' >> prepping output folder:',args.outfolder)
if not os.path.exists(args.outfolder): os.mkdir(args.outfolder)

print(' >> looking for bins')
for f in os.listdir(args.binfolder):
   if not f.endswith('.fa'): continue
   print('  >>> processing',f)
   contignr = 0
   with open(os.path.join(args.binfolder,f)) as iF:
      outname = f
      bintax = ''
      if not args.taxtable == '':
         bintax = '|'+taxtbl[f.strip().replace('.fa','')]
      if args.renamefiles == 'Y': outname = args.samplename+'.'+f
      with open(os.path.join(args.outfolder,outname),'w') as oF:
         for l in iF:
            # header (for renaming)
            if l.startswith('>'):
               contignr += 1
               hdrnew = '>'+args.samplename+'|'+f.replace('.fa','')+'|contig'+str(contignr).zfill(3)+bintax
               oF.write(hdrnew+'\n')
            # rest of FA
            else: 
               oF.write(l)
#   exit()
print('> DONE!')
