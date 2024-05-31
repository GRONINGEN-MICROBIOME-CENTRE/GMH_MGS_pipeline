#!/bin/bash
#SBATCH --job-name=tPPBuild
#SBATCH --error=__panphlan_extract.err
#SBATCH --output=__panphlan_extract.out
#SBATCH --mem=16gb
#SBATCH --time=01:59:00
#SBATCH --cpus-per-task=8
#SBATCH --open-mode=truncate

# =======================================================
# PANPHLAN PANGENOME EXPORTER RUNNINER
# - runs panphlan_exporter.py job for one folder
# > param 1: input folder (with fasta files)
# > param 2: output folder
# =======================================================
CONDA=/scratch/hb-tifn/condas/conda_biobakery3
CODEPY=/scratch/hb-tifn/condas/conda_biobakery3/PanPhlAn_pangenome_exporter/panphlan_exporter.py
DB=/scratch/hb-tifn/DBs/panphlan_genome_extractor_DB
IN=${1}
OUT=${2}
THREADS=8
# == load environment ==
module purge
module load Anaconda3
conda deactivate
source activate ${CONDA}
python ${CODEPY} -d ${DB} -i ${IN} -c ${OUT} -p ${OUT} -n ${THREADS} 
