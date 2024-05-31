# ==================================================================
# runs metacompass submitter script for all samples in current dir
# ==================================================================
# > runner script
RUNNER=/data/umcg-tifn/rgacesa/dag3_pipeline_3c/utils/MetaCompass/runMetaCompassPERef_v2.sh
# > reference genome / assembly / co-assembly
REF=${1}
# > make sure JOB_OUT exists
mkdir -p JOB_OUT
for F in *_1.fq.gz
do
   SMPL=${F/_1\.fq\.gz/}
   echo "sbatch --error=JOB_OUT/__mcompass.${SMPL}.err --output=JOB_OUT/__mcompass.${SMPL}.out ${RUNNER} ${SMPL} ${REF}"
done
