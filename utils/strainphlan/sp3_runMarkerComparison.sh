#!/bin/bash
#SBATCH --mem=32gb
#SBATCH --time=0-07:59:00
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
N=50 # --marker_in_n_samples
S=20 # --sample_with_n_markers 20
MODE=fast # {accurate,fast}
#CM= # clade markers

# purge modules
module purge
# load conda
ml Miniconda3/4.8.3
# load conda env
source activate /data/umcg-tifn/rgacesa/conda_dag3_v3

# prep results folder (where clade result goes)
mkdir ${2}
# run strainphlan for that clade
strainphlan -s ${1}/*.pkl --output_dir ./${2} --clade ${2} --marker_in_n_samples $N --sample_with_n_markers $S --nprocs 8 --phylophlan_mode $MODE 
