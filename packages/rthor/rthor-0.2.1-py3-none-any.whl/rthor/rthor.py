"""Public API for RTHOR analyses."""

from __future__ import annotations

from pathlib import Path
from typing import overload

import numpy as np
import pandas as pd

from rthor._core import (
    compare_multiple_matrices,
    test_multiple_matrices,
)
from rthor._input import process_input
from rthor._permutations import generate_permutations
from rthor.formatting import (
    print_comparison as print_comparison_fn,
)
from rthor.formatting import (
    print_results as print_results_fn,
)


@overload
def test(
    data: Path | str,
    order: str | list[int] = "circular6",
    labels: list[str] | None = None,
    *,
    n_matrices: int,
    n_variables: int,
    print_results: bool = False,
) -> pd.DataFrame: ...


@overload
def test(
    data: list[pd.DataFrame] | np.ndarray,
    order: str | list[int] = "circular6",
    labels: list[str] | None = None,
    *,
    print_results: bool = False,
) -> pd.DataFrame: ...


def test(
    data: Path | str | list[pd.DataFrame] | np.ndarray,
    order: str | list[int] = "circular6",
    labels: list[str] | None = None,
    n_matrices: int | None = None,
    n_variables: int | None = None,
    *,
    print_results: bool = False,
) -> pd.DataFrame:
    """Randomization Test of Hypothesized Order Relations (RTHOR).

    Tests whether correlation matrices conform to a hypothesized ordering
    of variables using permutation-based randomization tests.

    !!! info "About RTHOR"
        The RTHOR test evaluates whether the pattern of correlations in a
        correlation matrix matches a hypothesized ordering of variables. This is
        particularly useful for testing circumplex or circular models where
        variables are hypothesized to fall along a circular continuum.

        The test uses a randomization approach: the observed Correspondence Index
        (CI) is compared to CIs from permuted data to obtain a p-value. CI ranges
        from -1 (perfect disagreement) to +1 (perfect agreement).

        The Python implementation produces numerically identical results to the
        original R RTHORR package[^1].

        [^1]: Tracey TJG, Morris ML (2025). _RTHORR: randomization test of
          hypothesized order relations (RTHOR) and comparisons_. R package
          version 0.1.3, commit c3edb36287c77733ec0a23236b478cc53c1cac0f,
          <https://github.com/michaellynnmorris/RTHORR>.

    Args:
        data: Input data in various formats:

            - **File path** (`Path | str`):
                Path to text file containing correlation matrices.
                Requires `n_matrices` and `n_variables` parameters.
            - **DataFrames** (`list[pd.DataFrame]`):
                List of DataFrames with raw data. Correlations
                computed automatically. Each DataFrame should contain only the
                numeric columns to analyze.
            - **Arrays** (`np.ndarray`):
                Pre-computed correlation matrices. Can be 2D (nxn)
                for single matrix or 3D (nxnxm) for multiple matrices.
        order: Hypothesized ordering of variables. Options:

            - `"circular6"`: Preset for 6-variable circular/circumplex model
            - `"circular8"`: Preset for 8-variable circular/circumplex model
            - Custom list of integers specifying pairwise ordering
              (length must be $n*(n-1)/2$)
        labels: Descriptive labels for each matrix. Length must equal number
            of matrices.
        n_matrices: Number of matrices in file (required for file input only).
        n_variables: Number of variables per matrix (required for file input only).
        print_results: If True, print formatted results table before returning.

    Returns:
        DataFrame with test results containing columns:

            - `matrix`: Matrix identifier (1-indexed)
            - `predictions`: Number of hypothesized predictions
            - `agreements`: Number of predictions satisfied
            - `ties`: Number of tied correlations
            - `ci`: Correspondence Index (-1 to +1)
            - `p_value`: Randomization test p-value
            - `label`: Descriptive label for matrix
            - `n_permutations`: Number of permutations tested
            - `n_variables`: Number of variables per matrix

    Examples:
        Test correlation matrices from file:

        >>> import rthor
        >>> df = rthor.test(
        ...     "correlations.txt",
        ...     order="circular6",
        ...     n_matrices=3,
        ...     n_variables=6,
        ...     labels=["Sample 1", "Sample 2", "Sample 3"]
        ... )
        >>> print(df)
        >>> df[df['p_value'] < 0.05]  # Filter significant results

        Test from raw data DataFrames:

        >>> df = rthor.test(
        ...     [df1, df2, df3],
        ...     order="circular6",
        ...     labels=["Group A", "Group B", "Group C"]
        ... )

        Test with custom ordering:

        >>> custom_order = [1, 2, 3, 2, 1, 1, 2, 3, 2, 1]  # For 5 variables
        >>> df = rthor.test(data, order=custom_order)

        Test single correlation matrix:

        >>> import numpy as np
        >>> corr_matrix = np.array([[1.0, 0.8, 0.6],
        ...                          [0.8, 1.0, 0.7],
        ...                          [0.6, 0.7, 1.0]])
        >>> df = rthor.test(corr_matrix, order=[1, 2, 1])

    See Also:
        - [`rthor.compare`][rthor.compare]:
            For pairwise comparisons between matrices

        - [`randall.R` in RTHORR](https://github.com/mgurtman/RTHORR/blob/main/R/randall.R):
            Original R implementation of RTHOR

    """
    # Process input to 3D array
    correlation_matrices, n_vars, _ = process_input(data, n_matrices, n_variables)

    results_df = test_multiple_matrices(correlation_matrices, order, labels)
    permutations = generate_permutations(n_vars)
    n_perms = permutations.shape[0]

    # Add metadata columns
    results_df["n_permutations"] = n_perms
    results_df["n_variables"] = n_vars

    # Print formatted results if requested
    if print_results:
        print_results_fn(results_df)

    return results_df


