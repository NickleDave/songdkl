import numpy as np
import songdkl

import pytest


@pytest.mark.smoke
def test_load_wav(wav_path):
    """Test that ``load_wav`` returns expected objects"""
    out = songdkl.audio.load_wav(wav_path)
    assert len(out) == 2
    samp_freq, data = out
    assert isinstance(samp_freq, int)
    assert isinstance(data, np.ndarray)


@pytest.mark.smoke
def test_filtersong(wav_data):
    """Test that ``filtersong`` returns expected objects"""
    filtered = songdkl.audio.filtersong(wav_data)
    assert isinstance(filtered, np.ndarray)
    # TODO: actually test that filtering worked somehow


@pytest.mark.smoke
@pytest.mark.parametrize(
    'window',
    [
        2, 3, 4,
    ]
)
def test_smoothrect(samp_freq_and_wav_data, window):
    samp_freq, data = samp_freq_and_wav_data
    out = songdkl.audio.smoothrect(data, window, samp_freq)
    assert isinstance(out, np.ndarray)
    # TODO: actually test that smoothing works somehow


WINDOW_FOR_FINDOBJ = 2


@pytest.mark.smoke
def test_findobject(samp_freq_and_wav_data):
    samp_freq, data = samp_freq_and_wav_data
    smoothrect = songdkl.audio.smoothrect(data, WINDOW_FOR_FINDOBJ, samp_freq)
    objs = songdkl.audio.findobject(smoothrect)
    assert isinstance(objs, list)
    assert all(
        [isinstance(obj, tuple) for obj in objs]
    )
    assert all(
        [len(obj) == 1 for obj in objs]
    )
    assert all(
        [isinstance(obj[0], slice) for obj in objs]
    )


@pytest.mark.smoke
def test_getsyls(samp_freq_and_wav_data):
    samp_freq, data = samp_freq_and_wav_data
    out = songdkl.audio.getsyls(data, samp_freq)
    assert len(out) == 2
    syllables, slices = out
    assert isinstance(syllables, list)
    assert all(
        [isinstance(syl, np.ndarray) for syl in syllables]
    )

    assert isinstance(slices, list)
    assert all(
        [isinstance(slice_, tuple) for slice_ in slices]
    )
    assert all(
        [len(slice_) == 1 for slice_ in slices]
    )
    assert all(
        [isinstance(slice_[0], slice) for slice_ in slices]
    )


@pytest.mark.smoke
@pytest.mark.parametrize(
    'thresh',
    [
        None,
        'std'
    ]
)
def test_threshold(wav_data, thresh):
    if thresh is not None:
        if thresh == 'std':
            # this is default but we pass in directly to test parameter works
            thresh = wav_data.std()
    threshed = songdkl.audio.threshold(wav_data, thresh)
    assert isinstance(threshed, np.ndarray)
