# rthor

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Tests status][tests-badge]][tests-link]
[![Linting status][linting-badge]][linting-link]
[![Documentation status][documentation-badge]][documentation-link]
[![License][license-badge]](./LICENSE.md)

<!-- prettier-ignore-start -->
[tests-badge]:              https://github.com/MitchellAcoustics/rthor/actions/workflows/tests.yml/badge.svg
[tests-link]:               https://github.com/MitchellAcoustics/rthor/actions/workflows/tests.yml
[linting-badge]:            https://github.com/MitchellAcoustics/rthor/actions/workflows/linting.yml/badge.svg
[linting-link]:             https://github.com/MitchellAcoustics/rthor/actions/workflows/linting.yml
[documentation-badge]:      https://github.com/MitchellAcoustics/rthor/actions/workflows/docs.yml/badge.svg
[documentation-link]:       https://github.com/MitchellAcoustics/rthor/actions/workflows/docs.yml
[license-badge]:            https://img.shields.io/badge/License-MIT-yellow.svg
<!-- prettier-ignore-end -->

**rthor** is a Python implementation of RTHOR (Randomization Test of Hypothesized Order Relations), a statistical test for circumplex and circular models in correlation matrices.

## Features

- **Exact Parity with RTHORR**: Produces numerically identical results to the original [RTHORR package](https://github.com/michaellynnmorris/RTHORR)
- **Multiple Input Formats**: Works with files, pandas DataFrames, or numpy arrays
- **Flexible Analysis**: Test single matrices or compare multiple matrices pairwise
- **Fast Performance**: Vectorized operations using NumPy for efficient computation

## Quick Start

```python
import rthor
import pandas as pd

# Test from correlation matrix file
result = rthor.rthor_test(
    "correlations.txt",
    order="circular6",
    n_matrices=3,
    n_variables=6,
    labels=["Sample 1", "Sample 2", "Sample 3"]
)

# View results
print(result.summary())
print(result.results)

# Test from DataFrames
result = rthor.rthor_test(
    [df1, df2, df3],
    order="circular6",
    labels=["Group A", "Group B", "Group C"]
)

# Compare multiple matrices
comparison = rthor.compare_matrices([df1, df2, df3], order="circular6")
print(comparison.summary())
print(comparison.comparisons)  # Pairwise differences
```

## Installation

### From PyPI

```sh
pip install rthor
```

### From Source

```sh
pip install git+https://github.com/MitchellAcoustics/rthor.git
```

### For Development

```sh
git clone https://github.com/MitchellAcoustics/rthor.git
cd rthor
pip install -e .[dev]
```

## Requirements

- Python 3.11, 3.12, or 3.13
- NumPy ≥ 1.24.0
- pandas ≥ 2.0.0

## What is RTHOR?

RTHOR (Randomization Test of Hypothesized Order Relations) is a statistical method for testing whether correlation matrices conform to a hypothesized ordering of variables [@Tracey2025RTHORR;@Tracey1997RANDALL]. This is particularly useful for:

- **Circumplex Models**: Variables arranged in a circular pattern (e.g., interpersonal behavior, emotions)
- **Circular Structures**: Testing theoretical predictions about variable ordering
- **Correlation Patterns**: Validating expected patterns in correlation matrices

The test uses a randomization approach to compute p-values, comparing the observed Correspondence Index (CI) with values from permuted data. CI ranges from -1 (perfect disagreement) to +1 (perfect agreement).

## Key Functions

### [`rthor_test()`][rthor.rthor_test]

Test whether correlation matrices conform to a hypothesized ordering.

**Parameters:**

- `data`: Input data (file path, list of DataFrames, or numpy array)
- `order`: Hypothesized ordering ("circular6", "circular8", or custom list)
- `labels`: Optional descriptive labels for matrices
- `n_matrices`: Number of matrices (required for file input)
- `n_variables`: Number of variables (required for file input)

**Returns:** `RTHORResult` object with results DataFrame and metadata

### [`compare_matrices()`][rthor.compare_matrices]

Compare multiple correlation matrices pairwise to determine which fits the hypothesis better.

**Parameters:** Same as `rthor_test()` but requires at least 2 matrices

**Returns:** `ComparisonResult` object with individual results and pairwise comparisons

## Documentation

Full documentation is available at [https://drandrewmitchell.com/rthor](https://drandrewmitchell.com/rthor)

### Validation Against Original Paper

The implementation has been validated against the original Hubert & Arabie (1987) [@Hubert1987Evaluating] paper. See [docs/examples/paper-validation.py](docs/examples/paper-validation.py) for a detailed demonstration that replicates Table 1 from the paper and confirms exact agreement with the expected results:

- ✓ 72 predictions, 61 agreements, 11 violations
- ✓ p-value = 0.0167 (12/720)
- ✓ CI = 0.694

## Testing

Run tests across all supported Python versions:

```sh
tox
```

Run tests in current environment:

```sh
pytest tests
```

Run tests with coverage:

```sh
pytest --cov --cov-report=xml
```

## Development

This project uses:

- **uv** for dependency management
- **ruff** for linting and formatting
- **pytest** for testing
- **mkdocs** with Material theme for documentation
- **pre-commit** hooks (via prek) for code quality

Install development dependencies:

```sh
UV sync --all-extras
```

Run pre-commit hooks:

```sh
prek run
```

Build documentation:

```sh
mkdocs serve
```

## Project Team

**Andrew Mitchell** ([andrew.mitchell.research@gmail.com](mailto:andrew.mitchell.research@gmail.com))

### Research Software Engineering Contact

Centre for Advanced Research Computing, University College London
([arc.collaborations@ucl.ac.uk](mailto:arc.collaborations@ucl.ac.uk))

## Citation

If you use rthor in your research, please cite both this package and the original method paper:

**rthor (Python implementation):**

```bibtex
---8<-- "docs/refs.bib:Mitchell2025rthor"
```

**Original RTHOR method:**

```bibtex
---8<-- "docs/refs.bib:Hubert1987Evaluating"
```

**R RTHORR package:**

```bibtex
---8<-- "docs/refs.bib:Tracey2025RTHORR"
```

## License

MIT License. See [LICENSE.md](LICENSE.md) for details.

## Acknowledgments

This project is developed in collaboration with the
[Centre for Advanced Research Computing](https://ucl.ac.uk/arc), University College London.

`rthor` is a Python port of the R package RTHORR by Michael B. Gurtman. The implementation maintains exact numerical parity with the original R version while providing a Pythonic interface and improved performance through vectorization.
