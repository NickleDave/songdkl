import pathlib

import numpy as np
import pytest

import songdkl


@pytest.mark.smoke
def test_norm_rand():
    in_ = np.random.rand(3200, 1)
    out = songdkl.syllables.norm(in_)
    assert isinstance(out, np.ndarray)
    np.testing.assert_almost_equal(out.mean(), 0.0)
    np.testing.assert_almost_equal(out.std(), 1.0)


@pytest.mark.smoke
def test_norm_wav_data(wav_data):
    out = songdkl.syllables.norm(wav_data)
    assert isinstance(out, np.ndarray)
    np.testing.assert_almost_equal(out.mean(), 0.0)
    np.testing.assert_almost_equal(out.std(), 1.0)


def syls_from_wav_has_expected_attrs(syls_from_wav):
    assert isinstance(syls_from_wav, songdkl.syllables.SyllablesFromWav)
    assert hasattr(syls_from_wav, 'syls')
    assert isinstance(syls_from_wav.syls, list)
    assert hasattr(syls_from_wav, 'slices')
    assert isinstance(syls_from_wav.syls, list)
    assert hasattr(syls_from_wav, 'rate')
    assert isinstance(syls_from_wav.rate, int)
    assert hasattr(syls_from_wav, 'threshold')
    assert isinstance(syls_from_wav.threshold, float)
    assert hasattr(syls_from_wav, 'wav_path')
    assert isinstance(syls_from_wav.wav_path, pathlib.Path)


@pytest.mark.smoke
def test_SyllablesFromWav():
    fake_syllables = [
        np.random.rand(3200, 1) for _ in range(10)
    ]
    fake_slices = [
        slice(0, fake_syl.shape[0]) for fake_syl in fake_syllables
    ]
    rate = 32000
    threshold = 0.5
    wav_path = pathlib.Path('dummy.wav')
    syls_from_wav = songdkl.syllables.SyllablesFromWav(
        syls=fake_syllables, slices=fake_slices, threshold=threshold, wav_path=wav_path, rate=rate)
    syls_from_wav_has_expected_attrs(syls_from_wav)


@pytest.mark.smoke
def test_get_all_syls(list_of_wav_paths):
    out = songdkl.syllables.get_all_syls(list_of_wav_paths)
    assert isinstance(out, list)
    assert len(out) == len(list_of_wav_paths)
    assert all(
        [isinstance(element, songdkl.syllables.SyllablesFromWav)
         for element in out]
    )
    for element in out:
        syls_from_wav_has_expected_attrs(element)


@pytest.mark.smoke
def test_convert_syl_to_psd(list_of_wav_paths):
    syls_from_wavs = songdkl.syllables.get_all_syls(list_of_wav_paths)
    psds = songdkl.syllables.convert_syl_to_psd(syls_from_wavs)
    assert isinstance(psds, list)
    assert all(
        [isinstance(psd, np.ndarray) for psd in psds]
    )
