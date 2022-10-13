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

