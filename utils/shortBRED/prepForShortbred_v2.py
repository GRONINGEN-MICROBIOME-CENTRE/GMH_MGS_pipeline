import sys
import re
import csv
chk = set()
mapper = dict()
with open('out.fa','w') as oF:
    with open(sys.argv[1]) as iF:
        for l in iF:        
            ls = l.strip()
            if ls.startswith('>'):
                lsorig = ls
                #s = ls.split(' ')[0]
                ls =  re.sub('[^a-zA-Z0-9>\n]', '_', ls)
                ls =  re.sub('_$', '', ls)
                ls =  re.sub('__', '_', ls)
                ls =  re.sub('__', '_', ls)
                #ls = ls.split('|')[0]
                #print (ls,'->',lsorig)
                mapper[ls] = lsorig
                if ls in chk:
                    print ('WARNING, duplicate ID',lss)
#                print(ls)
            oF.write(ls+'\n')
with open('out_mapper.txt','w') as oF:
    csvw = csv.writer(oF,quoting=csv.QUOTE_ALL)
    for k in mapper.keys():
        csvw.writerow([k,mapper[k]])
