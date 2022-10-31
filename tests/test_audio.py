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
def test_segment_audio(samp_freq_and_wav_data):
    samp_freq, data = samp_freq_and_wav_data
    smoothrect = songdkl.audio.smoothrect(data, WINDOW_FOR_FINDOBJ, samp_freq)
    objs = songdkl.audio.segment_audio(smoothrect)
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
def test_get_syllable_clips_from_audio(samp_freq_and_wav_data):
    samp_freq, data = samp_freq_and_wav_data
    out = songdkl.audio.get_syllable_clips_from_audio(data, samp_freq)
    assert len(out) == 3
    syllables, slices, threshold_value = out
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

    assert isinstance(threshold_value, float)


@pytest.mark.parametrize(
    'threshold_method',
    [
        'half-otsu',
        'half-average',
    ]
)
def test_get_syllable_clips_from_audio_threshold_iou(threshold_method,
                                                     wav_path_from_all_song_data,
                                                     pcb_script_slice_df_factory,
                                                     song_data_subdir_factory,
                                                     segmentation_iou_factory,
                                                     ):
    """Test that the segmentation
    done by ``get_syllable_clips_from_audio_threshold``
    achieves the expected Intersection-Over-Union value
    when compared to segmentation from the original
    PLOS Comp. Bio. scripts
    """
    wav_path = wav_path_from_all_song_data
    bird_id = wav_path.parent.name
    bird_slice_df = pcb_script_slice_df_factory(bird_id)


    rate, audio_arr = songdkl.audio.load_wav(wav_path)
    _, slices, _ = songdkl.audio.get_syllable_clips_from_audio(audio_arr,
                                                               rate,
                                                               threshold=threshold_method)
    label_vec = np.zeros_like(audio_arr)
    for slice_tup in slices:
        slice = slice_tup[0]
        label_vec[slice.start:slice.stop] = 1.0
    reference_df = bird_slice_df[bird_slice_df.filename == wav_path.name]
    reference_start, reference_stop = reference_df.start.values, reference_df.stop.values
    reference_label_vec = np.zeros_like(audio_arr)
    for start, stop in zip(reference_start, reference_stop):
        reference_label_vec[start:stop] = 1.0
    intersection = np.where(
        np.logical_and(label_vec, reference_label_vec)
    )[0].sum()
    union = np.where(
        np.logical_or(label_vec, reference_label_vec)
    )[0].sum()
    iou = (intersection / union) * 100
    expected_iou = segmentation_iou_factory(bird_id, wav_path, threshold_method)
    assert iou == pytest.approx(expected_iou)


@pytest.mark.smoke
@pytest.mark.parametrize(
    'thresh',
    [
        None,
        'std'
    ]
)
def test_apply_threshold(wav_data, thresh):
    if thresh is not None:
        if thresh == 'std':
            # this is default but we pass in directly to test parameter works
            thresh = wav_data.std()
    threshed = songdkl.audio.apply_threshold(wav_data, thresh)
    assert isinstance(threshed, np.ndarray)
