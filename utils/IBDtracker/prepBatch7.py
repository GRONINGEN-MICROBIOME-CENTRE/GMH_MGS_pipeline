# ================================================
# rename files & merge lanes to prep for pipeline
# ================================================
import os
import fnmatch
import re
fls = set()
samples = {} # sample -> {sample,(lane1_1,lane2_1...),(lane2_1,lane2_2,...)}
todel = set()
for f in os.listdir('.'):
   fn = os.fsdecode(f)
   if '.fastq.gz' in fn:
      fn2 = fn.replace('HNW2FDRX3_1_0420637951_','').replace('_R2_001.','_2.').replace('_R1_001.','_1.').replace('HNW2FDRX3_2_0420637951_','')
      os.system('rename '+fn+' '+fn2+' '+fn+' --no-overwrite')

for f in os.listdir('.'):
   fn = os.fsdecode(f)
   if fnmatch.fnmatch(fn,'*_L00*_1.fastq.gz'):
       sname = (re.sub('_L00[1234567890]_1.fastq.gz','',fn))
       try:
          samples[sname][0].append(fn)
       except:
          samples[sname] = [[fn],[]]
   elif fnmatch.fnmatch(fn,'*_L00*_2.fastq.gz'):
       sname = (re.sub('_L00[1234567890]_2.fastq.gz','',fn))
       try:
          samples[sname][1].append(fn)
       except:
          samples[sname] = [[],[fn]]

for (k,v) in samples.items():
    print(k,'->',v)
    if len(v[0]) == 1:
       os.system('mv '+v[0][0]+' '+k+'_1.fastq.gz')
       os.system('mv '+v[1][0]+' '+k+'_2.fastq.gz')
