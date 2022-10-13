import pytest

import songdkl


@pytest.mark.smoke
def test_em_of_gmm_cluster(list_of_wav_paths):
    wav_paths = list_of_wav_paths[:4]  # shorten to make smoke test quick
    syls_from_wavs = songdkl.syllables.get_all_syls(wav_paths)
    segedpsds = songdkl.syllables.convert_syl_to_psd(syls_from_wavs)
    sylno_bic = songdkl.numsyls.em_of_gmm_cluster(segedpsds)
    assert isinstance(sylno_bic, int)


@pytest.mark.smoke
@pytest.mark.parametrize(
    'dir_path',
    [
        './tests/data-for-tests/source/song_data/bk1bk3'
    ]
)
def test_numsyls(dir_path):
    n_syls = songdkl.numsyls.numsyls(dir_path=dir_path)
    assert isinstance(n_syls, int)
