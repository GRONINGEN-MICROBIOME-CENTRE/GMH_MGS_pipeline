# =======================================================================
# Lane merger with sample => lane file
# 
# =======================================================================
# set CL params
import argparse
import pandas
import os

parser = argparse.ArgumentParser()
parser.add_argument('-F', "--filelist", help="list of files [MUST include columns: Sample_ID, Lane, Barcode_start, Barcode_end",required=True)
parser.add_argument('-I','--input_path', help="where to look for files? [def='.']",default='.')
parser.add_argument('-O', '--output_path', help="where to put merged, renamed, files? [def='out/']",default='out/')
args = parser.parse_args()

# load datafile
if not os.path.isfile(args.filelist):
    print(' >> ERROR: sample list file',args.filelist,' does not exist!')
    exit()

if not os.path.isdir(args.input_path):
    print(' >> ERROR: input path',args.input_path,' does not exist!')
    exit()

if not os.path.isdir(args.output_path):
    print(' >> WARNING: output path',args.output_path,' does not exist!')
    try:
        os.makedirs(args.output_path)
        print('   >>> output folder successfully created!')
    except:
        print(' >> ERROR: cannot create output folder!') 

# load file with samples and check if it is OK
# ============================================
try:
    inDF = pandas.read_csv(args.filelist)
    inDF['filename'] = inDF['Lane'].astype(str)+'.'+inDF['Barcode_start']+'_'+inDF['Barcode_end']
except:
    print(' >> ERROR: cannot load ',args.filelist)
    exit()

colN = list(inDF.columns)
if ('Sample_ID' not in colN) or ('Lane' not in colN) or ('Barcode_start' not in colN) or ('Barcode_end' not in colN):
    print(' >> ERROR: filelist table column names MUST include SampleID, Lane, Barcode_start, Barcode_end!')

# === file list ====
fls = os.listdir('.')

# === collect per sample ===
for i in inDF['Sample_ID'].unique():
    print(' > processing ',i)
    df2 = inDF[inDF['Sample_ID'] == i]
    print('  >> pair 1')
    tomerge = []
    newfile = args.output_path+'/'+i+'_1.fastq.gz'
    for f in fls:
        for ff in df2['filename']:
           if ff in f and '1.fastq.gz' in f:
              tomerge.append(f)
    if os.path.exists(newfile):
        cmd = 'rm '+newfile
        print(cmd)
        os.system(cmd)
    for ff in tomerge:
       cmd = 'cat '+ff+' >> '+newfile       
       print(cmd)
       os.system(cmd)

    print('  >> pair 2')
    tomerge = []
    newfile = args.output_path+'/'+i+'_2.fastq.gz'
    for f in fls:
        for ff in df2['filename']:
           if ff in f and '2.fastq.gz' in f:
              tomerge.append(f)
    if os.path.exists(newfile):
        cmd = 'rm '+newfile
        print(cmd)
        os.system(cmd)
    for ff in tomerge:
       cmd = 'cat '+ff+' >> '+newfile       
       print(cmd)
       os.system(cmd)
