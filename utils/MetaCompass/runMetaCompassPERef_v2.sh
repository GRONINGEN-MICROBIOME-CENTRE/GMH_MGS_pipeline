#!/bin/bash
#SBATCH --job-name=MComp
#SBATCH --error=__metacompass_test.err
#SBATCH --output=__metacompass_test.out
#SBATCH --mem=36gb
#SBATCH --time=11:59:00
#SBATCH --cpus-per-task=8
#SBATCH --open-mode=truncate

# METACOMPASS RUNNER FOR SAMPLE ID
# > paired end reads
# > reference genomes

# ==== JOB INIT (i) ====
echo "========================================== "
echo "> STARTING METACOMPASS"
echo "========================================== "
# set python paths (otherwise pipeline does weird stuff)
PY=/data/umcg-tifn/rgacesa/conda_metacompass/bin/python
PYTHONPATH=${PY}
METACOMPASS=/data/umcg-tifn/rgacesa/MetaCompass/go_metacompass2.py

# PARSE CL PARAMS AND INIT VARS
SID=${1/\/}
OUT=${SID}/assembly_metacompass
IN1=${SID}_1.fastq.gz
IN2=${SID}_2.fastq.gz
REF=${2}
#echo ${SID}
#echo ${OUT}
#exit

# PURGING ENVIRUMENT
echo "> purging environment "
module purge
echo "> loading modules "
# --- LOAD MODULES ---
module load Miniconda3/4.7.10
# --- CLEAN CONDA  ---
echo "> cleaning conda env. "
source deactivate
# --- LOAD CONDA ---
echo "> loading conda env. "
source activate /data/umcg-tifn/rgacesa/conda_metacompass
# --- MAKE FOLDERS ----
rm -r ${OUT}
${PY} ${METACOMPASS} -r ${REF} -1 ${IN1} -2 ${IN2} -o ${OUT} -m 35 -t 8 --minctglen 500
