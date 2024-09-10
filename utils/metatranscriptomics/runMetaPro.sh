#!/bin/bash
#SBATCH --nodes=1
#SBATCH --cpus-per-task=16
#SBATCH --time=7:59:00
#SBATCH --mem=512gb
#SBATCH --job-name mpro
CONTAINER='/scratch/p287673/condas_tools/metapro/metapro_v3.0.1.sif'
CONFIG='/scratch/p287673/condas_tools/metapro/metapro_config.ini' 

# INPUT
IN1=${1}
IN2=${1/_1.fastq/_2.fastq}
SNAME=${IN1/_1.fastq/}
OUT=${SNAME}_metapro

module load Python
singularity exec -B /scratch ${CONTAINER} python3 /pipeline/MetaPro.py -c ${CONFIG} -1 ${IN1} -2 ${IN2} --verbose_mode leave -o ${OUT}
