from __future__ import annotations
import pathlib

import numpy as np
import scipy
import scipy.signal
from scipy.io import wavfile
from scipy import ndimage
from skimage.filters import threshold_otsu


def load_wav(wav_path: str | pathlib.Path) -> (int, np.array):
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


def filtersong(data: np.ndarray) -> np.ndarray:
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
    offset = int(round((len(smooth) - len(data)) / 2))  # calculate offset imposed by convolution
    smooth = smooth[(1 + offset):(len(data) + offset)]  # correct for offset
    return smooth


def findobject(arr: np.ndarray,
               thresh: str | float | int = 'half-otsu') -> list[tuple[slice]]:
    """Segment audio into syllables
    using ``scipy.ndimage.find_objects``.
    Expects a smoothed rectified amplitude envelope,
    e.g. as returned by ``songdkl.audio.smoothrect``.

    Parameters
    ----------
    arr : numpy.ndarray
        Containing smoothed rectified amplitude envelope
        from a .wav file.
    thresh : str, float, int
        Thresholding method.
        If a string, one of {'half-otsu', 'half-average'}.
        When ``threshold='half-otsu'`` then Otsu's method
        is used to find the threshold,
        and half this value is used.
        When ``threshold='half-average'``, then
        the threshold is set to half the average of ``arr``.
        Float or int values will be used directly
        as the threshold. Default is 'half-otsu'.

    Returns
    -------
    objs : list
        Of tuples of slices;
        the segments identified by
        ``scipy.ndimage.find_objects``.
    """
    if thresh == 'otsu':
        thresh_val = threshold_otsu(arr) / 2
    elif thresh == 'half-average':
        # heuristic way of establishing threshold
        thresh_val = (np.average(arr)) / 2
    elif isinstance(thresh, float) or isinstance(thresh, int):
        thresh_val = thresh
    else:
        raise ValueError(
            "'thresh` must be {'otsu', 'half-average'} or a float or int value,"
            f"but was: {thresh}"
        )

    thresh = threshold(arr, thresh_val)  # threshold the envelope data
    thresh = threshold(ndimage.convolve(thresh, np.ones(512)), 0.5)  # pad the threshold
    label = (ndimage.label(thresh)[0])  # label objects in the threshold
    objs = ndimage.find_objects(label)  # recover object positions
    return objs, value


def getsyls(data: np.ndarray,
            rate: int,
            min_syl_dur=10,
            syls_filtered=False) -> tuple[list[np.array], list[tuple[slice]]]:
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
        of ``numpy.ndarray``.
    slices : list
        of tuples of slices.
    """
    data_filtered = filtersong(data)
    slices, threshold_value = findobject(smoothrect(data_filtered, 10, rate))

    # get objects of sufficient duration
    frqs = rate / 1000  # calculate length of a ms in samples
    # use name ``slice_`` to not clobber ``slice`` function
    slices = [slice_ for slice_ in slices if data[slice_].shape[0] > min_syl_dur * frqs]

    if syls_filtered:
        syllables = [x for x in [data_filtered[slice_] for slice_ in slices]]
    else:
        syllables = [x for x in [data[slice_] for slice_ in slices]]

    return syllables, slices, threshold_value


def threshold(a: np.ndarray, thresh: int | float | None = None) -> np.ndarray:
    """Returns a thresholded array of the same length as input
    with everything below a specific threshold set to 0.

    By default threshold is sigma."""
    if thresh is None:
        thresh = a.std()
    return np.where(abs(a) > thresh, a, np.zeros(a.shape))
