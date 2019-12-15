"""functions to compute song divergence"""
import sys
import os
from glob import glob

import scipy.spatial as spatial
from matplotlib.pylab import psd
import numpy as np
from sklearn.mixture import GaussianMixture as GMM

from .utils import audio


def norm(a):
    """normalizes a string by its average and syd"""
    a=(np.array(a) - np.average(a)) / np.std(a)
    return a


def _get_all_syls(files):
    """get all syllables from all .wav files in a folder

    Parameters
    ----------
    files : list
        of str, absolute paths to .wav files
        (output of using glob to find all *.wav files in path)

    Returns
    -------
    syls : 
    objss :
    """
    syls = []
    objss = []
    for file in files:
        song = audio.impwav(file)
        if len(song[0]) < 1:
            break
        syls_this_song, objs, frq = audio.getsyls(song)
        objss.append(objs)
        syls.append([frq] + syls_this_song)
    return syls, objss


def convert_syl_to_psd(syls, max_num_psds):
    """convert syllable segments to power spectral density

    Parameters
    ----------
    syls : list
        of ndarray, syllable segments extracted from .wav files
    max_num_psds : int
        maximum number of psds to calculate

    Returns
    -------
    segedpsds
    """
    segedpsds = []
    for x in syls[:max_num_psds]:
        fs = x[0]
        nfft = int(round(2**14/32000.0*fs))
        segstart = int(round(600/(fs/float(nfft))))
        segend = int(round(16000/(fs/float(nfft))))
        psds = [psd(norm(y), NFFT=nfft, Fs=fs) for y in x[1:]]
        spsds = [norm(n[0][segstart:segend]) for n in psds]
        for n in spsds:
            segedpsds.append(n)
    return segedpsds


def calculate(path1, path2, k, k2, max_wavs=120, max_num_psds=10000):
    """calculate songdkl metric

    Parameters
    ----------
    path1 : str
        path to folder with .wav files of songs from bird 1
    path2 : str
        path to folder with .wav files of songs from bird 2
    k : int
        number of syllable classes in song 1
    k2 : int
        number of syllable classes in song 2
    max_wavs : int
        maximum number of wav files to use. Default is 120.
    max_num_psds : int
        maximum number of psds to calculate. Default is 10000

    Returns
    -------
    None

    prints estimate of song D(KL) to stdout
    """
    fils1 = glob(os.path.join(path1, '*.wav'))
    fils2 = glob(os.path.join(path2, '*.wav'))

    fils1 = fils1[:max_wavs]
    fils2 = fils2[:max_wavs]

    syls1, objss1 = _get_all_syls(fils1) 
    syls2, objss2 = _get_all_syls(fils2)

    segedpsds1 = convert_syl_to_psd(syls1, max_num_psds)
    segedpsds2 = convert_syl_to_psd(syls2, max_num_psds)

    # select the first 50 syllables of the reference song as the basis set
    basis_set = segedpsds1[:50] 
    # select a random set of 50 syllablse as the basis set
    # basis_set=[segedpsds1[rnd.randint(0,len(segedpsds1))] for x in range(50)]

    lone = len(segedpsds1)
    ltwo = len(segedpsds2)
    lone_half = int(lone / 2)
    ltwo_half = int(ltwo / 2)

    # calculate distance matrices
    d1 = spatial.distance.cdist(segedpsds1[:lone_half], basis_set, 'sqeuclidean')
    d1_2 = spatial.distance.cdist(segedpsds1[lone_half:lone], basis_set, 'sqeuclidean')
    d2 = spatial.distance.cdist(segedpsds2[:ltwo_half], basis_set, 'sqeuclidean')
    d2_2 = spatial.distance.cdist(segedpsds2[ltwo_half:ltwo], basis_set, 'sqeuclidean')

    mx = np.max([np.max(d1), np.max(d2), np.max(d1_2), np.max(d2_2)])

    # convert to similarity matrices
    s1 = 1 - (d1 / mx)
    s1_2 = 1 - (d1_2 / mx)
    s2 = 1 - (d2 / mx)
    s2_2 = 1 - (d2_2 / mx)

    # estimate GMMs
    mod1 = GMM(n_components=k, max_iter=100000, n_init=5, covariance_type='full')
    mod1.fit(s1)

    mod2 = GMM(n_components=k2, max_iter=100000, n_init=5, covariance_type='full')
    mod2.fit(s2)

    len2 = len(s2)
    len1 = len(d1)

    # calculate likelihoods for held out data
    score1_1 = mod1.score(s1_2)
    score2_1 = mod2.score(s1_2)

    score1_2 = mod1.score(s2_2)
    score2_2 = mod2.score(s2_2)

    len2 = float(len(basis_set))
    len1 = float(len(basis_set))

    # calculate song divergence (DKL estimate)
    score1 = np.log2(np.e) * ((np.mean(score1_1)) - (np.mean(score2_1)))
    score2 = np.log2(np.e) * ((np.mean(score2_2)) - (np.mean(score1_2)))

    score1 = score1 / len1
    score2 = score2 / len2

    # output
    print(path1 + '\t' + path2 + '\t' + str(k) + '\t' + str(k2) 
          + '\t' + str(len2) + '\t' + str(score1) + '\t' + str(score2)
          + '\t' + str(len(segedpsds1)) + '\t' + str(len(segedpsds2)))


if __name__ == '__main__':
    path1 = sys.argv[1]
    path2 = sys.argv[2]
    k = int(sys.argv[3])
    k2 = int(sys.argv[4])
    calculate(path1, path2, k, k2)
