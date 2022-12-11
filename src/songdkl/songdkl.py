"""functions to compute song divergence"""
from __future__ import annotations
import dataclasses
import logging
import pathlib
from typing import Any, Tuple, Union

import scipy.spatial as spatial
import numpy as np
from sklearn.mixture import GaussianMixture

from .constants import DefaultGaussianMixtureKwargs, DEFAULT_GMM_KWARGS
from .load import load_or_prep


logger = logging.getLogger(__name__)


def calculate(psds_ref: np.ndarray,
              psds_compare: np.ndarray,
              k_ref: int,
              k_compare: int,
              n_basis: int = 50,
              basis: str = 'first',
              gmm_kwargs: DEFAULT_GMM_KWARGS | dict = DEFAULT_GMM_KWARGS
              ) -> Tuple[Union[float, Any], Union[float, Any], int, int]:
    """Calculate :math:`\text{Song }D_{KL}` metric.

    Parameters
    ----------
    psds_ref : numpy.ndarray
        Array of PSDs from bird that should be used as reference.
    psds_compare : numpy.ndarray
        Array of PSDs from bird that should be compared with reference.
    k_ref : int
        Number of syllable classes in song of bird used as reference.
    k_compare : int
        Number of syllable classes in song of bird compared with reference.
    n_basis : int
        Number of syllables to use as basis set. Default is 50.
    basis : str
        One of {'first', 'random'}.
        Controls which syllables are used as the basis set.
        If 'first', use the first `n_basis` syllables.
        If `random`, grab a random set of size `n_basis`.
        Default is 'first'.
    gmm_kwargs : dict, DefaultGaussianMixtureKwargs
        Optional dict with keyword argument to pass into
        ``sklearn.GaussianMixtureModel`` when instantiating.
        If not supplied, the defaults are used,
        that are represented by a dataclass,
        ``songdkl.constants.DefaultGaussianMixtureKwargs``.
        Note that specifying ``n_components``
        as one of the ``gmm_kwargs`` will raise an
        error since those are specified as the ``k_ref``
        and ``k_compare`` arguments to this function.

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
        msg=(f'Calculating songdkl with psds_ref (shape: {psds_ref.shape}) '
             f'and psds_compare (shape: {psds_compare.shape}.), '
             f'and parameters k_ref={k_ref}, k_compare={k_compare}, n_basis={n_basis}, basis={basis}.'),
        level=logging.INFO
    )

    if basis == 'first':
        # select the first `n_basis` syllables of the reference song as the basis set
        basis_set = psds_ref[:n_basis]
    elif basis == 'random':
        # select a random set of `n_basis` syllables as the basis set
        basis_set = [psds_ref[ind]
                     for ind in np.random.randint(0, len(psds_ref), size=n_basis)]
    else:
        raise ValueError(
            f"Invalid value for basis: {basis}. Must be one of {{'first', 'random'}}"
        )

    len_ref_half = int(len(psds_ref) / 2)
    len_compare_half = int(len(psds_compare) / 2)

    logger.log(
        msg=f'Calculating distance matrices',
        level=logging.INFO
    )

    # calculate distance matrices
    D_ref = spatial.distance.cdist(psds_ref[:len_ref_half], basis_set, 'sqeuclidean')
    D_ref_2 = spatial.distance.cdist(psds_ref[len_ref_half:], basis_set, 'sqeuclidean')
    D_compare = spatial.distance.cdist(psds_compare[:len_compare_half], basis_set, 'sqeuclidean')
    D_compare_2 = spatial.distance.cdist(psds_compare[len_compare_half:], basis_set, 'sqeuclidean')

    mx = np.max([np.max(D_ref), np.max(D_compare), np.max(D_ref_2), np.max(D_compare_2)])

    logger.log(
        msg='Converting to similarity matrices',
        level=logging.INFO
    )
    # convert to similarity matrices
    s_ref = 1 - (D_ref / mx)
    s_ref_2 = 1 - (D_ref_2 / mx)
    s_compare = 1 - (D_compare / mx)
    s_compare_2 = 1 - (D_compare_2 / mx)

    logger.info(
        msg=f'Fitting Gaussian Mixture Models',
    )
    # estimate GMMs
    P = GaussianMixture(n_components=k_ref, **gmm_kwargs)
    P.fit(s_ref)

    Q = GaussianMixture(n_components=k_compare, **gmm_kwargs)
    Q.fit(s_compare)

    logger.log(
        msg=f'Calculating likelihoods for held out data',
        level=logging.INFO
    )
    # calculate likelihoods for held out data
    p_hat_p = P.score(s_ref_2)
    q_hat_p = Q.score(s_ref_2)

    p_hat_q = P.score(s_compare_2)
    q_hat_q = Q.score(s_compare_2)

    logger.log(
        msg=f'Calculating Song_D_KL, divergence estimate',
        level=logging.INFO
    )
    # calculate song divergence (DKL estimate)
    DKL_PQ = np.log2(np.e) * ((np.mean(p_hat_p)) - (np.mean(q_hat_p)))
    DKL_QP = np.log2(np.e) * ((np.mean(q_hat_q)) - (np.mean(p_hat_q)))

    DKL_PQ = DKL_PQ / len(basis_set)
    DKL_QP = DKL_QP / len(basis_set)

    n_psds_ref = len(psds_ref)
    n_psds_compare = len(psds_compare)

    return DKL_PQ, DKL_QP, n_psds_ref, n_psds_compare


def calculate_from_path(ref_path: str | pathlib.Path,
                        compare_path: str | pathlib.Path,
                        k_ref: int,
                        k_compare: int,
                        max_wavs: int = 120,
                        max_num_psds: int = 10000,
                        n_basis: int = 50,
                        basis: str = 'first',
                        gmm_kwargs: DEFAULT_GMM_KWARGS | dict = DEFAULT_GMM_KWARGS
                        ) -> Tuple[Union[float, Any], Union[float, Any], int, int]:
    """Calculate :math:`\text{Song }D_{KL}` metric.

    Parameters
    ----------
    ref_path : str
        Path to data from bird that should be used as reference.
        Either a path to a directory with .wav files of songs,
        or a path to a .songdkl.zarr file generated by songdkl prep.
    compare_path : str
        Path to data from bird that should be compared with reference.
        Either a path to a directory with .wav files of songs,
        or a path to a .songdkl.zarr file generated by songdkl prep.
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
    gmm_kwargs : dict, DefaultGaussianMixtureKwargs
        Optional dict with keyword argument to pass into
        ``sklearn.GaussianMixtureModel`` when instantiating.
        If not supplied, the defaults are used,
        that are represented by a dataclass,
        ``songdkl.constants.DefaultGaussianMixtureKwargs``.
        Note that specifying ``n_components``
        as one of the ``gmm_kwargs`` will raise an
        error since those are specified as the ``k_ref``
        and ``k_compare`` arguments to this function.

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
    logger.log(
        msg=f'Getting PSDs from ref_path: {ref_path}',
        level=logging.INFO
    )

    segedpsds_ref = load_or_prep(ref_path, max_wavs, max_num_psds)

    logger.log(
        msg=f'Getting PSDs from compare_path: {compare_path}',
        level=logging.INFO
    )
    segedpsds_compare = load_or_prep(compare_path, max_wavs, max_num_psds)
    return calculate(segedpsds_ref,
                     segedpsds_compare,
                     k_ref,
                     k_compare,
                     n_basis,
                     basis,
                     gmm_kwargs)
