# =============================================================================
# > INPUT (-I): bin_stats.csv file produced by 
#                /projects/hb-tifn/tools/GMH_pipeline/utils/binning_ptmp/collectBinStatsSortedSamples.py
# > TAX (-T, --tax): by which taxon to subset / grep? [e.g. s__Faecalibacterium]
# > OUT (-O, --out): where to copy appropriate bins
# =============================================================================
import argparse
import csv
import os

# args
parser = argparse.ArgumentParser()
parser.add_argument("-I",'--input', help="bin_stats.csv file", default = 'bin_stats.csv', required=False)
parser.add_argument("-O","--out", help="output folder [no default]", required=True)
parser.add_argument("-T","--tax", help="which taxon to collect [partial matching works, no default]", required=True)
args = parser.parse_args()
print('Loading ',args.input)
print(' > finding bins with taxonomy: ',args.tax)
with open(args.input) as iF:
   rdr = csv.reader(iF, delimiter=',')
   for l in rdr:
       tx = l[2]
       pt = l[9]
       if args.tax in tx:
           #print(tx,pt)
           print(' > copying bin ',pt,' to ',args.out)
           os.system('cp '+pt+' '+args.out)
print('DONE')
