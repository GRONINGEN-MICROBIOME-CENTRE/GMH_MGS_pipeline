import os

os.system('iquest "SELECT RESC_FREE_SPACE" | grep FREE > _tmpst.tst')
units = 0
total = 0
with open('_tmpst.tst') as iF:
  for l in iF:
     ll = l.split(' ')[2].strip()
     if ll != '':
        units +=1
        total += int(ll)

print('detected: ',units,'HDDs, total free space: ',round(total*9.313225746154785e-10),'GB')
