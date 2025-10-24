#!/bin/bash
#SBATCH --mem=64gb
#SBATCH --time=0-07:59:00
#SBATCH --cpus-per-task=2

module load R

echo "> finding bin RGI results"

find . -name "*.rgi_out_basic_wild.txt" > __bins_rgi_paths
echo "> collecting!"
Rscript /scratch/hb-tifn/tools/GMH_pipeline/utils/Antibiotic_Resistance/run_resfinder_allsamples_MAGs_collectall_v02.R
