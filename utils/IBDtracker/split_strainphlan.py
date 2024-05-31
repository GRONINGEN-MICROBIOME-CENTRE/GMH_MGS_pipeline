import csv
import os
# === splitter for panphlan results === 
splitter = {}
with open('filelist.tsv') as iF:
   rdr = csv.reader(iF,delimiter='\t')
   for l in rdr:
      #print(l)
      try: 
         splitter[l[0]].append(l[2])
      except:
         splitter[l[0]] = [l[2]]

for k in sorted(splitter.keys()):
   print(' >> splitting panphlan results per patient ',k)
   cleanCmd = 'rm -r IBDt_strainphlan_split/'+k
   print(cleanCmd)
   os.system(cleanCmd)
   mkdirCmd = 'mkdir -p IBDt_strainphlan_split/'+k
   print(mkdirCmd)
   os.system(mkdirCmd)
   for v in splitter[k]:
      mrgCmd = 'cp IBDtracker_sorted/strainphlan4/'+v+'*.pkl IBDt_strainphlan_split/'+k+'/'
      print(mrgCmd)
      os.system(mrgCmd)
