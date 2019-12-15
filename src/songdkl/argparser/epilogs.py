PARSER_EPILOG = """call commands with --help option for further information, e.g. songdkl calculate --help"""

CALCULATE_EPILOG = """
Example
-------
$ songdkl calculate ~/data/bird_data/y25/ ~/data/bird_data/y34br6/ 9 10

Songs should be in mono wave format and have a .wav suffix.

The output is a tab delimited string formatted as follows:

directory1 directory2 n_syl1 n_syl2 n_basis_set SD_bd1_ref_bd2_song SD_bd2_ref_bd1_comp n_syls_bd1 n_syls_bd2

e.g. 

y25 y32br6 9 10 50 0.039854682578 0.0340690226514 3000 3000

Notes
-----
Throughout the paper we calculated PSDs for the raw wave forms of syllables. 
The default setting for this script. 
If your song is contaminated with low 
frequency noise this noise may be incorporated into the model for song potentially 
causing over estimates of song D_KL if there is low frequency noise in the tutor song but 
not the tutee song.  This could occur if the birds were recorded under different 
conditions or in different sound recording boxes.  If you uncomment line 99 below, 
the script will calculate the song D_KL using filtered syllable data. We only advise 
this if you have low frequency noise that is differential between the tutor and tutee 
song and you don't want that noise incorporated into the song D_KL calculations.

In Mets Brainard 2018, the number of syllables in the tutor song is used for both 
syllable # values. This is meant to be conservative, basically give the bird learning the 
benefit of the doubt that it actually copied all of the syllables in the tutor song.  
Empirically, changing these numbers doesn't have much impact on the divergence calculations 
(see the paper)
"""

NUMSYLS_EPILOG = """
fits a series of gaussian mixture models with an 
increasing number of mixtures, and identifies the best number 
of mixtures to describe the data by BIC.

Songs should be in mono wave format and have a .wav suffix.

The output is a tab delimited string as follows:
foldername_bird	number_of_syllables

e.g. y34br6 9
"""
