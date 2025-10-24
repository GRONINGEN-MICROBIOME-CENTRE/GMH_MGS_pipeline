# ============================================================================
# cleaner / filtering for collected MAGs / RGI results [strainatlas only!]
# ============================================================================
# step 1: run this in folder with RGI results for genomes
import os
import argparse
import csv
parser = argparse.ArgumentParser()
parser.add_argument("--inpath",required=False,default='.')
parser.add_argument("--min_identity",required=False,default=50)
parser.add_argument("--min_bitscore",required=False,default=250)
parser.add_argument("--min_length",required=False,default=50)
parser.add_argument("--max_length",required=False,default=200)
parser.add_argument("--outpath",required=False,default='filtered')
args = parser.parse_args()

# make output folder (if it does not exist)
os.system('mkdir -p '+args.outpath)

# iterate over all .txt files in --inpath:

for infile in os.listdir(args.inpath):
    if 'rgi_out_basic_wild.txt' not in infile: 
        continue
    cnt = 0
    cnt_s = 0
    cnt_loose =0
    cnt_strict = 0
    cnt_perfect = 0
    outf = args.outpath+'/'+infile
    print(' processing',infile,'->',outf)
    #exit(0)
    with open(infile) as iF:
        with open(outf,'w' ) as oF:
            csvr = csv.reader(iF,delimiter='\t',quotechar='"')
            csvw = csv.writer(oF,delimiter='\t',quotechar='"')
            for l in csvr:
                #print(l)
                l = l[0:17]+l[20:len(l)]
                #print(l)
                cnt += 1
                #if cnt == 2: exit(1)
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
