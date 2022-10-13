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


@pytest.mark.smoke
def test_SyllablesFromWav():
    fake_syllables = [
        np.random.rand(3200, 1) for _ in range(10)
    ]
    rate = 3200
    syls_from_wav = songdkl.syllables.SyllablesFromWav(fake_syllables, rate)
    assert isinstance(syls_from_wav, songdkl.syllables.SyllablesFromWav)
    assert hasattr(syls_from_wav, 'syls')
    assert isinstance(syls_from_wav.syls, list)
    assert hasattr(syls_from_wav, 'rate')
    assert isinstance(syls_from_wav.rate, int)


@pytest.mark.smoke
def test_get_all_syls(list_of_wav_paths):
    wav_paths = list_of_wav_paths[:4]  # just need a short list for a smoke test
    out = songdkl.syllables.get_all_syls(wav_paths)
    assert isinstance(out, list)
    assert len(out) == len(wav_paths)
    assert all(
        [isinstance(element, songdkl.syllables.SyllablesFromWav)
         for element in out]
    )


@pytest.mark.smoke
def test_convert_syl_to_psd(list_of_wav_paths):
    wav_paths = list_of_wav_paths[:4]  # just need a short list for a smoke test
    syls_from_wavs = songdkl.syllables.get_all_syls(wav_paths)
    psds = songdkl.syllables.convert_syl_to_psd(syls_from_wavs)
    assert isinstance(psds, list)
    assert all(
        [isinstance(psd, np.ndarray) for psd in psds]
    )
