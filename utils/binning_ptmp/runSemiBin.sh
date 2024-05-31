#!/bin/bash
#SBATCH --job-name=jB_semibin
#SBATCH --error=JOB_OUT/__binning_semibin.err
#SBATCH --output=JOB_OUT/__binning_semibin.out
#SBATCH --mem=8gb
#SBATCH --time=0-00:59:00
#SBATCH --cpus-per-task=4
#SBATCH --open-mode=truncate

# ==========================
# SEMIBIN RUNNER [tmp user]
# ==========================

# --- LOAD MODULES --- 
module load Miniconda3/4.8.3
# --- LOAD CONDA ENV ---
CONDA=/data/umcg-tifn/rgacesa/conda_semibin/ 
source activate $CONDA
# --- parse sample name from folder name ---
SNAME=${PWD##*/}
# --- setup ---
CONTIGS=assembly_megahit/${SNAME}_megahit_contigs.fa
OUT=bins_semibin
OUT_TMP=${TMPDIR}/${SNAME}/bins_semibin
CONTIG_LT=1000
ENV=human_gut
BAM=assembly_coverage_metabinner/${SNAME}_kneaddata_cleaned_repaired.bam
# prep folders
echo "mkdir -p ${OUT}"
mkdir -p ${OUT}
echo "mkdir -p ${OUT_TMP}"
mkdir -p ${OUT_TMP}
# run binner
echo "SemiBin single_easy_bin -i ${CONTIGS} -b ${BAM} -o ${OUT_TMP} --environment ${ENV} --threads 4"
SemiBin single_easy_bin -i ${CONTIGS} -b ${BAM} -o ${OUT_TMP} --environment ${ENV} --threads 4
# collect data
echo "cp ${OUT_TMP}/output_recluster_bins/* ${OUT}/"
cp ${OUT_TMP}/output_recluster_bins/* ${OUT}/
echo "rm -r ${OUT_TMP}"
rm -r ${OUT_TMP}
# clean & rename bins
echo " > renaming bins "
cd ${OUT}
CNT=0
for fa in *.fa
do
  CNT=$((CNT+1))
  mv $fa bin.${CNT}.fa
done
cd ..
# === run GRAPHBIN on top of it ===
FLD=/data/umcg-tifn/rgacesa/dag3_pipeline_3c/utils/binning_ptmp
sbatch ${FLD}/runGraphBin.sh
