"""This is a version of the `calc_sylno.py` script
from the original PLOS Comp. Biology paper
that has been modified to save the segmentation
obtained with Otsu's method from the ``mahotas`` library,
to use as data for testing,
specifically for comparison with the implementation
of Otsu's method in ``scikit-image``.

This modified version only runs up to the point
where the segmentation is generated,
and then saves the threshold, onsets, and offsets
in .csv files
"""
import sys as sys
import os as os
import scipy as sc
from scipy import io
from scipy.io import wavfile

from scipy import ndimage
from scipy import signal
import numpy as np
from mahotas import otsu


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
    return (objs), value


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
    objs, threshold_val = findobject(smoothrect(fa[0], 10, frq))  # get syllable positions
    sylables = [x for x in [a[y] for y in objs] if int(len(x)) > (10 * frqs)]  # get syllable dat$
    objs = [y for y in objs if int(len(a[y])) > 10 * frqs]  # get objects of sufficient duraiton
    return sylables, objs, frq, threshold_val


def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    out = []
    lens = (len(l) / n)
    for i in range(0, lens):
        out.append(l[i * n:i * n + n])
    out.append(l[lens * n:])
    return out[:-1]


path1 = sys.argv[1]

fils1 = [x for x in os.listdir(path1) if x[-4:] == '.wav']

fils1 = fils1[:120]

filename1 = path1.split('/')[-2]

datano = 15000  # maximum number of syllables to be analyzed

# get syllables from all of the songs in folder
syls1 = []
objss1 = []
threshold_vals = []
for file in fils1:
    song = impwav(path1 + file)
    if len(song[0]) < 1: break
    syls, objs, frq, threshold_val = (getsyls(song))
    objss1.append(objs)
    syls1.append([frq] + syls)
    threshold_vals.append(threshold_val)

csv = []
for ind, filename in enumerate(fils1):
    for slice_tup in objss1[ind]:
        slice_ = slice_tup[0]  # [0][0] because we get back tuples of (slice, None)
        csv.append([ind, filename, slice_.start, slice_.stop])  # one row of csv

csv = np.array(csv, dtype=np.object)
bird_id = path1.split("/")[-2]
fname = bird_id + '-pcb-calc-sylno-slices.csv'
csv_path = './tests/data-for-tests/generated/' + fname

np.savetxt(
    csv_path,
    csv,
    fmt=['%u', '%s', '%u', '%u'],
    delimiter=",",
    header="filenum,filename,start,stop"
)

threshold_vals = np.array(threshold_vals)
np.save('./tests/data-for-tests/generated/' + bird_id + '-pcb-calc-sylno-threshold-vals.npy', threshold_vals)
