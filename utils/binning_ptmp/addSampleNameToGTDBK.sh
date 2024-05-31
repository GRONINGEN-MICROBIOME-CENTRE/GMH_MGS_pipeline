#!/bin/bash
for F in */
do
   if [ ${F} != "JOB_OUT/" ] 
   then
      echo ${F}
      cd ${F}/bins_GTDBK
      for i in *.tsv
      do
         mv ${i} ${F/\/}.${i}
      done
      cd ../..
   fi
done
