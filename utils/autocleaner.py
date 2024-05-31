import os
# autocleaner:
# - goes through folders
# - looks for finished jobs
#  --> cleans stuff (fastq and gz) if job is done

d = 0
for l in os.listdir('.'):
#   print l
   if os.path.isdir(l):
      d += 1
#      print d
#      if d % 10 == 0:
#          print d
      rfDone = False
      vfdbDone = False
      # has resfinder results
      if os.path.isdir(l+'/ResFinderSB'):
         if len(os.listdir(l+'/ResFinderSB')) >= 4:
            rfDone = True
      # has vfdb results 
      if os.path.isdir(l+'/VFDB_SB'):
         if len(os.listdir(l+'/VFDB_SB')) >= 4:
            vfdbDone = True
      if vfdbDone and rfDone:
          #print l+'/clean_reads'
          if os.path.isdir(l+'/clean_reads'):
             rmcmd = 'rm -r '+l+'/clean_reads' 
             print rmcmd        
             os.system(rmcmd)
             rmcmd = 'rm '+l+'*.fq.gz'
             print rmcmd
             os.system(rmcmd)
