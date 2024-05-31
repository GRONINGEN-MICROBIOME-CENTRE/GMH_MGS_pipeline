#!/bin/bash
#SBATCH --job-name=drep_dr
#SBATCH --error=__drep_dereplicate.err
#SBATCH --output=__drep_dereplicate.out
#SBATCH --mem=16gb
#SBATCH --time=01:59:00
#SBATCH --cpus-per-task=8
#SBATCH --open-mode=truncate

# =======================================================
# RUNNER FOR DRep tool
#  > two command line parameters: 
#  [1] : input (should be something like "input/*.fa")
#  [2] : output (should be something like "drep_out")
#  [3] : checkM table (create it using /projects/hb-tifn/tools/GMH_pipeline/utils/binning_ptmp/collectCheckMonefolder.py)
# > example: 
# sbatch <path>/rundrep "input/*.fa" drep_dereplicate_out bin_stats_checkm.csv 
# =======================================================
CONDA=/scratch/hb-tifn/condas/conda_ROARY
BIN=dRep
COMMAND=dereplicate
INPUT=${1}
OUTPUT=${2}
CHECKM=${3}
THREADS=8
# SET parameters here
# --length LENGTH: Minimum genome length (default: 50000)
LENGTH=50000
# --completeness COMPLETENESS: Minimum genome completeness (default: 75)
COMPLETNESS=85
# --contamination CONTAMINATION Maximum genome contamination (default: 25)
CONTAMINATION=10
# EXTRA:
EXTRA=--run_tertiary_clustering 

# test for correct input
if [ "$#" -ne 3 ]; then
   echo " > script requires 3 positional arguments: [Input] [Output] [CheckM results table]"
   echo "example: sbatch <path>/runDrepCompare.sh \"input/*.fa\" drep_dereplicate_out bin_stats_checkm.csv"
   exit 9
fi


# load conda
module purge
module load Anaconda3
source deactivate
source activate ${CONDA}
# run it
mkdir -p ${TMP}
CMD="dRep ${COMMAND} ${OUTPUT} -p ${THREADS} -g ${INPUT} --genomeInfo ${CHECKM} --completeness ${COMPLETNESS} --contamination ${CONTAMINATION} --length ${LENGTH} --debug ${EXTRA}"
echo ${CMD}
${CMD}
