#!/bin/bash
#SBATCH --job-name=jB_fixr
#SBATCH --error=JOB_OUT/__fixreads.err
#SBATCH --output=JOB_OUT/__fixreads.out
#SBATCH --mem=16gb
#SBATCH --time=0-00:59:00
#SBATCH --cpus-per-task=4
#SBATCH --open-mode=truncate
# --- LOAD MODULES --- 
module load BBMap/37.93-foss-2018a
# --- LOADING CONDA ENV for METAWRAP --- 
SNAME=${PWD##*/}
mkdir -p clean_reads_fixed
repair.sh in=clean_reads/${SNAME}_kneaddata_cleaned_pair_1.fastq in2=clean_reads/${SNAME}_kneaddata_cleaned_pair_2.fastq out=clean_reads_fixed/${SNAME}_kneaddata_cleaned_repaired_1.fastq out2=clean_reads_fixed/${SNAME}_kneaddata_cleaned_repaired_2.fastq outs=clean_reads_fixed/${SNAME}_kneaddata_cleaned_repaired_s.fastq
