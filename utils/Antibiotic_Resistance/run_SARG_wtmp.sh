#!/bin/bash
#SBATCH --mem=32gb
#SBATCH --time=0-11:59:00
#SBATCH --cpus-per-task=16

# defaults:
# - output folder = ${PWD}/ARO_SARG/
# - temp folder for running = node tmp
# - input = ${1} / ${2} [requires fastq files]
# - SLURM out: ./<slurm out>
#
# example:
# from: /scratch/p287673/2025_Indian_IBD_LLD_1000IBD/1000IBD/2017_1000IBD_raw/G105191/
# sbatch /projects/hb-tifn/tools/GMH_pipeline/utils/Antibiotic_Resistance/run_SARG_wtmp.sh clean_reads/G105191_kneaddata_cleaned_pair_1.fastq clean_reads/G105191_kneaddata_cleaned_pair_2.fastq


# PROCESS CLI
IN1=${1}
IN1B=$(basename ${1})
IN2=${2}
IN2B=$(basename ${2})
CONDA_P=/scratch/hb-tifn/condas/2025_ARO
THREADS=16

# STARTUP
echo "loading modules"
module load Miniconda3/22.11.1-1
echo "loading conda"
source activate ${CONDA_P}

# prep sample name
SN=$(basename ${PWD})
OUT=ARO_SARG

# work in node TMP:
# > prep paths
NWD=${TMPDIR}/${SN}
# > make folder for tmp files
echo "mkdir -p ${NWD}"
mkdir -p ${NWD}
# > copy input to tmp
echo "cp $(realpath ${IN1}) ${NWD}/${IN1B/.fastq/.fq}"
cp $(realpath ${IN1}) ${NWD}/${IN1B/.fastq/.fq}
echo "cp $(realpath ${IN2}) ${NWD}/${IN2B/.fastq/.fq}"
cp $(realpath ${IN2}) ${NWD}/${IN2B/.fastq/.fq}

# prep output
mkdir -p ${OUT}

# RUN
# > run part 1
CMD="args_oap stage_one -i ${NWD} -o ${OUT} -t ${THREADS}"
echo ${CMD}
${CMD}
# > run part 2
CMD2="args_oap stage_two -i ${OUT} -t ${THREADS}"
echo ${CMD2}
${CMD2}
