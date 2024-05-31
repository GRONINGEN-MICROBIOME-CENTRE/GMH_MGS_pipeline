#!/bin/bash
#SBATCH --job-name=jCheckMa
#SBATCH --error=JOB_OUT/__binning_CheckM_all.err
#SBATCH --output=JOB_OUT/__binning_CheckM_all.out
#SBATCH --mem=48gb
#SBATCH --time=0-03:59:00
#SBATCH --cpus-per-task=8
#SBATCH --open-mode=truncate

# CHECKM RUNNER [use tmp]
checkmrunner () {
   NFA=0
   BDIR=$1
   echo "  >>> looking for bins in ${BDIR}"
   if [ -d ${BDIR} ] 
   then
      NFA=$(ls -l ${BDIR}/*.fa | grep ^- | wc -l)
      if [ "${NFA}" -gt "1" ]; then
         echo "   >>> found ${NFA} bins"
         # prep folder
         mkdir -p ${OUT_TMP}/${BDIR}
         mkdir -p ${OUT}
         # run checkm
         echo "checkm lineage_wf -t 8 -x fa ${BDIR} ${OUT_TMP}/${BDIR} --tab_table --pplacer_threads 8"
         checkm lineage_wf -t 8 -x fa ${BDIR} ${OUT_TMP}/${BDIR} --tab_table --pplacer_threads 8
         # parse results
         echo "python ${CMPARSER} --input ${OUT_TMP}/${BDIR}/storage/bin_stats_ext.tsv --output ${OUT}/${BDIR}_checkM_results_parsed.csv --completeness ${COMPL_MIN} --contamination ${CONT_MAX}"
         python ${CMPARSER} --input ${OUT_TMP}/${BDIR}/storage/bin_stats_ext.tsv --output ${OUT}/${BDIR}_checkM_results_parsed.csv --completeness ${COMPL_MIN} --contamination ${CONT_MAX}
         # cleanup
         rm -r ${OUT_TMP}/${BDIR}
      fi
   else
      echo "   >>> no bins found!"
fi
}

# ==========================
# RUN CHECKM ON ALL BINNERS
# ==========================

echo "> STARTING CHECKM RUNNER"
# --- SETTINGS ---
CMPARSER=/data/umcg-tifn/rgacesa/dag3_pipeline_3c/utils/binning/parseCheckM.py
COMPL_MIN=25
CONT_MAX=25
OUT=checkM_all
SNAME=${PWD##*/}
OUT_TMP=${TMPDIR}/${SNAME}/checkM_all
# --- LOAD MODULES ---
module load Miniconda3/4.8.3
# --- LOADING CONDA ENV for METAWRAP ---
CONDA=/data/umcg-tifn/rgacesa/conda_metabinner/
echo "  >> loading conda env: ${CONDA}"
source activate $CONDA
# --- parse sample name from folder name ---
echo " > LOOKING FOR BINS AND RUNNING CHECKM ..."
# --- prep DAS tsv files ---
#  >> 1) CONCOCT
checkmrunner "bins_concoct"
# >> 2) MAXBIN2
checkmrunner "bins_maxbin2"
# >> 3) METABAT2
checkmrunner "bins_metabat2"
# >> 4) GRAPHBIN
checkmrunner "bins_graphBin"
# >> 5) VAMB
checkmrunner "bins_vamb"
# >> 6) semiBIN
checkmrunner "bins_semibin"
# >> 7) metaCOAG
checkmrunner "bins_metaCOAG"
# >> 8) metaBINNER
checkmrunner "bins_metabinner"
# >> 9) DAS
checkmrunner "bins_DAS"
# >> 10) metaWRAP refined bins
checkmrunner "bins_metawrap_refined"
