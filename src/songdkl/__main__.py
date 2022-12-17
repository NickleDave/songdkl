"""run when songdkl is called from the command-line, e.g. '$ songdkl --help'"""
from __future__ import annotations
import dataclasses
import logging

from . import argparser
from .constants import DefaultGaussianMixtureKwargs
from .numsyls import numsyls_from_path
from .prep import prep_and_save
from .songdkl import calculate_from_path


from .logging import config_logging_for_cli, log_version


logger = logging.getLogger(__name__)


def main(argv=None):
    parser = argparser.get()
    args = parser.parse_args(argv)

    config_logging_for_cli()
    log_version(logger)

    if args.command == 'prep':
        # handle edge case where user passes only one output dir,
        # but argparse wraps in list because nargs='+'.
        # We don't want `prep_and_save` responsible for catching it since this is a cli thing.
        if args.output_dir_path is not None:
            if len(args.output_dir_path) == 1:
                output_dir_path = args.output_dir_path[0]
            else:
                output_dir_path = args.output_dir_path
        else:
            output_dir_path = None
        prep_and_save(dir_path=args.dir_path, output_dir_path=output_dir_path,
                      max_wavs=args.max_wavs, max_syllables=args.max_syllables)

    if args.command in ('calculate', 'numsyls'):
        gmm_kwargs = dataclasses.asdict(DefaultGaussianMixtureKwargs())
        for arg in ('max_iter', 'n_init', 'covariance_type', 'random_state', 'reg_covar'):
            gmm_kwargs.update({arg: getattr(args, arg)})

    if args.command == 'calculate':
        score1, score2, n_psds_ref, n_psds_compare = calculate_from_path(ref_path=args.ref_path,
                                                                         compare_path=args.compare_path,
                                                                         k_ref=args.k_ref,
                                                                         k_compare=args.k_compare,
                                                                         max_wavs=args.max_wavs,
                                                                         max_syllables=args.max_syllables,
                                                                         psds_per_syl=args.psds_per_syl,
                                                                         n_basis=args.n_basis,
                                                                         basis=args.basis,
                                                                         gmm_kwargs=gmm_kwargs)
        print(
            f'{args.ref_path}\t{args.compare_path}\t'
            f'{args.k_ref}\t{args.k_compare}\t'
            f'{args.n_basis}\t{score1}\t{score2}\t'
            f'{n_psds_ref}\t{n_psds_compare}'
        )

    elif args.command == 'numsyls':
        n_syls = numsyls_from_path(ref_path=args.ref_path,
                                   max_wavs=args.max_wavs,
                                   max_syllables=args.max_syllables,
                                   n_basis=args.n_basis,
                                   basis=args.basis,
                                   min_components=args.min_components,
                                   max_components=args.max_components,
                                   psds_per_syl=args.psds_per_syl,
                                   n_splits=args.n_splits,
                                   gmm_kwargs=gmm_kwargs,
                                   )
        print(
            f'{args.ref_path}\t{n_syls}'
        )

    elif args.command is None:
        parser.print_help()


if __name__ == "__main__":
    main()
