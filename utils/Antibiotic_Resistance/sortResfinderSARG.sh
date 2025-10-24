#!/bin/bash

if [ "$#" -ne 1 ]; then
   echo "Error: CL argument (output path) mssing."
   echo "Usage: $0 <argument>"
   exit 1
fi

OUTF=${1}
OUT_SARG=${OUTF}/ARO_SARG
OUT_RGI=${OUTF}/ARO_RGI

mkdir -p ${OUT_SARG}
mkdir -p ${OUT_RGI}

for F in */
do
   echo " >> sorting ${F} "
   SNAME=${F/\//}
   echo ${SNAME}
   if [ -d ${F}/ARO_SARG/ ]; then
      cp ${F}/ARO_SARG/rpkm.type.txt ${OUT_SARG}/${SNAME}_SARG_abtype.rpkm.txt
      cp ${F}/ARO_SARG/rpkm.subtype.txt ${OUT_SARG}/${SNAME}_SARG_subtype.rpkm.txt
      cp ${F}/ARO_SARG/rpkm.gene.txt ${OUT_SARG}/${SNAME}_SARG_gene.rpkm.txt
   fi
   if [ -d ${F}/RGI/ ]; then
      cp ${F}/RGI/* ${OUT_RGI}/
   fi
 
done
