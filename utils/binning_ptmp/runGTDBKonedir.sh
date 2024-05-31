#!/bin/bash
#SBATCH --job-name=jB_gtdbk
#SBATCH --error=__gtdbtk.err
#SBATCH --output=__gtdbtk.out
#SBATCH --mem=64gb
#SBATCH --time=0-02:29:00
#SBATCH --cpus-per-task=8
#SBATCH --open-mode=truncate

# ==========================
# GTDBK RUNNER
# ==========================
echo "> STARTING"
# --- LOAD MODULES --- 
echo " >> loading modules"
module load Miniconda3/4.8.3
# --- LOAD CONDA ENV ---
CONDA=/scratch/hb-tifn/condas/conda_GTDB_TK/
echo " >> loading conda ${CONDA}"
source activate $CONDA
# load DB
export GTDBTK_DATA_PATH=/scratch/hb-tifn/DBs/DB_GTDB/release207_v2
# --- parse sample name from folder name ---
SNAME=${PWD##*/}
# --- setup ---
CPUS=8
# --- run it ---
echo " >> running GTDBK"
echo "gtdbtk classify_wf --genome_dir ${1} --out_dir ${2} --extension .fa --cpus ${CPUS}"
gtdbtk classify_wf --genome_dir ${1} --out_dir ${2} --extension .fa --cpus ${CPUS}
echo "> DONE"
