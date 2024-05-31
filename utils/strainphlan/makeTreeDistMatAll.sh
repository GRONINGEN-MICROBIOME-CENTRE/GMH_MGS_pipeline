#!/bin/bash
TREEDIST=/scratch/hb-tifn/tools/pyphlan/tree_pairwisedists.py

echo "maker of distance matrices"
echo " > goes through each folder and attempts to make tree-based distmat"
echo " > loading conda"
ml Anaconda3
conda activate /scratch/hb-tifn/condas/conda_biobakery3.1
for F in */
do
   SN=${F/\/}
   echo ${SN}
   FM=RAxML_bestTree.${SN}.StrainPhlAn4.tre
   echo "  >> making distmat for ${SN}/${FM}"
   python ${TREEDIST} -n -m ${SN}/${FM} ${SN}/${SN}_tree.dmat
done
