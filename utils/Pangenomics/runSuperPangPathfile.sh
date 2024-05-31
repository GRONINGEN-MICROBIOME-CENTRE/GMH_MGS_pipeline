#!/bin/bash
#SBATCH --job-name=superpang
#SBATCH --error=__superpang.err
#SBATCH --output=__superpang.out
#SBATCH --mem=48gb
#SBATCH --time=15:59:00
#SBATCH --cpus-per-task=16
#SBATCH --open-mode=truncate

# =======================================================
# RUNNER for SuperPang Pangenomics tool
# - runs SuperPang on input file with paths (entered as CL param 1)
# - NOTE: input files MUST be text file with path to ONE MAG PER LINE
# - example input file ${1}:
#       </scratch/cookie_DNA/cookie_MAG1.fa>     
#       </scratch/cookie_DNA/cookie_MAG2.fa>     
#       </scratch/cookie_DNA_try2/bad_cookie_MAG1.fa>     
#       </scratch/cookie_DNA_try2/bad_cookie_MAG2.fa>   
# ${2}: tab-delimited file ended with a .tsv extension, in the form genome1 percent_completeness
#    example:
#        <cookie_MAG1\t50>
#        <cookie_MAG2\t80>
#           ...
#    
# =======================================================

# WORKFLOW:
# > copies input to node tmp: ${TMPDIR}
# > runs GGcaller
# > pulls results back 

# > parameters:
OUTPUT=superpang_out # where to put output
ALIGNER=def # aligner ( --aligner [def,ref] )
THREADS=16 # --threads (should be same as CPUs in #SBATCH )
MMST=200 # -m : mismatch size threshold [def 100]: more means more aggressive merging of contigs
IDST=200 # -g : indel size threshold [def 100]: more means more agressive merging of contigs
GAT=0.5 # -a : genome-assignment-threshold [def 0.5]. Fractio kmers required to assign a contig to an input genome, less = more aggressive
KSIZE=301 # -k : kmer size [def 301]
BIT=0.95 # -b : bubble-identity-threshold to squish the bubble [def = 0.95] (less = more agressive)

# START OF CODE
echo "> starting superpang runner "
CONDA=/scratch/hb-tifn/condas/conda_SuperPang
INPUT=${1}
CMPL=${2}
# check for number of CL params
if [ "$#" -ne 2 ]; then
    echo "ERROR: number of CL parameters is not correct!"
    echo "Usage: $0 <param1> <param2>"
    exit 1  # Exit the script with a non-zero status code
fi

echo " >> loading conda env."
# load conda
module purge
module load Anaconda3
source activate ${CONDA}
# prep tmp folder on node
echo " >> preparing temp folder on node"
NTMP=$(mktemp -q -d ${TMPDIR}/spank.XXX)
# check if it worked
if [ $? -ne 0 ]; then
   echo "ERROR: $0: cannot create temp folder on node, quitting"
   exit 1
fi
# copy input files to tmp:
echo " >> copying input data (${INPUT}) to temp folder"
mkdir -p ${NTMP}/input/
mkdir -p ${NTMP}/tmp/
mkdir -p ${NTMP}/superpang_out/
cp ${INPUT} ${NTMP}/input/

echo " >> running SuperPang on ${INPUT}"
CMD="SuperPang.py --force-overwrite -k ${KSIZE} -b ${BIT} -a ${GAT} -g ${IDST} -m ${MMST} -f ${INPUT} -q ${CMPL} -d ${NTMP}/tmp/ -o ${NTMP}/superpang_out -t ${THREADS}"
echo ${CMD}
${CMD}

# get data
echo " >> retrieving data from temp folder"
mkdir -p ${OUTPUT}
cp -r ${NTMP}/superpang_out/* ${OUTPUT}
rm -r ${NTMP}/superpang_out
# DONE
echo "> DONE"
