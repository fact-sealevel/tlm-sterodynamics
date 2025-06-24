# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Added ocean dynamics component to project localized sea level rise. This uses the component from the original facts module. See `--help` for new features and configurations with this addition. This addition does not change the method used to project GLSR. ([PR#3](https://github.com/stcaf-org/tlm-sterodynamics/pull/3), [@brews](https://github.com/brews))

### Changed

- BREAKING CHANGE. Options `--output-lslr-file`, `--location-file`, `--model-dir` are now required, even if you only need the "GSLR" projection file. These options are required now that localized ocean dynamics are part of projections. ([PR#3](https://github.com/stcaf-org/tlm-sterodynamics/pull/3), [@brews](https://github.com/brews))

## [0.1.0] - 2025-06-12

- Initial release.


[Unreleased]: https://github.com/stcaf-org/tlm-sterodynamics/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/stcaf-org/tlm-sterodynamics/releases/tag/v0.1.0
