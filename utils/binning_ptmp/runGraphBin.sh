#!/bin/bash
#SBATCH --job-name=jB_GBin
#SBATCH --error=JOB_OUT/__binning_GraphBin.err
#SBATCH --output=JOB_OUT/__binning_GraphBin.out
#SBATCH --mem=4gb
#SBATCH --time=0-00:29:00
#SBATCH --cpus-per-task=1
#SBATCH --open-mode=truncate

# =======================================
# GraphBIN Binner RUNNER [uses node tmp]
# =======================================

# === PREP BINS FROM MAXBIN2 ===
# --- LOAD MODULES ---
module load Miniconda3/4.8.3
# --- LOAD CONDA ENV ---
SCRIPT=/data/umcg-tifn/rgacesa/dag3_pipeline_3c/utils/binning_ptmp/prepbins_for_graphbin.py
CONDA=/data/umcg-tifn/rgacesa/conda_graphbin
PY=/data/umcg-tifn/rgacesa/conda_graphbin/bin/python
source activate $CONDA
# --- parse sample name from folder name ---
SNAME=${PWD##*/}
# --- setup ---
START_BINS=${PWD}/bins_semibin/
CLEANER=/data/umcg-tifn/rgacesa/dag3_pipeline_3c/utils/binning_ptmp/fastaShortenHdrs.py


# === RUN GRAPHBIN ===
# --- setup ---
ASSEMBLER=megahit
CONTIGS=${PWD}/assembly_megahit/${SNAME}_megahit_contigs.fa
GRAPH=${PWD}/assembly_megahit/${SNAME}_megahit_contigs_graph.gfa
OUT=${PWD}/bins_graphBin
OUT_TMP=${TMPDIR}/${SNAME}/bins_graphBin
OUT_BINCSV=${OUT_TMP}/graphbin_prep/
ABUNDANCE=${PWD}/assembly_coverage_coverm/abundance.tsv
# prep folders
mkdir -p ${OUT}
mkdir -p ${OUT_TMP}
mkdir -p ${OUT_BINCSV}
# prep bins for GRAPHBIN
echo "$PY ${SCRIPT} --binned ${START_BINS} --output ${OUT_BINCSV}"
$PY ${SCRIPT} --binned ${START_BINS} --output ${OUT_BINCSV}
# run GRAPHBIN
echo "graphbin --assembler megahit --graph $GRAPH --contigs $CONTIGS --binned ${OUT_BINCSV}/initial_contig_bins.csv --output ${OUT_TMP}"
graphbin --assembler megahit --graph $GRAPH --contigs $CONTIGS --binned ${OUT_BINCSV}/initial_contig_bins.csv --output ${OUT_TMP}
# rename bins
echo "  >>  renaming bins in ${OUT_TMP}/bins/ [fasta -> fa]"
for i in ${OUT_TMP}/bins/*.fasta
do 
   mv ${i} ${i/fasta/fa}
done
# collect data
echo " >> collecting data: cp ${OUT_TMP}/bins/* ${OUT}"
cp ${OUT_TMP}/bins/* ${OUT}
rm -r ${OUT_BINCSV}
rm -r ${OUT_TMP}
# clean and rename bins
echo " >> cleaning and renaming bins"
CNT=0
cd ${OUT}
rm *.txt
for fa in *.fa
do
  CNT=$((CNT+1))
  mv ${fa} tmp.bin.${CNT}.fa
  python ${CLEANER} --input tmp.bin.${CNT}.fa --output bin.${CNT}.fa
  rm tmp.bin.${CNT}.fa
done
cd ..
echo " > GRAPHBIN done!! "
