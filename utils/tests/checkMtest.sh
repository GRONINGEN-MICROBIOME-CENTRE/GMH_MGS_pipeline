#!/bin/bash
#SBATCH --job-name=jB_checkM
#SBATCH --error=__checkM.err
#SBATCH --output=__checkM.out
#SBATCH --mem=40gb
#SBATCH --time=0-00:59:00
#SBATCH --cpus-per-task=8
#SBATCH --open-mode=truncate

# NOTES:
# > $1 = input folder with bins
# > $2 = output folder
echo "Invoking runCheckM.sh"
echo "CLs: ${1} ${2}"

# HELP / USE
if [[ $# -ne 2 ]];
    then
    echo "ERROR: script requires two command line parameters:"
    echo " <input folder with bins> <output folder>"
    exit 2
fi

# --- LOAD MODULES --- 
module load Miniconda3/4.8.3
# --- LOADING CONDA ENV for METAWRAP ---
#CONDA=/data/umcg-tifn/metaGEM/envs/metawrap 
CONDA=/scratch/hb-tifn/condas/conda_metawrap/
source activate $CONDA
# --- parse sample name from folder name ---
SNAME=${PWD##*/}
# --- setup ---
IN=$1
OUT=$2
# prep folder
mkdir -p ${OUT}
# run checkm
checkm lineage_wf -t 8 -x fasta ${IN} ${OUT} --tab_table --pplacer_threads 8
# parse results
#CMPARSER=/data/umcg-tifn/rgacesa/dag3_pipeline_3c/utils/binning/parseCheckM.py
#python ${CMPARSER} --input ${OUT}/storage/bin_stats_ext.tsv --output ${OUT}/checkM_results_parsed.csv --completeness 5 --contamination 50
