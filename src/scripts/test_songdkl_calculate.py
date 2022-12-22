#!/usr/bin/env python
# coding: utf-8
import argparse
import pathlib
import sys

import pandas as pd
import songdkl

if not sys.warnoptions:
    # suppress warning about loading .zarr (will remove, it's annoying)
    import warnings
    warnings.simplefilter("ignore")


fath_offspring_csv = './tests/data-for-tests/source/fath_offspring.csv'

fath_df = pd.read_csv(fath_offspring_csv, header=None)
fath_df.columns = ['father', 'son']

sylno_out_csv = './tests/data-for-tests/source/sylno_out.csv'

sylno_df = pd.read_csv(sylno_out_csv, header=None)
sylno_df.columns = ['bird_id', 'k']

song_data_root = pathlib.Path('./results/pcb_data/song_data/')

for col in fath_df.columns:
    fath_df = fath_df[fath_df[col].isin(sylno_df.bird_id.values)].copy()
    fath_df = fath_df.reset_index()


def main(n_ref=None):
    """pairwise comparison between all birds, using syllable numbers from .csv"""
    records = []

    for ref_n, ref in enumerate(fath_df.father.unique()):
        if n_ref:
            if ref_n + 1 > n_ref:  # +1 because zero indexing
                break
        k_ref = int(sylno_df[sylno_df.bird_id == ref].k)
        ref_path = song_data_root / f'{ref}.songdkl.zarr'

        for compare in fath_df.son.values:
            k_compare = int(sylno_df[sylno_df.bird_id == compare].k)
            compare_path = song_data_root / f'{compare}.songdkl.zarr'
            dkl_pq, dkl_qp, n_psds_ref, n_psds_compare = songdkl.songdkl.calculate_from_path(ref_path, compare_path, k_ref, k_ref)
            record = {
                'ref': ref,
                'compare': compare,
                'k_ref': k_ref,
                # NOTE: We use k_ref to match what was done in the paper. From calc_sylno.py:
                # > In our paper we always use the number of syllables in the tutor song for both syllable # values.
                # > This is meant to be conservative, basically give the bird learning the benefit of the doubt
                # > that it actually copied all of the syllables in the tutor song.
                'k_compare': k_ref,
                'DKL_PQ': dkl_pq,
                'DKL_QP': dkl_qp,
                'n_psds_ref': n_psds_ref,
                'n_psds_compare': n_psds_compare,
            }
            print(
                ', '.join([f'{k}: {v}' for k, v in record.items()])
            )
            records.append(record)

            # save every time through loop, in case of script interrupt or crash
            results_df = pd.DataFrame.from_records(records)
            results_df.to_csv('./results/test-songdkl-calculate.csv', index=False)


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--n-ref', type=int
    )
    return parser


parser = get_parser()
args = parser.parse_args()
main(n_ref=args.n_ref)
