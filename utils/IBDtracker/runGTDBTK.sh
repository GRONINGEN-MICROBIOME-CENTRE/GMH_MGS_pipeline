#!/bin/bash
#SBATCH --job-name=jGTDBKall
#SBATCH --error=JOB_OUT/__gtdbk.err
#SBATCH --output=JOB_OUT/__gtdbk.out
#SBATCH --mem=64gb
#SBATCH --time=0-07:59:00
#SBATCH --cpus-per-task=8
#SBATCH --open-mode=truncate

# ==========================
# ==== RUNNER FUNCTION =====
# ==========================
# > $1 = input folder
runGTDBK () {
   NFA=0
   BDIR=$1
   echo " > Looking for bins in ${1}"
   if [ -d ${BDIR} ] 
   then
      # check if done already
      if [ -f "${OUT}/${BDIR}_checkM_results_parsed.csv" ]
      then
         echo "  >>> ${OUT}/${BDIR}_checkM_results_parsed.csv exists, skipping checkM for ${BDIR}"
      else
      # if not, check if there are bins to test
         NFA=$(ls -l ${BDIR}/*.fa | grep ^- | wc -l)
         if [ "${NFA}" -gt "1" ]; then
            echo "   >>> found ${NFA} bins"
            # prep folder
            mkdir -p ${OUT_TMP}/${BDIR}
            mkdir -p ${OUT_TMP}/${BDIR}_tmp
            # run GTDBTK
            echo "gtdbtk classify_wf --genome_dir ${BDIR} --out_dir ${OUT_TMP}/${BDIR}_tmp --extension .fa --cpus ${CPUS}"
            gtdbtk classify_wf --genome_dir ${BDIR} --out_dir ${OUT_TMP}/${BDIR}_tmp --extension .fa --cpus ${CPUS}
            # sort data
            mkdir -p ${OUT}/${BDIR}
            cp ${OUT_TMP}/${BDIR}_tmp/identify/* ${OUT}/${BDIR}
            cp ${OUT_TMP}/${BDIR}_tmp/classify/*.tsv ${OUT}/${BDIR}
            # cleanup
            rm -r ${OUT_TMP}
         else
            echo "   >>> no bins found!"
         fi
      fi
   fi
}
# ==========================


# ==========================
# GTDBK runner
# ==========================

echo "> STARTING GTDBTK RUNNER"
# --- SETTINGS ---
CPUS=8
OUT=bins_refined_GTDBTK
OUT_TMP=${TMPDIR}/${SNAME}/GTDBK_all
echo " > loading modules and conda"
# --- LOAD MODULES ---
module load Miniconda3/4.8.3
# --- LOADING CONDA ENV for METAWRAP ---
CONDA=/data/umcg-tifn/rgacesa/conda_GTDBK
source activate $CONDA
# --- load DB ---
echo " > setting up GTDBTK database"
export GTDBTK_DATA_PATH=/data/umcg-tifn/rgacesa/DB_GTDB/release207_v2
echo "  >> GTDBK DB set to ${GTDBTK_DATA_PATH}"
echo " > LOOKING FOR BINS in bins_metawrap_refined ..."
runGTDBK "bins_metawrap_refined"
echo " > ALL DONE! "
