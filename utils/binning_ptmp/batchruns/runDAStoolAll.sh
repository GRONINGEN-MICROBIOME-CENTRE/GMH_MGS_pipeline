#!/bin/bash
FLD=/data/umcg-tifn/rgacesa/dag3_pipeline_3c/utils/binning_ptmp
# iterate over folders, submit refiner for each folder
for F in */
do
cd ${F}
sbatch ${FLD}/runDasTool.sh
cd ..
done
