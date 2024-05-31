#!/bin/bash

#SBATCH --mem=24gb
#SBATCH --time=0-03:59:59
#SBATCH --cpus-per-task=8
#SBATCH --open-mode=truncate
#SBATCH --job-name=SP4pr
#SBATCH --error=__SP4_profile.err
#SBATCH --output=__SP4_profile.out

# NOTES:
# script profiles all clades in the dataset in given folder ($1)
# puts results in the current folder!

# PARAMS
N=50 # --marker_in_n_samples
S=20 # --sample_with_n_markers 20
DB=/scratch/hb-tifn/condas/conda_biobakery4/lib/python3.10/site-packages/metaphlan/metaphlan_databases/mpa_vOct22_CHOCOPhlAnSGB_202212.pkl

# purge modules
module purge
# load conda
ml Anaconda3
# load conda env
source activate /scratch/hb-tifn/condas/conda_biobakery4
# run clade profiling
strainphlan -s ${1}/*.pkl --marker_in_n_samples ${N} --sample_with_n_markers ${S} --print_clades_only --output_dir . > strainphlan4_clades_${N}.txt
