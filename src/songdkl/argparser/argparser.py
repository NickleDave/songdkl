import argparse

from .epilogs import PARSER_EPILOG, CALCULATE_EPILOG, NUMSYLS_EPILOG


def get():
    """creates argparser, used by __main__.main function"""
    parser = argparse.ArgumentParser(prog='songdkl',
                                     description='a similarity metric for birdsong',
                                     formatter_class=argparse.RawTextHelpFormatter,
                                     epilog=PARSER_EPILOG)

    subparser = parser.add_subparsers(title='commands',
                                      description='''valid commands when calling songdkl from the command line,
                                      e.g., "songdkl calculate"''',
                                      dest='command',)

    # ---- prep command ----
    prep_subparser = subparser.add_parser('prep',
                                          help=('Prepare datasets. Executes `prep_and_save` function, saving resulting '
                                                'array in compressed file with extension `.songdkl.zarr`.')
                                          )
    prep_subparser.add_argument('dir_path', metavar='dir-path', nargs='+',
                                help=('Path(s) to directory containing songs from bird(s).'
                                      'If more than one path, should be a space separated list.')
                                )
    prep_subparser.add_argument('--output-dir-path', nargs='+',
                                help=('Path(s) to directory where arrays should be saved.'
                                      'If more than one path, should be a space separated list.')
                                )
    prep_subparser.add_argument('--max-wavs', type=int, default=120,
                                help='Maximum number of .wav files to use per directory. Default  is 120.')
    prep_subparser.add_argument('--max-num-psds', type=str, default=10000,
                                help=('Maximum number of power spectral densities (PSDs) to use per directory. '
                                      'Default is 10000.')
                                )

    # ---- calculate command ----
    calculate_subparser = subparser.add_parser('calculate',
                                               help='calculate the song divergence between two birds',
                                               epilog=CALCULATE_EPILOG)
    calculate_subparser.add_argument('ref_path', metavar='ref-path', type=str,
                                     help=('Path to data from bird that should be used as reference. '
                                           'Either a path to a directory with .wav files of songs, '
                                           'or a path to a .songdkl.zarr file generated by songdkl prep'))
    calculate_subparser.add_argument('compare_path', metavar='compare-path', type=str,
                                     help=('Path to data from bird that should be compared with reference.'
                                           'Either a path to a directory with .wav files of songs, '
                                           'or a path to a .songdkl.zarr file generated by songdkl prep'
                                           ))
    calculate_subparser.add_argument('k_ref', metavar='k-ref', type=int,
                                     help=('Number of syllable classes in song of bird used as reference.'
                                           'Also the number of components $k_{ref}$ used for Gaussian Mixture '
                                           'Model fit to the reference distances.'))
    calculate_subparser.add_argument('k_compare', metavar='k-compare', type=int,
                                     help=('Number of syllable classes in song of bird compared with reference.'
                                           'Also the number of components $k_{compare}$ used for Gaussian Mixture '
                                           'Model fit to the comparison distances.'))
    calculate_subparser.add_argument('--max-wavs', type=int, default=120,
                                     help='Maximum number of .wav files to use. Default  is 120.')
    calculate_subparser.add_argument('--max-num-psds', type=str, default=10000,
                                     help='Maximum number of power spectral densities (PSDs) to use. Default is 10000.')
    calculate_subparser.add_argument('--n-basis', type=int, default=50,
                                     help='Number of PSDs to use for the basis set. Default is 50.')
    calculate_subparser.add_argument('--basis', type=str, default='first', choices={'first', 'random'},
                                     help="How to select PSDs for basis set. Either 'first' (default) or 'random'")

    # ---- numsyls command ----
    numsyls_subparser = subparser.add_parser('numsyls',
                                             help="estimate the number of syllable types in a song.",
                                             epilog=NUMSYLS_EPILOG)
    numsyls_subparser.add_argument('ref_path', metavar='ref-path',
                                   type=str,
                                   help=('Path to data from bird that should be used as reference. '
                                           'Either a path to a directory with .wav files of songs, '
                                           'or a path to a .songdkl.zarr file generated by songdkl prep'))
    numsyls_subparser.add_argument('--max-wavs', type=int, default=120,
                                   help='Maximum number of .wav files to use. Default  is 120.')
    numsyls_subparser.add_argument('--max-num-psds', type=str, default=10000,
                                   help='Maximum number of power spectral densities (PSDs) to use. Default is 10000.')
    numsyls_subparser.add_argument('--n-basis', type=int, default=50,
                                   help='Number of PSDs to use for the basis set. Default is 50.')
    numsyls_subparser.add_argument('--basis', type=str, default='first', choices={'first', 'random'},
                                   help="How to select PSDs for basis set. Either 'first' (default) or 'random'")
    numsyls_subparser.add_argument('--min-components', type=int, default=2,
                                   help='Minimum number of components to fit with. Default is 2.')
    numsyls_subparser.add_argument('--max-components', type=int, default=22,
                                   help='Maximum number of components to fit with. Default is 22.')
    numsyls_subparser.add_argument('--n-splits', type=int, default=1,
                                   help=("Number of splits to use when estimating components. "
                                         "Default is 1, in which case ``psds_ref`` is not split."
                                         "If sufficient data are available,"
                                         "a good rule of thumb is to use 3 splits.")
                                   )

    for subparser in (calculate_subparser, numsyls_subparser):
        # add args for GaussianMixture that both subparsers use
        subparser.add_argument('--max-iter', type=int, default=100000,
                               help=('The number of EM iterations to perform when fitting GaussianMixture. '
                                     'Default is 100000.'))
        subparser.add_argument('--n-init', type=int, default=5,
                               help=("The number of initializations to perform when fitting GaussianMixture. "
                                     "The best results are kept. Default is 5."))
        subparser.add_argument('--covariance-type', type=str, default='full',
                               choices={'full', 'tied', 'diag', 'spherical'},
                               help=("String describing the type of covariance parameters to use"
                                     "when fitting GaussianMixture. Default is 'full'."))
        subparser.add_argument('--random-state', type=int, default=42,
                               help="Int seed to random number generator. Default is 42.")
        subparser.add_argument('--reg-covar', type=float, default=1e-6,
                               help=("Non-negative regularization added to the diagonal of covariance "
                                     "when fitting GaussianMixture. Default is 1e-6."))
    return parser
