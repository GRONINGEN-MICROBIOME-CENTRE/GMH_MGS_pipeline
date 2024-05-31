#!/bin/bash
#SBATCH --job-name=jB_mw_q
#SBATCH --error=JOB_OUT/__metawrap_quantify_binab.err
#SBATCH --output=JOB_OUT/__metawrap_quantify_binab.out
#SBATCH --mem=12gb
#SBATCH --time=0-00:29:00
#SBATCH --cpus-per-task=6
#SBATCH --open-mode=truncate

# =====================================
# METAWRAP BIN REL.AB QUANTIFICATION
# =====================================

# --- LOAD MODULES --- 
module load Miniconda3/4.8.3
# --- LOAD CONDA ENV ---
CONDA=/data/umcg-tifn/metaGEM/envs/metawrap
source activate $CONDA
# --- parse sample name from folder name ---
SNAME=${PWD##*/}
# --- setup ---
#  > which BINS to quantify?
BINS_IN=bins_DAS
# ---
OUT_TMP=${TMPDIR}/${SNAME}/bins_quantified
BINS_IN_CLN=${OUT_TMP}/bins_quantification_input_q
OUT=bins_quantified
FQ1=clean_reads_fixed/${SNAME}_kneaddata_cleaned_repaired_1.fastq
FQ2=clean_reads_fixed/${SNAME}_kneaddata_cleaned_repaired_2.fastq

#ASSEMBLY=assembly_megahit/${SNAME}_megahit_contigs.fa
#ASSEMBLY_I_F=assembly_megahit_clean
#ASSEMBLY_I_FN=${ASSEMBLY_I_F}/${SNAME}_megahit_contigs.fa
#ASSEMBLY_CLEANER=/data/umcg-tifn/rgacesa/dag3_pipeline_3c/utils/binning/prepCleanContigs.py
# prep folder
mkdir -p ${OUT_TMP}
mkdir -p ${BINS_IN_CLN}
# move bins to temporary foldr
cp ${BINS_IN}/*.fa ${BINS_IN_CLN} 

# prep "clean" assembly contig names [not used]
#rm -r ${ASSEMBLY_I_F}
#mkdir -p ${ASSEMBLY_I_F}
#echo "python ${ASSEMBLY_CLEANER} --contigs ${ASSEMBLY} --output ${ASSEMBLY_I_FN} --minlt 0"
#python ${ASSEMBLY_CLEANER} --contigs ${ASSEMBLY} --output ${ASSEMBLY_I_FN} --minlt 0

# run it [using node tmp]
echo "metawrap quant_bins -t 6 -b ${BINS_IN_CLN} -o ${OUT_TMP} ${FQ1} ${FQ2}"
metawrap quant_bins -t 6 -b ${BINS_IN_CLN} -o ${OUT_TMP} ${FQ1} ${FQ2}
# collect data
mkdir -p ${OUT}
mv ${OUT_TMP}/bin_abundance_table.tab ${OUT}/${BINS_IN}_quantified_ab_table.tab
rm -r ${OUT_TMP}
rm -r ${BINS_IN_CLN}
