import pytest
import zarr

from .fixtures.data import SONG_DATA_SUBDIRS, SONG_DATA_ZARR_PATHS

import songdkl


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


@pytest.mark.smoke
def test_numsyls():
    array = zarr.load(ZARR_PATH_TO_USE)
    out = songdkl.numsyls.numsyls(array)
    assert isinstance(out, int)


@pytest.mark.smoke
@pytest.mark.parametrize(
    'ref_path, max_wavs, max_syllables',
    [
        # load data
        (ZARR_PATH_TO_USE, None, None),
        # prep data, default args
        (SUBDIR_TO_USE, None, None),
        # prep data, specified args
        (SUBDIR_TO_USE, None, 25),  # need to use > max num components (default 22)
        # prep data, specified args
        (SUBDIR_TO_USE, 2, 25),  # need to use > max num components (default 22)
    ]
)
def test_numsyls_from_path(ref_path, max_wavs, max_syllables, kwargify):
    kwargs = kwargify(ref_path=ref_path, max_wavs=max_wavs, max_syllables=max_syllables)
    out = songdkl.numsyls.numsyls_from_path(**kwargs)
    assert isinstance(out, int)
