import numpy as np
import pytest

from .fixtures.data import SONG_DATA_SUBDIRS, SONG_DATA_ZARR_PATHS

import songdkl.load

# just use fixed bird for tests
REF_BIRD_ID = 'bk1bk3'
SUBDIR_TO_USE = [
    dir_ for dir_ in SONG_DATA_SUBDIRS if REF_BIRD_ID in dir_.name and dir_.name.endswith('-small')
]
assert len(SUBDIR_TO_USE) == 1
SUBDIR_TO_USE = SUBDIR_TO_USE[0]
ZARR_PATH_TO_USE = [
    path_ for path_ in SONG_DATA_ZARR_PATHS if REF_BIRD_ID in path_.name and '-small' in path_.name
]
assert len(ZARR_PATH_TO_USE) == 1
ZARR_PATH_TO_USE = ZARR_PATH_TO_USE[0]


@pytest.mark.parametrize(
    'data_path, max_wavs, max_syllables',
    [
        # load data
        (ZARR_PATH_TO_USE, None, None),
        # prep data, default args
        (SUBDIR_TO_USE, None, None),
        # prep data, specified args
        (SUBDIR_TO_USE, None, 10),
        # prep data, specified args
        (SUBDIR_TO_USE, 2, 10),
    ]
)
def test_load_or_prep(data_path, max_wavs, max_syllables, kwargify):
    kwargs = kwargify(data_path=data_path, max_wavs=max_wavs, max_syllables=max_syllables)
    out = songdkl.load.load_or_prep(**kwargs)
    if max_syllables:
        assert out.shape[0] <= max_syllables


def test_load_zarr(song_data_zarr_factory,
                   test_data_bird_id):
    zarr_path = song_data_zarr_factory(test_data_bird_id, dataset_size='small')
    out = songdkl.load.load(zarr_path)
    assert isinstance(out, np.ndarray)
