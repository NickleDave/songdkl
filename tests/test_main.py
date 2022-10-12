import unittest.mock

import pytest

import songdkl.__main__


@pytest.mark.smoke
@pytest.mark.parametrize(
    'argv, expected_function_called, return_value',
    [
        (
            [
                'calculate',
                './tests/data-for-tests/source/song_data/bk1bk3',
                './tests/data-for-tests/source/song_data/bk1bk9',
                '6',
                '9',
            ],
            'songdkl.__main__.calculate',
            (0.5, 0.5, 50, 50),
        ),
        (
            [
                'numsyls',
                './tests/data-for-tests/source/song_data/bk1bk3',
            ],
            'songdkl.__main__.numsyls',
            6,
        )
    ]
)
def test_main(argv, expected_function_called, return_value):
    with unittest.mock.patch(expected_function_called,
                             autospec=True,
                             return_value=return_value) as patched:
        songdkl.__main__.main(argv)
    assert patched.called
