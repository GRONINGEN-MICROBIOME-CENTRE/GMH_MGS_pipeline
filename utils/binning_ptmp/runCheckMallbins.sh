#!/bin/bash
#SBATCH --job-name=jCheckMa
#SBATCH --error=JOB_OUT/__binning_CheckM_all.err
#SBATCH --output=JOB_OUT/__binning_CheckM_all.out
#SBATCH --mem=48gb
#SBATCH --time=0-03:59:00
#SBATCH --cpus-per-task=8
#SBATCH --open-mode=truncate

# CHECKM RUNNER
checkmrunner () {
   NFA=0
   BDIR=$1
   echo "  >>> looking for bins in ${BDIR}"
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
            mkdir -p ${OUT}/${BDIR}
            # run checkm
            echo "checkm lineage_wf -f ${OUT}/${BDIR}_checkM_results_parsed.csv -t 8 -x fa ${BDIR} ${OUT}/${BDIR} --tab_table --pplacer_threads 8"
            checkm lineage_wf -t 8 -f ${OUT}/${BDIR}_checkM_results_parsed.csv -x fa ${BDIR} ${OUT}/${BDIR} --tab_table --pplacer_threads 8
            # parse results
            python ${CMPARSER} --input ${OUT}/${BDIR}/storage/bin_stats_ext.tsv --output ${OUT}/${BDIR}_checkM_results_parsed.csv --completeness ${COMPL_MIN} --contamination ${CONT_MAX}
            #echo "python ${CMPARSER} --input ${OUT}/${BDIR}/storage/bin_stats_ext.tsv --output ${OUT}/${BDIR}_checkM_results_parsed.csv --completeness ${COMPL_MIN} --contamination ${CONT_MAX}"
            # cleanup
            rm -r ${OUT}/${BDIR}
         else
             echo "   >>> no bins found!"
         fi
     fi
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
checkmrunner "bins_metawrap_refined"
# >> 9) DAS
checkmrunner "bins_DAS"
# >> 10) DAS v2
checkmrunner "bins_DAS_v2"
# >> 11) metawrap v2
checkmrunner "bins_metawrap_refined_v2"
# >> 12) resseambly
checkmrunner "bins_reassembled"
