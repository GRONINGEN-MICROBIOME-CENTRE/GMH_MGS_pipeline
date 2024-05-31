#!/bin/bash
#SBATCH --job-name=tRoary
#SBATCH --error=__roary.err
#SBATCH --output=__roary.out
#SBATCH --mem=16gb
#SBATCH --time=07:59:00
#SBATCH --cpus-per-task=8
#SBATCH --open-mode=truncate

# =======================================================
# ROARY RUNNER
# - runs ROARY job for one file [command line param]
# =======================================================
CONDA=/scratch/hb-tifn/condas/conda_ROARY/
INPUT=${1}
# load conda
module purge
module load Anaconda3
source activate ${CONDA}

# -cd = CORE GENE CUTOFF (default = 99, 90 is recommended for MAGs)
# -i = blast identity (Default = 95, we cut it to 90 for MAGs)
CUTOFF=90
BLASTI=90
CMD="roary -e --mafft -p 8 -f ROARY_output -i ${BLASTI} -cd ${CUTOFF} -r  ${INPUT}/*.gff3"
echo ${CMD}
${CMD}
