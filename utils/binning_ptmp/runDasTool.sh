#!/bin/bash
#SBATCH --job-name=jDAS
#SBATCH --error=JOB_OUT/__binning_DAS.err
#SBATCH --output=JOB_OUT/__binning_DAS.out
#SBATCH --mem=4gb
#SBATCH --time=0-00:19:59
#SBATCH --cpus-per-task=8
#SBATCH --open-mode=truncate

# ==========================
# DAS TOOL RUNNER
# ==========================

#NOTES:
# - metacoag requires conversion [/data/umcg-tifn/rgacesa/conda_dastool/DAS_Tool/src/Fasta_to_Contig2Bin.sh -e fa -i bins_metaCOAG/bins > bins_metaCOAG/bins_metaCOAG.tsv]
# - vamb requires conversion AND cleaning of headers
echo "> STARTING DASTOOL RUNNER"
# --- LOAD MODULES ---
module load Miniconda3/4.8.3
# --- LOAD CONDA ENV ---
CONDA=/data/umcg-tifn/rgacesa/conda_dastool
# --- PARAMS ---
SCORE=0.4
# --- setup ---
SNAME=${PWD##*/}
CONTIGS=assembly_megahit/${SNAME}_megahit_contigs.fa
CONTIGS_TO_BINS=/data/umcg-tifn/rgacesa/conda_dastool/DAS_Tool/src/Fasta_to_Contig2Bin.sh
CLEANER=/data/umcg-tifn/rgacesa/dag3_pipeline_3c/utils/binning_ptmp/fastaShortenHdrs.py
OUTDIR_TMP=${TMPDIR}/${SNAME}/bins_DAS_tmp
OUTDIR=bins_DAS
OUTPREF=das
#HDRFIX=/data/umcg-tifn/rgacesa/dag3_pipeline_3c/utils/binning/fixBinsTsvHdrs.py
# load DAStool conda
echo " >> loading conda env: ${CONDA}"
source activate $CONDA
# --- DAS INPUT, we build these from what is available ---"
DASIN=
DASLBLS=
# --- cleanup
rm -r ${OUTDIR}
echo " > PREPPING DASTOOL INPUT FILES"
# --- prep DAS tsv files ---
echo " >> prepping BIN-CONTIG files for DASTOOL"
#  >> 1) CONCOCT
echo "  >>> parsing CONCOCT"
NFA=0
BDIR=bins_concoct
if [ -d ${BDIR} ] 
then
   NFA=$(ls -l ${BDIR}/*.fa | grep ^- | wc -l)
   if [ "${NFA}" -gt "1" ]; then      
      echo "   >>> found ${NFA} bins"
      echo "${CONTIGS_TO_BINS} -e fa -i ${BDIR} > ${BDIR}/${BDIR}.tsv"
      ${CONTIGS_TO_BINS} -e fa -i ${BDIR} > ${BDIR}/${BDIR}.tsv
      DASIN=${DASIN}${BDIR}/${BDIR}.tsv,
      DASLBLS=${DASLBLS}concoct,
   fi
else
   echo "   >>> no bins found!"
fi
# === 2) metabat 2 ===
echo "  >>> parsing METABAT2"
BDIR=bins_metabat2
NFA=0
if [ -d ${BDIR} ] 
then
   NFA=$(ls -l ${BDIR}/*.fa | grep ^- | wc -l)
   if [ "${NFA}" -gt "1" ]; then      
      echo "   >>> found ${NFA} bins"
      echo "${CONTIGS_TO_BINS} -e fa -i ${BDIR} > ${BDIR}/${BDIR}.tsv"
      ${CONTIGS_TO_BINS} -e fa -i ${BDIR} > ${BDIR}/${BDIR}.tsv
      DASIN=${DASIN}${BDIR}/${BDIR}.tsv,
      DASLBLS=${DASLBLS}metabat2,
   fi
else
   echo "   >>> no bins found!"
fi
# === 3) maxbin2 ===
echo "  >>> parsing MAXBIN2"
BDIR=bins_maxbin2
NDA=0
if [ -d ${BDIR} ] 
then
   NFA=$(ls -l ${BDIR}/*.fa | grep ^- | wc -l)
   if [ "${NFA}" -gt "1" ]; then      
      echo "   >>> found ${NFA} bins"
      echo "${CONTIGS_TO_BINS} -e fa -i ${BDIR} > ${BDIR}/${BDIR}.tsv"
      ${CONTIGS_TO_BINS} -e fa -i ${BDIR} > ${BDIR}/${BDIR}.tsv
      DASIN=${DASIN}${BDIR}/${BDIR}.tsv,
      DASLBLS=${DASLBLS}maxbin2,
   fi
else
   echo "   >>> no bins found!"
fi
# === 4) VAMB ===
echo "  >>> parsing VAMB"
BDIR=bins_vamb
NFA=0
if [ -d ${BDIR} ] 
then
   NFA=$(ls -l ${BDIR}/*.fa | grep ^- | wc -l)
   if [ "${NFA}" -gt "1" ]; then      
      echo "   >>> found ${NFA} bins"
      echo "${CONTIGS_TO_BINS} -e fa -i ${BDIR} > ${BDIR}/${BDIR}.tsv"
      ${CONTIGS_TO_BINS} -e fa -i ${BDIR} > ${BDIR}/${BDIR}.tsv
      echo "     >>> fixing headers"
      #python $HDRFIX --in ${BDIR}/${BDIR}.tsv --out ${BDIR}/${BDIR}_dasrdy.tsv
      DASIN=${DASIN}${BDIR}/${BDIR}.tsv,
      DASLBLS=${DASLBLS}vamb,
   fi
else
   echo "   >>> no bins found!"
fi
# === 5) metaCOAG ===
echo "  >>> parsing metaCOAG"
BDIR=bins_metaCOAG
NFA=0
if [ -d ${BDIR} ] 
then
   NFA=$(ls -l ${BDIR}/*.fa | grep ^- | wc -l)
   if [ "${NFA}" -gt "1" ]; then      
      echo "   >>> found ${NFA} bins"
      echo "${CONTIGS_TO_BINS} -e fa -i ${BDIR} > ${BDIR}/${BDIR}.tsv"
      ${CONTIGS_TO_BINS} -e fa -i ${BDIR} > ${BDIR}/${BDIR}.tsv
      DASIN=${DASIN}${BDIR}/${BDIR}.tsv,
      DASLBLS=${DASLBLS}metaCOAG,
   fi
else
   echo "   >>> no bins found!"
fi
# === 6) semibin  ===
echo "  >>> parsing semibin"
BDIR=bins_semibin
NFA=0
if [ -d ${BDIR} ] 
then
   NFA=$(ls -l ${BDIR}/*.fa | grep ^- | wc -l)
   if [ "${NFA}" -gt "1" ]; then      
      echo "   >>> found ${NFA} bins"
      echo "${CONTIGS_TO_BINS} -e fa -i ${BDIR} > ${BDIR}/${BDIR}.tsv"
      ${CONTIGS_TO_BINS} -e fa -i ${BDIR} > ${BDIR}/${BDIR}.tsv
      DASIN=${DASIN}${BDIR}/${BDIR}.tsv,
      DASLBLS=${DASLBLS}semibin,
   fi
else
   echo "   >>> no bins found!"
fi
# === 7) graphbin  ===
echo "  >>> parsing graphbin"
BDIR=bins_graphBin
NFA=0
if [ -d ${BDIR} ] 
then
   NFA=$(ls -l ${BDIR}/*.fa | grep ^- | wc -l)
   if [ "${NFA}" -gt "1" ]; then      
      echo "   >>> found ${NFA} bins"
      echo "${CONTIGS_TO_BINS} -e fa -i ${BDIR} > ${BDIR}/${BDIR}.tsv"
      ${CONTIGS_TO_BINS} -e fa -i ${BDIR} > ${BDIR}/${BDIR}.tsv
      echo "     >>> fixing headers"
      #python $HDRFIX --in ${BDIR}/${BDIR}.tsv --out ${BDIR}/${BDIR}_dasrdy.tsv
      DASIN=${DASIN}${BDIR}/${BDIR}.tsv,
      DASLBLS=${DASLBLS}graphbin,
   fi
else
   echo "   >>> no bins found!"
fi
# === 8) metabinner  ===
echo "  >>> parsing metabinner"
BDIR=bins_metabinner
NFA=0
if [ -d ${BDIR} ] 
then
   NFA=$(ls -l ${BDIR}/*.fa | grep ^- | wc -l)
   if [ "${NFA}" -gt "1" ]; then      
      echo "   >>> found ${NFA} bins"
      echo "${CONTIGS_TO_BINS} -e fa -i ${BDIR} > ${BDIR}/${BDIR}.tsv"
      ${CONTIGS_TO_BINS} -e fa -i ${BDIR} > ${BDIR}/${BDIR}.tsv
      DASIN=${DASIN}${BDIR}/${BDIR}.tsv,
      DASLBLS=${DASLBLS}metabinner,
   fi
else
   echo "   >>> no bins found!"
fi

# drop last comma
DASLBLS2=$( echo ${DASLBLS} | sed -e 's/\,$//g' )
DASIN2=$( echo ${DASIN} | sed -e 's/\,$//g' )
echo "DASTOOL labels: ${DASLBLS2}"
echo "DASTOOL input: ${DASIN2}"

# run DAS
echo " > RUNNING DASTOOL"
mkdir -p ${OUTDIR_TMP}
echo "DAS_Tool --score_threshold $SCORE -t 8 -i ${DASIN2} -l ${DASLBLS2} -c ${CONTIGS} -o ${OUTDIR_TMP}/${OUTPREF}"
DAS_Tool --score_threshold $SCORE -t 8 -i ${DASIN2} -l ${DASLBLS2} -c ${CONTIGS} -o ${OUTDIR_TMP}/${OUTPREF}
echo "  >> converting results to FASTA"
# results => fasta
/data/umcg-tifn/rgacesa/conda_dastool/DAS_Tool/src/Contigs2Bin_to_Fasta.sh -i ${OUTDIR_TMP}/${OUTPREF}_DASTool_contig2bin.tsv -a ${CONTIGS} -o ${OUTDIR_TMP}/DAS_bins
rm -r ${OUTDIR}
mkdir -p ${OUTDIR}
echo "  >> collecting results"
for f in ${OUTDIR_TMP}/DAS_bins/*.fasta; do mv ${f} ${f/fasta/fa}; done

# move to real storage
mv ${OUTDIR_TMP}/DAS_bins/*.fa ${OUTDIR}/
# clean fastas
echo "  >> renaming bins"
CNT=0
cd ${OUTDIR}
for fa in *.fa
do
  CNT=$((CNT+1))
  mv $fa tmp.bin.${CNT}.fa
  python ${CLEANER} --input tmp.bin.${CNT}.fa --output bin.${CNT}.fa
  rm tmp.bin.${CNT}.fa
done
cd ..
#mv ${OUTDIR_TMP}/das_DASTool_contig2bin.tsv ${OUTDIR}/
#mv ${OUTDIR_TMP}/das_DASTool_summary.tsv ${OUTDIR}/
#mv ${OUTDIR_TMP}/das_DASTool.log ${OUTDIR}/
rm -r ${OUTDIR_TMP}
echo " > ALL DONE! "
