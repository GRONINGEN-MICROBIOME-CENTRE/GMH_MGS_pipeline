#!/bin/bash

#SBATCH --mem=16gb
#SBATCH --time=0-00:30:00
#SBATCH --cpus-per-task=4
#SBATCH --open-mode=truncate
#SBATCH --job-name=SP3_profile
#SBATCH --error=__SP3_profile.err
#SBATCH --output=__SP3_profile.out

# NOTES:
# script profiles all clades in the dataset in given folder ($1)
# puts results in the current folder!

# PARAMS
N=50 #N = --marker_in_n_samples 80

# purge modules
module purge
# load conda
ml Anaconda3
# load conda env
source activate /scratch/hb-tifn/condas/conda_biobakery3.1
# run clade profiling
strainphlan -s ${1}/*.pkl --print_clades_only --output_dir .  > strainphlan3_clades_${N}.txt
