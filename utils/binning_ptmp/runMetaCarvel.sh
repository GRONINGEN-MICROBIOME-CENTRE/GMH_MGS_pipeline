#!/bin/bash
#SBATCH --job-name=jB_MCarvel
#SBATCH --error=JOB_OUT/__metacarvel.err
#SBATCH --output=JOB_OUT/__metacarvel.out
#SBATCH --mem=32gb
#SBATCH --time=0-01:59:00
#SBATCH --cpus-per-task=2
#SBATCH --open-mode=truncate

# ==========================
# METACARVEL RUNNER
# ==========================

# --- LOAD MODULES --- 
module load Miniconda3/4.8.3
# --- LOAD CONDA ENV ---
CONDA=/data/umcg-tifn/rgacesa/conda_binnacle/
MY_PYTHON=${CONDA}/bin/python
source activate $CONDA
# --- parse sample name from folder name ---
SNAME=${PWD##*/}
# --- setup ---
CONTIGS=assembly_megahit/${SNAME}_megahit_contigs.fa
SCRIPT_METACARVEL=${CONDA}/MetaCarvel/run.py 
SCRIPT_FINDMOTIFS=${CONDA}/MetaCarvel/find_motifs.py
OUT=metacarvel_out
OUT_TMP=${TMPDIR}/${SNAME}/metacarvel_out
CONTIG_LT=1000
ENV=human_gut
BAM=assembly_coverage_metabinner/${SNAME}_kneaddata_cleaned_repaired.bam
# prep folder
echo "mkdir -p ${OUT_TMP}"
mkdir -p ${OUT_TMP}
# run metacarvel
echo "${MY_PYTHON} ${SCRIPT_METACARVEL} -a ${CONTIGS} -m ${BAM} -d ${OUT_TMP} -k TRUE -r TRUE"
${MY_PYTHON} ${SCRIPT_METACARVEL} -a ${CONTIGS} -m ${BAM} -d ${OUT_TMP} -k TRUE -r TRUE
echo "${MY_PYTHON} ${SCRIPT_FINDMOTIFS} -d ${OUT_TMP}"
${MY_PYTHON} ${SCRIPT_FINDMOTIFS} -d ${OUT_TMP}
# move data back
echo "mkdir -p ${OUT}"
mkdir -p ${OUT}
cp ${OUT_TMP}/* ${OUT}
# cleanup
echo "rm -r ${OUT_TMP}"
rm -r ${OUT_TMP}
