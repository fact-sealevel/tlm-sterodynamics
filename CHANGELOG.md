# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.1] - 2026-01-22

### Fixed

- Fix error when writing NetCDF4 file output by pinning h5py==3.14.0 and netcdf4==1.7.2 ([PR#14](https://github.com/fact-sealevel/tlm-sterodynamics/pull/14), [ @e-marshall](https://github.com/e-marshall)).


## [0.3.0] - 2025-10-27

### Added

- Build multiplatform container images. We're now experimenting with support for linux/arm64, in addition to linux/amd64.

- Added logging system with messages at start and stop of each step ([PR#9](https://github.com/fact-sealevel/tlm-sterodynamics/pull/9), [@brews](https://github.com/brews)).

### Changed

- Update docs to use public `ghcr.io/fact-sealevel/tlm-sterodynamics` container image at new host Github organization. THIS IS A BREAKING CHANGE.

- Update README and docs to use new repository URL at https://github.com/fact-sealevel/tlm-sterodynamics.


## [0.2.1] - 2025-08-25

### Fixed

- Fixed bad `--scenario` default argument ([PR#8](https://github.com/fact-sealevel/tlm-sterodynamics/pull/8), [@e-marshall](https://github.com/e-marshall)).
- Fixed typo on input data download command in README example.


## [0.2.0] - 2025-06-27

### Added

- Added ocean dynamics component to project localized sea level rise. This uses the component from the original facts module. The module has been refactored to run significantly larger projections faster by using available CPU cores. See `--help` for new features and configurations with this addition. This addition does not change the method used to project GLSR. ([PR#3](https://github.com/fact-sealevel/tlm-sterodynamics/pull/3), [PR#4](https://github.com/fact-sealevel/tlm-sterodynamics/pull/4), [@brews](https://github.com/brews))

### Changed

- BREAKING CHANGE. Options `--output-lslr-file`, `--location-file`, `--model-dir` are now required, even if you only need the "GSLR" projection file. These options are required now that localized ocean dynamics are part of projections. ([PR#3](https://github.com/fact-sealevel/tlm-sterodynamics/pull/3), [@brews](https://github.com/brews))

- The program now depends on `"xarray[accel,parallel]>=2025.4.0"`. This is needed to run faster and better manage memory for large projections. ([PR#4](https://github.com/fact-sealevel/tlm-sterodynamics/pull/4), [@brews](https://github.com/brews))
- `uv.lock` has been updated. ([PR#4](https://github.com/fact-sealevel/tlm-sterodynamics/pull/4), [@brews](https://github.com/brews))

## [0.1.0] - 2025-06-12

- Initial release.

[0.3.1]: https://github.com/fact-sealevel/tlm-sterodynamics/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/fact-sealevel/tlm-sterodynamics/compare/v0.2.1...v0.3.0
[0.2.1]: https://github.com/fact-sealevel/tlm-sterodynamics/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/fact-sealevel/tlm-sterodynamics/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/fact-sealevel/tlm-sterodynamics/releases/tag/v0.1.0
