import argparse

from .epilogs import PARSER_EPILOG, CALCULATE_EPILOG, NUMSYLS_EPILOG


def get():
    """creates argparser, used by __main__.main function"""
    parser = argparse.ArgumentParser(description='a similarity metric for birdsong',
                                     formatter_class=argparse.RawTextHelpFormatter,
                                     epilog=PARSER_EPILOG)

    subparser = parser.add_subparsers(title='commands',
                                      description='''valid commands when calling songdkl from the command line,
                                      e.g., "songdkl calculate"''',
                                      dest='command',)

    calculate_subparser = subparser.add_parser('calculate',
                                               help='calculate the song divergence between two birds',
                                               epilog=CALCULATE_EPILOG)
    calculate_subparser.add_argument('path1', type=str,
                                     help='path to directory containing songs from bird 1')
    calculate_subparser.add_argument('path2', type=str,
                                     help='path to directory containing songs from bird 1')
    calculate_subparser.add_argument('n_syl1', type=int,
                                     help='number of syllable_classes for bird 1')
    calculate_subparser.add_argument('n_syl2', type=int,
                                     help='number of syllable_classes for bird 2')

    numsyls_subparser = subparser.add_parser('numsyls',
                                             help="estimate the number of syllable types in a song.",
                                             epilog=NUMSYLS_EPILOG)
    numsyls_subparser.add_argument('path', type=str, help='path to directory containing songs from bird')

    return parser
