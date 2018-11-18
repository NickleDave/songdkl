"""
Invokes songdkl.__main__.main when the module is run as a script.
Example: python -m songdkl --help
The same function is run by the script `songdkl-cli` which is installed on the
path by pip, so `$ songdkl-cli --help` would have the same effect (i.e., no need
to type the python -m)
"""
import argparse
import songdkl

def parse_compute_args(string):
    """"convert arg from str to int, if it doesn't raise an error.
    gets applied to every arg for --compute"""
    try:
        string = int(string)
        return string
    except ValueError:
        return string


def parse_songdkl_args():
    parser = argparse.ArgumentParser(description='main script',
                                     formatter_class=argparse.RawTextHelpFormatter,)
    parser.add_argument('-c', '--compute', nargs=4, type=parse_compute_args,
                        help='compute SongD(KL) metric between two birds'
                             '.ini file, by passing the name of that file.\n'
                             '$ songdkl-cli --compute ./bird1_songs/ ./bird2_songs/')
    parser.add_argument('-n', '--numsyls', type=str,
                        help='use SongD(KL) metric to estimate number of '
                             'syllables in one bird\'s song.\n'
                             '$ songdkl-cli --numsyls ./bird1_songs/')
    return parser.parse_args()


def main():
    args = parse_songdkl_args()
    if sum([bool(arg)
            for arg in [args.compute, args.numsyls,]
            ]) != 1:
        parser.error("Please specify exactly one of the following flags: "
                     "--compute, --numsyls.\n"
                     "Run 'songdkl-cli --help' for an explanation of each.")

    if args.compute:
        songdkl.compute_songdkl(path1=args.compute[0],
                                path2=args.compute[1],
                                k=args.compute[2],
                                k2=args.compute[3])
    elif args.numsyls:
        songdkl.numsyls()

if __name__ == "__main__":
    main()
