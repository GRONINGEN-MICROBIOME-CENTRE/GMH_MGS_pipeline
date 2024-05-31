#!/bin/bash
ml Python
echo " Starting parsing of kneaddata reports and sorting them to ./kneaddata_sorted "
mkdir -p kneaddata_sorted
for FLD in */
do
   echo " > looking for kneaddata reports in $FLD "
   cd $FLD
   KN=${FLD/\//}
   if [ -f "${KN}_kneaddata.log" ]; then
      echo "  >> parsing ..."
      python /data/umcg-tifn/rgacesa/dag3_pipeline_3c/utils/knead3parser.py --infile ${KN}_kneaddata.log --outfile ${KN}_kneaddata_reads_stats.csv
      cp ${KN}_kneaddata_reads_stats.csv ../kneaddata_sorted/
   fi
   cd ..
done
echo " Done !"

echo " Merging reports and putting them to ./kneaddata_merged "
mkdir -p kneaddata_merged
python /data/umcg-tifn/rgacesa/dag3_pipeline_3c/utils/mergeKneadReadReports.py --infolder kneaddata_sorted/ --out kneaddata_merged/kneaddata_reports_merged.csv
echo " Done!"
