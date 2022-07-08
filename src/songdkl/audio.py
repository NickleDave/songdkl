import numpy as np
import scipy.signal as signal
from scipy.io import wavfile
from scipy import ndimage


def impwav(a):
    """Imports a wave file as an array where a[1] 
    is the sampling frequency and a[0] is the data"""
    wav = wavfile.read(a)
    out = [wav[1], wav[0]]
    return out


def filtersong(a):
    """highpass iir filter for song."""
    out = []
    b = signal.iirdesign(wp=0.04, ws=0.02, gpass=1, gstop=60, ftype='ellip')
    out.append(signal.filtfilt(b[0], b[1], a[0]))
    out.append(a[1])
    return out


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


def threshold(a, thresh=None):
    """Returns a thresholded array of the same length as input
    with everything below a specific threshold set to 0.
    By default threshold is sigma."""
    if thresh == None: thresh = sc.std(a)
    out = np.where(abs(a) > thresh, a, np.zeros(a.shape))
    return out


# TODO: add option to use scikit-image implementation of Otsu's method
# https://github.com/NickleDave/songdkl/issues/37
def findobject(file):
    """finds objects.  Expects a smoothed rectified amplitude envelope"""
    # heuristic way of establishing threshold
    value = (np.average(file)) / 2
    thresh = threshold(file, value)  # threshold the envelope data
    thresh = threshold(ndimage.convolve(thresh, np.ones(512)), 0.5)  # pad the threshold
    label = (ndimage.label(thresh)[0])  # label objects in the threshold
    objs = ndimage.find_objects(label)  # recover object positions
    return objs
