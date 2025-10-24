#!/bin/bash
RUNNER=/projects/hb-tifn/tools/GMH_pipeline/utils/Antibiotic_Resistance/run_resfinder_wtmp.sh

while read l
do
echo "(re)-running ${l}"	
R1=${l}_1.fastq.gz
R2=${l}_2.fastq.gz
SNM=${l}
echo ${SNM}
mkdir -p ${SNM}
cd ${SNM}
rm *.out
YOGG_SLURMOTH="sbatch ${RUNNER} ../${R1} ../${R2}"
echo ${PWD}
echo ${YOGG_SLURMOTH}
${YOGG_SLURMOTH}
cd ..
done < __RGI_ndone
