import csv
import os
# === merger of IBDtracker fastq files ===
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
   print(' >> merging files for co-assembly of ',k)
   cleanCmd = 'rm -r '+k
   print(cleanCmd)
   os.system(cleanCmd)
   mkdirCmd = 'mkdir -p '+k
   print(mkdirCmd)
   os.system(mkdirCmd)
   for v in splitter[k]:
      mrgCmd = 'cat all_samples/'+v+'.1.fastq.gz >> '+k+'/'+k+'_1.fastq.gz'
      print(mrgCmd)
      os.system(mrgCmd)
      mrgCmd = 'cat all_samples/'+v+'.2.fastq.gz >> '+k+'/'+k+'_2.fastq.gz'
      print(mrgCmd)
      os.system(mrgCmd)
