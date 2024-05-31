#!/bin/bash
#SBATCH --job-name=h3_rg
#SBATCH --error=__regroup.err
#SBATCH --output=__regroup.out
#SBATCH --mem=16gb
#SBATCH --time=7:29:00
#SBATCH --cpus-per-task=1
#SBATCH --open-mode=truncate

ml Miniconda3/4.7.10
source activate /data/umcg-tifn/rgacesa/conda_dag3_v3
mkdir -p KEGG
for i in gene_families/*.tsv
do
   O=${i/_genefamilies/_KEGG}
   O=${O/gene_families\//}
   echo "regrouping ${i} to KEGG"
   humann_regroup_table -i ${i} -o KEGG/${O} -g uniref90_ko
done
