# =============================================================================
# bin stat collector script
# > collects checkM stats for all bins
# =============================================================================
import argparse
import csv
import os

# args
parser = argparse.ArgumentParser()
parser.add_argument("-I","--infolder", help="folder with sorted samples ()", default = '.', required=False)
parser.add_argument("-O","--out", help="output file [Def: bin_stats_checkM.csv]", default='bin_stats_checkM.csv',required=False)
args = parser.parse_args()

res = []
hdr = False
for f in os.listdir(args.infolder):
    ff = os.path.join(args.infolder,f)
    #print(ff)
    if not ff.endswith('.csv'): continue
    with open(ff) as iF:
        print(' > parsing',ff)
        rdr = csv.reader(iF,delimiter='\t')
        for l in rdr:
            if l[0].startswith('Bin Id') and not hdr:
                l[0] = 'genome'
                hdr = True
                for c in range(0,len(l)):
                    l[c] = l[c].lower()
                res.append(l)
            elif not l[0].startswith('Bin Id'):               
                l[0] = l[0]+'.fa'
                res.append(l)
                
with open(args.out,'w') as oF:
    wrt = csv.writer(oF,delimiter=',')
    for l in res:
        wrt.writerow(l)
