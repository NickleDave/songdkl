from __future__ import annotations
import copy
import logging
import pathlib

import crowsetta
import numpy as np
import rich.progress
import zarr

from .syllables import get_all_syls, convert_syl_to_psd, SyllablesFromWav


logger = logging.getLogger(__name__)


def prep(dir_path: str | pathlib.Path,
         max_wavs: int = 120,
         max_num_psds: int = 10000) -> tuple[list[SyllablesFromWav], np.ndarray]:
    """Prepare dataset for use with either
    ``songdkl.numsyls`` or ``songdkl.calculate``.

    For a given directory, load all .wav files,
    segment into syllables, compute PSDs for each segment,
    and return as an array.

    Parameters
    ----------
    dir_path : str, pathlib.Path
    max_wavs : int
        Maximum number of .wav files to use. Default is 120.
    max_num_psds : int
        Maximum number of PSDs to compute. Default is 10k.
    """
    logger.log(
        msg=f'Preparing dataset from dir_path: {dir_path}, '
            f'with max_wavs={max_wavs} and max_num_psds={max_num_psds}.',
        level=logging.INFO
    )
    dir_path = pathlib.Path(dir_path)

    wav_paths = sorted(pathlib.Path(dir_path).glob('*.wav'))
    if max_wavs:
        wav_paths = wav_paths[:max_wavs]

    logger.log(
        msg=f'Segmenting .wav files to get syllables',
        level=logging.INFO
    )
    syls_from_wavs = get_all_syls(wav_paths)
    logger.log(
        msg=f'Computing PSDs from syllable segments',
        level=logging.INFO
    )
    segedpsds = convert_syl_to_psd(syls_from_wavs, max_num_psds)
    return syls_from_wavs, np.array(segedpsds)


def prep_and_save(dir_path: str | pathlib.Path | list[str | pathlib.Path],
                  output_dir_path: str | pathlib.Path | list[str | pathlib.Path] | None = None,
                  max_wavs: int = 120,
                  max_num_psds: int = 10000) -> None:
    """Prepare dataset for use with either
    ``songdkl.numsyls`` or ``songdkl.calculate``.

    For each directory in a list, load all .wav files,
    segment into syllables,
    compute PSDs for each segment,
    and then save resulting set of PSDs,
    persisting to disk with ``zarr``.

    Parameters
    ----------
    dir_path : str, pathlib.Path, list of str or pathlib.Path
    output_dir_path: str, pathlib.Path, list of str or pathlib.Path
        Optional location of where to save output.
        If None, defaults to ``dir_path``.
    max_wavs : int
        Maximum number of .wav files to use. Default is 120.
    max_num_psds : int
        Maximum number of PSDs to compute. Default is 10k.
    """
    if isinstance(dir_path, (str, pathlib.Path)):
        dir_path = [dir_path]
    dir_path = [pathlib.Path(dir_path_) for dir_path_ in dir_path]
    if output_dir_path is None:
        # use `dir_path` as `output_dir_path`
        output_dir_path = copy.deepcopy(dir_path)
    else:
        if isinstance(output_dir_path, (str, pathlib.Path)):
            # use a single output_dir_path for all dir_paths
            output_dir_path = [output_dir_path] * len(dir_path)
        # make sure all items in list are pathlib.Path
        output_dir_path = [pathlib.Path(dir_path_) for dir_path_ in output_dir_path]
        # catch the case where we got a list from user but it was a diff't length than dir_paths
        if len(output_dir_path) != len(dir_path):
            raise ValueError(
                'Number of `output_dir_path`s specified did not match number of `dir_path`s. '
                'Please specify either a single output_dir_path (used for all `dir_path`s, or '
                'one `output_dir_path` per `dir_path`.'
            )

    for a_dir_path, an_output_dir_path in zip(dir_path, output_dir_path):
        logger.log(
            msg=f'Preparing dataset from dir_path: {a_dir_path}',
            level=logging.INFO
        )
        syls_from_wavs, segedpsds = prep(a_dir_path, max_wavs, max_num_psds)
        logger.log(
            msg=f'Saving syllable segmentation in annotation files: {an_output_dir_path}',
            level=logging.INFO
        )
        annots = []
        for syls in rich.progress.track(syls_from_wavs, 'Saving segmentation'):
            segments = []
            for slice_ in syls.slices:
                segment = crowsetta.Segment.from_keyword(
                    label='-',  # dummy label
                    onset_sample=slice_.start,
                    offset_sample=slice_.stop,
                    onset_s=np.around(slice_.start / syls.threshold, decimals=3),  # 3 because milliseconds
                    offset_s=np.around(slice_.stop / syls.threshold, decimals=3),
                )
                segments.append(segment)
            seq = crowsetta.Sequence.from_segments(segments)
            # save segments from each file in simple-seq format
            annot_path = an_output_dir_path / f'{pathlib.Path(syls.wav_path).name}-threshold-{syls.threshold}'
            simpleseq = crowsetta.formats.seq.SimpleSeq(labels=seq.labels, onsets_s=seq.onsets_s,
                                                        offsets_s=seq.offsets_s, annot_path=annot_path)
            simpleseq.to_file(annot_path=annot_path)
            annot = crowsetta.Annotation(seq=seq, annot_path=annot_path, notated_path=syls.wav_path)
            annots.append(annot)

        # save segments from all files in generic-seq format
        generic_seq = crowsetta.formats.seq.GenericSeq(annots=annots)
        generic_seq.to_file(
            annot_path=an_output_dir_path / f'{a_dir_path.name}.annot.csv'
        )

        logger.log(
            msg=f'Saving array to: {an_output_dir_path}',
            level=logging.INFO
        )
        zarr.save(
            str(an_output_dir_path / f'{a_dir_path.name}.songdkl.zarr'),
            segedpsds
        )
