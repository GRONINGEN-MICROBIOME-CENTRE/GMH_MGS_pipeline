#!/bin/bash
#SBATCH --mem=24gb
#SBATCH --time=0-09:59:00
#SBATCH --cpus-per-task=8
#SBATCH --open-mode=truncate

# NOTES:
# > $1 is input folder
# > $2 is clade name

echo "Invoking runMarkerComparison.sh"
echo "CLs: ${1} ${2}"

# HELP / USE
if [[ $# -ne 2 ]]; 
    then 
    echo "ERROR: script requires two command line parameters:"
    echo " <input folder with pkl files> <clade name>"
    exit 2
fi

# PARAMS
# ===================
N=5 # --marker_in_n_samples [def 50]
S=15 # --sample_with_n_markers [def 20]
MODE=accurate # {accurate,fast}
CONDA=/scratch/hb-tifn/condas/conda_biobakery4
#CM= # clade markers
DB=/scratch/hb-tifn/condas/conda_biobakery4/lib/python3.10/site-packages/metaphlan/metaphlan_databases/mpa_vJan21_CHOCOPhlAnSGB_202103.pkl

# purge modules
module purge
# load conda
ml Anaconda3
# load conda env
source activate ${CONDA}

# prep results folder (where clade result goes)
mkdir ${2}
# run strainphlan for that clade
echo "strainphlan -s ${1}/*.pkl -d ${DB} --output_dir ./${2} --clade ${2} --marker_in_n_samples ${N} --sample_with_n_markers ${S} --nprocs 8 --phylophlan_mode ${MODE}"
strainphlan -s ${1}/*.pkl -d ${DB} --output_dir ./${2} --clade ${2} --marker_in_n_samples ${N} --sample_with_n_markers ${S} --nprocs 8 --phylophlan_mode ${MODE} #--tmp ${OUT_TMP}
