import pathlib

import pytest

# define all these outside fixtures in case we need to import them elsewhere
# i.e., other fixtures modules or even in tests, to parametrize functions
TEST_DATA_ROOT = pathlib.Path(__file__).parent / '..' / 'data-for-tests'


@pytest.fixture
def test_data_root():
    return TEST_DATA_ROOT


SOURCE_DATA_ROOT = TEST_DATA_ROOT / 'source'


@pytest.fixture
def source_data_root():
    return SOURCE_DATA_ROOT


SONG_DATA_ROOT = SOURCE_DATA_ROOT / 'song_data'


@pytest.fixture
def song_data_root():
    return SONG_DATA_ROOT


SONG_DATA_SUBDIRS = [
    dir_ for dir_ in SONG_DATA_ROOT.iterdir() if dir_.is_dir()
]


SONG_DATA_SUBDIR_MAP = {
    dir_.name: dir_
    for dir_ in SONG_DATA_SUBDIRS
}


@pytest.fixture
def song_data_subdir_factory():
    """Factory parameter that,
    given a bird ID and a dataset size,
    returns the corresponding path"""
    def _song_data_subdir_factory(bird_id, dataset_size):
        return SONG_DATA_SUBDIR_MAP[f'{bird_id}-{dataset_size}']
    return _song_data_subdir_factory


GENERATED_DATA_ROOT = TEST_DATA_ROOT / 'generated'


@pytest.fixture
def generated_data_root():
    return GENERATED_DATA_ROOT


GENERATED_SONG_DATA_ROOT = GENERATED_DATA_ROOT / 'song_data'


@pytest.fixture
def generated_song_data_root():
    return GENERATED_SONG_DATA_ROOT


GENERATED_SONG_DATA_SUBDIRS = [
    dir_ for dir_ in GENERATED_SONG_DATA_ROOT.iterdir()
    if dir_.is_dir()
]


SONG_DATA_ZARR_PATHS = []
for generated_song_data_subdir in GENERATED_SONG_DATA_SUBDIRS:
    zarr_path = sorted(generated_song_data_subdir.glob('*.songdkl.zarr'))
    SONG_DATA_ZARR_PATHS.append(zarr_path[0])


@pytest.fixture
def song_data_zarr_factory():
    """Factory fixture that returns path to a .zarr file
    containing arrays of PSDs from syllable segments,
    generated by ``songdkl.prep.prep_and_save``,
    using data in ./tests/data-for-tests/source/song_data.
    """
    def _song_data_zarr_factory(bird_id, dataset_size):
        return GENERATED_SONG_DATA_ROOT / f'{bird_id}-{dataset_size}' / f'{bird_id}-{dataset_size}.songdkl.zarr'
    return _song_data_zarr_factory
