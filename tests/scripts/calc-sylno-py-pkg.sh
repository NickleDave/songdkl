# this script runs the `songdkl` package command `numsyls` on the Bengalese finch song dataset from the PLOS Comp Bio paper
FIRST_N=$1

PY_PKG_SYL_COUNTS_FILE=tests/data-for-tests/generated/py-pkg-syl-counts.txt

rm -f $PY_PKG_SYL_COUNTS_FILE
touch $PY_PKG_SYL_COUNTS_FILE

BIRD_FOLDERS=(./data/pcb_data/song_data/*/)
for BIRD_FOLDER in ${BIRD_FOLDERS[@]:1:$FIRST_N};do
  echo running songdkl for $BIRD_FOLDER
  songdkl numsyls $BIRD_FOLDER >> $PY_PKG_SYL_COUNTS_FILE
done
