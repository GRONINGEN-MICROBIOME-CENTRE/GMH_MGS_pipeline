#!/bin/bash
# =========================
# RUNNER FOR BAKTA JOBS
# - goes through all .fa files in the folder
# - submits BAKTA job for each file
# =========================
BAKTA_RUNNER=/scratch/hb-tifn/tools/GMH_pipeline/utils/BAKTA/runBAKTA.sh
for SMPL in *.fa
do
   sbatch --error=__bakta.${SMPL}.err --output=__bakta.${SMPL}.out ${BAKTA_RUNNER} ${SMPL}
#   sleep 1
done
