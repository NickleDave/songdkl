"""functions to estimate the number of syllables in a bird's song"""
from __future__ import annotations
import pathlib

import numpy as np
from sklearn.mixture import GaussianMixture
import scipy.spatial

from .syllables import (
    convert_syl_to_psd,
    get_all_syls,
)


def em_of_gmm_cluster(segedpsds: list,
                      n_basis: int = 50,
                      basis: str = 'first',
                      min_components: int = 2,
                      max_components: int = 22,
                      n_splits: int = 1,
                      ) -> int:
    """Identifies the best number of mixtures to describe the data.

    Takes an array of segmented syllables, fits a series of
    gaussian mixture models with an increasing number of mixtures,
    and identifies the best number of mixtures to describe the data
    by Bayesian Information Criterion (BIC).

    Parameters
    ----------
    segedpsds : list
        Of ``numpy.ndarray``, PSDs of segmented syllables,
        returned by ``songdkl.songdkl.convert_syls_to_psd``.
    n_basis : int
        Number of syllables to use as basis set. Default is 50.
    basis : str
        One of {'first', 'random'}.
        Controls which syllables are used as the basis set.
        If 'first', use the first `n_basis` syllables.
        If `random`, grab a random set of size `n_basis`.
        Default is 'first'.
    min_components : int
        Minimum number of components to consider
        when fitting Gaussian Mixture Models. Default is 2.
    max_components : int
        Maximum number of components to consider
        when fitting Gaussian Mixture Models. Default is 22.
    n_splits : int
        Number of splits to use when estimating components.
        Default is 1, in which case ``segedpsds`` is not split.
        If sufficient data are available,
        a good rule of thumb is to use 3 splits.
        See Notes below for more detail.

    Returns
    -------
    n_syls : int
        The number of components that gave the minimum
        Bayesian Information Criterion, plus two.

    Notes
    -----
    If data is limiting, we don't recommend using
    splits to estimate BIC.
    When the data are limiting,
    values from splits underestimate
    the number of syllables relative to
    human assessment or BIC values
    computed without splits.
    """
    if basis == 'first':
        # select the first `n_basis` syllables of the reference song as the basis set
        basis_set = segedpsds[:n_basis]
    elif basis == 'random':
        # select a random set of `n_basis` syllables as the basis set
        basis_set = [segedpsds[ind]
                     for ind in np.random.randint(0, len(segedpsds), size=n_basis)]

    D = scipy.spatial.distance.cdist(segedpsds, basis_set, 'sqeuclidean')
    s = 1 - D / np.max(D) * 1000
    bics = []
    n_components_list = list(range(min_components, max_components))
    for n_components in n_components_list:
        if n_splits > 1:
            split_bics = []
            splits = np.array_split(s, n_splits)
            for split in splits:
                gmm = GaussianMixture(n_components=n_components, max_iter=100000, n_init=5, covariance_type='full')
                gmm.fit(split)
                split_bics.append(gmm.bic(split))
            bics.append(np.mean(split_bics))
        else:
            gmm = GaussianMixture(n_components=n_components, max_iter=100000, n_init=5, covariance_type='full')
            gmm.fit(np.array(s))
            bics.append(gmm.bic(np.array(s)))
    lowest_bic_ind = np.argmin(bics)
    n_syls = n_components_list[lowest_bic_ind]
    return n_syls


def numsyls(dir_path: str | pathlib.Path,
            max_wavs: int = 120,
            max_num_psds: int = 15000,
            ) -> int:
    """Determine number of syllable classes in a bird's song,
    by fitting Gaussian Mixture Models to PSDs of segmented
    syllable renditions, and selecting the number of components
    that maximizes the Bayesian Information Criterion.

    Parameters
    ----------
    max_wavs : int
        Maximum number of wav files to use. Default is 120.
    max_num_psds : int
        Maximum number of power spectral densities (PSDs) to calculate.

    Returns
    -------
    sylno_bic : int
        The estimated number of syllables, equal to
        the number of components
        that produced the fit Gaussian Mixture Model
        with the lowest Bayesian Information Criterion.
    """
    wav_paths = sorted(pathlib.Path(dir_path).glob('*.wav'))
    wav_paths = wav_paths[:max_wavs]

    syls_from_wavs = get_all_syls(wav_paths)
    segedpsds = convert_syl_to_psd(syls_from_wavs, max_num_psds)
    sylno_bic = em_of_gmm_cluster(segedpsds)
    return sylno_bic
