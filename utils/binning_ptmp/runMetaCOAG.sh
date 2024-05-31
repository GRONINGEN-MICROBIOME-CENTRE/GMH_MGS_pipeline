#!/bin/bash
#SBATCH --job-name=jB_mCOAG
#SBATCH --error=JOB_OUT/__binning_MetaCOAG.err
#SBATCH --output=JOB_OUT/__binning_MetaCOAG.out
#SBATCH --mem=8gb
#SBATCH --time=0-00:29:00
#SBATCH --cpus-per-task=2
#SBATCH --open-mode=truncate

# =======================================
# METACOAG Binner RUNNER [uses node tmp]
# =======================================

# --- LOAD MODULES --- 
module load Miniconda3/4.8.3
# --- LOAD CONDA ENV ---
CONDA=/data/umcg-tifn/rgacesa/conda_metacoag 
source activate $CONDA
# --- parse sample name from folder name ---
SNAME=${PWD##*/}
# --- setup ---
COV_F=assembly_coverage_metabinner
ASSEMBLER=megahit
CONTIGS=assembly_megahit/${SNAME}_megahit_contigs.fa
GRAPH=assembly_megahit/${SNAME}_megahit_contigs_graph.gfa
COV_PROFILE=${COV_F}/coverage_profile_f1k.tsv
OUT=bins_metaCOAG
OUT_TMP=${TMPDIR}/${SNAME}/bins_metaCOAG
# tmp folder for contigs
CONTIGS_TMPD=${OUT_TMP}/assembly_megahit_tmp/
# tmp name for contigs
CONTIGS_TMPF=${SNAME}_megahit_contigs.fa
ABUNDANCE=assembly_coverage_coverm/abundance.tsv
# prep folder
mkdir -p ${OUT}
mkdir -p ${OUT_TMP}
# prep tmp (metacoag generates gunk in assembly folder)
echo "mkdir -p ${CONTIGS_TMPD}"
mkdir -p ${CONTIGS_TMPD}
#  > copy assembly there
echo cp "${CONTIGS} ${CONTIGS_TMPD}/${CONTIGS_TMPF}"
cp ${CONTIGS} ${CONTIGS_TMPD}/${CONTIGS_TMPF}
# run it
echo "metacoag --graph ${GRAPH} --contigs ${CONTIGS_TMPD}/${CONTIGS_TMPF} --abundance ${ABUNDANCE} --assembler ${ASSEMBLER} --output ${OUT_TMP} --min_length 1000"
metacoag --graph ${GRAPH} --contigs ${CONTIGS_TMPD}/${CONTIGS_TMPF} --abundance ${ABUNDANCE} --assembler ${ASSEMBLER} --output ${OUT_TMP} --min_length 1000
# rename bins
for i in ${OUT_TMP}/bins/*.fasta
do 
   mv ${i} ${i/fasta/fa}
done
# collect data
cp ${OUT_TMP}/bins/* ${OUT}
rm -r ${OUT_TMP}
# rename bins part II
CNT=0
cd ${OUT}
for fa in *.fa
do
  CNT=$((CNT+1))
  mv $fa bin.${CNT}.fa
done
cd ..
