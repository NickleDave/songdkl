"""functions to estimate the number of syllables in a bird's song"""
import pathlib
import sys as sys

import numpy as np
from sklearn.mixture import GaussianMixture
import scipy.spatial

from .songdkl import (
    convert_syl_to_psd,
    get_all_syls,
)


def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    out = []
    lens = (len(l) / n)
    for i in range(0, lens):
        out.append(l[i * n:i * n + n])
    out.append(l[lens * n:])
    return out[:-1]


def EMofgmmcluster(segedpsds: list,
                   n_basis: int = 50,
                   basis:str = 'first',
                   min_components=2,
                   max_components=22,
                   ):
    """takes an array of segmented syllables, fits a series of
    gaussian mixture models with an increasing number of mixtures,
    and identifies the best number of mixtures to describe the data
    by BIC.

    If data is limiting, we don't recommend using cross validation
    for BIC.  If you have sufficient data 3-fold cross-validated BIC values
    compare well with un-cross validated values and human assessment of syllable
    number.  If data are limiting, cross-validated values underestimate
    the number of syllables relative to human assessment or non-cross
    validated BIC values.

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

    Returns
    -------
    n_syls : int
        The number of components that gave the minimum
        Bayesian Information Criterion, plus two.
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
    # xv=3
    n_components_list = list(range(min_components, max_components))
    for n_components in n_components_list:
        # this commented section implements cross validation for the BIC values
        '''ss=chunks(s,len(s)/xv)
        for y in range(len(ss)):
        testset=ss[y]
        trainset=[]
        [trainset.extend(ss[n]) for n in [z for z in range(len(ss)) if z!=y]]
        gmm = mixture.GMM(n_components=x, n_iter=100000,n_init=5, covariance_type='full')
        gmm.fit(np.array(s))
        bics.append(gmm.bic(np.array(s)))
        bic.append(np.mean(bics))'''
        gmm = GaussianMixture(n_components=n_components, max_iter=100000, n_init=5, covariance_type='full')
        gmm.fit(np.array(s))
        bics.append(gmm.bic(np.array(s)))
    lowest_bic_ind = np.argmin(bics)
    n_syls = n_components_list[lowest_bic_ind]
    return n_syls


def numsyls(dir_path,
            max_wavs: int = 120,
            max_num_psds: int = 15000,
            ):
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
    """
    wav_paths = sorted(pathlib.Path(dir_path).glob('*.wav'))
    wav_paths = wav_paths[:max_wavs]

    syls, slices = get_all_syls(wav_paths)
    segedpsds = convert_syl_to_psd(syls, max_num_psds)
    sylno_bic = EMofgmmcluster(segedpsds)
    return sylno_bic


if __name__ == '__main__':
    # main program
    path1 = sys.argv[1]
    numsyls(path1)
