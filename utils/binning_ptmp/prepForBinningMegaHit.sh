#!/bin/bash
#SBATCH --job-name=jB_prep
#SBATCH --error=JOB_OUT/__util_prepforbinning_MEGAHIT.err
#SBATCH --output=JOB_OUT/__util_prepforbinning_MEGAHIT.out
#SBATCH --mem=12gb
#SBATCH --time=0-05:00:00
#SBATCH --cpus-per-task=8
#SBATCH --open-mode=truncate

echo "> Starting binning-prep [MEGAHIT assembler]"

# --- LOAD MODULES ---
module load Miniconda3/4.8.3
CONDA=/data/umcg-tifn/metaGEM/envs/metawrap/
source activate ${CONDA}
# --- parse sample name from folder name ---
SNAME=${PWD##*/}
mkdir -p JOB_OUT

# ==========================
# READ FIX / re-sorting
# ==========================
echo " >> re-sorting & fixing reads"
mkdir -p clean_reads_fixed
echo "repair.sh in=clean_reads/${SNAME}_kneaddata_cleaned_pair_1.fastq in2=clean_reads/${SNAME}_kneaddata_cleaned_pair_2.fastq out=clean_reads_fixed/${SNAME}_kneaddata_cleaned_repaired_1.fastq out2=clean_reads_fixed/${SNAME}_kneaddata_cleaned_repaired_2.fastq outs=clean_reads_fixed/${SNAME}_kneaddata_cleaned_repaired_s.fastq"
repair.sh in=clean_reads/${SNAME}_kneaddata_cleaned_pair_1.fastq in2=clean_reads/${SNAME}_kneaddata_cleaned_pair_2.fastq out=clean_reads_fixed/${SNAME}_kneaddata_cleaned_repaired_1.fastq out2=clean_reads_fixed/${SNAME}_kneaddata_cleaned_repaired_2.fastq outs=clean_reads_fixed/${SNAME}_kneaddata_cleaned_repaired_s.fastq

# ==============================
# MEGAHIT GRAPH MAKER
# ==============================
# >> used by: GraphBin, MetaCOAG
# ==============================
echo " >> prepping megahit assembly graph"
# --- LOAD CONDA ENV ---
CONDA=/data/umcg-tifn/metaGEM/envs/metawrap/
TOGFA=/data/umcg-tifn/metaGEM/envs/metawrap/gfaview/misc/fastg2gfa
source activate $CONDA
# --- setup ---
IN=${PWD}/assembly_megahit/${SNAME}_megahit_contigs.fa
OUT1=${PWD}/assembly_megahit/${SNAME}_megahit_contigs_graph.fastg
OUT2=${PWD}/assembly_megahit/${SNAME}_megahit_contigs_graph.gfa
# run it
echo "megahit_toolkit contig2fastg 141 ${IN} > ${OUT1}"
megahit_toolkit contig2fastg 141 ${IN} > ${OUT1}
# convert it
echo ${TOGFA} ${OUT1} > ${OUT2}
${TOGFA} ${OUT1} > ${OUT2}

# ==== RUN COVERAGE ESTIMATORS ===
# ================================
# =========== MINIMAP ============
# ================================
# >> USED BY: VAMB
# ================================
# > works
echo " >> prepping coverage for VAMB"
# --- LOADING CONDA ENV for VAMB -
source activate /data/umcg-tifn/rgacesa/conda_vamb
# --- setup ---
CONTIGS=assembly_megahit/${SNAME}_megahit_contigs.fa
FQ1=clean_reads_fixed/${SNAME}_kneaddata_cleaned_repaired_1.fastq
FQ2=clean_reads_fixed/${SNAME}_kneaddata_cleaned_repaired_2.fastq
OUT_TMP=${TMPDIR}/${SNAME}/assembly_coverage_minimap2
OUT=assembly_coverage_minimap2
# prep tmp 
echo "mkdir -p ${OUT_TMP}"
mkdir -p ${OUT_TMP}
# prep folder
mkdir -p ${OUT}
echo "mkdir -p ${OUT}"
# prep index
echo "minimap2 -d ${OUT_TMP}/catalogue.mmi ${CONTIGS}"
minimap2 -d ${OUT_TMP}/catalogue.mmi ${CONTIGS}
# prep coverage
echo "minimap2 -t 8 -N 5 -ax sr ${OUT_TMP}/catalogue.mmi ${FQ1} ${FQ2} | samtools view -F 3584 -b --threads 8 > ${OUT_TMP}/sample_cov_minimap2.bam"
minimap2 -t 8 -N 5 -ax sr ${OUT_TMP}/catalogue.mmi ${FQ1} ${FQ2} | samtools view -F 3584 -b --threads 8 > ${OUT_TMP}/sample_cov_minimap2.bam
# collect data
echo "rm ${OUT_TMP}/catalogue.mmi"
rm ${OUT_TMP}/catalogue.mmi
echo "cp ${OUT_TMP}/* ${OUT}/"
cp ${OUT_TMP}/* ${OUT}/
echo "rm -r ${OUT_TMP}"
rm -r ${OUT_TMP}

# =============================================
# =========== METABINNER ===============
# =============================================
# >> used by Metabinner, SemiBin, metaCOAG
# =============================================
echo " >> prepping coverage for MetaBinner "
# --- LOAD CONDA ENV ---
CONDA=/data/umcg-tifn/rgacesa/conda_metabinner/
SCRIPT=${CONDA}/bin/scripts/gen_coverage_file.sh
SCRIPTKMERS=${CONDA}/bin/scripts/gen_kmer.py
source activate $CONDA
# --- parse sample name from folder name ---
SNAME=${PWD##*/}
# --- setup ---
ASSEMBLY_F=assembly_megahit
CONTIGS=${ASSEMBLY_F}/${SNAME}_megahit_contigs.fa
FQ1=clean_reads_fixed/${SNAME}_kneaddata_cleaned_repaired_1.fastq
FQ2=clean_reads_fixed/${SNAME}_kneaddata_cleaned_repaired_2.fastq
OUT=assembly_coverage_metabinner
OUT_TMP=${TMPDIR}/${SNAME}/assembly_coverage_metabinner
CONTIG_LT=1000

