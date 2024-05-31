#!/bin/bash
echo "maker of distance matrices"
echo " > goes through each folder and attempts to make distmat"
META=${1}
ANNOTATOR=/data/umcg-tifn/rgacesa/dag3_pipeline_3c/utils/strainphlan/annotateStrainPhlanResultsTree.py
ADDN=Y
#-I INPUT [-O OUT] -M META [--addn ADDN]
for F in */
do
   SN=${F/\/}
   echo ${SN}
   FM=RAxML_result.${SN}.StrainPhlAn4.tre
   echo "  >> annotating ${FM}"
   echo python ${ANNOTATOR} -I ${SN}/${FM} -O ${SN}/${FM/tre/annot\.tre} -M $META --addn ${ADDN}
   python ${ANNOTATOR} -I ${SN}/${FM} -O ${SN}/${FM/tre/annot\.tre} -M $META --addn ${ADDN}
done
