import pytest
from scipy.io import wavfile

from .data import SONG_DATA_ROOT, SONG_DATA_SUBDIRS


A_WAV_DIR = SONG_DATA_ROOT / 'bk1bk3'


LIST_OF_WAV_PATHS = sorted(A_WAV_DIR.glob('*.wav'))


@pytest.fixture
def list_of_wav_paths():
    return LIST_OF_WAV_PATHS


@pytest.fixture(params=LIST_OF_WAV_PATHS)
def wav_path(request):
    return request.param


@pytest.fixture(params=LIST_OF_WAV_PATHS)
def samp_freq_and_wav_data(request):
    wav_path = request.param
    return wavfile.read(wav_path)


@pytest.fixture(params=LIST_OF_WAV_PATHS)
def wav_data(request):
    wav_path = request.param
    samp_freq, wav_data = wavfile.read(wav_path)
    return wav_data


LIST_OF_ALL_WAV_PATHS = [
    sorted(SONG_DATA_SUBDIR.glob('*.wav'))
    for SONG_DATA_SUBDIR in SONG_DATA_SUBDIRS
]
LIST_OF_ALL_WAV_PATHS = [wav_path_  # don't shadow fixture name
                         for list_of_wav_paths in LIST_OF_ALL_WAV_PATHS
                         for wav_path_ in list_of_wav_paths
                         ]


@pytest.fixture(params=LIST_OF_ALL_WAV_PATHS)
def wav_path_from_all_song_data(request):
    """Fixture that returns path to a .wav file.

    Unlike ``wav_path``, this fixture is parametrized
    with **all** .wav paths in
    './tests/data-for-tests/source/song_data'.
    """
    return request.param
