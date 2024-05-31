#!/bin/bash
# =========================
# RUNNER FOR BAKTA JOBS
# - goes through all .fa files in the folder
# - submits BAKTA job for each file
# ========================
BAKTA_RUNNER=/projects/hb-tifn/tools/GMH_pipeline/utils/BAKTA/runBAKTA.sh
   echo " > running samples in ${PWD}"
   for SMPL in *.fa
   do
       # check if already done
       SMPL_RES=${SMPL/\.fa/}/${SMPL/\.fa/}.gff3
       #echo ${F}/bins_metawrap_refined/${SMPL_RES}
       if [ -f ${SMPL_RES} ]; then
          echo " + BAKTA DONE for ${SMPL}"
       fi
       if ! [ -f ${SMPL_RES} ]; then
          echo " - BAKTA NOT DONE for ${SMPL}, submitting job"
       sbatch --error=/scratch/hb-tifn/tmp/tmp_err --output=/scratch/hb-tifn/tmp/tmp_out ${BAKTA_RUNNER} ${SMPL}
          sleep 1
       fi
   done
