#!/bin/bash
#SBATCH --job-name=ggcaller
#SBATCH --error=__ggcaller.err
#SBATCH --output=__ggcaller.out
#SBATCH --mem=32gb
#SBATCH --time=07:59:00
#SBATCH --cpus-per-task=16
#SBATCH --open-mode=truncate

# =======================================================
# RUNNER for GGcaller Pangenomics tool
# - runs GGcaller on input files (entered as CL param 1)
# - NOTE: input files MUST be .fa or .fasta (and can be mix)
# - example:
#    
# =======================================================

# WORKFLOW:
# > copies input to node tmp: ${TMPDIR}
# > creates GGcaller input
# > runs GGcaller with that input
# > pulls results back 

# > parameters:
OUTPUT=ggcaller_out # where to put output
ALIGNER=def # aligner ( --aligner [def,ref] )
ALIGNMENT=core # what to align ( --alignment [pan,core] )
THREADS=16 # --threads (should be same as CPUs in #SBATCH )
ANNOTATION=ultrasensitive # --annotation [none, fast,sensitive,ultrasensitive] (fast or sensitive makes sense)
ANNOTATION_DB=/scratch/hb-tifn/DBs/uniref90_2023_06_13/uniref90.fasta # --diamonddb (path to diamond db, not used unless annotation != none)
CLEANING=moderate # --clean-mode () [strict,moderate,sensitive]
CLUSTERIDENTITY=0.95 #  --identity-cutoff [Default = 0.98]
CLUSTERLEN=0.95 # --len-diff-cutoff [Default = 0.98]
FAMTHRESHOLD=0.7 # --family-threshold protein family sequence identity threshold [Default = 0.7]
MERGEPARALOGS=True # --merge-paralogs don't split paralogs [Default = False]
CORETHRESHOLD=0.9 # treshold for "core genes" [def = 0.99, MAGs should be ~0.9]

# START OF CODE
echo "> starting ggcaller runner "
CONDA=/scratch/hb-tifn/condas/conda_ggcaller
INPUT=${1}
echo " >> loading conda env. for ggcaller"
# load conda
module purge
module load Anaconda3
source activate ${CONDA}
# prep tmp folder on node
echo " >> preparing temp folder on node"
NTMP=$(mktemp -q -d ${TMPDIR}/ggcaller.XXXXXX)
#NTMP=/scratch/p287673/2024_Niels/genomes/tmp
# check if it worked
if [ $? -ne 0 ]; then
   echo "ERROR: $0: cannot create temp folder on node, quitting"
   exit 1
fi
# copy input files to tmp:
echo " >> copying input data (${INPUT}) to temp folder"
mkdir -p ${NTMP}/input/
cp ${INPUT} ${NTMP}/input/

# prep ggcaller input:
echo " > preparing ggcaller input file"
ls -d -1 ${NTMP}/input/*.fa > ${NTMP}/ggcaller_input.txt
ls -d -1 ${NTMP}/input/*.fasta >> ${NTMP}/ggcaller_input.txt

# run ggcaller
#ALIGNER=def # aligner ( --aligner [def,ref] )
#ALIGNMENT=pan # what to align ( --alignment [pan,core] )
#THREADS=8 # --threads (should be same as CPUs in #SBATCH )
#ANNOTATION=none # --annotation [none, fast,sensitive,ultrasensitive] (fast or sensitive makes sense)
#ANNOTATION_DB=NA # --diamonddb (path to diamond db, not used unless annotation != none)
#CLEANING=moderate # --clean-mode () [strict,moderate,sensitive]
#CLUSTERIDENTITY=0.98 #  --identity-cutoff [Default = 0.98]
#CLUSTERLEN=0.98 # --len-diff-cutoff [Default = 0.98]
#FAMTHRESHOLD=0.7 # --family-threshold protein family sequence identity threshold [Default = 0.7]
#MERGEPARALOGS=False # --merge-paralogs don't split paralogs[Default = False]

echo " >> running ggcaller"
CMD="ggcaller --merge-paralogs --refs ${NTMP}/ggcaller_input.txt --aligner ${ALIGNER} --alignment ${ALIGNMENT} --save --out ${NTMP}/ggcaller_out --threads ${THREADS} --annotation ${ANNOTATION} --diamonddb ${ANNOTATION_DB} --clean-mode ${CLEANING} --identity-cutoff ${CLUSTERIDENTITY} --len-diff-cutoff ${CLUSTERLEN} --family-threshold ${FAMTHRESHOLD} --core-threshold ${CORETHRESHOLD}"
echo ${CMD}
${CMD}

# get data
echo " >> retrieving data from temp folder"
mkdir -p ${OUTPUT}
cp -r ${NTMP}/ggcaller_out/* ${OUTPUT}
# DONE
echo "> DONE"
