"""functions to compute song divergence"""
from __future__ import annotations
import dataclasses
import pathlib
from typing import Any, Optional, Tuple, Union

import scipy.spatial as spatial
import matplotlib.mlab
import numpy as np
from sklearn.mixture import GaussianMixture

from . import audio


def norm(arr: np.ndarray) -> np.ndarray:
    """Normalize an array by
    subtracting off the mean
    and dividing by the standard deviation.

    Parameters
    ----------
    arr : numpy.ndarray
        A numpy array

    Returns
    -------
    normed : numpy.ndarray
        ``arr`` with
    """
    # replace use of ``np.average`` with ``np.mean``
    # since ``np.average`` calls ``np.mean`` anyways,, Any
    # and we are not using weighting that ``np.average`` provides
    return (np.array(arr) - arr.mean()) / np.std(arr)


@dataclasses.dataclass
class SyllablesFromWav:
    """
    Dataclass representing
    all the syllables
    found by segmenting a
    .wav file.

    Attributes
    ----------
    syls : list
        Of ``numpy.ndarray``, syllables
        returned by ``songdkl.audio.getsyls``
    rate : int
        Sampling rate of .wav file.
    """
    syls: list
    rate: int


def get_all_syls(wav_paths: list[str]) -> list[SyllablesFromWav]:
    """Get all syllables from a list of .wav files.

    Parameters
    ----------
    wav_paths : list
        Of str, absolute paths to .wav files

    Returns
    -------
    syls_from_wavs : list
        of ``SyllablesFromWav`` instances,
        same length as ``wav_paths``.
        Each ``SyllablesFromWav`` has an
        attribute ``syls``, a list of
        ``numpy.ndarray``s, and an attribute
        ``rate``, the sampling rate
        for the .wav file the syllables
        are taken from.
    """
    syls_from_wavs = []
    for wav_path in wav_paths:
        rate, data = audio.load_wav(wav_path)
        syls_this_wav, slices_this_wav = audio.getsyls(data, rate)
        syls_from_wavs.append(
            SyllablesFromWav(syls=syls_this_wav, rate=rate)
        )
    return syls_from_wavs


def convert_syl_to_psd(syls_from_wavs: list[SyllablesFromWav],
                       max_num_psds: Optional[int] = None) -> list[np.ndarray]:
    """Convert syllable segments to power spectral densities (PSDs).

    Parameters
    ----------
    syls_from_wavs : list
        Of ``SyllablesFromWav`` instances,
        syllable segments extracted from .wav files.
    max_num_psds : int
        Maximum number of PSDs to calculate.
        Default is None, in which case
        PSDs will be computed for all syllables.

    Returns
    -------
    segedpsds : list
        Of ``numpy.ndarray``,
        PSDs from segmented syllables.
    """
    segedpsds = []
    for syls_from_wav in syls_from_wavs:
        fs = syls_from_wav.rate
        nfft = int(round(2 ** 14 / 32000.0 * fs))
        segstart = int(round(600 / (fs / float(nfft))))
        segend = int(round(16000 / (fs / float(nfft))))
        psds = []
        for syl in syls_from_wav.syls:
            Pxx, _ = matplotlib.mlab.psd(norm(syl), NFFT=nfft, Fs=fs)
            psds.append(Pxx)
        spsds = [norm(psd[segstart:segend]) for psd in psds]
        segedpsds.extend(spsds)
        if max_num_psds:
            if len(segedpsds) > max_num_psds:
                break

    if max_num_psds:
        # since we are likely over `max_num_psds` even after `break` above
        segedpsds = segedpsds[:max_num_psds]

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

    syls_from_wavs_ref = get_all_syls(wav_paths_ref)
    syls_from_wavs_compare = get_all_syls(wav_paths_compare)

    segedpsds_ref = convert_syl_to_psd(syls_from_wavs_ref, max_num_psds)
    segedpsds_compare = convert_syl_to_psd(syls_from_wavs_compare, max_num_psds)

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
