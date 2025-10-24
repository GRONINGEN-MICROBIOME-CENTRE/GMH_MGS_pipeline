#!/bin/bash
#SBATCH --mem=32gb
#SBATCH --time=0-03:59:00
#SBATCH --cpus-per-task=16

# PROCESS CLI
IN=${1}
CONDA_P=/scratch/hb-tifn/condas/2025_ARO
THREADS=16
#CLEANUP=Y

# STARTUP
echo "loading modules"
module load Miniconda3/22.11.1-1
echo "loading conda"
source activate ${CONDA_P}

# prep sample name
WD=${PWD}
FN=$(basename "${1}")
SN=${FN%%_*}

# work in node TMP:
NWD=${SN}

echo "${NWD}"
mkdir -p ${NWD}
cd ${NWD}
echo ${PWD}

# run part 1
CMD="args_oap stage_one -i ${IN} -o ${OUT} -f  -t ${THREADS}

args_oap stage_one -i input -o output -f fa -t 8
args_oap stage_two -i output -t 8

echo ${CMD}

# run part 2

# collect results
cp * ${WD}
cd ${WD}
