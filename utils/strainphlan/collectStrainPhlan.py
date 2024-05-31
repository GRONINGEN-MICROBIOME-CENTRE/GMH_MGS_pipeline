import os
import os.path
import sys

if not os.path.isdir('../done'):
   os.system('mkdir ../done')

for f in os.listdir('.'):
   if os.path.isfile(f): 
      continue
   isDone = False
   if os.path.exists(f+'/strainphlan/') and os.path.exists(f+'/metaphlan'):
      pl = os.listdir(f+'/strainphlan/')
      for pp in pl:
#         print pp
         if pp.endswith('.markers'):
            isDone=True
   if isDone:
      print f
      os.system('rm -r '+f+'/clean_reads/')
      os.system('rm '+f+'*.sh')
      os.system('mv '+f+' ../done')
      os.system('mv '+f+'*.fq ../done')
