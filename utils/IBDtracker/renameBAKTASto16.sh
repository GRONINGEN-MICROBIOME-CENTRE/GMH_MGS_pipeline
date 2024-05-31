#!/bin/bash
for BATCH in all_samples_TR_2*/
do
   echo " >> BATCH ${BATCH}"
   cd ${BATCH}
   for SMPL in TR_*/
   do
      echo "  >>> sample ${SMPL}"
      cd ${SMPL}
      rm bins_metawrap_refined/__*
      rm -r bins_metawrap_refined/*/
      mv bins_metawrap_refined_BAKTA/ bins_metawrap_refined_BAKTA_1.6/
      mv bins_metawrap_refined_BAKTA_taxsorted/ bins_metawrap_refined_BAKTA_taxsorted_1.6/
      cd ..
   done
   cd ..
done
