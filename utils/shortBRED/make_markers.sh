#!/bin/bash
#SBATCH --job-name=ResF_makem
#SBATCH --error=ResF_makem.err
#SBATCH --output=ResF_makem.out
#SBATCH --mem=32gb
#SBATCH --time=5:23:59:00
#SBATCH --cpus-per-task=24

module load Biopython
module load DIAMOND/2.0.13-GCC-11.2.0
USEARCH=/scratch/hb-tifn/tools/GMH_pipeline/utils/usearch10.0.240_i86linux32
REF=/scratch/hb-tifn/DBs/uniref90_2023_06_13/uniref90.fasta.gz
IN=${1}

./shortbred_identify.py --goi ${1} --ref ${REF} --markers shortbred_markers.fa --tmp tmp_shortbred_identify --usearch ${USEARCH} --threads 24
