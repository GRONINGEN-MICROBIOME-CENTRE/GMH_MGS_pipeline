# ======================================================
# RGI MAG run collector
# ======================================================
# > first run:
#   find . -name "*.rgi_out_basic_wild.txt" > __bins_rgi_paths
# > then run this from sorted data folder (e.g., /scratch/hb-tifn/Metagenome_data/2023_08_LLD_sorted)
# - goes through all RGI results, collects them into one table, also makes sure MAG IDs are correct for linking with bin_stats
#
#

# Get all files ending with ".rgi_out_basic_wild.txt" in the current directory (recursively)
#files <- list.files(path = ".", pattern = "\\.rgi_out_basic_wild\\.txt$", full.names = TRUE, recursive = TRUE)

library(readr)

inFiles <- read.table('__bins_rgi_paths')

# Iterate over each file
allTables <- list()
cnt <- 0
for (fl in inFiles$V1) {
   print(paste0(' > parsing ',fl))
   cnt <- cnt + 1
   inDF <- read.table(fl,sep='\t',header=T,quote='"',fill=F)
   inDF$Bin.ID <- gsub('.rgi_out_basic_wild.txt','',basename(fl))
   inDF$Sample <- gsub('.bin.[1234567890]+','',inDF$Bin.ID)
   allTables[[cnt]] <- inDF
}
masterTbl <- do.call(rbind,allTables)
write.table('bins_RGI_results.csv',sep=',',row.names=F)
