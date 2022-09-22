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

"""A script to calculate the song divergence between two birds. It is aplied as follows:
python Song_D_KL_calc.py folder_with_songs_from_bird_1 folder_with_songs_from_bird_2 number_of_syllable_calsses_bird_1 number_of_syllable_classes_bird_2
e.g.  python bird_data/y25/ bird_data/y34br6/ 9 10
It expects the songs to be in mono wave format and have a .wav suffix.
The output is a tab delimited string formatted as follows:
foldername_bird1 foldername_bird2 n_syl_classes_bd1 n_syl_classes_bd2 n_basis_set SD_bd1_ref_bd2_song SD_bd2_ref_bd1_comp n_syls_bd1 n_syls_bd2
e.g. y25 y32br6 9 10 50 0.039854682578 0.0340690226514 3000 3000

IMPORTANT! In our paper we always use the number of syllables in the tutor song for both syllable # values.  
This is meant to be conservative, basically give the bird learning the benefit of the doubt that it actually coppied all
of the syllables in the tutor song.  Emperically, changing these numbers doesn't have much impact on the divergence
calculations (see the paper)

IMPORTANT! Throughout the paper we calculated PSDs for the raw wave forms of syllables.  This is the default setting for this script. If your song is contaminated with low frequency noise this noise may be incorporated into the model for song potentially causing over estimates of song D_KL if there is low frequency noise in the tutor song but not the tutee song.  This could occur if the birds were recorded under different conditions or in different sound recording boxes.  If you uncomment line 99 below, the script will calculate the song D_KL using filtered syllable data. We only advise this if you have low frequency noise that is differential between the tutor and tutee song and you don't want that noise incorporated into the song D_KL calculations."""


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
    # value=(np.average(file))/2 #heuristically, this also usually works  for establishing threshold
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
    sylables = [x for x in [a[y] for y in objs] if
                int(len(x)) > (10 * frqs)]  # get syllable data if of sufficient duration
    '''uncomment the next line to recover syllables that have been high pass filtered as opposed to raw data.
    Using data filtered prior to PSD calculation helps if you data are contaminated
    with low frequency noise'''
    # sylables=[x for x in [fa[0][y] for y in objs] if int(len(x))>(10*frqs)] #get syllable data if of sufficient duration.
    objs = [y for y in objs if int(len(a[y])) > 10 * frqs]  # get objects of sufficient duraiton
    return sylables, objs, frq


# main program

path1 = sys.argv[1]
path2 = sys.argv[2]

fils1 = [x for x in os.listdir(path1) if x[-4:] == '.wav']
fils2 = [x for x in os.listdir(path2) if x[-4:] == '.wav']

fils1 = fils1[:120]
fils2 = fils2[:120]

filename1 = path1.split('/')[-2]
filename2 = path2.split('/')[-2]

datano = 10000  # variable to constrain the amount of data used

k = int(sys.argv[3])  # number of syllable classes in song 1
k2 = int(sys.argv[4])  # number of syllable classes in song 2

# get syllables from all of the songs in folder 1
syls1 = []
objss1 = []
for file in fils1:
    song = impwav(path1 + file)
    if len(song[0]) < 1: break
    syls, objs, frq = (getsyls(song))
    objss1.append(objs)
    syls1.append([frq] + syls)

# get syllables from all of the songs in folder 2
syls2 = []
objss2 = []
for file in fils2:
    song = impwav(path2 + file)
    if len(song[0]) < 1: break
    syls, objs, frq = (getsyls(song))
    objss2.append(objs)
    syls2.append([frq] + syls)

# convert syllables into PSDs
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

# convert syllables to PSDs
segedpsds2 = []
for x in syls2[:datano]:
    fs = x[0]
    nfft = int(round(2 ** 14 / 32000.0 * fs))
    segstart = int(round(600 / (fs / float(nfft))))
    segend = int(round(16000 / (fs / float(nfft))))
    psds = [psd(norm(y), NFFT=nfft, Fs=fs) for y in x[1:]]
    spsds = [norm(n[0][segstart:segend]) for n in psds]
    for n in spsds: segedpsds2.append(n)
    if len(segedpsds2) > datano: break

# establish basis set:
basis_set = segedpsds1[:50]  # select the first 50 syllables of the reference song as the basis set
# basis_set=[segedpsds1[rnd.randint(0,len(segedpsds1))] for x in range(50)] #select a random set of 50 syllablse as the basis set


lone = len(segedpsds1)
ltwo = len(segedpsds2)
lone_half = int(lone / 2)
ltwo_half = int(ltwo / 2)

# calculate distance matrices:
d1 = sc.spatial.distance.cdist(segedpsds1[:lone_half], basis_set, 'sqeuclidean')

d1_2 = sc.spatial.distance.cdist(segedpsds1[lone_half:lone], basis_set, 'sqeuclidean')

d2 = sc.spatial.distance.cdist(segedpsds2[:ltwo_half], basis_set, 'sqeuclidean')

d2_2 = sc.spatial.distance.cdist(segedpsds2[ltwo_half:ltwo], basis_set, 'sqeuclidean')

mx = np.max([np.max(d1), np.max(d2), np.max(d1_2), np.max(d2_2)])

# convert to similarity matrices:
s1 = 1 - (d1 / mx)
s1_2 = 1 - (d1_2 / mx)
s2 = 1 - (d2 / mx)
s2_2 = 1 - (d2_2 / mx)

# estimate GMMs:
mod1 = mixture.GMM(n_components=k, n_iter=100000, n_init=5, covariance_type='full')
mod1.fit(s1)

mod2 = mixture.GMM(n_components=k2, n_iter=100000, n_init=5, covariance_type='full')
mod2.fit(s2)

len2 = len(s2)
len1 = len(d1)

# calculate likelihoods for held out data:
score1_1 = mod1.score(s1_2)
score2_1 = mod2.score(s1_2)

score1_2 = mod1.score(s2_2)
score2_2 = mod2.score(s2_2)

len2 = float(len(basis_set))
len1 = float(len(basis_set))

# calculate song divergence (DKL estimate):
score1 = np.log2(np.e) * ((np.mean(score1_1)) - (np.mean(score2_1)))
score2 = np.log2(np.e) * ((np.mean(score2_2)) - (np.mean(score1_2)))

score1 = score1 / len1
score2 = score2 / len2

# output
print
filename1 + '\t' + filename2 + '\t' + str(k) + '\t' + str(k2) + '\t' + str(len2) + '\t' + str(score1) + '\t' + str(
    score2) + '\t' + str(len(segedpsds1)) + '\t' + str(len(segedpsds2))
