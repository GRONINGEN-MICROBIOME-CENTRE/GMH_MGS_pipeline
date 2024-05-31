#!/bin/bash
#SBATCH --job-name=jB_mbinner
#SBATCH --error=JOB_OUT/__binning_metabinner.err
#SBATCH --output=JOB_OUT/__binning_metabinner.out
#SBATCH --mem=4gb
#SBATCH --time=0-02:00:00
#SBATCH --cpus-per-task=8
#SBATCH --open-mode=truncate

# ==========================
# METABINNER RUNNER [uses node tmp]
# ==========================
echo "> STARTING METABINNER RUNNER"
echo " >> loading modules"
# --- LOAD MODULES --- 
module load Miniconda3/4.8.3
# --- LOAD CONDA ENV ---
echo " >> loading conda"
CONDA=/data/umcg-tifn/rgacesa/conda_metabinner 
echo "source activate ${CONDA}"
source activate $CONDA
# --- parse sample name from folder name ---
SNAME=${PWD##*/}
# --- setup ---
OUT_TMP=${TMPDIR}/${SNAME}/bins_metabinner
# --- metabinner sucks, so we need to copy everything to tmp for it ---
SCRIPT=${CONDA}/bin/run_metabinner.sh
METABINNER_PATH=${CONDA}/bin
echo " >> copying input files to node TMP"
COV_F=assembly_coverage_metabinner
CONTIGS=${PWD}/assembly_megahit/${SNAME}_megahit_contigs.fa
KMERS=${PWD}/assembly_coverage_metabinner/kmer_4_f1000.csv
COV_PROFILE=${PWD}/assembly_coverage_metabinner/coverage_profile_f1k.tsv
echo "mkdir -p ${OUT_TMP}"
mkdir -p ${OUT_TMP}
mkdir -p ${OUT_TMP}/input
cp ${COV_PROFILE} ${OUT_TMP}/input
cp ${KMERS} ${OUT_TMP}/input
cp ${CONTIGS} ${OUT_TMP}/input
# ======== copied, re-init input files ---
CONTIGS_T=${OUT_TMP}/input/${SNAME}_megahit_contigs.fa
KMERS_T=${OUT_TMP}/input/kmer_4_f1000.csv
COV_PROFILE_T=${OUT_TMP}/input/coverage_profile_f1k.tsv

OUT=bins_metabinner
COLLECTBINS=/data/umcg-tifn/rgacesa/dag3_pipeline_3c/utils/binning/metaBinnerCollectBins.py
# prep folder
echo " >> prepping folders"
echo "mkdir -p ${OUT}"
mkdir -p ${OUT}
# run MetaBinner
echo " >> running MetaBinner"
echo "bash ${SCRIPT} -a ${CONTIGS_T} -o ${OUT_TMP} -d ${COV_PROFILE_T} -k ${KMERS_T} -p ${METABINNER_PATH} -t 8"
bash ${SCRIPT} -a ${CONTIGS_T} -o ${OUT_TMP} -d ${COV_PROFILE_T} -k ${KMERS_T} -p ${METABINNER_PATH} -t 8
# convert to actual bin fasta files and collect
echo " >> collecting results"
echo "${CONDA}/bin/python ${COLLECTBINS} --contigs ${CONTIGS} --mbres ${OUT_TMP}/metabinner_res/metabinner_result.tsv --out ${OUT}"
${CONDA}/bin/python ${COLLECTBINS} --contigs ${CONTIGS} --mbres ${OUT_TMP}/metabinner_res/metabinner_result.tsv --out ${OUT}
# collect data
echo "cp ${OUT_TMP}/metabinner_res/metabinner_result.tsv ${OUT}/bins_metabinner.tsv"
cp ${OUT_TMP}/metabinner_res/metabinner_result.tsv ${OUT}/bins_metabinner.tsv
mkdir -p ${OUT}/logs/
echo "mv ${OUT_TMP}/metabinner_res/*.log ${OUT}/logs/"
mv ${OUT_TMP}/metabinner_res/*.log ${OUT}/logs/
# clean trash
rm -r ${OUT_TMP}
echo "> DONE <"
