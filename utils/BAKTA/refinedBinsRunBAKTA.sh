#!/bin/bash
# =========================
# RUNNER FOR BAKTA JOBS
# - run sortresults first and go to folder with sorted results (bins_refined folder should be there!)
# - goes through all .fa files in the folder
# - submits BAKTA job for each file
# ========================
BAKTA_RUNNER=/projects/hb-tifn/tools/GMH_pipeline/utils/BAKTA/runBAKTA.sh
cd bins_refined/
for FLDR in */
do 
   cd ${FLDR}
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
#      sbatch --error=__bakta.${SMPL}.err --output=__bakta.${SMPL}.out --partition=short ${BAKTA_RUNNER} ${SMPL}
       #sbatch --error=__bakta.${SMPL}.err --output=__bakta.${SMPL}.out ${BAKTA_RUNNER} ${SMPL}
       sbatch --error=/scratch/hb-tifn/tmp/tmp_err --output=/scratch/hb-tifn/tmp/tmp_out ${BAKTA_RUNNER} ${SMPL}
          sleep 5
       fi
   done
   cd ..
done
cd ..
