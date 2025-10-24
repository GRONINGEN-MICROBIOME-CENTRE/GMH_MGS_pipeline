#!/bin/bash
if [ -f "__missing_RGI" ]
then
   rm __missing_RGI
fi
for SMPL in */
do
   if [[ "${SMPL}" != "JOB_OUT/" ]]; then
      SN=${SMPL}
      SN=${SN/\//}
      echo "examining ${SMPL}"
      # check what is done
      for SAMPLE in `find ${SMPL} -maxdepth 2 -name "*[1234567890].faa"`
      do
	 FN=$(basename "${SAMPLE}")
	 OUT_FILE=${SMPL}/RGI/${FN/.faa/}.rgi_out_basic_wild.txt
	 # run metagenomic classifier
	 #echo ${OUT_FILE}
	 if [ -f "$OUT_FILE" ] && [ $(stat -c%s "${OUT_FILE}") -gt 100 ]
	 then
	    :
         else
	    echo "${SAMPLE} not done!"
	    echo "${SAMPLE}" >> __missing_RGI
	 fi
   	 done
   fi
done

