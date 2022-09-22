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

    calculate_subparser = subparser.add_parser('calculate',
                                               help='calculate the song divergence between two birds',
                                               epilog=CALCULATE_EPILOG)
    calculate_subparser.add_argument('ref_dir_path', type=str,
                                     help=('Path to directory with .wav files of songs from bird '
                                           'that should be used as reference.'))
    calculate_subparser.add_argument('compare_dir_path', type=str,
                                     help=('Path to directory with .wav files of songs from bird '
                                           'that should be compared with reference.'))
    calculate_subparser.add_argument('k_ref', type=int,
                                     help=('Number of syllable classes in song of bird used as reference.'
                                           'Also the number of components $k_{ref}$ used for Gaussian Mixture '
                                           'Model fit to the reference distances.'))
    calculate_subparser.add_argument('k_compare', type=int,
                                     help=('Number of syllable classes in song of bird compared with reference.'
                                           'Also the number of components $k_{compare}$ used for Gaussian Mixture '
                                           'Model fit to the comparison distances.'))
    calculate_subparser.add_argument('--max_wavs', type=int, default=120,
                                     help='Maximum number of .wav files to use. Default  is 120.')
    calculate_subparser.add_argument('--max_num_psds', type=str, default=10000,
                                     help='Maximum number of power spectral densities (PSDs) to use. Default is 10000.')
    calculate_subparser.add_argument('--n_basis', type=int, default=50,
                                     help='Number of PSDs to use for the basis set. Default is 50.')
    calculate_subparser.add_argument('--basis', type=str, default='first', choices={'first', 'random'},
                                     help="How to select PSDs for basis set. Either 'first' (default) or 'random'")

    numsyls_subparser = subparser.add_parser('numsyls',
                                             help="estimate the number of syllable types in a song.",
                                             epilog=NUMSYLS_EPILOG)
    numsyls_subparser.add_argument('dir_path', type=str, help='path to directory containing songs from bird')

    return parser
