# ==========================================
# COLLECTOR SCRIPT
# ==========================================
# collects samples from ${1} to current folder
# > preserves structure of folders
# > does not collect clean reads and other big stuff
for F in ${1}/*/
do 
FF=${F: : -1}
SNAME=${FF##*/}
echo "copying ${FF} -> ${SNAME}"
mkdir ${SNAME}
cp -r ${FF}/assembly_megahit ${SNAME}
cp -r ${FF}/bins_checkM ${SNAME}
cp -r ${FF}/bins_GTDBK ${SNAME}
cp -r ${FF}/bins_metawrap_refined ${SNAME}
cp -r ${FF}/bins_metawrap_refined_BAKTA ${SNAME}
cp -r ${FF}/bins_metawrap_refined_BAKTA_taxsorted ${SNAME}
cp -r ${FF}/metaphlan*/ ${SNAME}
cp -r ${FF}/humann*/ ${SNAME}
cp -r ${FF}/Panphlan ${SNAME}
done
