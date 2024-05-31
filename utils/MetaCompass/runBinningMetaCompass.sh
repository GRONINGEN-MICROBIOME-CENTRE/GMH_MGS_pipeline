#!/bin/bash
#SBATCH --job-name=jB_MCompass
#SBATCH --error=JOB_OUT/__metacompass_metawrap_binning.err
#SBATCH --output=JOB_OUT/__metacompass_metawrap_binning.out
#SBATCH --mem=64gb
#SBATCH --time=0-11:59:00
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
CONTIGS=assembly_metacompass/metacompass_assembly.fa
#READS=clean_reads_fixed
OUT_TMP=metacompass_bins_metawrap_tmp
#OUT=bins_metawrap
CONTIG_LT=1000
# prep folder
mkdir -p ${OUT_TMP}
# run it [using node tmp]
metawrap binning -m 64 -t 12 -a ${CONTIGS} -o ${OUT_TMP} --metabat2 --maxbin2 --concoct -l $CONTIG_LT $1 $2 
# collect data
cp -r ${OUT_TMP}/concoct_bins/ ./metacompass_bins_concoct/
cp -r ${OUT_TMP}/maxbin2_bins/ ./metacompass_bins_maxbin2/
cp -r ${OUT_TMP}/metabat2_bins/ ./metacompass_bins_metabat2/
