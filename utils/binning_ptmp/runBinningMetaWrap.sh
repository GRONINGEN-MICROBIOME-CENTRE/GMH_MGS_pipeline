#!/bin/bash
#SBATCH --job-name=jB_mwrap
#SBATCH --error=JOB_OUT/__metawrap_binning.err
#SBATCH --output=JOB_OUT/__metawrap_binning.out
#SBATCH --mem=12gb
#SBATCH --time=0-04:29:00
#SBATCH --cpus-per-task=8
#SBATCH --open-mode=truncate

# ==========================
# METAWRAP BINNERS RUNNER
# ==========================

# --- LOAD MODULES --- 
module load Miniconda3/4.8.3
# --- LOAD CONDA ENV ---
CONDA=/data/umcg-tifn/metaGEM/envs/metawrap
source activate $CONDA
# --- parse sample name from folder name ---
SNAME=${PWD##*/}
# --- setup ---
CONTIGS=assembly_megahit/${SNAME}_megahit_contigs.fa
READS=clean_reads_fixed
OUT_TMP=${TMPDIR}/${SNAME}/bins_metawrap
#OUT=bins_metawrap
CONTIG_LT=1000
# prep folder
#mkdir -p ${OUT}
mkdir -p ${OUT_TMP}
# run it [using node tmp]
metawrap binning -m 12 -t 8 -a $CONTIGS -o ${OUT_TMP} --metabat2 --maxbin2 --concoct -l $CONTIG_LT ${READS}/*_1.fastq ${READS}/*_2.fastq 
# collect data
mv ${OUT_TMP}/concoct_bins/ ./bins_concoct/
mv ${OUT_TMP}/maxbin2_bins/ ./bins_maxbin2/
mv ${OUT_TMP}/metabat2_bins/ ./bins_metabat2/
# collect tmp
rm -r ${OUT_TMP}
# clean gunk
rm bins_metabat2/bin.unbinned.fa
rm bins_concoct/unbinned.fa
