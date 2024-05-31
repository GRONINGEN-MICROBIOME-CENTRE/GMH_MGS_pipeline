# ====================================================
# renamer for bin fasta files
# > goes through all fasta files (.fa) in the folder
# > edits headers to include bin name ( = file name )
# > saves it to tmp file and then overwrites the original with it
# ====================================================
import argparse
import os

# args
parser = argparse.ArgumentParser()
parser.add_argument("-I","--infolder", help="folder with bins [in .fa]", default = '.', required=False)
args = parser.parse_args()

for f in os.listdir(args.infolder): 
    if (f.endswith('.fa') or f.endswith('.fasta')) and not 'tmp.fa' in f :
        print(' > renaming headers in ',f)
        with open('tmp.fa','w') as oF:
            with open(f) as iF:
                for l in iF:
                    if l.startswith('>'):
                        l = l.replace('>','>'+f.strip()+'_')
                    oF.write(l)
        os.system('mv tmp.fa '+f)
os.system('rm tmp.fa')
