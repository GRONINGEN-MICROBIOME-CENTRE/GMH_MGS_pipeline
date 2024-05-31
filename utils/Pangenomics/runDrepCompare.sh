#!/bin/bash
#SBATCH --job-name=drep
#SBATCH --error=__drep.err
#SBATCH --output=__drep.out
#SBATCH --mem=16gb
#SBATCH --time=01:59:00
#SBATCH --cpus-per-task=8
#SBATCH --open-mode=truncate

# =======================================================
# RUNNER FOR DRep tool
#  > two command line parameters: 
#  [1] : input (should be something like "input/*.fa")
#  [2] : output (should be something like "drep_out")
# > example: 
# sbatch <path>/runDrep compare "input/*.fa" drep_out
# =======================================================
CONDA=/scratch/hb-tifn/condas/conda_ROARY
BIN=dRep
COMMAND=compare
INPUT=${1}
THREADS=8
OUT=${2}
# test for correct input
if [ "$#" -ne 2 ]; then
  echo " > script requires two positional arguments: [Input] & [Output]"
  exit 9
fi
# load conda
module purge
module load Anaconda3
source activate ${CONDA}
# run it
mkdir -p ${TMP}
CMD="dRep ${COMMAND} ${OUT} -p ${THREADS} -g ${INPUT}"
echo ${CMD}
${CMD}
