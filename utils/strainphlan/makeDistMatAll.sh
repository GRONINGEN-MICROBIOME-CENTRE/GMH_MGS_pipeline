#!/bin/bash
echo "maker of distance matrices"
echo " > goes through each folder and attempts to make distmat"

echo " > loading EMBOSS"
ml EMBOSS
for F in */
do
   SN=${F/\/}
   echo ${SN}
   FM=${SN}.StrainPhlAn4_concatenated.aln
   echo "  >> making distmat"
   echo "distmat -sequence ${SN}/${FM} -nucmethod 2 -outfile ${SN}/${SN}.dmat"
   distmat -sequence ${SN}/${FM} -nucmethod 2 -outfile ${SN}/${SN}.dmat
done
