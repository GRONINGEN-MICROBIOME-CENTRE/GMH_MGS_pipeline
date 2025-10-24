#!/bin/bash
module purge
module load Anaconda3/2022.05
CONDAP=/scratch/hb-tifn/condas/conda_biobakery4/
OUTF=results_merged
echo " > loading conda"
conda activate ${CONDAP}
mkdir -p ${OUTF}
echo " >> merging SARG: antibiotic type table"
humann_join_tables -i ARO_SARG/ --file_name _SARG_abtype.rpkm -o ${OUTF}/results_ARO_SARG_abtype_merged.txt
echo " >> merging SARG: gene table"
humann_join_tables -i ARO_SARG/ --file_name _SARG_gene.rpkm -o ${OUTF}/results_ARO_SARG_gene_merged.txt
echo " >> merging SARG: antibiotic gene table"
humann_join_tables -i ARO_SARG/ --file_name _SARG_subtype.rpkm -o ${OUTF}/results_ARO_SARG_subtype_merged.txt
echo " > DONE"

conda deactivate
