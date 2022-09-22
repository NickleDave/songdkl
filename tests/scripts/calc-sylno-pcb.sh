FIRST_N=$1

PCB_SCRIPT_SYL_COUNTS_FILE=tests/data-for-tests/generated/pcb-script-syl-counts.txt

rm -f $PCB_SCRIPT_SYL_COUNTS_FILE
touch $PCB_SCRIPT_SYL_COUNTS_FILE

BIRD_FOLDERS=(./tests/data-for-tests/song_data/*/)
for BIRD_FOLDER in ${BIRD_FOLDERS[@]:1:$FIRST_N};do
  echo running script for $BIRD_FOLDER
  conda run -n songdkl-pcb python ./src/pcb-scripts/calc_sylno.py $BIRD_FOLDER >> $PCB_SCRIPT_SYL_COUNTS_FILE
done
