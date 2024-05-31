#!/bin/bash
#SBATCH --job-name=RSEM_prep
#SBATCH --output=__RSEM_prepare_reference.out
#SBATCH --error=__RSEM_prepare_reference.err
#SBATCH --mem=8gb
#SBATCH --time=00:19:30
#SBATCH --cpus-per-task=4
#SBATCH --export=NONE
#SBATCH --get-user-env=L
#SBATCH --partition=short

TARGET=$1
echo "preparing RSEM reference for ${1} into ${2}"

module purge 
module load RSEM/1.3.3-foss-2020a
ml Bowtie2

DIR="${2}"
DIR="${DIR%/}"             # strip trailing slash (if any)
DIR="${DIR##*/}"
mkdir -p ${DIR}
rsem-prepare-reference ${1} --bowtie2 ${2}

