#!/bin/bash
RUNNER=/data/umcg-tifn/rgacesa/dag3_pipeline_3c/utils/BAKTA/runBAKTA.sh
for BATCH in all_samples_TR_2*/
do
   echo " > BATCH ${BATCH}"
   cd ${BATCH}
   for SMPL in TR_*/
   do
      echo "  >>  sample ${SMPL}"
      cd ${SMPL}
      cd bins_metawrap_refined
      for FA in *.fa
      do
         echo "   >>> ${FA}"
         sbatch --partition=short --error=__bakta.${FA}.err --output=__bakta.${FA}.out ${RUNNER} ${FA}
         sleep 20
      done
      cd ..
      cd ..
   done
   cd ..
done
