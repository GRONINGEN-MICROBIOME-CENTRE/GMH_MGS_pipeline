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

#library(readr)   # for read_tsv()
library(data.table)
library(vroom)
# Read the list of input files
inFiles <- read.table("__bins_rgi_paths", stringsAsFactors = FALSE)
allTables <- list()
cnt <- 1
for (fl in inFiles$V1[cnt:length(inFiles$V1)]) {
  message(paste0(" > parsing cnt=",cnt," : ", fl))
  # Try reading each file, skip on error
  chk <- tryCatch(
    {
      #read_tsv(fl, col_types = cols())  # faster than read.table
      inDF <- read.table(fl,sep='\t',header=T,quote='"')
      #fread(fl, sep = "\t", header = T, fill = F, showProgress = FALSE, nThread = 4) #getDTthreads())
      #vroom(fl, delim = "\t", col_types = cols(.default = col_guess()), progress = FALSE)
      # Add identifiers
      inDF$Bin.ID <- gsub("\\.rgi_out_basic_wild\\.txt$", "", basename(fl))
      inDF$Sample <- gsub("\\.bin\\.[0-9]+", "", inDF$Bin.ID)
      allTables[[cnt]] <- inDF
      cnt <- cnt + 1 
      #return(1)
    },
    error = function(e) {
      message("   ! Failed to read ", fl, ": ", conditionMessage(e))
      cnt <- cnt + 1 
      #return(NULL)  # skip this file
    }
  )
}
# Combine all results into one data.frame
masterTbl <- do.call(rbind, allTables)
# Save as CSV
write.csv(masterTbl, "bins_RGI_results.csv", row.names = FALSE)
saveRDS(masterTbl,"bins_RGI_results.RDS")
# cleanup
masterTbl$CARD_Protein_Sequence <- NULL
masterTbl$Predicted_Protein <- NULL
masterTbl$Predicted_DNA <- NULL

write.csv(masterTbl, "bins_RGI_results_cleaned.csv", row.names = FALSE)
saveRDS(masterTbl,"bins_RGI_results_cleaned.RDS")
