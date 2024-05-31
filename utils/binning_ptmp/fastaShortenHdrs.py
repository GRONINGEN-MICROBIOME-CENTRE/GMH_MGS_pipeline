# R.Gacesa (UMCG, 2022)
# ========================================================
# cleans contig names for downstream binning compatibility
# =========================================================
# > uses BioPython for loading FASTA
# > uses argparse for parsing sys input

# === MAIN ===
from Bio import SeqIO
import argparse
import csv
parser = argparse.ArgumentParser()
parser.add_argument('--input',required=True,help='fasta file input')
parser.add_argument('--output',help='output file',default=None,required=True)
args = parser.parse_args()
contigs = args.input
outfile = args.output
print('> STARTING fasta header cleaner')
# load fasta
print(' >> loading',contigs)
fa = {rec.id : rec.seq for rec in SeqIO.parse(contigs, "fasta")}
# clean headers, save contigs >= minlength
contigNR = 0
dropped = 0
kept = 0
n = 60
with open(outfile,'w') as oF:
   print('   >> writing fasta to',outfile)
   for fh in fa.keys():
      oF.write('>'+fh.strip().split(' ')[0].strip()+'\n')
      seq = str(fa[fh]).strip()
      chunks = [seq[i:i+n] for i in range(0, len(seq), n)]
      for c in chunks:
         oF.write((c).strip()+'\n')
print(' >> done')
