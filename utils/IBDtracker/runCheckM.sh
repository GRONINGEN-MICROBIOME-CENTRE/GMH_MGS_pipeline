#!/bin/bash
#SBATCH --job-name=jB_checkM
#SBATCH --error=JOB_OUT/__checkM.err
#SBATCH --output=JOB_OUT/__checkM.out
#SBATCH --mem=40gb
#SBATCH --time=0-03:59:00
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

echo " > loading modules & conda"
# --- LOAD MODULES --- 
module load Miniconda3/4.8.3
# --- LOADING CONDA ENV for METAWRAP ---
CONDA=/data/umcg-tifn/metaGEM/envs/metawrap
source activate $CONDA
# --- parse sample name from folder name ---
SNAME=${PWD##*/}
# --- setup ---
IN=$1
OUT=$2
# prep folder
echo " > prepping folders"
mkdir -p ${OUT}
echo " > running checkM: input ${IN}, output: ${OUT}"
# run checkm
checkm lineage_wf -t 8 -f ${OUT}/${SNAME}_checkM_results_parsed.csv -x fa ${IN} ${OUT}/${SNAME} --tab_table --pplacer_threads 8
echo " >> DONE << " 
