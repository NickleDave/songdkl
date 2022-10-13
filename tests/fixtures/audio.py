import pytest
from scipy.io import wavfile

from .data import SONG_DATA_ROOT


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
