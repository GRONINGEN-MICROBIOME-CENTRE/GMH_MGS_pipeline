import csv
import os
# === merger of IBDtracker fastq files ===
splitter = {}
with open('filelist.tsv') as iF:
   rdr = csv.reader(iF,delimiter='\t')
   for l in rdr:
      #print(l)
      try: 
         fn = l[2]+'/clean_reads/'+l[2]+'_kneaddata_cleaned_pair'
         splitter[l[0]].append(fn)
      except:
         splitter[l[0]] = [fn]

for k in sorted(splitter.keys())[1:]:
   print(' >> merging cleaned files for co-assembly of ',k)
   cleanCmd = 'rm -r '+k
   print(cleanCmd)
   os.system(cleanCmd)
   mkdirCmd = 'mkdir -p '+k
   print(mkdirCmd)
   os.system(mkdirCmd)
   for v in splitter[k]:
      mrgCmd = 'cat all_samples/'+v+'_1.fastq >> '+k+'/'+k+'_clean_1.fastq'
      print(mrgCmd)
      os.system(mrgCmd)
      mrgCmd = 'cat all_samples/'+v+'_2.fastq >> '+k+'/'+k+'_clean_2.fastq'
      print(mrgCmd)
      os.system(mrgCmd)
   exit()
