#!/bin/bash
#SBATCH --job-name=jB_rosella
#SBATCH --error=JOB_OUT/__binning_rosella.err
#SBATCH --output=JOB_OUT/__binning_rosella.out
#SBATCH --mem=8gb
#SBATCH --time=0-00:29:00
#SBATCH --cpus-per-task=4
#SBATCH --open-mode=truncate

# ==========================
# ROSELLA RUNNER [tmp user]
# ==========================
#details: https://github.com/rhysnewell/rosella

# --- LOAD MODULES --- 
module load Miniconda3/4.8.3
# --- LOAD CONDA ENV ---
CONDA=/data/umcg-tifn/rgacesa/conda_rosella
source activate $CONDA
# --- parse sample name from folder name ---
SNAME=${PWD##*/}
# --- setup ---
CONTIGS=assembly_megahit/${SNAME}_megahit_contigs.fa
OUT=bins_rosella
OUT_TMP=${TMPDIR}/${SNAME}/bins_rosella
NR_THREADS=4
CONTIG_LT=1000
COV=assembly_coverage_coverm/abundance.tsv
FQ1=clean_reads_fixed/${SNAME}_kneaddata_cleaned_repaired_1.fastq
FQ2=clean_reads_fixed/${SNAME}_kneaddata_cleaned_repaired_2.fastq
#BAM=assembly_coverage_metabinner/${SNAME}_kneaddata_cleaned_repaired.bam
# prep folders
echo "mkdir -p ${OUT}"
mkdir -p ${OUT}
echo "mkdir -p ${OUT_TMP}"
mkdir -p ${OUT_TMP}
# run binner
#rosella bin -r ${CONTIGS} --coverage-values ${COV} -o ${OUT} -t ${NR_THREADS}
#rosella recover -r ${CONTIGS} --coverage-values ${COV} --output-directory ${OUT} --threads ${NR_THREADS}

rosella recover --coupled ${FQ1} ${FQ2} --reference ${CONTIGS} --threads 4 --output-directory ${OUT}

# collect data
#echo "cp ${OUT_TMP}/output_recluster_bins/* ${OUT}/"
#cp ${OUT_TMP}/output_recluster_bins/* ${OUT}/
#echo "rm -r ${OUT_TMP}"
#rm -r ${OUT_TMP}
# clean & rename bins
#echo " > renaming bins "
#cd ${OUT}
#CNT=0
#for fa in *.fa
#do
#  CNT=$((CNT+1))
#  mv $fa bin.${CNT}.fa
#done
#cd ..
