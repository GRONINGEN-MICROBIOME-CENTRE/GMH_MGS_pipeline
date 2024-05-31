#!/bin/bash
#SBATCH --job-name=m_install
#SBATCH --error=__mp4_install.out
#SBATCH --output=__mp4_install.err
#SBATCH --mem=32gb
#SBATCH --time=3:59:00
#SBATCH --cpus-per-task=8
#SBATCH --open-mode=truncate
# PURGING ENVIRUMENT 
echo "> purging environment "
module purge 
echo "> loading modules "
# --- LOAD MODULES --- 
module load Miniconda3/4.7.10
# --- CLEAN CONDA  --- 
echo "> cleaning conda env. "
source deactivate
# --- LOAD CONDA --- 
echo "> loading conda env. "
source activate /data/umcg-tifn/rgacesa/conda_biobakery4
metaphlan --install
