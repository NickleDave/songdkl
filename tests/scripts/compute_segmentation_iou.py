"""Script that generates benchmark value used by tests,
the Intersection Over Union (IOU, Jaccard's index)
for two of the methods used to segment audio
when compared with the segmentation from the original
PLOS Comp. Bio. scripts.

This script assumes that the script
'./tests/scripts/make_otsu_test_data.py'
has already been run and its outputs
exist in './tests/data-for-tests/generated'.
"""
import pathlib

import numpy as np
import pandas as pd
import songdkl

HERE = pathlib.Path(__file__).parent
TEST_DATA_ROOT = HERE / '..' / 'data-for-tests'
SOURCE_TEST_DATA_ROOT = TEST_DATA_ROOT / 'source'
GENERATED_TEST_DATA_ROOT = TEST_DATA_ROOT / 'generated'

SLICE_CSVS = sorted(GENERATED_TEST_DATA_ROOT.glob('*slices.csv'))

SLICE_DFS = {}
for slice_csv in SLICE_CSVS:
    df = pd.read_csv(slice_csv)
    bird_id = slice_csv.name.split('-')[0]
    SLICE_DFS[bird_id] = df

records = []
for bird_id in SLICE_DFS.keys():
    bird_slice_df = SLICE_DFS[bird_id]

    bird_wavs_dir = SOURCE_TEST_DATA_ROOT / 'song_data' / bird_id
    bird_wavs = sorted(bird_wavs_dir.glob('*.wav'))

    for threshold_method in ('half-otsu', 'half-average'):
        for wav_path in bird_wavs:
            rate, audio_arr = songdkl.audio.load_wav(wav_path)
            _, slices, _ = songdkl.audio.get_syllable_clips_from_audio(audio_arr,
                                                                       rate,
                                                                       threshold=threshold_method)
            label_vec = np.zeros_like(audio_arr)
            for slice_tup in slices:
                slice = slice_tup[0]
                label_vec[slice.start:slice.stop] = 1.0
            reference_df = bird_slice_df[bird_slice_df.filename == wav_path.name]
            reference_start, reference_stop = reference_df.start.values, reference_df.stop.values
            reference_label_vec = np.zeros_like(audio_arr)
            for start, stop in zip(reference_start, reference_stop):
                reference_label_vec[start:stop] = 1.0
            intersection = np.where(
                np.logical_and(label_vec, reference_label_vec)
            )[0].sum()
            union = np.where(
                np.logical_or(label_vec, reference_label_vec)
            )[0].sum()
            iou = (intersection / union) * 100
            record = {
                'bird_id': bird_id,
                'wav_path': wav_path,
                'threshold_method': threshold_method,
                'intersection': intersection,
                'union': union,
                'iou': iou,
            }
            print(
                ';'.join([f'{k}: {v}' for k, v in record.items()])
            )
            records.append(record)

iou_df = pd.DataFrame.from_records(records)
iou_df.to_csv(
    GENERATED_TEST_DATA_ROOT / 'segmentation-iou.csv',
    index=False
)
