#!/bin/bash
FLD=/data/umcg-tifn/rgacesa/dag3_pipeline_3c/utils/binning_ptmp
# iterate over folders, submit binning for each sample
for F in */
do
cd ${F}
sbatch ${FLD}/runBinnersAll.sh
cd ..
done
