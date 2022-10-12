"""Script to make "source" data used for tests,
by creating a subset of the Dryad dataset that
accompanied the original paper.

Assumes that `src/script/download_pcb_dataset.py`
has already been run.
"""
import pathlib
import shutil
import time


PCB_SONG_DATA_ROOT = pathlib.Path("./data/pcb_data/song_data")
SOURCE_TEST_DATA_ROOT_DIR = pathlib.Path("./tests/data-for-tests/source")
SOURCE_TEST_DATA_DST = SOURCE_TEST_DATA_ROOT_DIR / "song_data"

bird_ids = ('bk1bk3', 'bk1bk9')
for bird_id in bird_ids:
    src = PCB_SONG_DATA_ROOT / bird_id
    dst = SOURCE_TEST_DATA_DST / bird_id
    print(
        f'copying {src} to {SOURCE_TEST_DATA_DST}'
    )
    shutil.copytree(src, dst)


print(
    f'making archive from {SOURCE_TEST_DATA_DST}'
)
shutil.make_archive(
    './tests/data-for-tests/source/source-test-data',
    'gztar',
    root_dir=SOURCE_TEST_DATA_ROOT_DIR,
    base_dir="song_data",  # needs to be relative to root
)
