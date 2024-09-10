#!/bin/bash
#SBATCH --job-name=phyloFlash
#SBATCH --mem=40gb
#SBATCH --time=0-07:59:00
#SBATCH --cpus-per-task=16
#SBATCH --open-mode=truncate

# NOTES:
# > $1 = input fastq1
echo "Invoking phyloFlash"
echo "CLs: ${1} ${2}"

# CONFIG:
# > database
DB=/scratch/p287673/tools_DBs/138.1/
# > CPUS:
CPUS=16

#phyloFlash.pl -lib LIB -everything -read1 reads_F.fq.gz -read2 reads_R.fq.gz

# HELP / USE
if [[ $# -ne 1 ]];
    then
    echo "ERROR: script requires ONE command line parameter:"
    echo " <input file (fastq, ending with _1)> "
    echo "NOTE: _2 file is automatically selected from _1 file"
    exit 2
fi
# --- LOAD MODULES --- 
module load Miniconda3/4.8.3
# --- LOADING CONDA ENV ---
CONDA=/scratch/p287673/condas_tools/phyloFlash/
source activate $CONDA
# --- setup ---
IN1=$1
IN2=${1/_1.fastq/_2.fastq}
# --- parse sample name from input name ---
SNAME=${IN1/_1.fastq/}
OUT=${SNAME}_phyloflash
mkdir -p ${OUT}
phyloFlash.pl -lib ${OUT} -almosteverything -read1 ${IN1} -read2 ${IN2} -dbhome ${DB}
