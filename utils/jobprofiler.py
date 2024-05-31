# =======================================================
# by R.Gacesa (2022, UMCG)
# Simple job profiler for SLURM
# =======================================================

def parseOneL(ln,debug):
   ls = ln.strip().split(':')
   ret = [ls[0].strip(), ls[1].strip()]
   ret[1] = ret[1].replace(' (Until last completed step)','')
   if debug == 'Y':
      print(ret[1])
   if 'CANCELLED' in ret[1] or 'TIMEOUT' in ret[1] or 'FAILED' in ret[1]: ret[1] = ret[1]
   elif ret[1].endswith('G') and not ret[1] == 'RUNNING': ret[1] = float(ret[1].replace('G',''))*1000
   elif ret[1].endswith('M'): ret[1] = float(ret[1].replace('M',''))
   elif ret[1].endswith('K'): ret[1] = float(ret[1].replace('K',''))/1000
   elif ret[1].endswith('T'): ret[1] = float(ret[1].replace('T',''))*1000000
   return ret

def parseTimeL(ln,debug):
   if debug == 'Y':
      print(ln)
   ls = ln.strip().split(':')
   ret = [ls[0].strip(), ':'.join(ls[1:]).strip() ]
   ret[1] = ret[1].replace(' (Until last completed step)','').replace('  ',' ').replace('  ',' ')
   # calculate time in ours
   toth = 0.0
   if '--' in ret[1]:
      days = 0.0
      hrss = '0:0:0'
   elif '-' in ret[1] and '--' not in ret[1]:
      days = float(ret[1].split('-')[0])
      hrss = ret[1].split('-')[1]
   else:
      days = 0.0
      hrss = ret[1]
   toth = days * 24 + float(hrss.split(':')[0])+float(hrss.split(':')[1])/60.0+float(hrss.split(':')[2])/60/60
   toth = round(toth,2)
   ret[1] = toth
   return ret

def parseEffL(ln,debug):
   if debug == 'Y':
      print(' >>> D: running parseEffL')
      print(' >>> D: input = <'+str(ln)+'>')
   if 'efficiency' not in ln:
      ret = [ln.strip(),0.0]
   else:
      ls = ln.strip().split('efficiency: ')
      ret = [ls[0].strip(),ls[1].replace(')','').strip().replace('%','')]
      ret[1] = ret[1].replace(' (Until last completed step)','')
   if debug == 'Y':
      print(' >>> D: parseEffL returns <'+str(ret)+'>')
   return ret

def resAdd(res,key,val):
   if key == 'Req.Cores' or key == 'CPU.Effic' or key == 'Req.Mem' or key == 'Used.Mem' or key == 'Disk.Read' or key == 'Disk.Write':
      val = float(val)
   try: res[key].append(val) #parseOneL(l)[1])
   except: res[key] = [val] #parseOneL(l)][1]
   return res

import argparse
import statistics
import os
from pathlib import Path

# argument parser
parser = argparse.ArgumentParser(description='SLURM job profiler')
parser.add_argument('--jobnames','-J', default='*',help='job name filter [can use wildchars - e.g. -J "*_kn" will find jobs ending with _kn.out] ')
parser.add_argument('--infolder','-I', default='.',help='where to look for jobs output files [def = .] ')
parser.add_argument('--outfile','-O',help="output file [def = _profiles]",default='_profiles')
parser.add_argument('--ignorefail',help="if Y, treates FAILED job as COMPLETED [def = N]",default='N')
parser.add_argument('--verbose',help='if Y, output is verbose [def=N]',default='N')
parser.add_argument('--debug',help='if Y, produces debug output [def=N]',default='N')
args = parser.parse_args()

