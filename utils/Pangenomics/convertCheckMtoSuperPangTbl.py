# Make SuperPang completeness file from CheckM file

# checkM file is:
# genome,marker lineage,# genomes,# markers,# marker sets,0,1,2,3,4,5+,completeness,contamination,strain heterogeneity
# TR_2101_Week12Q3.bin.1.fa,f__Bifidobacteriaceae (UID1460),70,502,225,120,369,12,1,0,0,75.88,1.96,20.00


# superpang: 
# > should be TAB-separated and needs a header line with 'Bin Id', 'Completeness', and 'Contamination' in it

import argparse
import csv
parser = argparse.ArgumentParser()
parser.add_argument('--input','-I', required=True, help="input file (checkM table)")
parser.add_argument('--out','-O', help="output file [def = out.tsv]",default='out.tsv')
args = parser.parse_args()

out = []
#out.append(['Bin Id','Completeness','Contamination'])
#out.append(['Bin Id','Completeness'])
with open(args.input) as iF:
   cnt = 0
   rdr = csv.reader(iF,delimiter='\t')
   for l in rdr:
       cnt += 1
       if cnt == 1: continue
       #out.append([l[0].replace('.fasta','').replace('.fa',''),l[11],l[12]])
       out.append([l[0].replace('.fasta','').replace('.fa',''),l[11]])
       #print(l)
with open(args.out,'w') as oF:
    writ = csv.writer(oF,delimiter='\t')
    for ol in out:
        writ.writerow(ol)
