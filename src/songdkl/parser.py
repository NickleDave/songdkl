import argparse

COMPUTE_HELP = """
calculate the song divergence between two birds. It is applied as follows:

$ songdkl compute folder_with_songs_from_bird_1 folder_with_songs_from_bird_2 number_of_syllable_calsses_bird_1 number_of_syllable_classes_bird_2

e.g.,  

$ songdkl compute bird_data/y25/ bird_data/y34br6/ 9 10

It expects the songs to be in mono wave format and have a .wav suffix.
The output is a tab delimited string formatted as follows:

foldername_bird1 foldername_bird2 n_syl_classes_bd1 n_syl_classes_bd2 n_basis_set SD_bd1_ref_bd2_song SD_bd2_ref_bd1_comp n_syls_bd1 n_syls_bd2

e.g. 

y25 y32br6 9 10 50 0.039854682578 0.0340690226514 3000 3000

IMPORTANT! In Mets Brainard 2018,  the number of syllables in the tutor song for both 
syllable # values. This is meant to be conservative, basically give the bird learning the 
benefit of the doubt that it actually coppied all of the syllables in the tutor song.  
Empirically, changing these numbers doesn't have much impact on the divergence calculations 
(see the paper)

IMPORTANT! Throughout the paper we calculated PSDs for the raw wave forms of syllables. 
This is the default setting for this script. If your song is contaminated with low 
frequency noise this noise may be incorporated into the model for song potentially 
causing over estimates of song D_KL if there is low frequency noise in the tutor song but 
not the tutee song.  This could occur if the birds were recorded under different 
conditions or in different sound recording boxes.  If you uncomment line 99 below, 
the script will calculate the song D_KL using filtered syllable data. We only advise 
this if you have low frequency noise that is differential between the tutor and tutee 
song and you don't want that noise incorporated into the song D_KL calculations.
"""

NUMSYLS_HELP = """
estimate the number of syllable types in a song.
It fitsfits a series of gaussian mixture models with an 
increasing number of mixtures, and identifies the best number 
of mixtures to describe the data by BIC.
It is applied as follows:
python calc_sylno.py folder_with_bird_songs
e.g. python calc_sylno.py bird_data/y34br6/
It expects the songs to be in mono wave format and have a .wav suffix.
The output is a tab delimited string as follows:
foldername_bird	number_of_syllables
e.g. y34br6 9
"""


def get_parser():
    parser = argparse.ArgumentParser(prog='songdkl',
                                     description='computes a similarity metric for birdsong',
                                     formatter_class=argparse.RawTextHelpFormatter,)

    subparser = parser.add_subparsers()

    compute_subparser = subparser.add_parser('compute', help=COMPUTE_HELP)
    compute_subparser.add_argument('path1', type=str)
    compute_subparser.add_argument('n_syl1', type=int)
    compute_subparser.add_argument('path2', type=str)
    compute_subparser.add_argument('n_syl2', type=int)

    numsyls_subparser = subparser.add_parser('numsyls', help=NUMSYLS_HELP)
    numsyls_subparser.add_argument('path1', type=str)

    return parser
