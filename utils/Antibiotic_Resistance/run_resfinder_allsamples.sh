#!/bin/bash

# runs ALL samples in a folder (patched on top of GMH pipeline), requires following:
# 1) run cleaning part of GMH pipeline
# 2) go to folder with samples (raw data / sbatch jobs)
# 3) run this

RUNNER=/projects/hb-tifn/tools/GMH_pipeline/utils/Antibiotic_Resistance/run_resfinder_wtmp.sh

for SMPL in */
do 
   if [[ "${SMPL}" != "JOB_OUT/" ]]; then
      echo ${SMPL}
      cd ${SMPL}
      SN=${SMPL}
      SN=${SN/\//}
      R1=clean_reads/${SN}_kneaddata_cleaned_pair_1.fastq
      R2=clean_reads/${SN}_kneaddata_cleaned_pair_2.fastq
      echo "submitting run for ${SMPL}"
      #echo ${PWD}
      YOGG_SLURMOTH="sbatch ${RUNNER} ${R1} ${R2}"
      echo ${YOGG_SLURMOTH}
      ${YOGG_SLURMOTH}
      cd ..
   fi
done
