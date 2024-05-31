`# =============================================================================
# merges multi-lane samples in current folder
# =============================================================================
import os
import pandas as pd

smpls = {}
smpls['File'] = []
smpls['ID'] = []
smpls['Lane'] = []
smpls['Pair'] = []
for f in os.listdir('.'):
    if f.endswith('.fq.gz'):
        #print(f)
        fID = '_'.join(f.split('_')[0:2])
        #print(fID)
        # parse Lane and Pair
        fS = f.split('_L')[1].replace('.fq.gz','')
        # > lane
        fLn = fS.split('_')[0]
        # > pair
        fPr = fS.split('_')[1]
        #print(fID,'; Lane:',fLn,'; Pair:',fPr)
        smpls['File'].append(f)
        smpls['ID'].append(fID)
        smpls['Lane'].append(fLn)
        smpls['Pair'].append(fPr)


df = pd.DataFrame(smpls)
print(df)
df['ID_count'] = df.groupby('ID')['Lane'].transform('count')
df2 = df[df['ID_count'] > 2]
df2 = df2.sort_values('ID')

print('copying samples to "/mrg"')
os.system('mkdir -p mrg')
for f in df2['File'].values: 
    print(f)
    os.system('cp '+f+' mrg/')

print('moving multi-lane samples to "/mrg ')
os.system('mkdir -p mrg')
for f in df2['File'].values: 
    print(f)
    os.system('mv '+f+' mrg/')

# go through them one by one, merge
df.to_csv('samples.csv')
df2.to_csv('multi_lane_samples.csv')
os.chdir('mrg')
for i in df2['ID'].unique(): 
    print(' > processing ',i)
    print('  >> pair 1')
    df3 = df2[(df2['ID'] == i) & (df2['Pair'] == '1')]
    for f in df3['File'].values:
        cmd = 'cat '+f+' >> '+i+'_Lmerged_1.fq.gz'
        print(cmd)
        os.system(cmd)
        cmd = 'rm '+f
        print(cmd)
        os.system(cmd)
    print('  >> pair 2')
    df3 = df2[(df2['ID'] == i) & (df2['Pair'] == '2')]
    for f in df3['File'].values:
        cmd = 'cat '+f+' >> '+i+'_Lmerged_2.fq.gz'
        print(cmd)
        os.system(cmd)
        cmd = 'rm '+f
        print(cmd)
        os.system(cmd)

# return samples to original folder and clean
cmd = 'mv * ..'
print(cmd)
os.system(cmd)
os.system('cd ..')
os.system('rm -r mrg/')
