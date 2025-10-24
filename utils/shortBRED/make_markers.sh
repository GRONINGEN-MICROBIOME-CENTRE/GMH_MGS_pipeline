#!/bin/bash
#SBATCH --job-name=ResF_makem
#SBATCH --error=ResF_makem.err
#SBATCH --output=ResF_makem.out
#SBATCH --mem=32gb
#SBATCH --time=5:23:59:00
#SBATCH --cpus-per-task=24

#module load Biopython
conda activate /scratch/hb-tifn/condas/conda_assemblers
module load DIAMOND/2.0.13-GCC-11.2.0

USEARCH=/scratch/hb-tifn/tools/GMH_pipeline/utils/usearch10.0.240_i86linux32
REF=/scratch/p287673/tools_DBs/2025_06_UniRef50/uniref50.fasta
IN=${1}

./shortbred_identify.py --goi ${1} --refdb ${REF} --markers shortbred_markers.fa --tmp tmp_shortbred_identify --usearch ${USEARCH} --threads 24
