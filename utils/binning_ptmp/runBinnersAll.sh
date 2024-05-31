#!/bin/bash
FLD=/data/umcg-tifn/rgacesa/dag3_pipeline_3c/utils/binning_ptmp
# run binners one by one
echo " >> submitting metawrap binners [maxbin2, metabat2, concoct]"
echo "sbatch ${FLD}/runBinningMetaWrap.sh"
sbatch ${FLD}/runBinningMetaWrap.sh
echo " >> submitting VAMB"
echo "sbatch ${FLD}/runVAMB.sh"
sbatch ${FLD}/runVAMB.sh
#echo " >> submitting metabinner"
#echo "sbatch ${FLD}/runMetaBinner.sh"
#sbatch ${FLD}/runMetaBinner.sh
echo " >> submitting metaCOAG"
echo "sbatch ${FLD}/runMetaCOAG.sh"
sbatch ${FLD}/runMetaCOAG.sh
echo " >> submitting semibin"
echo "sbatch ${FLD}/runSemiBin.sh"
sbatch ${FLD}/runSemiBin.sh
