"""Run ``songdkl numsyls`` on all prep'd PCB data.
Assumes that `prep-pcb-data` has already been run.
"""
import argparse
import pathlib

import pandas as pd
import songdkl


BIRDS_WITH_WAV_ERRORS = [
    # TODO: fix this
]

RESULTS_ROOT = pathlib.Path('./results')
PREPD_SONG_DATA_ROOT = RESULTS_ROOT / 'pcb_data/song_data'

REF_PATHS = sorted(PREPD_SONG_DATA_ROOT.glob('*.zarr'))


def main(n_ref_paths=None,
         n_times_run_numsyls=4):
    if n_ref_paths:
        ref_paths = REF_PATHS[:n_ref_paths]
    else:
        ref_paths = REF_PATHS

    records = []

    for ref_path in ref_paths:
        bird_id = ref_path.name.split('.')[0]  # name will be something like 'bk1bk9.songdkl.zarr'
        for run in range(n_times_run_numsyls):
            n_syls = songdkl.numsyls.numsyls_from_path(ref_path)
            record = {
                'bird_id': bird_id,
                'n_syls': n_syls,
                'run': run,
            }
            print(
                ', '.join([f'{k}: {v}' for k, v in record.items()])
            )
            records.append(record)

        # save every time through loop in case of crash in the middle
        df = pd.DataFrame.from_records(records)
        df.to_csv(
            './results/runall-numsyls.csv'
        )


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--n-ref-paths', type=int
    )
    parser.add_argument(
        '--n-times-run-numsyls', type=int,
        default=4,
    )
    return parser


parser = get_parser()
args = parser.parse_args()
main(n_ref_paths=args.n_ref_paths, n_times_run_numsyls=args.n_times_run_numsyls)
