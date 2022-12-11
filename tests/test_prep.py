import copy
import pathlib

import numpy as np
import pytest
import shutil
import zarr

from .fixtures.data import SONG_DATA_SUBDIRS

import songdkl.prep


# use just the '-small' subdirs so smoke tests are quicker
SONG_DATA_SUBDIRS_SMALL = [
    subdir
    for subdir in SONG_DATA_SUBDIRS
    if subdir.name.endswith('-small')
]


@pytest.mark.smoke
@pytest.mark.parametrize('dir_path', SONG_DATA_SUBDIRS_SMALL)
@pytest.mark.parametrize('max_wavs', [None, 5, 10])
@pytest.mark.parametrize('max_num_psds', [None, 10, 100])
def test_prep(dir_path, max_wavs, max_num_psds, kwargify):
    kwargs = kwargify(dir_path=dir_path, max_wavs=max_wavs, max_num_psds=max_num_psds)
    out = songdkl.prep.prep(**kwargs)
    assert len(out) == 2
    syls_from_wavs, segedpsds = out
    assert isinstance(syls_from_wavs, list)
    assert all([isinstance(syls_from_wav, songdkl.syllables.SyllablesFromWav)
                for syls_from_wav in syls_from_wavs])
    if max_wavs:
        assert len(syls_from_wavs) <= max_wavs
    assert isinstance(segedpsds, np.ndarray)
    if max_num_psds:
        assert segedpsds.shape[0] <= max_num_psds


@pytest.mark.smoke
@pytest.mark.parametrize(
    'dir_path, output_dir_path, max_wavs, max_num_psds',
    [
        # default max_wavs, max_num_psds
        (SONG_DATA_SUBDIRS_SMALL[0], None, None, None,),
        (SONG_DATA_SUBDIRS_SMALL, None, None, None),
        (SONG_DATA_SUBDIRS_SMALL[0], str(SONG_DATA_SUBDIRS_SMALL[0]) + '-out', None, None),
        (SONG_DATA_SUBDIRS_SMALL, [f'{subdir.name}-out' for subdir in SONG_DATA_SUBDIRS_SMALL], None, None),
        # default max_wavs, but specify max_num_psds
        (SONG_DATA_SUBDIRS_SMALL[0], None, None, 50),
        (SONG_DATA_SUBDIRS_SMALL, None, None, 50),
        (SONG_DATA_SUBDIRS_SMALL[0], str(SONG_DATA_SUBDIRS_SMALL[0]) + '-out', None, 50),
        (SONG_DATA_SUBDIRS_SMALL, [f'{subdir.name}-out' for subdir in SONG_DATA_SUBDIRS_SMALL], None, 50),
        # specify max_wavs and max_num_psds
        (SONG_DATA_SUBDIRS_SMALL[0], None, 2, 50),
        (SONG_DATA_SUBDIRS_SMALL, None, 2, 50),
        (SONG_DATA_SUBDIRS_SMALL[0], str(SONG_DATA_SUBDIRS_SMALL[0]) + '-out', 2, 50),
        (SONG_DATA_SUBDIRS_SMALL, [f'{subdir.name}-out' for subdir in SONG_DATA_SUBDIRS_SMALL], 2, 50),
    ]
)
def test_prep_and_save(dir_path, output_dir_path, max_wavs, max_num_psds, tmp_path, kwargify):
    if isinstance(dir_path, pathlib.Path):
        dir_path = shutil.copytree(dir_path, tmp_path, dirs_exist_ok=True)
    elif isinstance(dir_path, list):
        dir_path = [
            shutil.copytree(dir_path_, tmp_path / dir_path_.name, dirs_exist_ok=True) for dir_path_ in dir_path
        ]
    if output_dir_path:
        if isinstance(output_dir_path, (str, pathlib.Path)):
            output_dir_path = tmp_path / output_dir_path
            if output_dir_path.exists():
                shutil.rmtree(output_dir_path)
            output_dir_path.mkdir()
        elif isinstance(output_dir_path, list):
            output_dir_path = [
                tmp_path / output_dir_
                for output_dir_ in output_dir_path
            ]
            for p_ in output_dir_path:
                if p_.exists():
                    shutil.rmtree(p_)
                p_.mkdir()
    kwargs = kwargify(dir_path=dir_path, output_dir_path=output_dir_path,
                      max_wavs=max_wavs, max_num_psds=max_num_psds)

    songdkl.prep.prep_and_save(**kwargs)

    if isinstance(dir_path, pathlib.Path):
        dir_path = [dir_path]
    if output_dir_path is None:
        # use `dir_path` as `output_dir_path`
        output_dir_path = copy.deepcopy(dir_path)
    elif isinstance(output_dir_path, pathlib.Path):
        output_dir_path = [output_dir_path]
    for a_dir_path, an_output_dir_path in zip(dir_path, output_dir_path):
        wav_paths = sorted(a_dir_path.glob('*.wav'))
        if max_wavs:
            wav_paths = wav_paths[:max_wavs]
        for wav_path in wav_paths:
            simple_seq_path = sorted(an_output_dir_path.glob(f'{wav_path.name}-threshold-*'))
            assert len(simple_seq_path) == 1
            simple_seq_path = simple_seq_path[0]
            assert simple_seq_path.exists()
        generic_seq_path = an_output_dir_path / f'{a_dir_path.name}.annot.csv'
        assert generic_seq_path.exists()

        # NOTE an_output_dir_path can be == dir_path here
        expected = an_output_dir_path / f'{a_dir_path.name}.songdkl.zarr'
        assert expected.exists()
        saved = zarr.load(expected)
        assert isinstance(saved, np.ndarray)
        if max_num_psds:
            assert saved.shape[0] <= max_num_psds
