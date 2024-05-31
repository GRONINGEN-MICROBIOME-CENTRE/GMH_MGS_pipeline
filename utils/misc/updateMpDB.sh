#!/bin/bash
#SBATCH --mem=32gb
#SBATCH --time=0-05:59:00
#SBATCH --cpus-per-task=8
#SBATCH --open-mode=truncate
#SBATCH --job-name=MPdb
#SBATCH --error=__MP_update.err
#SBATCH --output=__MP_update.out

# purge modules
module purge
# load conda
ml Miniconda3

source activate /data/umcg-tifn/rgacesa/conda_biobakery4
metaphlan --install --force_download
