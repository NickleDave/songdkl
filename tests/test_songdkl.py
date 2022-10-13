import pytest

import songdkl


@pytest.mark.smoke
@pytest.mark.parametrize(
    'kwargs',
    [
        {
            'ref_dir_path': './tests/data-for-tests/source/song_data/bk1bk3',
            'compare_dir_path': './tests/data-for-tests/source/song_data/bk1bk9',
            'k_ref': 6,
            'k_compare': 9,
            'max_wavs': 4,
            'max_num_psds': 100,
            'n_basis': 25,
        }
    ]
)
def test_calculate(kwargs):
    score1, score2, n_psds_ref, n_psds_compare = songdkl.calculate(**kwargs)
    assert isinstance(score1, float)
    assert isinstance(score2, float)
    assert isinstance(n_psds_ref, int)
    assert isinstance(n_psds_compare, int)
