import shutil

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
def test_numsyls(list_of_wav_paths, tmp_path):
    tmp_dir_path = tmp_path / 'bk1bk3'
    tmp_dir_path.mkdir(exist_ok=True)
    wav_paths = list_of_wav_paths[:4]  # shorten to make smoke test quick
    for wav_path in wav_paths:
        shutil.copy(wav_path, tmp_dir_path)

    n_syls = songdkl.numsyls.numsyls(dir_path=tmp_dir_path)

    assert isinstance(n_syls, int)
