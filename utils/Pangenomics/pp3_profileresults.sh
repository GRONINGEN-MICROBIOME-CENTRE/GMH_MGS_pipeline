#!/bin/bash

#SBATCH --mem=8gb
#SBATCH --time=0-00:29:59
#SBATCH --cpus-per-task=1
#SBATCH --open-mode=truncate
#SBATCH --job-name=PP3_pr
#SBATCH --error=__PP3_profile.err
#SBATCH --output=__PP3_profile.out

# NOTES:
# script profiles all clades in the dataset in given folder ($1)
# puts results in the current folder!

# PARAMS
# purge modules
module purge
# load conda
ml Miniconda3/4.8.3
# load conda env
CONDA=/data/umcg-tifn/rgacesa/conda_dag3_mp3
source activate ${CONDA} 
# run clade profiling
CLADE=$1 # e.g. Faecalibacterium_prausnitzii
PANGENOMES=/data/umcg-tifn/rgacesa/Panphlan/panphlan_DBs/

echo "panphlan_profiling.py -i ${CLADE} --o_matrix result_${CLADE}.tsv -p ${PANGENOMES}/${CLADE}/${CLADE}_pangenome.tsv"
panphlan_profiling.py -i ${CLADE} --o_matrix result_${CLADE}.tsv -p ${PANGENOMES}/${CLADE}/${CLADE}_pangenome.tsv --min_coverage 0.5 --o_covmat result_${CLADE}_coverage.tsv --left_max 1.5 --right_min 0.5
#--func_annot ${PANGENOMES}/${CLADE}/panphlan_${CLADE}_annot.tsv 
