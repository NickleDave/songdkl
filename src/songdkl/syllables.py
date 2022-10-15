"""Functions to segment syllables or other vocalizations
out of audio, and to convert those segments to
power spectral densities (PSDs).
Used by both ``songdkl`` and ``numsyls`` modules.
"""
from __future__ import annotations
import dataclasses
import pathlib
from typing import Optional

import matplotlib.mlab
import numpy as np

from . import audio


def norm(arr: np.ndarray) -> np.ndarray:
    """Normalize an array by
    subtracting off the mean
    and dividing by the standard deviation.

    Parameters
    ----------
    arr : numpy.ndarray
        A numpy array

    Returns
    -------
    normed : numpy.ndarray
        ``arr`` with
    """
    arr = np.array(arr)
    return (arr - arr.mean()) / arr.std()


@dataclasses.dataclass
class SyllablesFromWav:
    """
    Dataclass representing
    all the syllables
    found by segmenting a
    .wav file.

    Attributes
    ----------
    syls : list
        Of ``numpy.ndarray``, syllables
        returned by ``songdkl.audio.getsyls``
    rate : int
        Sampling rate of .wav file.
    """
    syls: list[np.ndarray]
    rate: int


def get_all_syls(wav_paths: list[str] | list[pathlib.Path]) -> list[SyllablesFromWav]:
    """Get all syllables from a list of .wav files.

    Parameters
    ----------
    wav_paths : list
        Of str, absolute paths to .wav files

    Returns
    -------
    syls_from_wavs : list
        of ``SyllablesFromWav`` instances,
        same length as ``wav_paths``.
        Each ``SyllablesFromWav`` has an
        attribute ``syls``, a list of
        ``numpy.ndarray``s, and an attribute
        ``rate``, the sampling rate
        for the .wav file the syllables
        are taken from.
    """
    syls_from_wavs = []
    slices_from_wavs = []
    threshold_vals = []
    for wav_path in wav_paths:
        rate, data = audio.load_wav(wav_path)
        syls_this_wav, slices_this_wav, threshold_value = audio.getsyls(data, rate)
        syls_from_wavs.append(
            SyllablesFromWav(syls=syls_this_wav, rate=rate)
        )
        slices_from_wavs.append(slices_this_wav)
        threshold_vals.append(threshold_value)

    # ---- sticking in chunk of code to
    csv = []
    for ind, filename in enumerate(wav_paths):
        for slice_tup in slices_from_wavs[ind]:
            slice_ = slice_tup[0]  # [0][0] because we get back tuples of (slice, None)
            csv.append([ind, filename, slice_.start, slice_.stop])  # one row of csv

    csv = np.array(csv, dtype=np.object)
    bird_id = wav_paths[0].parent.name
    fname = bird_id + '-py-pkg-skimage-otsu-slices.csv'
    csv_path = './tests/data-for-tests/generated/' + fname

    np.savetxt(
        csv_path,
        csv,
        fmt=['%u', '%s', '%u', '%u'],
        delimiter=",",
        header="filenum,filename,start,stop"
    )

    threshold_vals = np.array(threshold_vals)
    np.save('./tests/data-for-tests/generated/' + bird_id + '-threshold-vals-py-pkg.npy', threshold_vals)

    quit()

    return syls_from_wavs


def convert_syl_to_psd(syls_from_wavs: list[SyllablesFromWav],
                       max_num_psds: Optional[int] = None) -> list[np.ndarray]:
    """Convert syllable segments to power spectral densities (PSDs).

    Parameters
    ----------
    syls_from_wavs : list
        Of ``SyllablesFromWav`` instances,
        syllable segments extracted from .wav files.
    max_num_psds : int
        Maximum number of PSDs to calculate.
        Default is None, in which case
        PSDs will be computed for all syllables.

    Returns
    -------
    segedpsds : list
        Of ``numpy.ndarray``,
        PSDs from segmented syllables.
    """
    segedpsds = []
    for syls_from_wav in syls_from_wavs:
        fs = syls_from_wav.rate
        nfft = int(round(2 ** 14 / 32000.0 * fs))
        segstart = int(round(600 / (fs / float(nfft))))
        segend = int(round(16000 / (fs / float(nfft))))
        psds = []
        for syl in syls_from_wav.syls:
            Pxx, _ = matplotlib.mlab.psd(norm(syl), NFFT=nfft, Fs=fs)
            psds.append(Pxx)
        spsds = [norm(psd[segstart:segend]) for psd in psds]
        segedpsds.extend(spsds)
        if max_num_psds:
            if len(segedpsds) > max_num_psds:
                break

    if max_num_psds:
        # since we are likely over `max_num_psds` even after `break` above
        segedpsds = segedpsds[:max_num_psds]

    return segedpsds
