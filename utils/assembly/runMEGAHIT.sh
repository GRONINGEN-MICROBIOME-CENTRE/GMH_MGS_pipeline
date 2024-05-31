#!/bin/bash
#SBATCH --job-name=jA_MH
#SBATCH --error=JOB_OUT/__assembly_megahit.err
#SBATCH --output=JOB_OUT/__assembly_megahit.out
#SBATCH --mem=500gb
#SBATCH --time=0-23:59:00
#SBATCH --cpus-per-task=16
#SBATCH --open-mode=truncate

# ==========================
# MEGAHIT RUNNER [uses tmp]
# ==========================
echo " > RUNNING MEGAHIT <"
# --- LOAD MODULES --- 
echo " > loading conda"
module load Miniconda3/4.8.3
# --- LOAD CONDA ENV ---
CONDA=/data/umcg-tifn/rgacesa/conda_dag3_assemblers
echo "source activate $CONDA"
source activate $CONDA
# --- parse sample name from folder name ---
SNAME=${PWD##*/}
# --- setup ---
NR_THREADS=16
IN1=${1}
IN2=${2}
OUT_F=assembly_megahit
MIN_CONTIG_LT=1000
# MAX MEM [current 400 GB]
MAX_MEM=495000000000
# prep folder
#echo "mkdir -p ${OUT_F}"
#mkdir -p ${OUT_F}
# run assembly
CMD="megahit -m ${MAX_MEM} --continue -1 ${1} -2 ${2} -o ${OUT_F} -t ${NR_THREADS} --min-contig-len ${MIN_CONTIG_LT}"
echo $CMD
$CMD
