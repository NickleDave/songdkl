"""Make the 'generated' test data,
i.e., make outputs using ``songdkl``
from inputs that would be the source/raw
data files.
This lets us run tests without re-creating
generated data for each unit test.
"""
import pathlib
import shutil

import songdkl


TEST_DATA_ROOT = pathlib.Path(__file__).parent / '..' / 'data-for-tests'
SOURCE_DATA_ROOT = TEST_DATA_ROOT / 'source'
SONG_DATA_ROOT = SOURCE_DATA_ROOT / 'song_data'
SONG_DATA_SUBDIRS = [
    dir_ for dir_ in SONG_DATA_ROOT.iterdir() if dir_.is_dir()
]

GENERATED_DATA_ROOT = TEST_DATA_ROOT / 'generated'
GENERATED_SONG_DATA_ROOT = GENERATED_DATA_ROOT / 'song_data'


def prep_and_save():
    """Prepare arrays as done by ``songdkl.prep.prep`` function,
    and save as .zarr files in compressed format,
    to use in tests."""
    for song_data_subdir in SONG_DATA_SUBDIRS:
        print(
            f"Preparing data from: {song_data_subdir}"
        )
        output_dir_path = GENERATED_SONG_DATA_ROOT / song_data_subdir.name
        output_dir_path.mkdir(exist_ok=True, parents=True)
        songdkl.prep.prep_and_save(dir_path=song_data_subdir,
                                   output_dir_path=output_dir_path)


def main():
    # --- main script ----
    print(
        "Generating data for tests."
    )

    print(
        "Preparing and saving arrays of PSDs from syllable segments."
    )
    prep_and_save()

    print(
        f'making archive from {GENERATED_SONG_DATA_ROOT}'
    )
    shutil.make_archive(
        './tests/data-for-tests/generated/generated-test-data',
        'gztar',
        root_dir=GENERATED_DATA_ROOT,
        # specify `base_dir` since we only want to archive song_data
        base_dir="song_data",  # needs to be written relative to root
    )

    print(
        "Done preparing generated data for tests."
    )


if __name__ == '__main__':
    main()