@overload
def compare(
    data: Path | str,
    order: str | list[int] = "circular6",
    *,
    n_matrices: int,
    n_variables: int,
    print_results: bool = False,
) -> tuple[pd.DataFrame, pd.DataFrame]: ...


@overload
def compare(
    data: list[pd.DataFrame] | np.ndarray,
    order: str | list[int] = "circular6",
    *,
    print_results: bool = False,
) -> tuple[pd.DataFrame, pd.DataFrame]: ...


def compare(
    data: Path | str | list[pd.DataFrame] | np.ndarray,
    order: str | list[int] = "circular6",
    n_matrices: int | None = None,
    n_variables: int | None = None,
    *,
    print_results: bool = False,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Pairwise comparison of multiple correlation matrices using RTHOR.

    Tests both individual matrices and pairwise differences between matrices
    to determine which matrices best fit the hypothesized ordering and whether
    matrices differ significantly from each other.

    Args:
        data: Input data (same formats as [`rthor.test`][rthor.test]).
        order: Hypothesized ordering (same as [`rthor.test`][rthor.test]).
        n_matrices: Number of matrices (required for file input).
        n_variables: Number of variables (required for file input).
        print_results: If True, print formatted results tables before returning.

    Returns:
        individual_results: Results of individual RTHOR tests for each matrix.

            Columns:

            - `matrix`: Matrix identifier (1-indexed)
            - `predictions`: Number of hypothesized predictions
            - `agreements`: Number of predictions satisfied
            - `ties`: Number of tied correlations
            - `ci`: Correspondence Index (-1 to +1)
            - `p_value`: Randomization test p-value
            - `label`: Descriptive label for matrix
            - `n_permutations`: Number of permutations tested
            - `n_variables`: Number of variables per matrix
        pairwise_comparisons: Results of pairwise comparisons between matrices.

            Columns:

                - `matrix1`: First matrix identifier
                - `matrix2`: Second matrix identifier
                - `both_agree`: Predictions both matrices satisfy
                - `only1`: Predictions only matrix 1 satisfies
                - `only2`: Predictions only matrix 2 satisfies
                - `neither`: Predictions neither matrix satisfies
                - `ci`: Comparison Correspondence Index
                - `p_value`: Randomization test p-value
                - `n_permutations`: Number of permutations tested
                - `n_variables`: Number of variables per matrix

    Examples:
        Compare multiple correlation matrices:

        >>> import rthor
        >>> individual, pairwise = rthor.compare(
        ...     "correlations.txt",
        ...     order="circular6",
        ...     n_matrices=3,
        ...     n_variables=6
        ... )
        >>> print(individual)
        >>> print(pairwise[pairwise['p_value'] < 0.05])

        Compare from DataFrames:

        >>> individual, pairwise = rthor.compare(
        ...     [df1, df2, df3], order="circular6"
        ... )

    Note:
        This function performs two types of tests:

        **Individual tests**: Each matrix is tested against the hypothesis
        independently (same as [`rthor.test`][rthor.test])

        **Pairwise comparisons**: Each pair of matrices is compared to determine
        if they differ in their fit to the hypothesis. The comparison CI indicates
        whether one matrix fits better than the other:

        - $CI > 0$: Matrix 2 fits better than Matrix 1
        - $CI < 0$: Matrix 1 fits better than Matrix 2
        - $CI ≈ 0$: Matrices fit similarly

        The comparison uses a randomization test where both matrices are permuted
        identically to assess whether the observed difference could occur by chance.

    See Also:
        [`rthor.test`][rthor.test]:
            For testing matrices without pairwise comparisons

    """
    # Process input to 3D array
    correlation_matrices, n_vars, _ = process_input(data, n_matrices, n_variables)

    # Check we have at least 2 matrices
    n_mats = correlation_matrices.shape[2]
    if n_mats < 2:
        msg = (
            f"Matrix comparison requires at least 2 matrices, got {n_mats}. "
            f"Use test() for single matrix analysis."
        )
        raise ValueError(msg)

    rthor_df, comparisons_df = compare_multiple_matrices(correlation_matrices, order)
    permutations = generate_permutations(n_vars)
    n_perms = permutations.shape[0]

    # Add metadata columns to both DataFrames
    rthor_df["n_permutations"] = n_perms
    rthor_df["n_variables"] = n_vars
    comparisons_df["n_permutations"] = n_perms
    comparisons_df["n_variables"] = n_vars

    # Print formatted results if requested
    if print_results:
        print_comparison_fn(rthor_df, comparisons_df)

    return rthor_df, comparisons_df
