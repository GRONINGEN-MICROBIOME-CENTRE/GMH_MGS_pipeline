#!/bin/bash

RUNNER=/projects/hb-tifn/tools/GMH_pipeline/utils/Antibiotic_Resistance/run_resfinder_allMAGs.sh

for SMPL in */
do
   if [[ "${SMPL}" != "JOB_OUT/" ]]; then
      echo ${SMPL}
      cd ${SMPL}
      SN=${SMPL}
      SN=${SN/\//}
      echo "submitting RGI run for MAGS in ${SMPL}"
      YOGG_SLURMOTH="sbatch ${RUNNER}"
      echo ${YOGG_SLURMOTH}
      ${YOGG_SLURMOTH}
      cd ..
   fi
done

