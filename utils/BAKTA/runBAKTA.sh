#!/bin/bash
#SBATCH --job-name=tBAKTA
#SBATCH --error=__bakta_test.err
#SBATCH --output=__bakta_test.out
#SBATCH --mem=23gb
#SBATCH --time=01:59:59
#SBATCH --cpus-per-task=4
#SBATCH --open-mode=truncate

# =======================================================
# BAKTA RUNNER
# - runs BAKTA job for one file [command line param]
# =======================================================
GENOME=${1}
DB=/scratch/hb-tifn/DBs/BAKTA_DB_v17/db
CONDA_ENV=/scratch/hb-tifn/condas/conda_BAKTA

module load Anaconda3/2022.05
source activate $CONDA_ENV

mkdir -p ${TMPDIR}/${GENOME}
echo "bakta --force --db ${DB} --threads 4 --keep-contig-headers --output ${GENOME/.fa/} --min-contig-length 200 --tmp-dir ${TMPDIR}/${GENOME} ${GENOME}"

bakta --force --db ${DB} --skip-plot --threads 4 --keep-contig-headers --output ${GENOME/.fa/} --min-contig-length 200 --tmp-dir ${TMPDIR}/${GENOME} ${GENOME}
# clean junk
rm ${GENOME/.fa/}/*.log
rm ${GENOME/.fa/}/*.json
rm ${GENOME/.fa/}/*.embl
#rm ${GENOME/.fa/}/*.txt
rm ${GENOME/.fa/}/*.tsv
rm ${GENOME/.fa/}/*.gbff
#rm ${GENOME/.fa/}/*.png
#rm ${GENOME/.fa/}/*.svg

