"""Script to make "source" data used for tests,
by creating a subset of the Dryad dataset that
accompanied the original paper.

Assumes that `src/script/download_pcb_dataset.py`
has already been run.
"""
import pathlib
import shutil


PCB_SONG_DATA_ROOT = pathlib.Path("./data/pcb_data/song_data")
SOURCE_TEST_DATA_ROOT_DIR = pathlib.Path("./tests/data-for-tests/source")
SOURCE_TEST_DATA_DST = SOURCE_TEST_DATA_ROOT_DIR / "song_data"

BIRD_IDS = ('bk1bk3', 'bk1bk9')
# make 'small' versions of dataset so tests will run quicker
DATASET_SIZES = ('small', 'all')
N_WAVS_SMALL_DATASET = 5


for dataset_size in DATASET_SIZES:
    for bird_id in BIRD_IDS:
        src = PCB_SONG_DATA_ROOT / bird_id
        dst = SOURCE_TEST_DATA_DST / f'{bird_id}-{dataset_size}'

        if dataset_size == 'all':
            print(
                f'Copying  {src} to {SOURCE_TEST_DATA_DST}\nas {dst.name}'
            )
            shutil.copytree(src, dst)
        elif dataset_size == 'small':
            print(
                f'Copying small subset of {src} to {SOURCE_TEST_DATA_DST}\nas {dst.name}'
            )
            dst.mkdir(exist_ok=True, parents=True)
            wavs = sorted(src.glob('*.wav'))
            for wav in wavs[:N_WAVS_SMALL_DATASET]:
                shutil.copy(wav, dst)


print(
    f'making archive from {SOURCE_TEST_DATA_DST}'
)
shutil.make_archive(
    './tests/data-for-tests/source/source-test-data',
    'gztar',
    root_dir=SOURCE_TEST_DATA_ROOT_DIR,
    base_dir="song_data",  # needs to be relative to root
)
