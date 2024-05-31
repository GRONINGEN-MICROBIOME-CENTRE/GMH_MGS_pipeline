#!/bin/bash
#SBATCH --job-name=jB_mw_ra
#SBATCH --error=JOB_OUT/__metawrap_reassembly.err
#SBATCH --output=JOB_OUT/__metawrap_reassembly.out
#SBATCH --mem=40gb
#SBATCH --time=0-23:59:00
#SBATCH --cpus-per-task=12
#SBATCH --open-mode=truncate

# ==========================
# METAWRAP BIN RE-ASSEMBLY
# ==========================
echo " > running METAWRAP reassembly!"
# --- LOAD MODULES --- 
module load Miniconda3/4.8.3
# --- LOAD CONDA ENV ---
CONDA=/data/umcg-tifn/metaGEM/envs/metawrap
source activate $CONDA
# --- update spades version ---
ml SPAdes/3.15.3-GCC-11.2.0
# --- parse sample name from folder name ---
SNAME=${PWD##*/}
# --- setup ---
# > which BINS to reassemble?
BINS_IN=bins_DAS
# ---
COMPLETENESS=50
CONTAMINATION=10
MIN_CONTIG_LT=500
READS=clean_reads_fixed
#BINS_IN_CLN=bins_reassembly_input
BINS_IN_CLN=${TMPDIR}/bins_reassembly_input
OUT_TMP=${TMPDIR}/${SNAME}/bins_reassembly
OUT=bins_reassembled
FQ1=clean_reads_fixed/${SNAME}_kneaddata_cleaned_repaired_1.fastq
FQ2=clean_reads_fixed/${SNAME}_kneaddata_cleaned_repaired_2.fastq
# parser
CMPARSER=/data/umcg-tifn/rgacesa/dag3_pipeline_3c/utils/binning/parseCheckM.py
# prep folder
echo " >> preppign folders & cleaning"
echo "rm -r ${OUT}"
rm -r ${OUT}
echo "mkdir -p ${OUT}"
mkdir -p ${OUT}
echo "mkdir -p ${OUT_TMP}"
mkdir -p ${OUT_TMP}
echo "rm -r ${BINS_IN_CLN}"
rm -r ${BINS_IN_CLN}
echo "mkdir -p ${BINS_IN_CLN}"
mkdir -p ${BINS_IN_CLN}
# move stuff around to prevent weird bugs
echo " >> prepping data"
echo "cp ${BINS_IN}/*.fa ${BINS_IN_CLN}"
cp ${BINS_IN}/*.fa ${BINS_IN_CLN}

# run it [using node tmp]
metaWRAP reassemble_bins -b ${BINS_IN_CLN} -1 ${FQ1} -2 ${FQ2} -l $MIN_CONTIG_LT --strict-cut-off 2 --permissive-cut-off 5 -o ${OUT_TMP} -t 12 -c $COMPLETENESS -x $CONTAMINATION 2>&1 | tee JOB_OUT/__reassembly.log
echo "metaWRAP reassemble_bins -b ${BINS_IN_CLN} -1 ${FQ1} -2 ${FQ2} -l $MIN_CONTIG_LT --strict-cut-off 2 --permissive-cut-off 5 -o ${OUT_TMP} -t 12 -c $COMPLETENESS -x $CONTAMINATION 2>&1 | tee JOB_OUT/__reassembly.log"

echo " >> collecting data"
# {OUT_TMP}/reassembled_bins <- final bins
cp "${OUT_TMP}/reassembled_bins/* ${OUT}"
cp ${OUT_TMP}/reassembled_bins/* ${OUT}

# parse results
echo " >> parsing checkM"
# {OUT_TMP}/reassembled_bins.checkm/storage/bin_stats_ext.tsv <-- checkM results
echo "python ${CMPARSER} --input ${OUT_TMP}/reassembled_bins.checkm/storage/bin_stats_ext.tsv --output ${OUT}/reassembled_bins_checkM_results_parsed.csv --completeness ${COMPLETENESS} --contamination ${CONTAMINATION}"
python ${CMPARSER} --input ${OUT_TMP}/reassembled_bins.checkm/storage/bin_stats_ext.tsv --output ${OUT}/reassembled_bins_checkM_results_parsed.csv --completeness ${COMPLETENESS} --contamination ${CONTAMINATION}
cp ${OUT}/reassembled_bins_checkM_results_parsed.csv checkM_all
# cleanup
rm -r ${OUT_TMP}
echo " > DONE ! <"
