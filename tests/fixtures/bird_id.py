import pytest


TEST_DATA_BIRD_IDS = [
    'bk1bk3',
    'bk1bk9',
]


@pytest.fixture(params=TEST_DATA_BIRD_IDS)
def test_data_bird_id(request):
    """Returns a bird ID,
    which is also the names of sub-directories
    in ./tests/data-for-tests/source/song_data.

    Used when calling factory fixtures to get
    data for testing for a particular bird ID,
    e.g. the .csv of segment onsets and offsets
    for the bird with ID 'bk1bk3'.

    This function is parametrized so that
    it creates one test case per bird ID.
    """
    return request.param
