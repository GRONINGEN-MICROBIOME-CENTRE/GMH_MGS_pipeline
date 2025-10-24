#!/bin/bash
#SBATCH --mem=32gb
#SBATCH --time=0-2:00:00
#SBATCH --cpus-per-task=16

CARDPATH=/scratch/hb-tifn/DBs/CARD_2025_06/
THREADS=1
CLEANUP=Y

# STARTUP
echo "loading modules"
module load Miniconda3/22.11.1-1
source activate /scratch/hb-tifn/condas/2025_CARD_RGI

# full load (RGI & wildcard plus indexes):
rgi load --wildcard_annotation ${CARDPATH}/wildcard_database_v4.0.1.fasta --card_json ${CARDPATH}/card.json --wildcard_index ${CARDPATH}/wildcard/index-for-model-sequences.txt --card_annotation ${CARDPATH}/card_database_v4.0.1.fasta --local

# ASVM-M-C19/ASVM-M-C19.bin.43/ASVM-M-C19.bin.43.faaASVM-M-C19/ASVM-M-C19.bin.43/ASVM-M-C19.bin.43.faa
while read SMPL
do
   echo " > running ${SMPL}"
   SN=${SMPL%%/*}
   #SN_REST="${SMPL#*/}"
   #SN2=${SN_REST%%/*}
   # prep run
   FN=$(basename "${SMPL}")
   # debug
   #echo ${SN}
   #echo ${FN}

   OUT_FILE=${SN}/RGI/${FN/.faa/}.rgi_out_basic_wild.txt

   CMDR="rgi main -i ${SMPL} --include_loose -t protein --clean --include_nudge --output_file ${OUT_FILE} --local -n ${THREADS}"
   echo ${CMDR}
   ${CMDR}
   # cleanup
   rm ${SN}/RGI/*.json
done < __missing_RGI

# cleanup
rm -r localDB
