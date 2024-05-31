#!/bin/bash

# ====================================================
# cleans all temporary files for finished pipeline run
# ======================================================
while read l
do 
   echo " >> cleaning intermediate data for ${l}"
   # logs
   rm ${l}/*.log
   # clean reads 
   rm -r ${l}/clean_reads/
   # raw reads
   rm ${l}*.fq.gz
   # non-refined bins
   rm -r ${l}/bins_metawrap/
   # assembly logs
   rm ${l}/assembly_megahit/*_log.log
   # clean GTDBK unnecessary stuff
   rm ${l}/bins_GTDBK/*.gtdbk.ar53.markers_summary.tsv
   rm ${l}/bins_GTDBK/*.gtdbk.failed_genomes.tsv
   rm ${l}/bins_GTDBK/*.gtdbk.translation_table_summary.tsv
   # metaphlan4 intermediate files
   rm ${l}/metaphlan4/*_metaphlan4_bowtie2.txt
   rm ${l}/metaphlan4/*_metaphlan4.sam.bz2
   # QC (no point in running these anyway)
   rm -r ${l}/qc_postclean/
   rm -r ${l}/qc_preclean/
done < _done_hum36.tsv