# look for job logs
res = {}
completeness = []
for f in Path(args.infolder).glob(args.jobnames+'.out'):
   print(f)
   if args.debug == 'Y':
      print(' > parsing',f)
   comp = ''
   if args.ignorefail == 'Y': 
      comp = 'COMPLETED'
   else: 
      with open(f) as iF:
         for l in iF:
            if l.startswith('State '): 
               #print(l)
               comp = parseOneL(l,args.debug)[1]
               completeness.append(comp)
               if comp != 'COMPLETED': break

   if comp == 'COMPLETED':
      with open(f) as iF:
         for l in iF:
            if l.startswith('Cores '): res = resAdd(res,'Req.Cores',parseOneL(l,args.debug)[1])
            elif l.startswith('State '): res = resAdd(res,'State',parseOneL(l,args.debug)[1])
            elif l.startswith('Reserved walltime '): res = resAdd(res,'Req.Time',parseTimeL(l,args.debug)[1])
            elif l.startswith('Used walltime '): res = resAdd(res,'Used.Time',parseTimeL(l,args.debug)[1])
            elif l.startswith('Used CPU time '): res = resAdd(res,'CPU.Effic',parseEffL(l,args.debug)[1])
            elif l.startswith('Mem reserved '): res = resAdd(res,'Req.Mem',parseOneL(l,args.debug)[1])
            elif l.startswith('Full Max Mem usage '): res = resAdd(res,'Used.Mem',parseOneL(l,args.debug)[1])
            elif l.startswith('Total Disk Read '): res = resAdd(res,'Disk.Read',parseOneL(l,args.debug)[1])
            elif l.startswith('Total Disk Write '): res = resAdd(res,'Disk.Write',parseOneL(l,args.debug)[1])

if args.debug == 'Y':
   for (k,v) in res.items():
      print(k,' -> ',v) 

# completeness
if args.verbose == 'Y':
   print('>> JOB COMPLETENESS:')
   for u in sorted(set(completeness)):
      print(u,' : ',completeness.count(u))

# make summaries
if 'Req.Cores' in res.keys():
   print('>> SUMMARY OF COMPLETED JOBS:')
   print('N =',len(res['Req.Cores']))
   for (k,v) in res.items():
      if k == 'Req.Cores':
         print('Cores',':','Mean:',round(statistics.mean(v),1),'SD:',round(statistics.stdev(v),1),'Min:',round(min(v),1) ,'Max:',round(max(v),1))
      elif k == 'Req.Mem':
         print('Req.Memory',':','Mean:',round(statistics.mean(v)/1000,2),'GB; SD:',round(statistics.stdev(v)/1000,2),'GB; Min:',round(min(v)/1000,2),'GB; Max:',round(max(v)/1000,2),'GB')
      elif k == 'Used.Mem':
         print('Used.Memory',':','Mean:',round(statistics.mean(v)/1000,2),'GB; SD:',round(statistics.stdev(v)/1000,2),'GB; Min:',round(min(v)/1000,2),'GB; Max:',round(max(v)/1000,2),'GB')
      elif k == 'CPU.Effic':
         print('CPU efficiency',':','Mean:',round(statistics.mean(v),2),'%; SD:',round(statistics.stdev(v),2),'%; Min:',round(min(v),2),'%; Max:',round(max(v),2),'%')
      elif k == 'Req.Time':
         print('Req.Time [h]',':','Mean:',round(statistics.mean(v),2),'; SD:',round(statistics.stdev(v),2),'; Min:',round(min(v),2),'; Max:',round(max(v),2),'')
      elif k == 'Used.Time':
         print('Used.Time [h]',':','Mean:',round(statistics.mean(v),2),'; SD:',round(statistics.stdev(v),2),'; Min:',round(min(v),2),'; Max:',round(max(v),2),'')
         print('Used.Time [m]',':','Mean:',round(statistics.mean(v)*60,2),'; SD:',round(statistics.stdev(v)*60,2),'; Min:',round(min(v)*60,2),'; Max:',round(max(v)*60,2),'')

# parse job logs

#Job ID              : 23822453
#Name                : i_E100025119_L01_69
#User                : umcg-rgacesa
#Partition           : regular
#Nodes               : pg-node155
#Reserved walltime   : 03:29:00
#Used walltime       : 00:15:16
#Used CPU time       : 00:10:56 (efficiency: 71.62%)
#% User (Computation): 72.79%
#% System (I/O)      : 27.21%
#Mem reserved        : 4G
#Max Mem (Node/step) : 4.63M (pg-node155, per node)
#Full Max Mem usage  : 4.63M
#Total Disk Read     : 26.28G
#Total Disk Write    : 42.03G

