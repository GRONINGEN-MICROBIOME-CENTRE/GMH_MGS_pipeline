# by R.Gaces (UMCG)
# Transforms Kraken2 report to metaphlan3 result format

# NOTES:
# - report must comply with level names:
#    > U = unclassifier
#    > D = domain (kingdom in metaphlan)
#    > P = phylum
#    > C = class
#    > O = order
#    > F = family
#    > G = genus
#    > S = species
# ==========================================================
import argparse
import re
import csv

def dropPrefix(inStr):
   inStr = re.sub('^d__','',inStr)
   inStr = re.sub('^k__','',inStr)
   inStr = re.sub('^p__','',inStr)
   inStr = re.sub('^c__','',inStr)
   inStr = re.sub('^o__','',inStr)
   inStr = re.sub('^f__','',inStr)
   inStr = re.sub('^g__','',inStr)
   inStr = re.sub('^s__','',inStr)
   return inStr

def getLvlNR(inStr):
   if inStr == 'U': return -1
   elif inStr == 'D': return 0
   elif inStr == 'P': return 1
   elif inStr == 'C': return 2
   elif inStr == 'O': return 3
   elif inStr == 'F': return 4
   elif inStr == 'G': return 5
   elif inStr == 'S': return 6
   else: return -2

def getMpName(nameList,cLvl):
   retList = []
   retList.append('k__'+nameList[0])
   retList.append('p__'+nameList[1])
   retList.append('c__'+nameList[2])
   retList.append('o__'+nameList[3])
   retList.append('f__'+nameList[4])
   retList.append('g__'+nameList[5])
   retList.append('s__'+nameList[6])
   return '|'.join(retList[0:cLvl+1])

# =========================== MAIN ===================
# ===================================================
parser = argparse.ArgumentParser()
parser.add_argument("--infile", help="Kraken report input file",required=True)
parser.add_argument("--out", help="metaphlan3 output file",required=True)
args = parser.parse_args()
# put report here first
mp3r = []

cLvl = -1
cLvlNR = -1
cK = ''
cP = ''
cC = ''
cO = ''
cG = ''
cS = ''
#         K  P  C  O  F  G  S
cFName = ['','','','','','','']

with open(args.out,'w') as oF:
   writ = csv.writer(oF,delimiter='\t')
   # header (required for MP3 merging)
   mp3r.append(['#KRAKEN2_Bracken'])
   mp3r.append(['#NA'])
   mp3r.append(['#SampleID',args.infile])
   mp3r.append(['#clade_name','clade_taxid','relative_abundance','coverage','estimated_number_of_reads_from_the_clade'])
   totalReads = 0
   with open(args.infile) as iF:
      rdr = csv.reader(iF,delimiter='\t')
      for l in rdr:  
          # parse one line
          #print(l)
          # tax level (0 = kingdom, 6 = species)
          lLvl = l[3].strip()
          lLvlNr = getLvlNR(lLvl)
          #print('lvl =',lLvl,'/',lLvlNr)
          # nr of reads
          lReads = l[1].strip()
          #print('nr reads =',lReads)
          # NOTE: we only count kingdoms and unknown into total reads
          if lLvlNr == -1 or lLvlNr == 0:
             totalReads += int(lReads)
          # taxonomy ID
          taxID = l[4].strip()
          if lLvlNr == -1:
             taxID = -1
          # name of taxon
          lName = dropPrefix(l[5].strip())
          # put it in "full name" list
          if lLvlNr >= 0:
             cFName[lLvlNr] = lName
          #print('tax name =',lName)
          # get full name
          if lLvlNr == -2: mp3name = 'NA'
          elif lLvlNr == -1: mp3name = 'UNKNOWN'          
          else: mp3name = getMpName(cFName,lLvlNr)
          #print('naming list =',cFName)
          #print('MP3 name =',mp3name)
          #print('TaxID =',taxID)
          #print(' ================ ')
          # write line for MP3 output
          if lLvlNr > -2:
             mp3r.append([mp3name,taxID,l[0].strip(),'NA',int(lReads)])

   # report done, now re-calculate relative abundances
   print('total reads =',totalReads,' re-calculating relative abundances')
   for oR in mp3r:
      if oR[0].startswith('#'): pass
      else: oR[2] = oR[4]/totalReads*100.0
      writ.writerow(oR)
