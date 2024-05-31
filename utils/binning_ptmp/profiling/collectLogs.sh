#!/bin/bash
# ======================================
# log collector for binning tests
# ======================================

# check CL:
# <1 : input folder>
# <2 : output folder>

if [ "$#" -ne 2 ]; then
    echo "Use CL[1] = input folder, CL[2] = output folder"
    exit
fi
# SETUP
PROFILER=/data/umcg-tifn/rgacesa/dag3_pipeline_3c/utils/jobprofiler.py

echo "> collecting binning results from ${1} into ${2}"
# > make folders for results
mkdir -p ${2}/prep
mkdir -p ${2}/checkM
mkdir -p ${2}/binning_metawrap
mkdir -p ${2}/refine_metawrap
mkdir -p ${2}/reassembly_metawrap
mkdir -p ${2}/refine_metawrap_v2
mkdir -p ${2}/refine_DAS
mkdir -p ${2}/refine_DAS_v2
mkdir -p ${2}/profile_GTDBK
mkdir -p ${2}/binning_semibin
mkdir -p ${2}/binning_metacoag
mkdir -p ${2}/binning_graphbin
mkdir -p ${2}/binning_vamb
mkdir -p ${2}/quantify_metawrap
mkdir -p ${2}/metaphlan4
mkdir -p ${2}/knead
mkdir -p ${2}/init
mkdir -p ${2}/kraken
mkdir -p ${2}/megahit

# > collect profiling jobs
cp ${1}/JOB_OUT/__*_m4.out ${2}/metaphlan4
cp ${1}/JOB_OUT/__*_kn.out ${2}/knead
cp ${1}/JOB_OUT/__*_i.out ${2}/init
cp ${1}/JOB_OUT/__*_aK2.out ${2}/kraken2
cp ${1}/JOB_OUT/__*_aMH.out ${2}/megahit

# > collect assembly binning logs
for F in ${1}/*/
do
   SNAME=${F%/}
   SNAME=${SNAME##*/}
   if [[ "$SNAME" != "JOB_OUT" ]]; then 
      echo " >> collecting ${F} " 
      # > clean junk
      #rm ${F}/JOB_OUT/*__JOB_OUT*
      # > binning prep
      cp ${F}/JOB_OUT/__util_prepforbinning_MEGAHIT.out ${2}/prep/__${SNAME}_prep.out
      # > checkM
      cp ${F}/JOB_OUT/__binning_CheckM_all.out ${2}/checkM/__${SNAME}_checkM.out
      # > metawrap binning
      cp ${F}/JOB_OUT/__metawrap_binning.out ${2}/binning_metawrap/__${SNAME}_mwBin.out
      # > metawrap refining
      cp ${F}/JOB_OUT/__metawrap_bin_refine.out ${2}/refine_metawrap/__${SNAME}_mwRef.out
      # > metawrap reassembly
      cp ${F}/JOB_OUT/__metawrap_reassembly.out ${2}/reassembly_metawrap/__${SNAME}_reAssembly.out
      # > metawrap refining [V2]
      cp ${F}/JOB_OUT/__metawrap_bin_refine2.out ${2}/refine_metawrap_v2/__${SNAME}_mwRef2.out
      # > DAS refining [v1]
      cp ${F}/JOB_OUT/__binning_DAS_all.out ${2}/refine_DAS/__${SNAME}_DASRef.out
      cp ${F}/JOB_OUT/__binning_DAS.out ${2}/refine_DAS/__${SNAME}_DASRef.out
      # > DAS refining [v2]
      cp ${F}/JOB_OUT/__binning_DAS_v2.out ${2}/refine_DAS_v2/__${SNAME}_DASRef2.out
      # > GTDBK
      cp ${F}/JOB_OUT/__gtdbk_allbinners.out ${2}/profile_GTDBK/__${SNAME}_GTDBK.out
      # > binning semibin
      cp ${F}/JOB_OUT/__binning_semibin.out ${2}/binning_semibin/__${SNAME}_semibin.out
      # > binning metacoag
      cp ${F}/JOB_OUT/__binning_MetaCOAG.out ${2}/binning_metacoag/__${SNAME}_metacoag.out
      # > binning graphbin
      cp ${F}/JOB_OUT/__binning_GraphBin.out ${2}/binning_graphbin/__${SNAME}_graphbin.out
      # > binning vamb
      cp ${F}/JOB_OUT/__binning_VAMB.out ${2}/binning_vamb/__${SNAME}_vamb.out
      # > binning quantification
      cp ${F}/JOB_OUT/__metawrap_quantify_binab.out ${2}/quantify_metawrap/__${SNAME}_quantify.out 
   fi
