#!/bin/bash
#SBATCH --mem=128gb
#SBATCH --time=0-15:59:00
#SBATCH --cpus-per-task=8

# runs RGI

# defaults:
# - output folder = ${PWD}/RGI
# - temp folder for running = node tmp
# - input = ${1} / ${2} [requires fastq files]
# - SLURM out: ./<slurm out>
#
# example:
# from: /scratch/p287673/2025_Indian_IBD_LLD_1000IBD/1000IBD/2017_1000IBD_raw/G105191/
# sbatch /projects/hb-tifn/tools/GMH_pipeline/utils/Antibiotic_Resistance/run_resfinder_wtmp.sh clean_reads/G105191_kneaddata_cleaned_pair_1.fastq clean_reads/G105191_kneaddata_cleaned_pair_2.fastq

# PROCESS CLI
IN1=${1}
IN2=${2}
CARDPATH=/scratch/hb-tifn/DBs/CARD_2025_06/
THREADS=8
CLEANUP=Y

# STARTUP
echo "loading modules"
module load Miniconda3/22.11.1-1
source activate /scratch/hb-tifn/condas/2025_CARD_RGI

# LOAD DB
echo "loading RGI database"
# base part only: rgi load --card_json ${CARDJSON} --local
# > sanity check: show version
#rgi database --version --local
# > dump to fasta for RGI KMA
#rgi card_annotation -i ${CARDJSON} > card_annotation.log 2>&1
#rgi load -i ${CARDJSON} --card_annotation card_database_v3.0.1.fasta --local

# prep sample name
WD=${PWD}
FN=$(basename "${1}")
#SN=${FN%%_*}
SN=${FN}
OUT_PREFIX=${SN}_rgi_out_basic_wild
OUTDIR=${WD}/RGI

# work in node TMP:
NWD=${TMPDIR}/${SN}
IN1_ABS=$(realpath "$IN1")
IN2_ABS=$(realpath "$IN2")

echo "running: rgi btw on ${IN1_ABS} ${IN2_ABS}; run done in ${NWD}; output is ${OUTDIR}"

echo "${NWD}"
mkdir -p ${NWD}
cd ${NWD}
echo ${PWD}

# full load (RGI & wildcard plus indexes):
rgi load --kmer_database ${CARDPATH}/wildcard/61_kmer_db.json --amr_kmers ${CARDPATH}/wildcard/all_amr_61mers.txt --kmer_size 61 --wildcard_annotation ${CARDPATH}/wildcard_database_v4.0.1.fasta --card_json ${CARDPATH}/card.json --wildcard_index ${CARDPATH}/wildcard/index-for-model-sequences.txt --card_annotation ${CARDPATH}/card_database_v4.0.1.fasta --local

# debug:
ls -l

# run metagenomic classifier
CMDR="rgi bwt --read_one ${IN1_ABS} --read_two ${IN2_ABS} --output_file ${OUT_PREFIX} --local -n ${THREADS} --include_wildcard"
echo ${CMDR}
${CMDR}

# run kmer tracker for origin of AR
#rgi kmer_query --bwt --kmer_size 61 --threads ${THREADS} --minimum 10 --input ${OUT_PREFIX}.temp.bam --output ./RGI_origin_kmer_classifier_results --local

if [[ "${CLEANUP}" == "Y" ]]; then
	rm *.temp.*
	rm *.bam*
	rm -r localDB
	rm *.out
	rm *.json
fi

# collect results
mkdir -p ${OUTDIR}
cp * ${OUTDIR}
cd ${WD}
