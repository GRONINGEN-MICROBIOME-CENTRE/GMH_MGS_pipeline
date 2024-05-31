#!/bin/bash
#SBATCH --job-name=jB_VAMB
#SBATCH --error=JOB_OUT/__binning_VAMB.err
#SBATCH --output=JOB_OUT/__binning_VAMB.out
#SBATCH --mem=8gb
#SBATCH --time=0-03:00:00
#SBATCH --cpus-per-task=4
#SBATCH --open-mode=truncate

# ==========================
# VAMB RUNNER [uses tmp]
# ==========================
echo " > RUNNING VAMB <"
# --- LOAD MODULES --- 
echo " > loading conda"
module load Miniconda3/4.8.3
# --- LOAD CONDA ENV ---
CONDA=/data/umcg-tifn/rgacesa/conda_vamb/ 
echo "source activate $CONDA"
source activate $CONDA
# --- parse sample name from folder name ---
SNAME=${PWD##*/}
# --- setup ---
CONTIGS=assembly_megahit/${SNAME}_megahit_contigs.fa
OUT=bins_vamb
OUT_TMP=${TMPDIR}/${SNAME}/bins_vamb
OUT_TMP_V=${TMPDIR}/${SNAME}
BAM=assembly_coverage_minimap2/*.bam
CLEANER=/data/umcg-tifn/rgacesa/dag3_pipeline_3c/utils/binning_ptmp/fastaShortenHdrs.py

# prep folder
echo "rm -r ${OUT}"
rm -r ${OUT}
echo "rm -r ${OUT_TMP_V}"
rm -r ${OUT_TMP_V}
echo "mkdir -p ${OUT}"
mkdir -p ${OUT}
#echo "mkdir -p ${OUT_TMP_V}"
#mkdir -p ${OUT_TMP_V}
# run kmer generator script
echo "vamb --outdir ${OUT_TMP_V} --fasta ${CONTIGS} --bamfiles ${BAM} --minfasta 100000"
vamb --outdir ${OUT_TMP_V} --fasta ${CONTIGS} --bamfiles ${BAM} --minfasta 100000
# rename for checkM compatibility
for i in ${OUT_TMP_V}/bins/*.fna; do mv ${i} ${i/\.fna/\.fa}; done
# collect and sort results
echo "cp ${OUT_TMP_V}/bins/* ${OUT}"
cp ${OUT_TMP_V}/bins/* ${OUT}
echo "rm -r ${OUT_TMP}"
rm -r ${OUT_TMP_V}
echo " > VAMB DONE <"
# rename bins
CNT=0
cd ${OUT}
for fa in *.fa
do
  CNT=$((CNT+1))
  mv $fa tmp.bin.${CNT}.fa
  python ${CLEANER} --input tmp.bin.${CNT}.fa --output bin.${CNT}.fa
  rm tmp.bin.${CNT}.fa
done
cd ..