done
echo "> COLLECTION DONE!"
echo "> PARSING JOB FILES"
echo " >> prep"
python ${PROFILER} -I ${2}/prep --ignorefail Y --debug N --verbose N  > ${2}/_jobstats_binprep.txt
echo " >> checkM"
python ${PROFILER} -I ${2}/checkM --ignorefail Y --debug N --verbose N  > ${2}/_jobstats_checkM.txt
echo " >> binning - metawrap"
python ${PROFILER} -I ${2}/binning_metawrap --ignorefail Y --debug N --verbose N  > ${2}/_jobstats_binning_metawrap.txt
echo " >> refining - metawrap"
python ${PROFILER} -I ${2}/refine_metawrap --ignorefail Y --debug N --verbose N  > ${2}/_jobstats_refining_metawrap.txt
echo " >> reassembly - metawrap"
python ${PROFILER} -I ${2}/reassembly_metawrap --ignorefail Y --debug N --verbose N  > ${2}/_jobstats_reassembly_metawrap.txt
echo " >> refining - metawrap [v2]"
python ${PROFILER} -I ${2}/refine_metawrap_v2 --ignorefail Y --debug N --verbose N  > ${2}/_jobstats_refining_metawrap_v2.txt
echo " >> refining - DAS"
python ${PROFILER} -I ${2}/refine_DAS --ignorefail Y --debug N --verbose N  > ${2}/_jobstats_refining_DAS.txt
echo " >> refining - DAS [v2]"
python ${PROFILER} -I ${2}/refine_DAS_v2 --ignorefail Y --debug N --verbose N  > ${2}/_jobstats_refining_DAS_v2.txt
echo " >> profiling - GTDBK"
python ${PROFILER} -I ${2}/profile_GTDBK --ignorefail Y --debug N --verbose N  > ${2}/_jobstats_GTDBK.txt
echo " >> binning - semibin"
python ${PROFILER} -I ${2}/binning_semibin --ignorefail Y --debug N --verbose N  > ${2}/_jobstats_binning_semibin.txt
echo " >> binning - metacoag"
python ${PROFILER} -I ${2}/binning_metacoag --ignorefail Y --debug N --verbose N  > ${2}/_jobstats_binning_metacoag.txt
echo " >> binning - graphbin"
python ${PROFILER} -I ${2}/binning_graphbin --ignorefail Y --debug N --verbose N  > ${2}/_jobstats_binning_graphbin.txt
echo " >> binning - vamb"
python ${PROFILER} -I ${2}/binning_vamb --ignorefail Y --debug N --verbose N  > ${2}/_jobstats_binning_vamb.txt
echo " >> quantification [metawrap]"
python ${PROFILER} -I ${2}/quantify_metawrap --ignorefail Y --debug N --verbose N  > ${2}/_jobstats_quantification_metawrap.txt
# basic pipeline jobs
echo " >> metaphlan4"
python ${PROFILER} -I ${2}/metaphlan4 --ignorefail Y --debug N --verbose N  > ${2}/_jobstats_p_metaphlan4.txt
echo " >> job init"
python ${PROFILER} -I ${2}/init --ignorefail Y --debug N --verbose N  > ${2}/_jobstats_p_init.txt
echo " >> kneaddata"
python ${PROFILER} -I ${2}/knead --ignorefail Y --debug N --verbose N  > ${2}/_jobstats_p_knead.txt
echo " >> kraken2"
python ${PROFILER} -I ${2}/kraken2 --ignorefail Y --debug N --verbose N  > ${2}/_jobstats_p_kraken2.txt
echo " >> megahit"
python ${PROFILER} -I ${2}/megahit --ignorefail Y --debug N --verbose N  > ${2}/_jobstats_p_megahit.txt
