#!/bin/bash
#SBATCH --job-name=jB_mwrap
#SBATCH --error=JOB_OUT/__metawrap_binning.err
#SBATCH --output=JOB_OUT/__metawrap_binning.out
#SBATCH --mem=64gb
#SBATCH --time=2-3:59:00
#SBATCH --cpus-per-task=12
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
CONTIGS=assembly_megahit/final.contigs.fa
#READS=clean_reads_fixed
OUT_TMP=bins_metawrap_tmp
#OUT=bins_metawrap
CONTIG_LT=1000
# prep folder
mkdir -p ${OUT_TMP}
# run it [using node tmp]
metawrap binning -m 64 -t 12 -a $CONTIGS -o ${OUT_TMP} --metabat2 --maxbin2 --concoct -l $CONTIG_LT $1 $2 
# collect data
cp -r ${OUT_TMP}/concoct_bins/ ./bins_concoct/
cp -r ${OUT_TMP}/maxbin2_bins/ ./bins_maxbin2/
cp -r ${OUT_TMP}/metabat2_bins/ ./bins_metabat2/
# collect tmp
#rm -r ${OUT_TMP}
# clean gunk
#rm bins_metabat2/bin.unbinned.fa
#rm bins_concoct/unbinned.fa
