# parses profiled clades, filters for min NR of samples
# outputs file we can iterate over for running strainphlan
# ===========================================================
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-I', '--input',help='input file (strainphlan clade profile)')
parser.add_argument('-N', '--min_samples',help='minimal number of samples to consider this clade')
args = parser.parse_args()
outfile = args.input.replace('.txt','_parsed.txt')

#TODO add text / debug / out text

with open(args.input) as iF:
   with open(outfile,'w') as oF:
      for l in iF:
         l = l.strip().replace(' samples.','')
         if '\t' in l:
            ls = l.split('\t')[1]
            lss = ls.split(': in ')
            clade = lss[0]
            nr = lss[1]
            if int(nr) >= int(args.min_samples): 
               oF.write(clade+'\n')
