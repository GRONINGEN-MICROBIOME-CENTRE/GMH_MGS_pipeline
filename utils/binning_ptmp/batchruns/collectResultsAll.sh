#!/bin/bash
# 
# collects binning results from $1 and puts them in $2
#
# check CL:

if [ "$#" -ne 2 ]; then
    echo "Use CL[1] = input folder, CL[2] = output folder"
    exit
fi

echo "> collecting binning results from ${1} into ${2}"
mkdir -p ${2}
for F in ${1}/*/
do
  echo " >> collecting ${F}"
  #echo ${F}
  FF=$(basename $F)
  #echo $FF
  TF=${2}/${FF}
  mkdir -p ${TF}
  cp -r ${F}/bins_checkM ${TF}
  cp -r ${F}/bins_GTDBK ${TF}
  cp -r ${F}/bins_metawrap_refined ${TF}
  cp -r ${F}/assembly* ${TF}
done

