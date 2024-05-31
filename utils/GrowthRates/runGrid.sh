#!/bin/bash
#SBATCH --job-name=tGRID
#SBATCH --error=__grid.err
#SBATCH --output=__grid.out
#SBATCH --mem=16gb
#SBATCH --time=15:59:00
#SBATCH --cpus-per-task=8
#SBATCH --open-mode=truncate

# =======================================================
# GRID Growth Rates Calculator RUNNER
# - runs GRID job for one microbiome sample
# =======================================================
# NOTE that when samples are fastq files, they must be in single-end format
CONDA=/data/umcg-tifn/rgacesa/conda_GRID/
# settings
DTYPE=fastq # type of file(s)
COV_MIN=0.2 # min coverage
THREADS=8
DB=/data/umcg-tifn/rgacesa/DB_GRID/Stool # database
# load conda
module load Anaconda3
source activate ${CONDA}
# --- parse sample name from folder name ---
SNAME=${PWD##*/}
OUT_TMP=${TMPDIR}/${SNAME}/grid
IN_TMP=${TMPDIR}/${SNAME}/grid_input
OUT=GRiD
# prep TMP folders
mkdir -p ${OUT_TMP}
mkdir -p ${IN_TMP}
# copy reads to TMP and merge them
cat clean_reads/*_kneaddata_cleaned_pair_[12].fastq > ${IN_TMP}/${SNAME}.fastq
# prep command
RUN="grid multiplex -r ${IN_TMP} -d ${DB} -e ${DTYPE} -c ${COV_MIN} -n ${THREADS} -o ${OUT_TMP}"
# run it
echo ${RUN}
${RUN}
# collect data
mkdir -p ${OUT}
cp  ${OUT_TMP}/*.GRiD.* ${OUT}
