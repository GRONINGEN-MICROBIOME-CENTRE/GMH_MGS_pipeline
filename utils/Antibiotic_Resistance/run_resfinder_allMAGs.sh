#!/bin/bash
#SBATCH --mem=32gb
#SBATCH --time=0-8:00:00
#SBATCH --cpus-per-task=4

# runs RGI for ALL MAGs (protein faa) files in the folder
CARDPATH=/scratch/hb-tifn/DBs/CARD_2025_06/
THREADS=4
CLEANUP=Y

# STARTUP
echo "loading modules"
module load Miniconda3/22.11.1-1
source activate /scratch/hb-tifn/condas/2025_CARD_RGI

# LOAD DB
echo "loading RGI database"

# prep sample name
OUT_F=RGI
#OUT_F=${SN/.faa/}
mkdir -p ${OUT_F}

# full load (RGI & wildcard plus indexes):
rgi load --wildcard_annotation ${CARDPATH}/wildcard_database_v4.0.1.fasta --card_json ${CARDPATH}/card.json --wildcard_index ${CARDPATH}/wildcard/index-for-model-sequences.txt --card_annotation ${CARDPATH}/card_database_v4.0.1.fasta --local
#rgi load --card_json ${CARDPATH}/card.json --local

#for SAMPLE in `find . -maxdepth 2 -name "*[1234567890].faa"`
for SAMPLE in `find . -maxdepth 2 -name "*.faa"`
do
FN=$(basename "${SAMPLE}")
OUT_PREFIX=${FN/.faa/}.rgi_out_basic_wild
# run metagenomic classifier
#CMDR="rgi main -i ${IN1} -a DIAMOND -t protein --clean --include_nudge --output_file ${OUT_F}/${OUT_PREFIX} --local -n ${THREADS}"
CMDR="rgi main -i ${SAMPLE} --include_loose -t protein --clean --include_nudge --output_file ${OUT_F}/${OUT_PREFIX} --local -n ${THREADS}"
echo ${CMDR}
${CMDR}
done
# cleanup
rm ${OUT_F}/*.json
rm -r localDB
