#!/bin/bash
smpl=$1
echo " > parsing kneaddata logs"
echo -e "SID\tRaw_Reads_NR_1\tRaw_Reads_NR_2\tClean_Reads_NR_1\tClean_Reads_NR_2\tHuman_reads_NR_1\tHuman_reads_NR_2" > ${smpl}/${smpl}_kneaddata_reads_stats.txt
echo ${smpl} > ${smpl}/${smpl}_tmp
cat ${smpl}/${smpl}_kneaddata.log | grep "Initial number of reads" | awk -F ":" '{print $7}' >> ${smpl}/${smpl}_tmp
cat ${smpl}/${smpl}_kneaddata.log | grep "INFO: Total reads after removing those found in reference database" | awk -F ":" '{print $5}' >> ${smpl}/${smpl}_tmp
cat ${smpl}/${smpl}_kneaddata.log | grep "INFO: Total contaminate sequences in file" | awk -F ":" '{print $5}' >> ${smpl}/${smpl}_tmp
cat ${smpl}/${smpl}_tmp | paste -s >> ${smpl}/${smpl}_tmp2
paste -d "\n" ${smpl}/${smpl}_tmp2 >> ${smpl}/${smpl}_kneaddata_reads_stats.txt
rm ${smpl}/${smpl}_tmp
rm ${smpl}/${smpl}_tmp2
