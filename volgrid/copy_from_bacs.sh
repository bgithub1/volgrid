# helper sh file to copy files created in the barchartacs project in to volgrid
# these are df_iv_final_XX.csv, df_iv_skew_XX.csv and df_cash_futures_XX.csv
#  files for each commodity that are regularly tracted (CB,CL,ES,NG)
# example:
# bash copy_from_bacs.sh # this copies CB CL ES and NG
# bash copy_from_bacs.sh CB NG # this copies just CB and NG

barchartacs_folder='../../barchartacs/barchartacs/temp_folder'
if [[ -z ${1} ]]
then
  commods=('CB' 'CL' 'ES' 'NG')
else
  commods=''
  for i in "$@"
  do
      commods="${commods} ${i}"
  done
  commods=(${commods})
fi

for c in "${commods[@]}"
do 
   cp ${barchartacs_folder}/df_iv_final_${c}.csv ./
   cp ${barchartacs_folder}/df_iv_skew_${c}.csv ./
   cp ${barchartacs_folder}/df_cash_futures_${c}.csv ./
done
