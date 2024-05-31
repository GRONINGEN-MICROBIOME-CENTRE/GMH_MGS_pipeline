#!/bin/bash
#SBATCH --job-name=K2t16S
#SBATCH --error=JOB_OUT/__testkrak.err
#SBATCH --output=JOB_OUT/__testkrak.out
#SBATCH --mem=32gb
#SBATCH --time=0:09:00
#SBATCH --cpus-per-task=1
#SBATCH --open-mode=truncate
# ==== JOB KRAKEN2 (aK2) ==== 
echo "========================================== " 
echo "> STARTING JOB KRAKEN2 (job aK2)" 
echo "========================================== " 
# OPTIONS
MINHIT=2 # min # of hits, default = 2--minimum-hit-groups
CONF=0.01 # confidence filter, default = 0
SEQOUT=0 # if not 0, write output sequences
DB=/data/umcg-tifn/rgacesa/kraken2_DB_17052021
OUTF=kraken2_NR
BRACKEN_MIN=5
# PURGING ENVIRUMENT 
echo "> purging environment "
module purge
echo "> loading modules "
# --- LOAD MODULES --- 
module load Miniconda3/4.7.10
# --- CLEAN CONDA  --- 
echo "> cleaning conda env. "
source deactivate
# --- LOAD CONDA --- 
echo "> loading conda env. "
source activate /data/umcg-tifn/rgacesa/conda_kraken2
echo "Running KRAKEN2 profiling"
# --- set sample name ---
SNAME=${1/sfinderOutput\./}
SNAME=${SNAME/\.fastq/}
SNAME=${SNAME/\.fa/}
#echo $SNAME
# --- RUN KRAKEN2 --- 
mkdir -p ${SNAME}/${OUTF}
# >> RUN KRAKEN2
if [ $1 != "0" ]
then
   OUTSCLASS=${SNAME}/${OUTF}/${SNAME}_classified_out
   OUTSUNCLASS=${SNAME}/${OUTF}/${SNAME}_unclassified_out
   kraken2 --db $DB --threads 1 --output - --classified-out $OUTSCLASS --unclassified-out $OUTSUNCLASS --report ${SNAME}/${OUTF}/${SNAME}.kreport $1 --minimum-hit-groups $MINHIT --confidence $CONF
else 

   kraken2 --db $DB --threads 1 --output - --report ${SNAME}/${OUTF}/${SNAME}.kreport $1 --minimum-hit-groups $MINHIT --confidence $CONF
fi
# >> RUN KRAKEN2 report fixed script (makes K2 UHGG DB report BRACKEN compatible)
python /data/umcg-tifn/rgacesa/dag3_pipeline_3c/utils/fixKraken2report.py ${SNAME}/${OUTF}/${SNAME}.kreport
python /data/umcg-tifn/rgacesa/dag3_pipeline_3c/utils/krakenReportToMP3.py --infile ${SNAME}/${OUTF}/${SNAME}.kreport.bc --out ${SNAME}/${OUTF}/${SNAME}.kreport.bc.mp3.txt
# >> RUN BRACKEN 
bracken -d /data/umcg-tifn/rgacesa/krakenDB_UHGG/ -i $SNAME/${OUTF}/${SNAME}.kreport.bc  -w $SNAME/${OUTF}/${SNAME}.bracken.result.kr -o ${SNAME}/${OUTF}/${SNAME}.bracken.result.kr -t $BRACKEN_MIN -l S -r 250
python /data/umcg-tifn/rgacesa/dag3_pipeline_3c/utils/krakenReportToMP3.py --infile ${SNAME}/${OUTF}/${SNAME}.bracken.result.kr --out ${SNAME}/${OUTF}/${SNAME}.bracken.result.mp3.txt

