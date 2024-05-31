# by: R.Gacesa (UMCG, 2011)
# =======================================
# fixes Kraken report from UHGG database
# to make it compatible with Bracken
# =======================================

import sys

if not len(sys.argv) == 2:
    print(' > ERROR: requires input file (Kraken report)')
    quit(0)

print(' > loading and fixing kraken report',sys.argv[1])

with open(sys.argv[1]) as iF:
   with open(sys.argv[1]+'.bc','w') as oF:
      for l in iF:
         l = l.replace('\tR7\t','\tS\t')
         l = l.replace('\tR6\t','\tG\t')
         l = l.replace('\tR5\t','\tF\t')
         l = l.replace('\tR4\t','\tO\t')
         l = l.replace('\tR3\t','\tC\t')
         l = l.replace('\tR2\t','\tP\t')
         l = l.replace('\tR1\t','\tD\t')
         oF.write(l)
print(' > DONE, output saved to',sys.argv[1]+'.bc')
