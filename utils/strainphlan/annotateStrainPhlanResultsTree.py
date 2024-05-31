import sys
import csv
import argparse

# Annotator for newick tree
# ===========================
# > input: newick tree
parser = argparse.ArgumentParser()
parser.add_argument('-I','--input',help='input file (newick tree)',required=True)
parser.add_argument('-O','--out',default='__out.tre',help='output file (newick tree) [def=__out.tre]')
parser.add_argument('-M','--meta',help='metadata file: tsv w. col1=samples,col2=annotation ',required=True)
parser.add_argument('--addn',help='if Y, adds sample numbers to avoid issues in downstream software (e.g. figtree) [def=Y]',default='Y')
args = parser.parse_args()

# PARSE NEWICK, HASH SAMPLES
with open(args.input) as iF:
   replacer = {}
   for l in iF:
         l = l.strip()
         if l.endswith(';'): 
            l=l[:-1]
         newTree = l
         ls = l.strip().split('(')
         for ll in ls:
            lls = ll.split(':')
            for f in lls:
               f = f.replace(')','')
               fs2 = f.split(',')
               for fs2i in fs2:
                  if len(fs2i) > 0 and not fs2i.startswith('0'):
                     fs2i = fs2i.strip()
                     replacer[fs2i] = [fs2i]
#print(replacer)

# PREP ANNOTATION HASH
annotrdy = {}
# > initiatlize annotation dict, cleanup metaphlan junk
for (k,v) in replacer.items():
   annot = []
   kknew = k.replace('_metaphlan4','').replace('_metaphlan3','')
   #print(kknew)
   annot.append(kknew)  
   annotrdy[k] = [kknew]

#link it to annotation table
annotTblHesh = {}
with open(args.meta) as iF:
   # read table, hash it   
   rdr = csv.reader(iF,delimiter='\t',quotechar='"')
   for r in rdr:
      annotTblHesh[r[0]] = r[1]
#print(annotTblHesh)

# REMAKE TREE BY REPLACING SAMPLES WITH ANNOTATED SAMPLES
cnt = 0
for (k,v) in annotrdy.items():
   cnt+=1
   #print(k,v)
   # now link it to annotTblHesh
   try:
      v.append(annotTblHesh[v[0]])
   except:
      print('WARNING: extra annotation table ID missing:',v)
   #print(k,'->',v)
   if args.addn == 'Y':
      newnode = v[1]+'.'+str(cnt)
   else: 
      newnode = v[1] 
   newTree = newTree.replace(k,newnode)

# SAVE NEW TREE
with open(args.out,'w') as oF:
   oF.write(newTree)
