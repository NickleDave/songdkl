"""
Invokes songdkl.__main__.main when the module is run as a script.
Example: python -m songdkl --help
The same function is run by the script `songdkl-cli` which is installed on the
path by pip, so `$ songdkl-cli --help` would have the same effect (i.e., no need
to type the python -m)
"""
from .parser import get_parser
from .songdkl import compute_songdkl
from .numsyls import numsyls


def main():
    parser = get_parser()
    args = parser.parse_args()

    if args.compute:
        compute_songdkl(path1=args.compute.path1,
                        path2=args.compute.path2,
                        k=args.compute.nsyls1,
                        k2=args.compute.nsyls2)

    elif args.numsyls:
        numsyls()


if __name__ == "__main__":
    main()
