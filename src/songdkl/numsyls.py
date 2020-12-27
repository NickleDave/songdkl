"""functions to estimate the number of syllables in a bird's song"""
import sys as sys
import os as os
import scipy as sc

from pylab import psd
import numpy as np
from sklearn.mixture import GaussianMixture as GMM

from .audio import impwav, getsyls
from .songdkl import norm


def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    out = []
    lens = (len(l) / n)
    for i in range(0, lens):
        out.append(l[i * n:i * n + n])
    out.append(l[lens * n:])
    return out[:-1]


def EMofgmmcluster(array_of_syls):
    """takes an array of segmented sylables, fits a series of
    gaussian mixture models with an increasing number of mixtures, 
    and identifies the best number of mixtures to describe the data
    by BIC. If data is limiting, we don't recommend using cross validation 
    for BIC.  If you have sufficient data 3 fold cross validated BIC values
    compare well with un-cross validated values and human assesment of syllable
    number.  If data are limiting, cross validated values underestimate
    the number of syllables relative to human assessment or non-cross
    validated BIC values.
    """
    nfft = 2 ** 14
    fs = 32000
    segstart = int(600 / (fs / nfft))
    segend = int(16000 / (fs / nfft))

    welchpsds = [psd(x, NFFT=nfft, Fs=fs) for x in array_of_syls]
    segedpsds1 = [norm(x[0][segstart:segend]) for x in welchpsds]

    models = range(2, 22)

    # select the first 50 syllables of the reference song as the basis set
    basis_set = segedpsds1[:50]
    # select a random set of 50 syllablse as the basis set
    # basis_set=[segedpsds1[rnd.randint(0,len(segedpsds1))] for x in range(50)]
    d = sc.spatial.distance.cdist(segedpsds1, basis_set, 'sqeuclidean')
    s = 1 - d / np.max(d) * 1000
    bic = []
    # xv=3
    for x in models:
        bics = []
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
        gmm = mixture.GMM(n_components=x, n_iter=100000, n_init=5, covariance_type='full')
        gmm.fit(np.array(s))
        bic.append(gmm.bic(np.array(s)))
    return segedpsds1, bic.index(min(bic)) + 2


def numsyls(path1):
    fils1 = [x for x in os.listdir(path1) if x[-4:] == '.wav']

    fils1 = fils1[:120]

    filename1 = path1.split('/')[-2]

    datano = 15000  # maximum number of syllables to be analyzed

    # get syllables from all of the songs in folder
    syls1 = []
    objss1 = []
    for file in fils1:
        song = impwav(path1 + file)
        if len(song[0]) < 1: break
        syls, objs, frq = (getsyls(song))
        objss1.append(objs)
        syls1.append([frq] + syls)

    # convert syllables so PSDs
    segedpsds1 = []
    for x in syls1[:datano]:
        fs = x[0]
        nfft = int(round(2 ** 14 / 32000.0 * fs))
        segstart = int(round(600 / (fs / float(nfft))))
        segend = int(round(16000 / (fs / float(nfft))))
        psds = [psd(norm(y), NFFT=nfft, Fs=fs) for y in x[1:]]
        spsds = [norm(n[0][segstart:segend]) for n in psds]
        for n in spsds: segedpsds1.append(n)
        if len(segedpsds1) > datano: break

    segedpsds, sylno_bic = EMofgmmcluster(segedpsds1)

    print(filename1 + '\t' + str(sylno_bic))


if __name__ == '__main__':
    # main program
    path1 = sys.argv[1]
    numsyls(path1)
