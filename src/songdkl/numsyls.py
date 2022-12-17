"""functions to estimate the number of syllables in a bird's song"""
from __future__ import annotations
import dataclasses
import logging
import pathlib

import numpy as np
import rich.progress
from sklearn.mixture import GaussianMixture
import scipy.spatial

from .constants import DefaultGaussianMixtureKwargs, DEFAULT_GMM_KWARGS
from .load import load_or_prep


logger = logging.getLogger(__name__)


def numsyls(psds_ref: np.ndarray,
            n_basis: int = 50,
            basis: str = 'first',
            min_components: int = 2,
            max_components: int = 22,
            n_splits: int = 1,
            gmm_kwargs: DEFAULT_GMM_KWARGS | dict = DEFAULT_GMM_KWARGS,
            ) -> int:
    """Determine number of syllable classes in a bird's song.

    Takes an array of PSDs from segmented syllables, fits them
    with a series of Gaussian Mixture Models with an increasing
    number of components, and then selects the number of components
    that maximizes the Bayesian Information Criterion (BIC).

    Parameters
    ----------
    psds_ref : numpy.ndarray
        PSDs of segmented syllables,
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
    gmm_kwargs : dict, DefaultGaussianMixtureKwargs
        Optional dict with keyword argument to pass into
        ``sklearn.GaussianMixtureModel`` when instantiating.
        If not supplied, the defaults are used,
        that are represented by a dataclass,
        ``songdkl.constants.DefaultGaussianMixtureKwargs``.
        Note that specifying ``n_components``
        as one of the ``gmm_kwargs`` will raise an
        error since this function searches for the best
        value for ``n_components``.

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
    if isinstance(gmm_kwargs, DefaultGaussianMixtureKwargs):
        gmm_kwargs = dataclasses.asdict(gmm_kwargs)
    elif isinstance(gmm_kwargs, dict):
        pass
    else:
        raise TypeError(
            '`gmm_kwargs` must be a dict or DefaultGaussianMixtureKwargs,'
            f'but was type: {type(gmm_kwargs)}'
        )
    if 'n_components' in gmm_kwargs:
        raise ValueError(
            "`gmm_kwargs` has key `n_components` but that argument to GaussianMixture "
            "are the `k_ref` and `k_compare` arguments to this function."
        )

    logger.log(
        msg=(f'Identifying best number of components to describe the data, psds_ref (shape: {psds_ref.shape}), '
             f'with parameters n_basis={n_basis}, basis={basis}, '
             f'min_components={min_components}, max_components={max_components}, n_splits={n_splits}.'),
        level=logging.INFO
    )

    if basis == 'first':
        # select the first `n_basis` syllables of the reference song as the basis set
        basis_set = psds_ref[:n_basis]
    elif basis == 'random':
        # select a random set of `n_basis` syllables as the basis set
        basis_set = [psds_ref[ind]
                     for ind in np.random.randint(0, len(psds_ref), size=n_basis)]

    logger.log(
        msg=f'Computing distances',
        level=logging.INFO
    )

    D = scipy.spatial.distance.cdist(psds_ref, basis_set, 'sqeuclidean')
    s = 1 - D / np.max(D) * 1000
    bics = []
    n_components_list = list(range(min_components, max_components))
    for n_components in rich.progress.track(n_components_list, 'Fitting components'):
        if n_splits > 1:
            split_bics = []
            splits = np.array_split(s, n_splits)
            for split_ind in range(len(splits)):
                train_split = np.concatenate([split for ind, split in enumerate(splits) if ind != split_ind])
                val_split = splits[split_ind]
                gmm = GaussianMixture(n_components=n_components, **gmm_kwargs)
                gmm.fit(train_split)
                split_bics.append(gmm.bic(val_split))
            bics.append(np.mean(split_bics))
        else:
            gmm = GaussianMixture(n_components=n_components, **gmm_kwargs)
            gmm.fit(np.array(s))
            bics.append(gmm.bic(np.array(s)))
    lowest_bic_ind = np.argmin(bics)
    n_syls = n_components_list[lowest_bic_ind]
    return n_syls


def numsyls_from_path(ref_path: str | pathlib.Path,
                      max_wavs: int = 120,
                      max_syllables: int = 10000,
                      psds_per_syl: int = 1,
                      n_basis: int = 50,
                      basis: str = 'first',
                      min_components: int = 2,
                      max_components: int = 22,
                      n_splits: int = 1,
                      gmm_kwargs: DEFAULT_GMM_KWARGS | dict = DEFAULT_GMM_KWARGS,
                      ) -> int:
    """Determine number of syllable classes in a bird's song,
    by fitting Gaussian Mixture Models to PSDs of segmented
    syllable renditions, and selecting the number of components
    that maximizes the Bayesian Information Criterion.

    Parameters
    ----------
    ref_path : str, pathlib.Path
        Path to data from bird that should be used.
        Either a path to a directory with .wav files of songs,
        or a path to a .songdkl.zarr file generated by songdkl prep.
    max_wavs : int
        Maximum number of wav files to use. Default is 120.
    max_syllables : int
        Maximum number of segmented syllables to use when generating
        power spectral densities (PSDs). Default is 10000.
    psds_per_syl : int
        Number of PSDs to compute per syllable. Default is 1.
        If greater than 1, the segment of audio corresponding
        to the syllable is split into ``psd_per_syl`` arrays,
        a PSD is computed for each, and they are concatenated
        to produce a single array of features for the syllable.
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
        Default is 1, in which case ``psds_ref`` is not split.
        If sufficient data are available,
        a good rule of thumb is to use 3 splits.
        See Notes below for more detail.
    gmm_kwargs : dict, DefaultGaussianMixtureKwargs
        Optional dict with keyword argument to pass into
        ``sklearn.GaussianMixtureModel`` when instantiating.
        If not supplied, the defaults are used,
        that are represented by a dataclass,
        ``songdkl.constants.DefaultGaussianMixtureKwargs``.
        Note that specifying ``n_components``
        as one of the ``gmm_kwargs`` will raise an
        error since this function searches for the best
        value for ``n_components``.

    Returns
    -------
    sylno_bic : int
        The estimated number of syllables, equal to
        the number of components
        that produced the fit Gaussian Mixture Model
        with the lowest Bayesian Information Criterion.
    """
    logger.log(
        msg=f'Getting PSDs from ref_path: {ref_path}',
        level=logging.INFO
    )
    psds_ref = load_or_prep(ref_path, max_wavs, max_syllables, psds_per_syl)

    sylno_bic = numsyls(psds_ref, n_basis, basis, min_components, max_components, n_splits, gmm_kwargs)
    return sylno_bic
