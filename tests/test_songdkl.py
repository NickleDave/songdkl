import pytest
import zarr

import songdkl


@pytest.mark.smoke
@pytest.mark.parametrize(
    'ref_psds_path, compare_psds_path, k_ref, k_compare',
    [
        (
            './tests/data-for-tests/generated/song_data/bk1bk3-small/bk1bk3-small.songdkl.zarr',
            './tests/data-for-tests/generated/song_data/bk1bk9-small/bk1bk9-small.songdkl.zarr',
            6, 9,
        ),
        (
            './tests/data-for-tests/generated/song_data/bk1bk9-small/bk1bk9-small.songdkl.zarr',
            './tests/data-for-tests/generated/song_data/bk1bk3-small/bk1bk3-small.songdkl.zarr',
            9, 6,
        ),
    ]
)
def test_calculate(ref_psds_path, compare_psds_path, k_ref, k_compare):
    psds_ref = zarr.load(ref_psds_path)
    psds_compare = zarr.load(compare_psds_path)
    out = songdkl.songdkl.calculate(psds_ref, psds_compare, k_ref, k_compare)
    assert len(out) == 4
    score1, score2, n_psds_ref, n_psds_compare = out
    assert isinstance(score1, float)
    assert isinstance(score2, float)
    assert isinstance(n_psds_ref, int)
    assert isinstance(n_psds_compare, int)


@pytest.mark.smoke
@pytest.mark.parametrize(
    'ref_path, compare_path, k_ref, k_compare, max_wavs, max_syllables',
    [
        (
            './tests/data-for-tests/source/song_data/bk1bk3-small',
            './tests/data-for-tests/source/song_data/bk1bk9-small',
            6, 9, 4, 25,
        ),
        (
            './tests/data-for-tests/source/song_data/bk1bk9-small',
            './tests/data-for-tests/source/song_data/bk1bk3-small',
            9, 6, 4, 25,
        ),
        (
            './tests/data-for-tests/generated/song_data/bk1bk3-small/bk1bk3-small.songdkl.zarr',
            './tests/data-for-tests/generated/song_data/bk1bk9-small/bk1bk9-small.songdkl.zarr',
            6, 9, None, None
        ),
        (
            './tests/data-for-tests/generated/song_data/bk1bk9-small/bk1bk9-small.songdkl.zarr',
            './tests/data-for-tests/generated/song_data/bk1bk3-small/bk1bk3-small.songdkl.zarr',
            9, 6, None, None,
        ),
    ]
)
def test_calculate_from_path(ref_path, compare_path, k_ref, k_compare, max_wavs, max_syllables, kwargify):
    kwargs = kwargify(ref_path=ref_path, compare_path=compare_path,
                      k_ref=k_ref, k_compare=k_compare, max_wavs=max_wavs, max_syllables=max_syllables)
    out = songdkl.songdkl.calculate_from_path(**kwargs)
    assert len(out) == 4
    score1, score2, n_psds_ref, n_psds_compare = out
    assert isinstance(score1, float)
    assert isinstance(score2, float)
    assert isinstance(n_psds_ref, int)
    assert isinstance(n_psds_compare, int)
