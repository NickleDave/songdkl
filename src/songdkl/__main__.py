"""run when songdkl is called from the command-line, e.g. '$ songdkl --help'"""
from . import argparser
from .songdkl import calculate
from .numsyls import numsyls


def main():
    parser = argparser.get()
    args = parser.parse_args()

    if args.command == 'calculate':
        calculate(path1=args.path1,
                  path2=args.path2,
                  k=args.n_syl1,
                  k2=args.n_syl2)

    elif args.command == 'numsyls':
        numsyls(path1=args.path)

    elif args.command is None:
        parser.print_help()


if __name__ == "__main__":
    main()
