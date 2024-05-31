#!/bin/bash
#SBATCH --job-name=SVmerge
#SBATCH --error=__SVmerge.err
#SBATCH --output=__SVmerge.out
#SBATCH --mem=16gb
#SBATCH --time=07:29:00
#SBATCH --cpus-per-task=1
#SBATCH --open-mode=truncate
#SBATCH --profile=task
echo "======= RUNNING SV MERGER ======================== " 
# PURGING ENVIRUMENT 
echo "> purging environment "
module purge
echo "> loading modules "
# --- LOAD MODULES --- 
module load Miniconda3/4.8.3
# --- CLEAN CONDA  --- 
echo "> cleaning conda env. "
# --- LOAD CONDA --- 
echo "> loading conda env. "
source activate /data/umcg-tifn/SV/conda_SV/
module purge
echo "> loading sys paths "
mkdir -p results
mkdir -p results/html
python /data/umcg-tifn/SV/SGVFinder/src/SGVF_cmd.py "*.jsdel" results/dsgv.csv results/vsgv.csv --min_samp_cutoff 5 --x_coverage 0.01 --rate_param 10 --browser_path results/html --csv_output
