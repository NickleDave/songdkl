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


BIRD_ID_SONG_DATA_SUBDIR_MAP = {
    dir_.name: dir_
    for dir_ in SONG_DATA_SUBDIRS
}


@pytest.fixture
def song_data_subdir_factory():
    """Factory parameter that, given a bird ID,
    returns the corresponding """
    def _song_data_subdir_factory(bird_id):
        return BIRD_ID_SONG_DATA_SUBDIR_MAP[bird_id]
    return _song_data_subdir_factory


GENERATED_DATA_ROOT = TEST_DATA_ROOT / 'generated'


@pytest.fixture
def generated_data_root():
    return SOURCE_DATA_ROOT
