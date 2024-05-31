import os
import os.path
import sys

dn = set()
nd = set()
for f in os.listdir('.'):
   if os.path.isfile(f): 
      continue

   if os.path.isfile(f+'/'+f+'.StrainPhlAn4_concatenated.aln'):
      dn.add(f)
   else:
      nd.add(f)

print(' done:',len(list(nd)), 'samples')
print(' not done:',len(list(dn)),'samples')
with open('__sp4_comp_ndone','w') as oF:
   for l in nd: oF.write(l.strip()+'\n')
with open('__sp4_comp_done','w') as oF:
   for l in dn: oF.write(l.strip()+'\n')
