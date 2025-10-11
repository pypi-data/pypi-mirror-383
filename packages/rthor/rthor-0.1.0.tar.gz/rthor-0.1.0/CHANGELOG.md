# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-10-10

### Added

- Initial release of rthor - Python implementation of RTHOR
- Core functionality:
  - `rthor_test()` function for testing correlation matrices against hypothesized orderings
  - `compare_matrices()` function for pairwise matrix comparisons
  - Support for multiple input formats (NumPy arrays, pandas DataFrames, text files)
  - Preset orderings: `circular6` and `circular8`
  - Custom ordering support for any number of variables
- Result classes:
  - `RTHORResult` dataclass with results DataFrame and metadata
  - `ComparisonResult` dataclass for pairwise comparisons
  - `summary()` methods for human-readable output
  - `to_dict()` methods for JSON export
- Comprehensive test suite:
  - Regression tests against R RTHORR package
  - Exact numerical parity with R implementation (rtol=1e-10, atol=1e-12)
  - Tests for all input formats and edge cases
- Full documentation:
  - API reference with detailed examples
  - User guide covering installation, quickstart, concepts, input formats, and results interpretation
  - Interactive marimo notebooks for basic and advanced usage
  - Complete docstrings in Google style
  - Type hints throughout codebase
- Development infrastructure:
  - uv for dependency management
  - ruff for linting and formatting
  - ty for type checking
  - pytest for testing with coverage reports
  - tox for multi-version testing (Python 3.11-3.13)
  - prek for pre-commit hooks
  - mkdocs-material for documentation
  - setuptools-scm for version management

### Implementation Details

- Vectorized NumPy operations for efficient computation
- Memory-efficient permutation algorithm
- Validated against R RTHORR package for numerical accuracy
- Supports Python 3.11, 3.12, and 3.13
- Type-safe with comprehensive input validation
- Optimized for matrices with 4-20 variables

### Dependencies

- Python >= 3.11
- numpy >= 1.24.0
- pandas >= 2.0.0

### Credits

- Based on the R RTHORR package by Ryan D. Yentes and Frank Wilhelm
- Original RTHOR method by Hubert & Arabie (1987)
- "Evaluating order hypotheses within proximity matrices" - _Psychological Bulletin_, 102(1), 172-178

[Unreleased]: https://github.com/MitchellAcoustics/rthor/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/MitchellAcoustics/rthor/releases/tag/v0.1.0
