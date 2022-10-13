"""run when songdkl is called from the command-line, e.g. '$ songdkl --help'"""
from __future__ import annotations

from . import argparser
from .songdkl import calculate
from .numsyls import numsyls


def main(argv=None):
    parser = argparser.get()
    args = parser.parse_args(argv)

    if args.command == 'calculate':
        score1, score2, n_psds_ref, n_psds_compare = calculate(ref_dir_path=args.ref_dir_path,
                                                               compare_dir_path=args.compare_dir_path,
                                                               k_ref=args.k_ref,
                                                               k_compare=args.k_compare,
                                                               max_wavs=args.max_wavs,
                                                               max_num_psds=args.max_num_psds,
                                                               n_basis=args.n_basis,
                                                               basis=args.basis)
        print(
            f'{args.ref_dir_path}\t{args.compare_dir_path}\t'
            f'{args.k_ref}\t{args.k_compare}\t'
            f'{args.n_basis}\t{score1}\t{score2}\t'
            f'{n_psds_ref}\t{n_psds_compare}'
        )

    elif args.command == 'numsyls':
        n_syls = numsyls(dir_path=args.dir_path)
        print(
            f'{args.dir_path}\t{n_syls}'
        )

    elif args.command is None:
        parser.print_help()


if __name__ == "__main__":
    main()