# prep folders
mkdir -p ${OUT}
mkdir -p ${OUT_TMP}
# run coverage generator script
echo "bash ${SCRIPT} -a ${CONTIGS} -o ${OUT_TMP} -t 8 -m 8 -l ${CONTIG_LT} ${FQ1} ${FQ2}"
bash ${SCRIPT} -a ${CONTIGS} -o ${OUT_TMP} -t 8 -m 8 -l ${CONTIG_LT} ${FQ1} ${FQ2}
# run kmer generator script
echo "python ${SCRIPTKMERS} $CONTIGS 1000 4" # work
python ${SCRIPTKMERS} $CONTIGS 1000 4
# move stuff
echo "mv ${OUT_TMP}/work_files/*.bam ${OUT}"
mv ${OUT_TMP}/work_files/*.bam ${OUT}  # BAM for other binners as well! works
echo "mv ${OUT_TMP}/work_files/mb2_master_depth.txt ${OUT}"
mv ${OUT_TMP}/work_files/mb2_master_depth.txt ${OUT}
echo "mv ${ASSEMBLY_F}/kmer*.csv ${OUT}"
mv ${ASSEMBLY_F}/kmer*.csv ${OUT}
echo "mv ${OUT_TMP}/* ${OUT}"
cp ${OUT_TMP}/* ${OUT}
# clean tmp files
rm -r ${OUT_TMP}

# =====================================
# =========== COVERM =================
# =====================================
echo " >> prepping coverage [CoverM] "
# --- LOADING CONDA ENV ---
CONDA=/data/umcg-tifn/rgacesa/conda_coverM
source activate $CONDA
# --- parse sample name from folder name ---
SNAME=${PWD##*/}
# --- setup ---
ASSEMBLY_F=assembly_megahit
CONTIGS=${ASSEMBLY_F}/${SNAME}_megahit_contigs.fa
FQ1=clean_reads_fixed/${SNAME}_kneaddata_cleaned_repaired_1.fastq
FQ2=clean_reads_fixed/${SNAME}_kneaddata_cleaned_repaired_2.fastq
OUT=assembly_coverage_coverm
OUT_TMP=${TMPDIR}/${SNAME}/assembly_coverage_coverm
# prep folders
mkdir -p ${OUT}
mkdir -p ${OUT_TMP}
echo "mkdir -p ${OUT}"
echo "mkdir -p ${OUT_TMP}"
# run coverage generator script
echo "coverm contig -1 ${FQ1} -2 ${FQ2} -r ${CONTIGS} -o ${OUT_TMP}/abundance.tsv -t 8"
coverm contig -1 ${FQ1} -2 ${FQ2} -r ${CONTIGS} -o ${OUT_TMP}/abundance.tsv -t 8
# remove header (for compatibility with megaCOAG
sed -i '1d' ${OUT_TMP}/abundance.tsv
echo "sed -i '1d' ${OUT_TMP}/abundance.tsv"
# collect & clean
cp ${OUT_TMP}/abundance.tsv ${OUT}/
echo "cp ${OUT_TMP}/abundance.tsv ${OUT}/"
rm -r ${OUT_TMP}
# =====================================
echo "> ALL DONE "
