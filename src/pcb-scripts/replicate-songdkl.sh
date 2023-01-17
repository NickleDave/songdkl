#!/bin/bash

# this script re-runs the script Song_D_KL_calc.py from the Plos Comp Bio paper
# on the Dryad dataset from that paper, running all possible father/unrelated comparisons with sons on that dataset
# it should be run in the environment specified by ./src/pcb-scripts/spec-file.txt

SCRIPT=src/pcb-scripts/Song_D_KL_calc.py
SONG_DATA_ROOT=data/pcb_data/song_data/
OUTPUT=results/replicate-songdkl-pcb-script.txt
TODO_CSV=src/pcb-scripts/replicate-songdkl-todo.csv

while IFS=, read -r refbird comparebird nsyls1 nsyls2; do
  echo "running: $refbird $comparebird $nsyls1 $nsyls2"
  # NOTE that nsyls1 and nsyls2 will be *the same* and are the number of syllables / components
  # specified for the father's song, as the script says was done for the paper.
  # See the docstring of that script for further detail.
  python $SCRIPT $SONG_DATA_ROOT/$refbird/ $SONG_DATA_ROOT/$comparebird/ $nsyls1 $nsyls2 >> $OUTPUT
done < $TODO_CSV
