"""Functions to segment syllables or other vocalizations
out of audio, and to convert those segments to
power spectral densities (PSDs).
Used by both ``songdkl`` and ``numsyls`` modules.
"""
from __future__ import annotations
import dataclasses
import pathlib

import dask.bag
import dask.diagnostics.progress
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
    slices: list
        Of ``slice`` objects,
        returned by ``audio.get_syllable_clips_from_audio``
    threshold: float
        Threshold value returned by
        ``audio.get_syllable_clips_from_audio``.
    wav_path : str, pathlib.Path
        Path to .wav file that syllables were generated from.
    rate : int
        Sampling rate of .wav file.
    """
    syls: list[np.ndarray]
    slices: list[slice]
    threshold: float
    wav_path: str | pathlib.Path
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
    bag = dask.bag.from_sequence(wav_paths)

    def _syllabify(wav_path):
        rate, data = audio.load_wav(wav_path)
        syls_this_wav, slices_this_wav, threshold_value = audio.get_syllable_clips_from_audio(data, rate)
        return SyllablesFromWav(syls=syls_this_wav, slices=slices_this_wav, threshold=threshold_value,
                                wav_path=wav_path, rate=rate)

    with dask.diagnostics.progress.ProgressBar():
        syls_from_wavs = bag.map(_syllabify).compute()

    return syls_from_wavs


def convert_syl_to_psd(syls_from_wavs: list[SyllablesFromWav],
                       max_syllables: int | None = None,
                       psds_per_syl: int = 1,
                       ) -> list[np.ndarray]:
    """Convert syllable segments to power spectral densities (PSDs).

    Parameters
    ----------
    syls_from_wavs : list
        Of ``SyllablesFromWav`` instances,
        syllable segments extracted from .wav files.
    max_syllables : int
        Maximum number of segmented syllables to use when generating
        power spectral densities (PSDs).
        Default is None, in which case PSDs will be computed
        for all syllables.
    psds_per_syl : int
        Number of PSDs to compute per syllable. Default is 1.
        If greater than 1, the segment of audio corresponding
        to the syllable is split into ``psd_per_syl`` arrays,
        using the ``numpy.array_split`` function, and a PSD
        is computed for each of those arrays.
        Then they are concatenated to produce a single
        array of features for the syllable,
        used when computing similarity matrices.

    Returns
    -------
    segedpsds : list
        Of ``numpy.ndarray``,
        PSDs from segmented syllables.
    """
    syl_fs_tups = []
    # Make a flattened list of tuples (syllable, sampling frequency).
    # We no longer care what song they came from, just need <= max_segments
    for syls_from_wav in syls_from_wavs:
        fs = syls_from_wav.rate
        syl_fs_tups.extend(
            [(syl, fs) for syl in syls_from_wav.syls]
        )
    syl_fs_tups = syl_fs_tups[:max_syllables]  # only compute PSDs for max_segments segments
    syl_fs_tups_bag = dask.bag.from_sequence(syl_fs_tups)

    def _to_psd(syl_fs_tup):
        syl, fs = syl_fs_tup
        nfft = int(round(2 ** 14 / 32000.0 * fs))
        segstart = int(round(600 / (fs / float(nfft))))
        segend = int(round(16000 / (fs / float(nfft))))
        if psds_per_syl > 1:
            x_for_psd = np.array_split(syl, psds_per_syl)
        else:
            x_for_psd = [syl]
        spsd = []
        for x in x_for_psd:
            Pxx, _ = matplotlib.mlab.psd(norm(x), NFFT=nfft, Fs=fs)
            spsd.append(
                Pxx[segstart:segend]
            )
        spsd = norm(
            np.concatenate(spsd)
        )
        return spsd

    with dask.diagnostics.progress.ProgressBar():
        segedpsds = syl_fs_tups_bag.map(_to_psd).compute()

    return segedpsds
