#!/bin/bash
#SBATCH --job-name=jB_mw_ref
#SBATCH --error=JOB_OUT/__metawrap_bin_refine.err
#SBATCH --output=JOB_OUT/__metawrap_bin_refine.out
#SBATCH --mem=40gb
#SBATCH --time=0-06:29:00
#SBATCH --cpus-per-task=8
#SBATCH --open-mode=truncate

# ==========================
# METAWRAP BINNERS REFINING
# ==========================

# --- LOAD MODULES --- 
module load Miniconda3/4.8.3
# --- LOAD CONDA ENV ---
CONDA=/data/umcg-tifn/metaGEM/envs/metawrap
source activate $CONDA
# --- parse sample name from folder name ---
SNAME=${PWD##*/}
# --- setup ---
IN_TMP=${TMPDIR}/${SNAME}
OUT_TMP=${TMPDIR}/${SNAME}/bins_metawrap_refined
OUT=bins_metawrap_refined
COMPLETENESS=50
CONTAMINATION=10
# prep TMP folders
mkdir -p ${IN_TMP}
mkdir -p ${OUT_TMP}
mkdir -p ${IN_TMP}/bins_maxbin2
mkdir -p ${IN_TMP}/bins_metabat2
mkdir -p ${IN_TMP}/bins_concoct
# copy data to TMP
cp -r ./bins_maxbin2/*.fa ${IN_TMP}/bins_maxbin2
cp -r ./bins_metabat2/*.fa ${IN_TMP}/bins_metabat2
cp -r ./bins_concoct/*.fa ${IN_TMP}/bins_concoct
# run it [using node tmp]
metawrap bin_refinement -t 8 -m 40 --quick -c $COMPLETENESS -x $CONTAMINATION -o ${OUT_TMP} -A ${IN_TMP}/bins_maxbin2 -B ${IN_TMP}/bins_metabat2 -C ${IN_TMP}/bins_concoct
# collect data
mkdir -p ${OUT}
rm -r ${OUT_TMP}/bins_maxbin2/
rm -r ${OUT_TMP}/bins_metabat2/
rm -r ${OUT_TMP}/bins_concoct/
rm -r ${OUT_TMP}/work_files/
rm ${OUT_TMP}/*
cp -r ${OUT_TMP}/metawrap_${COMPLETENESS}_${CONTAMINATION}_bins/*.fa ${OUT}/
# cleanup
rm -r ${IN_TMP}
rm -r ${OUT_TMP}
