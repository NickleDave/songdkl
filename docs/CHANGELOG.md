# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
- Make it easier to rapidly iterate on experiments with Dryad dataset 
  from Plos Comp. Bio. paper by adding scripts that run `songdkl.prep` 
  on all the the `song_data` then pack into .tar files, 
  and a `nox` session that will download all those files off of 
  [the OSF repo](https://osf.io/wgrzx).
  [#73](https://github.com/NickleDave/songdkl/pull/73).
  Fixes [#61](https://github.com/NickleDave/songdkl/issues/61).

## [0.4.0]
### Added
- Have `prep_and_save` also save the segmentation of .wav files,
  so that it can be more easily inspected
  [#71](https://github.com/NickleDave/songdkl/pull/71). 
  Segmentation is saved as annotated sequences with
  onsets, offsets, and dummy labels in .csv files
  Fixes [#68](https://github.com/NickleDave/songdkl/issues/68).
- Add ability to specify hyperparameters and other arguments 
  to the Gaussian mixture model, by adding `gmm_kwargs` parameter 
  to the `numsyls.numsyls` and `songdkl.calculate` functions, 
  and by adding corresponding arguments to the command-line interface
  [#72](https://github.com/NickleDave/songdkl/pull/72).
  Fixes [#69](https://github.com/NickleDave/songdkl/issues/70).

### Fixed
- Fix cross-validation done by `numsyls` function, 
  so that we measure BIC on each held out split after training 
  on the remaining splits 
  [#72](https://github.com/NickleDave/songdkl/pull/72).
  Fixes [#69](https://github.com/NickleDave/songdkl/issues/69).
  Before this we fit then measured BIC on each split separately, 
  which is not technically wrong
  but likely increased variance of the measure instead of 
  decreasing it.

## [0.3.1]
### Fixed
- Fix `songdkl prep` command option `--output-dir-path` 
  so user can specify one output dir for all `dir_path`s
  [#67](https://github.com/NickleDave/songdkl/pull/67).

## [0.3.0]
### Added
- Add logging and progress bars
  [#60](https://github.com/NickleDave/songdkl/pull/60).
  Fixes [#22](https://github.com/NickleDave/songdkl/issues/22).
- Add functions to prepare data for `songdkl.calculate` 
  and `numsyls.numsyls` functions, and save and load that data 
  as numpy arrays. Also add a `prep` command to the cli that 
  uses these functions 
  [#62](https://github.com/NickleDave/songdkl/pull/62).
  Fixes [#47](https://github.com/NickleDave/songdkl/issues/47),
  [#25](https://github.com/NickleDave/songdkl/issues/25),
  and [#19](https://github.com/NickleDave/songdkl/issues/19).
- Add use of `dask` to parallelize data prep
  [#63](https://github.com/NickleDave/songdkl/pull/63).
  Fixes [#18](https://github.com/NickleDave/songdkl/issues/18).
- Add cli options to control `numsyls` after refactoring it, 
  and clean up other parameters so they all use dashes
  [#66](https://github.com/NickleDave/songdkl/pull/63).
  Fixes [#27](https://github.com/NickleDave/songdkl/issues/27).

### Changed
- Combine `numsyls` and `em_of_gmm_cluster` into a single function,
  adding the `em_of_gmm_cluster` parameters to `numsyls` so a user 
  can easily control them, e.g. through corresponding cli options
  [#66](https://github.com/NickleDave/songdkl/pull/63).
  Fixes [#64](https://github.com/NickleDave/songdkl/issues/64).

## [0.2.0]
### Added
- Add scripts to download Dryad dataset
  [#53](https://github.com/NickleDave/songdkl/pull/53).
  Fixed [#50](https://github.com/NickleDave/songdkl/issues/50)
  and [#10](https://github.com/NickleDave/songdkl/issues/10).
- Add "source" data for tests (subset of Dryad dataset) +
  dev tooling to recreate this subset, download it for tests,
  etc. [#53](https://github.com/NickleDave/songdkl/pull/53)
  Fixed [#50](https://github.com/NickleDave/songdkl/issues/50)
  and [#10](https://github.com/NickleDave/songdkl/issues/10).
- Add initial suite of unit tests, using `pytest`
  [#54](https://github.com/NickleDave/songdkl/pull/54).
  Fixes [#17](https://github.com/NickleDave/songdkl/issues/17).
- Set up continuous integration
  [#55](https://github.com/NickleDave/songdkl/pull/55).
  Fixes [#6](https://github.com/NickleDave/songdkl/issues/6).
- Add functionality to find threshold for segmenting audio with 
  Otsu's method, as implemented in scikit-image
  [#58](https://github.com/NickleDave/songdkl/pull/58).
  Fixes [#37](https://github.com/NickleDave/songdkl/issues/37).

## [0.2.0b1]
### Added
- Add .csv files from original Dryad dataset
  and provided by [David Mets](https://github.com/dgmets) for testing
  [#43](https://github.com/NickleDave/songdkl/pull/43).
  Fixes [#40](https://github.com/NickleDave/songdkl/issues/40).

### Changed
- Refactor/revise codebase for readability
  [#46](https://github.com/NickleDave/songdkl/pull/46).
  Also add/revise docstrings, type annotations.
  Fixes [#21](https://github.com/NickleDave/songdkl/issues/21),
  [#23](https://github.com/NickleDave/songdkl/issues/23),
  and [#24](https://github.com/NickleDave/songdkl/issues/24).

## [0.1.0]
### Changed
- single-source version, by adding `__about__.py` to `songdkl`
  [#4](https://github.com/NickleDave/songdkl/pull/4)
- use `poetry` for development
  [#11](https://github.com/NickleDave/songdkl/pull/11)

### Fixed
- fix README so that it (1) points to dataset associated with paper 
  instead of another dataset, (2) has user and development install 
  instructions, and (3) properly explains usage of the command-line 
  interface
  [#16](https://github.com/NickleDave/songdkl/pull/16)
- fix imports in numsyls.py
  [ee25b35](https://github.com/NickleDave/songdkl/commit/ee25b359b05e492a455721e109f3b4514b03c4f9)
- fix parameter name in `numsyls.EMofgmmcluster`
  [2262f1c](https://github.com/NickleDave/songdkl/commit/2262f1c4a72aced20d6234b4bf846725f3160d7e)

### Removed
- remove previous test data set from another paper
  [de266b5](https://github.com/NickleDave/songdkl/commit/de266b5040b217bc4d9d123eda7776dd57c2c159)
- remove `utils` sub-package
  [f79dad2](https://github.com/NickleDave/songdkl/commit/f79dad28cba601dd1cf1085b980ead8edf35f144)
