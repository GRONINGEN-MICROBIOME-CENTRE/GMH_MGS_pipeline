#!/bin/bash
#SBATCH --job-name=jB_coverage
#SBATCH --error=JOB_OUT/__coverage.err
#SBATCH --output=JOB_OUT/__coverage.out
#SBATCH --mem=16gb
#SBATCH --time=0-03:59:00
#SBATCH --cpus-per-task=8
#SBATCH --open-mode=truncate
# --- LOAD MODULES --- 
module load Miniconda3/4.8.3
# --- LOADING CONDA ENV for METAWRAP --- 
source activate /data/umcg-tifn/rgacesa/conda_binnacle
# --- parse sample name from folder name ---
SNAME=${PWD##*/}
# --- setup ---
CONTIGS=assembly_megahit/${SNAME}_megahit_contigs.fa
FQ1=clean_reads_fixed/${SNAME}_kneaddata_cleaned_repaired_1.fastq
FQ2=clean_reads_fixed/${SNAME}_kneaddata_cleaned_repaired_2.fastq
INDEX=assembly_coverage/idx

# prep folder
mkdir -p assembly_coverage
# prep coverage [using bowtie]
bowtie2-build --threads 8 $CONTIGS assembly_coverage/idx #build the index
bowtie2 -p 8 -x assembly_coverage/idx -U $FQ1 | samtools view -bS - | samtools sort - -o assembly_coverage/alignment_1.bam #align first reads
bowtie2 -p 8 -x assembly_coverage/idx -U $FQ2 | samtools view -bS - | samtools sort - -o assembly_coverage/alignment_2.bam #align second reads
samtools merge assembly_coverage/alignment_total.bam assembly_coverage/alignment_1.bam assembly_coverage/alignment_2.bam --threads 8 #merge the alignments 
samtools sort -n assembly_coverage/alignment_total.bam -o assembly_coverage/alignment.bam --threads 8 #sort by read names 

