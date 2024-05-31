#!/bin/bash
#SBATCH --job-name=ggcaller
#SBATCH --error=__ggcaller.err
#SBATCH --output=__ggcaller.out
#SBATCH --mem=32gb
#SBATCH --time=23:59:00
#SBATCH --cpus-per-task=8
#SBATCH --open-mode=truncate

# =======================================================
# RUNNER for GGcaller Pangenomics tool
# - runs GGcaller on input file with paths (entered as CL param 1)
# - NOTE: input files MUST be text file with path to ONE MAG PER LINE
#       
# - example input file:
#       </scratch/cookie_DNA/cookie_MAG1.fa>     
#       </scratch/cookie_DNA/cookie_MAG2.fa>     
#       </scratch/cookie_DNA_try2/bad_cookie_MAG1.fa>     
#       </scratch/cookie_DNA_try2/bad_cookie_MAG2.fa>     
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
ALIGNMENT=pan # what to align ( --alignment [pan,core] )
THREADS=8 # --threads (should be same as CPUs in #SBATCH )
ANNOTATION=none # --annotation [none, fast,sensitive,ultrasensitive] (fast or sensitive makes sense)
ANNOTATION_DB=NA # --diamonddb (path to diamond db, not used unless annotation != none)
CLEANING=moderate # --clean-mode () [strict,moderate,sensitive]
CLUSTERIDENTITY=0.98 #  --identity-cutoff [Default = 0.98]
CLUSTERLEN=0.98 # --len-diff-cutoff [Default = 0.98]
FAMTHRESHOLD=0.7 # --family-threshold protein family sequence identity threshold [Default = 0.7]
MERGEPARALOGS=False # --merge-paralogs don't split paralogs[Default = False]

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
# check if it worked
if [ $? -ne 0 ]; then
   echo "ERROR: $0: cannot create temp folder on node, quitting"
   exit 1
fi
# copy input files to tmp:
echo " >> copying input data (${INPUT}) to temp folder"
mkdir ${NTMP}/input/
cp ${INPUT} ${NTMP}/input/

echo " >> running ggcaller"
CMD="ggcaller --refs ${INPUT} --aligner ${ALIGNER} --alignment ${ALIGNMENT} --save --out ${NTMP}/ggcaller_out --threads ${THREADS} --annotation ${ANNOTATION} --diamonddb ${ANNOTATION_DB} --clean-mode ${CLEANING} --identity-cutoff ${CLUSTERIDENTITY} --len-diff-cutoff ${CLUSTERLEN} --family-threshold ${FAMTHRESHOLD}"
echo ${CMD}
${CMD}

# get data
echo " >> retrieving data from temp folder"
mkdir -p ${OUTPUT}
cp -r ${NTMP}/ggcaller_out/* ${OUTPUT}
# DONE
echo "> DONE"
