#!/bin/bash
#SBATCH --job-name=jB_mw2_ref
#SBATCH --error=JOB_OUT/__metawrap_bin_refine2.err
#SBATCH --output=JOB_OUT/__metawrap_bin_refine2.out
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
OUT=bins_metawrap_refined_v2
COMPLETENESS=50
CONTAMINATION=10
# prep TMP folders
mkdir -p ${IN_TMP}
mkdir -p ${OUT_TMP}
mkdir -p ${IN_TMP}/bins_A
mkdir -p ${IN_TMP}/bins_B
mkdir -p ${IN_TMP}/bins_C
# copy data to TMP
# first set of bins is always concoct
BA=./bins_concoct
# select binner for 2nd set of bins (BB)
BDIR=./bins_semibin
BB=./bins_metabat2
if [ -d ${BDIR} ]
then
   NFA=$(ls -l ${BDIR}/*.fa | grep ^- | wc -l)
   if [ "${NFA}" -gt "1" ]; then
      BB=${BDIR}
   fi
fi
#  > select binner for 3rd set of bins (BC)
BDIR=./bins_metaCOAG
BC=./bins_maxbin2
if [ -d ${BDIR} ]
then
   NFA=$(ls -l ${BDIR}/*.fa | grep ^- | wc -l)
   if [ "${NFA}" -gt "1" ]; then
      BC=${BDIR}
   fi
fi
echo " > refining following datasets:"
echo "  >> A:'${BA}"
echo "  >> B:'${BB}"
echo "  >> C:'${BC}"

cp -r ${BA}/*.fa ${IN_TMP}/bins_A 
cp -r ${BB}/*.fa ${IN_TMP}/bins_B
cp -r ${BC}/*.fa ${IN_TMP}/bins_C
# run it [using node tmp]
echo "metawrap bin_refinement -t 8 -m 40 --quick -c ${COMPLETENESS} -x ${CONTAMINATION} -o ${OUT_TMP} -A ${IN_TMP}/bins_A -B ${IN_TMP}/bins_B -C ${IN_TMP}/bins_C"
metawrap bin_refinement -t 8 -m 40 --quick -c $COMPLETENESS -x $CONTAMINATION -o ${OUT_TMP} -A ${IN_TMP}/bins_A -B ${IN_TMP}/bins_B -C ${IN_TMP}/bins_C
# collect data
mkdir -p ${OUT}
rm -r ${OUT_TMP}/A/
rm -r ${OUT_TMP}/B/
rm -r ${OUT_TMP}/C/
rm -r ${OUT_TMP}/work_files/
rm ${OUT_TMP}/*
cp -r ${OUT_TMP}/metawrap_${COMPLETENESS}_${CONTAMINATION}_bins/*.fa ${OUT}/
# cleanup
rm -r ${IN_TMP}
rm -r ${OUT_TMP}
