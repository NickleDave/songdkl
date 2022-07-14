import numpy as np
import scipy
import scipy.signal
from scipy.io import wavfile
from scipy import ndimage


def load_wav(wav_path):
    """Load .wav file from path.

    Parameters
    ----------
    wav_path : str, pathlib.Path
        Path to a .wav file.

    Returns
    -------
    rate : int
        Sampling rate in Hz.
    data : np.ndarray
        Data from .wav file.
    """
    return wavfile.read(wav_path)


def filtersong(data: np.ndarray):
    """Apply highpass iir filter to ``data`` to remove low-frequency noise.
    """
    b, a = scipy.signal.iirdesign(wp=0.04, ws=0.02, gpass=1, gstop=60, ftype='ellip')
    return scipy.signal.filtfilt(b, a, data)


def smoothrect(data: np.ndarray,
               window: int = 2,
               rate: int = 32000) -> np.ndarray:
    """Smooth and rectify audio.

    Parameters
    ----------
    data : np.ndarray
        Audio data.
    window : int
        Default is 2.
    rate : int
        Sampling rate.
        Default is 32000.

    Returns
    -------
    smooth : np.ndarray
        Smoothed rectified audio.
    """
    le = int(round(rate * window / 1000))  # calculate boxcar kernel length
    h = np.ones(le) / le  # make boxcar
    smooth = np.convolve(h, abs(data))  # convolve boxcar with signal
    offset = int(round((len(smooth) - len(data) / 2))  # calculate offset imposed by convolution
    smooth = smooth[(1 + offset):(len(data) + offset)]  # correct for offset
    return smooth


def getsyls(data: np.ndarray,
            rate: int,
            min_syl_dur=10,
            syls_filtered=False):
    """Return a ``list`` of syllables segmented out of an array of audio.

    Parameters
    ----------
    data : np.ndarray
        Audio data.
    rate : int
        Sampling rate, in Hz.
    min_syl_dur : int
        Minimum syllable duration, in milliseconds.
    syls_filtered : bool
        If True, use audio data to which high-pass filter
        has been applied. Default is False.
        Using data filtered prior to PSD calculation helps
        if data are contaminated with low frequency noise.

    Returns
    -------
    syllables : list
        of ``numpy.ndarray``
    slices : np.slice
    """
    data_filtered = filtersong(data)
    slices = findobject(smoothrect(data_filtered, 10, rate))

    # get objects of sufficient duration
    frqs = rate / 1000  # calculate length of a ms in samples
    slices = [slice for slice in slices if int(len(data[slices])) > min_syl_dur * frqs]

    if syls_filtered:
        syllables = [x for x in [data_filtered[slice] for slice in slices]]
    else:
        syllables = [x for x in [data[slice] for slice in slices]]

    return syllables, slices


def threshold(a, thresh=None):
    """Returns a thresholded array of the same length as input
    with everything below a specific threshold set to 0.

    By default threshold is sigma."""
    if thresh is None:
        thresh = scipy.std(a)
    return np.where(abs(a) > thresh, a, np.zeros(a.shape))


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
