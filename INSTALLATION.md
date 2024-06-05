# GMH pipeline

##### WARNING: This pipeline was developed, deployed, and is used internally for data analysis at Groningen Microbiome Hub. *It is not publication-ready piece of software (and was never intended to be), and is provided as-is*. We cannot provide any support, debugging or other assistance in installation or deployment.

NOTES:

- Testing (and deployment) was done on UMCG/RUG HPC cluster habrok . It is an AMD architecture HPC cluster (mainly using Amd Epyc™ 7763 CPUS), running Rocky Linux release 8.9 (Green Obsidian) and SLURM job manager (v. 23.11.4). It will generate jobs for SLURM and *WILL NOT* work for other job managers without re-coding, but it might work for a workstation which runs *bash* (in which case the pipeline should run sequentially, please note this was not tested!)

- If running the pipeline on one computer (rather then HPC), make sure following parameters in config file are set: [PIPELINE]: useNodeTMP = 0; useSlurm = 0

- Requirements: software: linux, conda; hardware: ~300GB of disk space (mainly for databases), ~64 GB RAM

## Description

Pipeline is a combination of python codes used to write SLURM jobs, conda enviroments with appropriate software, and bioinformatics databases required to run the software.

## Pipeline deployment workflow:

1. Install conda (or miniconda or (micro)mamba)

2. Deploy conda environments, appropriate databases, and other details where necessary (see details and links to used tools below).
   
   to deploy conda, use:
   
    `conda create --prefix <new_env> --file <spec-file.txt>`
   
   Example: 
   
   `conda create --prefix /<my_folder_with_condas>/conda_BBduk --file ./conda_bbduk_specfile.txt`

3. Make sure pipeline config file has correct paths to conda environments and databases

4. Run it (see main README file)

###### Notes:

- *(micro)mamba* usually deploys environments *much faster* from *(mini)conda*. It, however, sometimes fails to resolve dependencies correctly.

#### Conda spec files:

- *conda_biobakery3_specfile.txt* : biobakery v3 tools (kneaddata, metaphlan, strainphlan, humann). See [GitHub - biobakery/humann](https://github.com/biobakery/humann) and  [GitHub - biobakery/MetaPhlAn](https://github.com/biobakery/MetaPhlAn) for details
  
  *humann* and *metaphlan* require appropriate databases. *Metaphlan* will attempt to automatically download the latest version if it is not present (or it cannot find it), while humann databases need manual download using `humann_databases `script. *Panphlan* requires pangenomes for all target species, use `panphlan_download_pangenome.py` script to download these.

- *conda_biobakery4_specfile.txt* : biobakery v4 tools. 

- *conda_assemblers_shortbred_specfile.txt* : (Meta)genome assemblers *MEGA-HIT* and *MetaSpades* and biobakery *shortBRED* toolkit. Note: while part of biobakery tools, *shortBRED* is bundled here because it is a reasonably old part of biobakery tools and has compatibility issues with the biobakery version 3+ tools (and thus requires its own environment)

- *conda_BAKTA_specfile.txt* : [BAKTA](https://github.com/oschwengers/bakta) pipeline for bacterial genome annotation (used for annotation of metagenome-assembled-genomes (MAGs)). 
  
  - BAKTA requires a (fairly large) set of annotation databases. These can be downloaded using `bakta_db `script bundled with BAKTA or (if it fails) manually from zenodo (see BAKTA documentation for details)

- *conda_bbduk_specfile.txt* : BBduk is a part of [BBTools](https://jgi.doe.gov/data-and-tools/software-tools/bbtools/) for quality control of raw sequencing data. It requires fasta file with sequencing adapters (see `miscfiles/adapters.fa`, note that non-standard sequencing setup might require adjusting these to experiment-appropriate adapters)

- *conda_GTDBTK_specfile.txt* : [GTDB-Tk toolkit](https://ecogenomics.github.io/GTDBTk/installing/index.html)] for assigning taxonomy to MAGs. It requires download of (~110 GB) database, see GTDB-Tk documentation for details.

- *conda_metawrap_specfile.txt* : [metaWRAP pipeline](https://github.com/bxlab/metaWRAP) is used for metagenomic assembly, binning, and bin refinement. It is a fairly bulky piece of software with many (>100) dependancies and requires a set of databases to run - please consult the its documentation to correctly deploy and test it.

- *conda_SVfinder_specfile.txt* :  [structual variation (SV) finder](https://github.com/segalab/SGVFinder) for metagenomic data. SVfinder is fairly particular about dependances, versions, and compatibilites between dependences and can be tricky to install. It also requires (a fairly large) database of reference genomes and some manual configuration of paths, see documentation at [GitHub - segalab/SGVFinder](https://github.com/segalab/SGVFinder)

- *conda_kraken2_specfile.txt* : [kraken2](https://github.com/DerrickWood/kraken2) - [Bracken](https://github.com/jenniferlu717/Bracken) classifier for metagenomic data. As everything else, it requires its own (fairly large) database(s). 




