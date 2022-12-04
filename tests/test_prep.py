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
    data = songdkl.prep.prep(**kwargs)
    assert isinstance(data, np.ndarray)
    if max_num_psds:
        assert data.shape[0] <= max_num_psds


@pytest.mark.smoke
@pytest.mark.parametrize(
    'dir_path, output_dir_path, max_wavs, max_num_psds',
    [
        # default max_wavs, max_num_psds
        (SONG_DATA_SUBDIRS_SMALL[0], None, None, None,),
        (SONG_DATA_SUBDIRS_SMALL, None, None, None),
        (SONG_DATA_SUBDIRS_SMALL[0], str([0])+'out', None, None),
        (SONG_DATA_SUBDIRS_SMALL, [f'{subdir.name}-out' for subdir in SONG_DATA_SUBDIRS_SMALL], None, None),
        # default max_wavs, but specify max_num_psds
        (SONG_DATA_SUBDIRS_SMALL[0], None, None, 50),
        (SONG_DATA_SUBDIRS_SMALL, None, None, 50),
        (SONG_DATA_SUBDIRS_SMALL[0], str([0])+'out', None, 50),
        (SONG_DATA_SUBDIRS_SMALL, [f'{subdir.name}-out' for subdir in SONG_DATA_SUBDIRS_SMALL], None, 50),
        # specify max_wavs and max_num_psds
        (SONG_DATA_SUBDIRS_SMALL[0], None, 2, 50),
        (SONG_DATA_SUBDIRS_SMALL, None, 2, 50),
        (SONG_DATA_SUBDIRS_SMALL[0], str([0]) + 'out', 2, 50),
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
            output_dir_path.mkdir()
        elif isinstance(output_dir_path, list):
            output_dir_path = [
                tmp_path / output_dir_
                for output_dir_ in output_dir_path
            ]
            for p_ in output_dir_path:
                p_.mkdir()
    kwargs = kwargify(dir_path=dir_path, output_dir_path=output_dir_path,
                      max_wavs=max_wavs, max_num_psds=max_num_psds)

    songdkl.prep.prep_and_save(**kwargs)

    if isinstance(dir_path, pathlib.Path):
        dir_path = [dir_path]
    if not output_dir_path:
        for dir_path_ in dir_path:
            expected = dir_path_ / f'{dir_path_.name}.songdkl.zarr'
            assert expected.exists()
            saved = zarr.load(expected)
            assert isinstance(saved, np.ndarray)
            if max_num_psds:
                assert saved.shape[0] <= max_num_psds
    else:
        if isinstance(output_dir_path, pathlib.Path):
            output_dir_path = [output_dir_path]
        for dir_path_, output_dir_path_ in zip(dir_path, output_dir_path):
            expected = output_dir_path_ / f'{dir_path_.name}.songdkl.zarr'
            assert expected.exists()
            saved = zarr.load(expected)
            assert isinstance(saved, np.ndarray)
            if max_num_psds:
                assert saved.shape[0] <= max_num_psds
