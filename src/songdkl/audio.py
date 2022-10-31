from __future__ import annotations
import pathlib

import numpy as np
import scipy
import scipy.signal
from scipy.io import wavfile
from scipy import ndimage
from skimage.filters import threshold_otsu


def load_wav(wav_path: str | pathlib.Path) -> tuple[int, np.array]:
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


def filtersong(audio_arr: np.ndarray) -> np.ndarray:
    """Apply highpass iir filter to ``audio_arr`` to remove low-frequency noise.
    """
    b, a = scipy.signal.iirdesign(wp=0.04, ws=0.02, gpass=1, gstop=60, ftype='ellip')
    return scipy.signal.filtfilt(b, a, audio_arr)


def smoothrect(audio_arr: np.ndarray,
               window: int = 2,
               rate: int = 32000) -> np.ndarray:
    """Smooth and rectify audio.

    Parameters
    ----------
    audio_arr : np.ndarray
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
    smooth = np.convolve(h, abs(audio_arr))  # convolve boxcar with signal
    offset = int(round((len(smooth) - len(audio_arr)) / 2))  # calculate offset imposed by convolution
    smooth = smooth[(1 + offset):(len(audio_arr) + offset)]  # correct for offset
    return smooth


def apply_threshold(audio_arr: np.ndarray, thresh: int | float | None = None) -> np.ndarray:
    """Returns a thresholded array of the same length as input
    with everything below a specific threshold set to 0.

    By default, threshold is sigma."""
    if thresh is None:
        thresh = audio_arr.std()
    return np.where(abs(audio_arr) > thresh, audio_arr, np.zeros(audio_arr.shape))


def segment_audio(audio_arr: np.ndarray) -> list[tuple[slice]]:
    """Segment audio into clips containing syllables,
    using ``scipy.ndimage.find_objects``.
    Expects ``audio_arr`` to have zero elements, e.g.,
    because ``apply_threshold`` has been applied to it.

    Continuous non-zero segments in ``audio_arr``
    are applied labels with ``scipy.ndimage.label``,
    and the indices of these segments are returned,
    as produced by ``scipy.ndimage.find_objects``.

    Parameters
    ----------
    audio_arr : numpy.ndarray
        Containing smoothed rectified amplitude envelope
        from a .wav file.

    Returns
    -------
    objs : list
        Of tuples of slices;
        the segments identified by
        ``scipy.ndimage.find_objects``.
    """
    label, _ = ndimage.label(audio_arr)  # label objects in the threshold
    objs = ndimage.find_objects(label)  # recover object positions
    return objs


def get_syllable_clips_from_audio(audio_arr: np.ndarray,
                                  rate: int,
                                  min_syl_dur=10,
                                  threshold: str | float | int = 'half-otsu',
                                  syls_filtered=False
                                  ) -> tuple[list[np.array], list[tuple[slice]], float | int]:
    """Return a ``list`` of syllables segmented out of an array of audio.

    Parameters
    ----------
    audio_arr : np.ndarray
        Audio data.
    rate : int
        Sampling rate, in Hz.
    min_syl_dur : int
        Minimum syllable duration, in milliseconds.
    threshold : str, float, int
        Thresholding method.
        If a string, one of {'half-otsu', 'half-average'}.
        When ``threshold='half-otsu'`` then Otsu's method
        is used to find the threshold,
        and half this value is used.
        When ``threshold='half-average'``, then
        the threshold is set to half the average of ``arr``.
        Float or int values will be used directly
        as the threshold. Default is 'half-otsu'.
    syls_filtered : bool
        If True, use audio data to which high-pass filter
        has been applied. Default is False.
        Using data filtered prior to PSD calculation helps
        if data are contaminated with low frequency noise.

    Returns
    -------
    syllable_clips : list
        Of ``numpy.ndarray``.
    slices : list
        Of tuples of slices.
    threshold_val : float or int
        Threshold value obtained
        using the method specified by
        ``threshold`` argument.
    """
    if isinstance(threshold, str):
        if threshold not in {'half-otsu', 'half-average'}:
            raise ValueError(
                "If 'threshold` is a string, it must be one of {'half-otsu', 'half-average'},"
                f"but was: {threshold}"

            )

    audio_filtered = filtersong(audio_arr)
    audio_smoothrect = smoothrect(audio_filtered, 10, rate)

    if threshold == 'half-otsu':
        # Dividing by two here is heuristic.
        # Value returned by Otsu would be too high otherwise.
        threshold_val = threshold_otsu(audio_smoothrect) / 2
    elif threshold == 'half-average':
        # dividing by two here is heuristic, as is just taking the average
        threshold_val = np.average(audio_smoothrect) / 2
    elif isinstance(threshold, float) or isinstance(threshold, int):
        threshold_val = threshold
    else:
        raise ValueError(
            "'thresh` must be {'half-otsu', 'half-average'} or a float or int value,"
            f"but was: {threshold}"
        )

    audio_thresholded = apply_threshold(audio_smoothrect, threshold_val)  # threshold the envelope data
    audio_thresholded = apply_threshold(
        ndimage.convolve(audio_thresholded, np.ones(512)), 0.5
    )  # pad the threshold

    slices = segment_audio(audio_thresholded)

    # get objects of sufficient duration
    frqs = rate / 1000  # calculate length of a ms in samples
    # use name ``slice_`` to not clobber ``slice`` function
    slices = [slice_ for slice_ in slices if audio_arr[slice_].shape[0] > min_syl_dur * frqs]

    if syls_filtered:
        syllable_clips = [x for x in [audio_filtered[slice_] for slice_ in slices]]
    else:
        syllable_clips = [x for x in [audio_arr[slice_] for slice_ in slices]]

    return syllable_clips, slices, threshold_val
