import sys as sys
import os as os
import scipy as sc
from scipy import io
from scipy.io import wavfile
from scipy import ndimage
from scipy import signal
from scipy import spatial
from pylab import specgram, psd
import numpy as np
import sklearn as skl
from sklearn import cluster
from sklearn import metrics
from scipy import spatial
from sklearn import mixture
from sklearn import decomposition
import random as rnd
from array import array
from mahotas import otsu

"""A script to estimate the number of syllable types in a song.
It fitsfits a series of gaussian mixture models with an 
increasing number of mixtures, and identifies the best number 
of mixtures to describe the data by BIC.
It is applied as follows:
python calc_sylno.py folder_with_bird_songs
e.g. python calc_sylno.py bird_data/y34br6/
It expects the songs to be in mono wave format and have a .wav suffix.
The output is a tab delimited string as follows:
foldername_bird	number_of_syllables
e.g. y34br6 9"""


# functions
def impwav(a):
    """Imports a wave file as an array where a[1]
    is the sampling frequency and a[0] is the data"""
    out = []
    wav = sc.io.wavfile.read(a)
    out = [wav[1], wav[0]]
    return out


def norm(a):
    """normalizes a string by it's average and sd"""
    a = (np.array(a) - np.average(a)) / np.std(a)
    return a


def filtersong(a):
    """highpass iir filter for song."""
    out = []
    b = sc.signal.iirdesign(wp=0.04, ws=0.02, gpass=1, gstop=60, ftype='ellip')
    out.append(sc.signal.filtfilt(b[0], b[1], a[0]))
    out.append(a[1])
    return (out)


def threshold(a, thresh=None):
    """Returns a thresholded array of the same length as input
    with everything below a specific threshold set to 0.
    By default threshold is sigma."""
    if thresh == None: thresh = sc.std(a)
    out = np.where(abs(a) > thresh, a, np.zeros(a.shape))
    return out


def findobject(file):
    """finds objects.  Expects a smoothed rectified amplitude envelope"""
    value = (otsu(np.array(file, dtype=np.uint32))) / 2  # calculate a threshold
    # value=(np.average(file))/2 #heuristically, this also usually works  for establishing a threshold
    thresh = threshold(file, value)  # threshold the envelope data
    thresh = threshold(sc.ndimage.convolve(thresh, np.ones(512)), 0.5)  # pad the threshold
    label = (sc.ndimage.label(thresh)[0])  # label objects in the threshold
    objs = sc.ndimage.find_objects(label)  # recover object positions
    return (objs)


def smoothrect(a, window=None, freq=None):
    """smooths and rectifies a song.  Expects (data,samprate)"""
    if freq == None: freq = 32000  # baseline values if none are provided
    if window == None: window = 2  # baseline if none are provided
    le = int(round(freq * window / 1000))  # calculate boxcar kernel length
    h = np.ones(le) / le  # make boxcar
    smooth = np.convolve(h, abs(a))  # convovlve boxcar with signal
    offset = int(round((len(smooth) - len(a)) / 2))  # calculate offset imposed by convolution
    smooth = smooth[(1 + offset):(len(a) + offset)]  # correct for offset
    return smooth


def getsyls(a):
    """takes a file read in with impwav and returns a list of sylables"""
    fa = filtersong(a)  # filter song input
    frq = a[1]  # get sampling frequency from data (a)
    a = a[0]  # get data from data (a)
    frqs = frq / 1000  # calcualte length of a ms in samples
    objs = findobject(smoothrect(fa[0], 10, frq))  # get syllable positions
    sylables = [x for x in [a[y] for y in objs] if int(len(x)) > (10 * frqs)]  # get syllable dat$
    objs = [y for y in objs if int(len(a[y])) > 10 * frqs]  # get objects of sufficient duraiton
    return sylables, objs, frq


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

    basis_set = segedpsds1[:50]  # select the first 50 syllables of the reference song as the basis set
    # basis_set=[segedpsds1[rnd.randint(0,len(segedpsds1))] for x in range(50)] #select a random set of 50 syllablse as the basis set
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


# main program
path1 = sys.argv[1]

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
    # not clear to me why norm is applied twice: once here
    psds = [psd(norm(y), NFFT=nfft, Fs=fs) for y in x[1:]]
    # and then applied here again. Might have no effect at this point?
    spsds = [norm(n[0][segstart:segend]) for n in psds]
    for n in spsds: segedpsds1.append(n)
    if len(segedpsds1) > datano: break

# we pass in segedpsds1 but then these get run through the code again that makes PSDs
segedpsds, sylno_bic = EMofgmmcluster(segedpsds1)

print filename1 + '\t' + str(sylno_bic)
