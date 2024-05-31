#!/bin/bash
#SBATCH --job-name=RSEM
#SBATCH --output=__RSEM_align.out
#SBATCH --error=__RSEM_align.err
#SBATCH --mem=8gb
#SBATCH --time=03:59:00
#SBATCH --cpus-per-task=8
#SBATCH --export=NONE
#SBATCH --get-user-env=L
module purge
module load RSEM/1.3.3-foss-2020a
module load Bowtie2/2.4.4-GCC-9.3.0

SID=${1}
REFID=${2}
TEMPF=${TMPDIR}
rsem-calculate-expression --bowtie2 --paired-end -p 8 --temporary-folder ${TEMPF} \
${SID}/clean_reads/*_1.fastq \
${SID}/clean_reads/*_2.fastq \
./${REFID}/bins_metawrap_refined_RSEM/RSEM_ref \
./${SID}/bins_metawrap_refined_RSEM_results
