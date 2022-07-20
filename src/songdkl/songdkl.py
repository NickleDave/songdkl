"""functions to compute song divergence"""
import pathlib
from typing import Tuple, Union, Any

import scipy.spatial as spatial
from matplotlib.pylab import psd
import numpy as np
from sklearn.mixture import GaussianMixture

from . import audio


def norm(a):
    """normalizes a string by its average and syd"""
    a=(np.array(a) - np.average(a)) / np.std(a)
    return a


def get_all_syls(wav_paths: list[str]):
    """Get all syllables from a list of .wav files

    Parameters
    ----------
    wav_paths : list
        of str, absolute paths to .wav files

    Returns
    -------
    syls : list
        of lists, same length as ``wav_paths``,
        where first element in each list
        is sampling rate, and the rest of the list
        is syllables
    slices : list
        of lists, same length as ``wav_paths``,
        numpy.slice objects used to
        find syllables.
    """
    syls = []
    slices = []
    for wav_path in wav_paths:
        rate, data = audio.load_wav(wav_path)
        syls_this_song, slices_this_song = audio.getsyls(rate, data)
        slices.append(slices_this_song)
        syls.append([rate] + syls_this_song)
    return syls, slices


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


def calculate(ref_dir_path: str,
              compare_dir_path: str,
              k_ref: int,
              k_compare: int,
              max_wavs: int = 120,
              max_num_psds: int = 10000,
              n_basis: int = 50,
              basis:str = 'first') -> Tuple[Union[float, Any], Union[float, Any], int, int]:
    """Calculate :math:`\text{Song }D_{KL}` metric.

    Parameters
    ----------
    ref_dir_path : str
        Path to directory with .wav files of songs from bird
        that should be used as reference.
    compare_dir_path : str
        Path to directory with .wav files of songs from bird
        that should be compared with reference.
    k_ref : int
        Number of syllable classes in song of bird used as reference.
    k_compare : int
        Number of syllable classes in song of bird compared with reference.
    max_wavs : int
        Maximum number of wav files to use. Default is 120.
    max_num_psds : int
        Maximum number of power spectral densities (PSDs) to calculate.
        Default is 10000.
    n_basis : int
        Number of syllables to use as basis set. Default is 50.
    basis : str
        One of {'first', 'random'}.
        Controls which syllables are used as the basis set.
        If 'first', use the first `n_basis` syllables.
        If `random`, grab a random set of size `n_basis`.
        Default is 'first'.

    Returns
    -------
    DKL_PQ : float
        Calculated value for :math:`D_{KL}(\hat{P}||\hat{Q}`,
        the information lost when encoding P with Q,
        as computed according to Equation 6 in Mets Brainard 2018.
        The main value of interest calculated by this function.
    DKL_QP : float
        Same computation as ``DKL_PQ``,
        but in the opposite direction:
        Q with respect to P.
    n_psds_ref : int
        Number of PSDs used from reference data set.
    n_psd_compare : int
        Number of PDSs used from comparison data set.
    """
    wav_paths_ref = sorted(pathlib.Path(ref_dir_path).glob('*.wav'))
    wav_paths_compare = sorted(pathlib.Path(compare_dir_path).glob('*.wav'))

    wav_paths_ref = wav_paths_ref[:max_wavs]
    wav_paths_compare = wav_paths_compare[:max_wavs]

    syls_ref, slices_ref = get_all_syls(wav_paths_ref)
    syls_compare, slices_compare = get_all_syls(wav_paths_compare)

    segedpsds_ref = convert_syl_to_psd(syls_ref, max_num_psds)
    segedpsds_compare = convert_syl_to_psd(syls_compare, max_num_psds)

    if basis == 'first':
        # select the first `n_basis` syllables of the reference song as the basis set
        basis_set = segedpsds_ref[:n_basis]
    elif basis == 'random':
        # select a random set of `n_basis` syllables as the basis set
        basis_set = [segedpsds_ref[ind]
                     for ind in np.random.randint(0, len(segedpsds_ref), size=n_basis)]
    else:
        raise ValueError(
            f"Invalid value for basis: {basis}. Must be one of {{'first', 'random'}}"
        )

    len_ref_half = int(len(segedpsds_ref) / 2)
    len_compare_half = int(len(segedpsds_compare) / 2)

    # calculate distance matrices
    D_ref = spatial.distance.cdist(segedpsds_ref[:len_ref_half], basis_set, 'sqeuclidean')
    D_ref_2 = spatial.distance.cdist(segedpsds_ref[len_ref_half:], basis_set, 'sqeuclidean')
    D_compare = spatial.distance.cdist(segedpsds_compare[:len_compare_half], basis_set, 'sqeuclidean')
    D_compare_2 = spatial.distance.cdist(segedpsds_compare[len_compare_half:], basis_set, 'sqeuclidean')

    mx = np.max([np.max(D_ref), np.max(D_compare), np.max(D_ref_2), np.max(D_compare_2)])

    # convert to similarity matrices
    s_ref = 1 - (D_ref / mx)
    s_ref_2 = 1 - (D_ref_2 / mx)
    s_compare = 1 - (D_compare / mx)
    s_compare_2 = 1 - (D_compare_2 / mx)

    # estimate GMMs
    P = GaussianMixture(n_components=k_ref, max_iter=100000, n_init=5, covariance_type='full')
    P.fit(s_ref)

    Q = GaussianMixture(n_components=k_compare, max_iter=100000, n_init=5, covariance_type='full')
    Q.fit(s_compare)

    # calculate likelihoods for held out data
    p_hat_p = P.score(s_ref_2)
    q_hat_p = Q.score(s_ref_2)

    p_hat_q = P.score(s_compare_2)
    q_hat_q = Q.score(s_compare_2)

    # calculate song divergence (DKL estimate)
    DKL_PQ = np.log2(np.e) * ((np.mean(p_hat_p)) - (np.mean(q_hat_p)))
    DKL_QP = np.log2(np.e) * ((np.mean(q_hat_q)) - (np.mean(p_hat_q)))

    DKL_PQ = DKL_PQ / len(basis_set)
    DKL_QP = DKL_QP / len(basis_set)

    n_psds_ref = len(segedpsds_ref)
    n_psds_compare = len(segedpsds_compare)

    return DKL_PQ, DKL_QP, n_psds_ref, n_psds_compare
