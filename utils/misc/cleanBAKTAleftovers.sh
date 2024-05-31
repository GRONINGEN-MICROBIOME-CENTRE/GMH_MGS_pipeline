#!/bin/bash

# go over folders, clean BAKTA unnecessary files

for i in */
do 
   cd ${i}
   rm bins_metawrap_refined_BAKTA_1.7/*.fa
   for j in bins_metawrap_refined_BAKTA_1.7/*/
   do 
      echo ${i}/${j}
      rm ${i}/${j}/*.embl; rm ${i}/${j}/*.png; rm ${i}/${j}/*.jpg; rm ${i}/${j}/*.gbff; rm ${i}/${j}/*.json; rm ${i}/${j}/*.log; rm ${i}/${j}/*.tsv
   done
   cd ..
done
