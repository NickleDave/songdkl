"""
Invokes songdkl.__main__.main when the module is run as a script.
Example: python -m songdkl --help
The same function is run by the script `songdkl-cli` which is installed on the
path by pip, so `$ songdkl-cli --help` would have the same effect (i.e., no need
to type the python -m)
"""

import argparse
import os
from glob import glob

import songdkl

parser = argparse.ArgumentParser(description='main script',
                                 formatter_class=argparse.RawTextHelpFormatter,)
parser.add_argument('-c', '--compute', type=str,
                    help='compute SongD(KL) metric between two birds'
                    '.ini file, by passing the name of that file.\n'
                            '$ songdkl-cli --compute ./bird1_songs/ ./bird2_songs/')
parser.add_argument('-n', '--numsyls', type=str,
                    help='use SongD(KL) metric to estimate number of '
                         'syllables in one bird's song.\n'
                         '$ cnn-bilstm --glob ./config_finches*.ini')
args = parser.parse_args()


def main():
    if sum([bool(arg)
            for arg in [args.compute, args.numsyls,]
            ]) != 1:
        parser.error("Please specify exactly one of the following flags: "
                     "--compute, --numsyls.\n"
                     "Run 'songdkl-cli --help' for an explanation of each.")

    if args.compuyte:
        config_files = glob(args.glob)
    elif args.numsyls:
        with open(args.txt, 'r') as config_list_file:
            config_files = config_list_file.readlines()


if __name__ == "__main__":
    main()
