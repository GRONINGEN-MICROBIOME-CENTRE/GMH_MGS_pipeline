# clean junk
cd strainphlan_TxL_out
for i in */
do
   echo $i
   cd $i
   rm *.dmat
   rm *_dmat_Rready.csv
   cd ..
done
cd ..

cd strainphlan_TxN_out
for i in */
do
   echo $i
   cd $i
   rm *.dmat
   rm *_dmat_Rready.csv
   cd ..
done
cd ..

bash ./makeDistMatsTxL.sh
bash ./makeDistMatsTxN.sh
bash ./parseDistMatsTxL.sh
bash ./parseDistMatsTxN.sh

