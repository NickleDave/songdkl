# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
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
