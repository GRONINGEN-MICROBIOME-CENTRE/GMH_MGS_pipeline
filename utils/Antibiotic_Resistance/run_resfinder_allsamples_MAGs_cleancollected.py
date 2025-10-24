# =================================================
# cleaner for collected MAGs / RGI results
# =================================================
# step 1: run collect script [run_resfinder_allsamples_MAGs_collectall_v02.R]
# step 2: run this one

import argparse
import csv
parser = argparse.ArgumentParser()
parser.add_argument("--infile",required=False,default='bins_RGI_results_cleaned.csv')
parser.add_argument("--min_identity",required=False,default=50)
parser.add_argument("--min_bitscore",required=False,default=250)
parser.add_argument("--min_length",required=False,default=50)
parser.add_argument("--max_length",required=False,default=200)
parser.add_argument("--outfile",required=False,default='bins_RGI_results_cleaned_filtered.csv')
args = parser.parse_args()

cnt = 0
cnt_s = 0
cnt_loose =0
cnt_strict = 0
cnt_perfect = 0
print(' processing...')
with open(args.infile) as iF:
    with open(args.outfile,'w' ) as oF:
        csvr = csv.reader(iF,delimiter=',',quotechar='"')
        csvw = csv.writer(oF,delimiter=',',quotechar='"')
        for l in csvr:
            cnt += 1
            if cnt == 1: csvw.writerow(l)
            else:
                bscore = float(l[7])
                iden = float(l[9])
                lt_vs_ref = float(l[17])
                if l[5] == 'Perfect' or l[5] == 'Strict':
                    if l[5]=='Perfect': cnt_perfect +=1
                    if l[5]=='Strict': cnt_strict +=1
                    csvw.writerow(l)
                    cnt_s +=1
                elif bscore >= float(args.min_bitscore) and iden >= float(args.min_identity) and lt_vs_ref >= float(args.min_length) and lt_vs_ref <= float(args.max_length):
                    csvw.writerow(l)
                    cnt_s +=1
                    cnt_loose +=1
            if cnt % 100000 == 0: print(cnt)
print(' > processed',cnt,' hits; saved: ',cnt_s,'/',cnt,'hits')
print('  => perfect:',cnt_perfect,'; strict:',cnt_strict,'loose:',cnt_loose)
