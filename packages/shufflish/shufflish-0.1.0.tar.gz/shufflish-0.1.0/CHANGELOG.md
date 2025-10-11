# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## Unreleased


## [0.1.0] - 2025-10-10
### Added
- Windows on ARM builds
### Changed
- Drop Python 3.8
- Depend on cython~=3.1


## [0.0.5] - 2024-11-12
### Added
- Add index method to AffineCipher
### Fixed
- Slices of slices with negative steps no longer have wrong extents


## [0.0.4] - 2024-11-04
### Added
- Return slices as new AffineCipher instances
- New methods implemented for AffineCipher
  - __len__
  - __contains__
  - expand: returns the full permutation instead of a slice
  - extents: return (start, stop, step) of the slice
  - invert: create an inverse cipher
  - is_slice: returns True if the instance is a slice
### Changed
- Depend on cython~=3.0


## [0.0.3] - 2024-10-14
### Fixed
- Very large seeds no longer cause integer overflow
- 0 is no longer selected as coprime for domain=1


## [0.0.2] - 2024-10-12
### Fixed
- Slices with negative step are no longer empty
- Slices with out of bounds start/stop no longer raise IndexError


## [0.0.1] - 2024-10-11
### Added
- Initial public release


[Unreleased]: https://github.com/jfolz/shufflish/compare/0.0.5...main
[0.0.5]: https://github.com/jfolz/shufflish/compare/0.0.4...0.0.5
[0.0.4]: https://github.com/jfolz/shufflish/compare/0.0.3...0.0.4
[0.0.3]: https://github.com/jfolz/shufflish/compare/0.0.2...0.0.3
[0.0.2]: https://github.com/jfolz/shufflish/compare/0.0.1...0.0.2
[0.0.1]: https://github.com/jfolz/shufflish/releases/tag/0.0.1
