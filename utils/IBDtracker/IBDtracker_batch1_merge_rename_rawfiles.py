import csv
import os
# === merger of IBDtracker fastq files ===
splitter = {}
cnt = 0
with open('/scratch/hb-tifn/rgacesa/IBDtracker/codes/IBD_tracker_filematching_v2.csv') as iF:
   rdr = csv.reader(iF,delimiter=',')
   for l in rdr:
      cnt += 1
      if cnt == 1: continue
      #print(l)
      try: 
         splitter[l[0]].append(l[8])
      except:
         splitter[l[0]] = [l[8]]

mkdirCmd = 'mkdir -p mrg'
print(mkdirCmd)
os.system(mkdirCmd)

for k in sorted(splitter.keys()):
   print(' >> merging lanes and renaming samples for ',k)
   t1 = 'mrg/'+k+'_1.fq.gz'
   t2 = 'mrg/'+k+'_1.fq.gz'

   if os.path.exists(t1):
      cleanCmd = 'rm '+t1
      print(cleanCmd)
      os.system(cleanCmd)

   if os.path.exists(t2):
      cleanCmd = 'rm '+t2
      print(cleanCmd)
      os.system(cleanCmd)

   for v in splitter[k]:
      mrgCmd = 'cat raw/'+v+' >> mrg/'+k+'_1.fastq.gz'
      print(mrgCmd)
      os.system(mrgCmd)
   for v in splitter[k]:
      mrgCmd = 'cat raw/'+v.replace('.1.fastq.gz','.2.fastq.gz')+' >> mrg/'+k+'_2.fastq.gz'
      print(mrgCmd)
      os.system(mrgCmd)
