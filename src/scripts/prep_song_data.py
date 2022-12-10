"""Script that prepares .zarr files
from all directories in the song_data
directory of the Plos Comp Bio. paper dataset.

This script assumes that the nox session
`download-pcb-dataset` has already been run."""
import pathlib

import songdkl

DATA_ROOT = pathlib.Path('./data')
SONG_DATA_ROOT = DATA_ROOT / 'pcb_data/song_data'
SONG_DATA_SUBDIRS = [
    dir_ for dir_ in SONG_DATA_ROOT.iterdir() if dir_.is_dir()
]

RESULTS_ROOT = pathlib.Path('./results')
PREPD_SONG_DATA_ROOT = RESULTS_ROOT / 'pcb_data/song_data'


def main():
    for song_data_subdir in SONG_DATA_SUBDIRS:
        print(
            f'Preparing dataset from: {song_data_subdir}'
        )
        songdkl.prep.prep_and_save(
            dir_path=song_data_subdir,
            output_dir_path=PREPD_SONG_DATA_ROOT,
        )


if __name__ == '__main__':
    # name == main required here to avoid multiprocess error with dask,
    # see https://github.com/dask/distributed/issues/2520
    main()
