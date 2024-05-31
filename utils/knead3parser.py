import argparse
import csv
import os

#SBATCH --partition=vulture
#SBATCH --partition=vulture
#SBATCH --partition=vulture
# set CL params
parser = argparse.ArgumentParser()
parser.add_argument("--infile",help="input file (kneadddata log)",required=True)
parser.add_argument("--outfile",help="out file",required=True)
args = parser.parse_args()

# load file and parse it
rawRead1 = 0
rawRead2 = 0
trimPE1 = 0
trimPE2 = 0
trimO1 = 0
trimO2 = 0

sampleName = os.path.basename(args.infile).replace('_kneaddata.log','').strip()

with open(args.infile) as iF:
   for l in iF:
      l = l.strip()
      # raw 1
      if 'kneaddata.utilities - INFO: READ COUNT: raw pair1 : Initial number of reads' in l:
          rawRead1 = int(float(l.split('Initial number of reads')[1].split(':')[1].strip()))
#          print(rawRead1)
      # raw 2
      if 'kneaddata.utilities - INFO: READ COUNT: raw pair2 : Initial number of reads' in l:
          rawRead2 = int(float(l.split('Initial number of reads')[1].split(':')[1].strip()))
#          print(rawRead2)
      # after trim 1 (PE)
      if 'kneaddata.utilities - INFO: READ COUNT: trimmed pair1 : Total reads after trimming' in l:
          trimPE1 = int(float(l.split('Total reads after trimming')[1].split(':')[1].strip()))
#          print(trimPE1)
      # after trim 1 (PE)
      if 'kneaddata.utilities - INFO: READ COUNT: trimmed pair2 : Total reads after trimming' in l:
          trimPE2 = int(float(l.split('Total reads after trimming')[1].split(':')[1].strip()))
#          print(trimPE2)
      # after trim orphans 1
      if 'kneaddata.utilities - INFO: READ COUNT: trimmed orphan1 : Total reads after trimming' in l:
          trimO1 = int(float(l.split('Total reads after trimming')[1].split(':')[1].strip()))
#          print(trimO1)
      # after trim orphans 2
      if 'kneaddata.utilities - INFO: READ COUNT: trimmed orphan2 : Total reads after trimming' in l:
          trimO2 = int(float(l.split('Total reads after trimming')[1].split(':')[1].strip()))
#          print(trimO2)

      # ======= TRF =======
      # TRF (PE 1)
      trfPE1 = 0
      if 'kneaddata.run - INFO: Total number of sequences with repeats removed from file' in l and '.trimmed.1.fastq' in l:
          trfPE1 = int(float(l.split('number of sequences with repeats removed from file')[1].split(':')[1].strip()))
#          print(trfPE1)
#          postTrfPE1 = trimPE1 - trfPE1
      # TRF (PE 2)
      trfPE2 = 0
      if 'kneaddata.run - INFO: Total number of sequences with repeats removed from file' in l and '.trimmed.2.fastq' in l:
          trfPE2 = int(float(l.split('number of sequences with repeats removed from file')[1].split(':')[1].strip()))
#          print(trfPE2)
#          postTrfPE2 = trimPE2 - trfPE2
      # TRF (O 1)
      trfO1 = 0
      if 'kneaddata.run - INFO: Total number of sequences with repeats removed from file' in l and '.trimmed.single.1.fastq' in l:
          trfO1 = int(float(l.split('number of sequences with repeats removed from file')[1].split(':')[1].strip()))
#          print(trfO1)
#          postTrfO1 = trimO1 - trfO1
      # TRF (O 2)
      trfO2 = 0
      if 'kneaddata.run - INFO: Total number of sequences with repeats removed from file' in l and '.trimmed.single.2.fastq' in l:
          trfO2 = int(float(l.split('number of sequences with repeats removed from file')[1].split(':')[1].strip()))
#          print(trfO2)
#          postTrfO2 = trimO2 - trfO2

      # ====== decontamination ======       
      # Cont (PE 1)
      if 'kneaddata.run - INFO: Total contaminate sequences in file' in l and 'paired_contam_1' in l:
          contPE1 = int(float(l.split('kneaddata.run - INFO: Total contaminate sequences in file')[1].split(':')[1].strip()))
#          postContPE1 = postTrfPE1 - contPE1
#          print(contPE1)
      # Cont (PE 2)
      if 'kneaddata.run - INFO: Total contaminate sequences in file' in l and 'paired_contam_2' in l:
          contPE2 = int(float(l.split('kneaddata.run - INFO: Total contaminate sequences in file')[1].split(':')[1].strip()))
#          postContPE2 = postTrfPE2 - contPE2
#          print(contPE2)
      # Cont (O 1)
      if 'kneaddata.run - INFO: Total contaminate sequences in file' in l and 'unmatched_1_contam' in l:
          contO1 = int(float(l.split('kneaddata.run - INFO: Total contaminate sequences in file')[1].split(':')[1].strip()))
#          postContO1 = postTrfO1 - contO1
#          print(contO1)
      # Cont (PE 2)
      if 'kneaddata.run - INFO: Total contaminate sequences in file' in l and 'unmatched_2_contam' in l:
          contO2 = int(float(l.split('kneaddata.run - INFO: Total contaminate sequences in file')[1].split(':')[1].strip()))
#          postContO2 = postTrfO2 - contO2
#          print(contO2)

      # ====== FINAL ======= 
      # PE1
      if 'kneaddata.utilities - INFO: READ COUNT: final pair1 : Total reads after merging results from multiple databases' in l:
          finalPE1 = int(float(l.split('Total reads after merging results from multiple databases')[1].split(':')[1].strip()))
#          print(finalPE1)
      # PE2
      if 'kneaddata.utilities - INFO: READ COUNT: final pair2 : Total reads after merging results from multiple databases' in l:
          finalPE2 = int(float(l.split('Total reads after merging results from multiple databases')[1].split(':')[1].strip()))
#          print(finalPE2)
      # O1
      if 'kneaddata.utilities - INFO: READ COUNT: final orphan1 : Total reads after merging results from multiple databases' in l:
          finalO1 = int(float(l.split('Total reads after merging results from multiple databases')[1].split(':')[1].strip()))
#          print(finalO1)
      # O2
      if 'kneaddata.utilities - INFO: READ COUNT: final orphan2 : Total reads after merging results from multiple databases' in l:
          finalO2 = int(float(l.split('Total reads after merging results from multiple databases')[1].split(':')[1].strip()))
#          print(finalO2)


res1 = ['Sample','Raw reads (p1)','Raw reads (p2)','Trimmed (p1)','Trimmed (p2)','Trimmed (o)','Trimmed (o2)','Repeats (p1)','Repeats (p2)','Repeats (o1)','Repeats (o2)','Contaminants (p1)','Contaminants (p2)','Contaminants (o1)','Contaminants (o2)','Final (p1)','Final (p2)','Final (o1)','Final (o2)']
res2 = [sampleName, rawRead1,rawRead2,trimPE1,trimPE2,trimO1,trimO2,trfPE1,trfPE2,trfO1,trfO2,contPE1,contPE2,contO1,contO2,finalPE1,finalPE2,finalO1,finalO2]

with open(args.outfile,'w') as oF:
   writ = csv.writer(oF)
   writ.writerow(res1)
   writ.writerow(res2)
