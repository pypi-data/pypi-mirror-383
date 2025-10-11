"""Public API for RTHOR analyses."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from rthor._core import (
    compare_multiple_matrices,
    generate_hypothesis,
    test_multiple_matrices,
)
from rthor._input import process_input
from rthor.permutations import generate_permutations
from rthor.results import ComparisonResult, RTHORResult


def rthor_test(
    data: Path | str | list[pd.DataFrame] | np.ndarray,
    order: str | list[int] = "circular6",
    labels: list[str] | None = None,
    n_matrices: int | None = None,
    n_variables: int | None = None,
) -> RTHORResult:
    """Randomization Test of Hypothesized Order Relations (RTHOR).

    Tests whether correlation matrices conform to a hypothesized ordering
    of variables using permutation-based randomization tests.

    Args:
        data: Input data in various formats:
            - **File path**: Path to text file containing correlation matrices.
              Requires `n_matrices` and `n_variables` parameters.
            - **DataFrames**: List of DataFrames with raw data. Correlations
              computed automatically. Each DataFrame should contain only the
              numeric columns to analyze.
            - **Arrays**: Pre-computed correlation matrices. Can be 2D (nxn)
              for single matrix or 3D (nxnxm) for multiple matrices.
        order: Hypothesized ordering of variables. Options:
            - `"circular6"`: Preset for 6-variable circular/circumplex model
            - `"circular8"`: Preset for 8-variable circular/circumplex model
            - Custom list of integers specifying pairwise ordering
              (length must be n*(n-1)/2)
        labels: Descriptive labels for each matrix. Length must equal number
            of matrices.
        n_matrices: Number of matrices in file (required for file input only).
        n_variables: Number of variables per matrix (required for file input only).

    Returns:
        Result object containing:
            - `results`: Main results DataFrame with columns (matrix, predictions,
              agreements, ties, ci, p_value, label)
            - `n_matrices`: Number of matrices analyzed
            - `n_variables`: Number of variables per matrix
            - `order`: The hypothesized ordering used
            - `n_predictions`: Number of hypothesized predictions
            - `n_permutations`: Number of permutations tested

    Examples:
        Test correlation matrices from file:

        >>> import rthor
        >>> result = pythor.rthor_test(
        ...     "correlations.txt",
        ...     order="circular6",
        ...     n_matrices=3,
        ...     n_variables=6,
        ...     labels=["Sample 1", "Sample 2", "Sample 3"]
        ... )
        >>> print(result.summary())
        >>> result.results  # Access results DataFrame

        Test from raw data DataFrames:

        >>> result = pythor.rthor_test(
        ...     [df1, df2, df3],
        ...     order="circular6",
        ...     labels=["Group A", "Group B", "Group C"]
        ... )

        Test with custom ordering:

        >>> custom_order = [1, 2, 3, 2, 1, 1, 2, 3, 2, 1]  # For 5 variables
        >>> result = pythor.rthor_test(data, order=custom_order)

        Test single correlation matrix:

        >>> import numpy as np
        >>> corr_matrix = np.array([[1.0, 0.8, 0.6],
        ...                          [0.8, 1.0, 0.7],
        ...                          [0.6, 0.7, 1.0]])
        >>> result = pythor.rthor_test(corr_matrix, order=[1, 2, 1])

    Note:
        The RTHOR test evaluates whether the pattern of correlations in a
        correlation matrix matches a hypothesized ordering of variables. This is
        particularly useful for testing circumplex or circular models where
        variables are hypothesized to fall along a circular continuum.

        The test uses a randomization approach: the observed Correspondence Index
        (CI) is compared to CIs from permuted data to obtain a p-value. CI ranges
        from -1 (perfect disagreement) to +1 (perfect agreement).

        The Python implementation produces numerically identical results to the
        original R RTHORR package (Gurtman, 2021).

    References:
        Gurtman, M. B. (2021). RTHORR: Randomization tests of hypothesized order
        relations. R package version 1.0.0.

    See Also:
        compare_matrices: For pairwise comparisons between matrices

    """
    # Process input to 3D array
    correlation_matrices, n_vars, n_mats = process_input(data, n_matrices, n_variables)

    # Run tests
    results_df = test_multiple_matrices(correlation_matrices, order, labels)

    # Get metadata for result object
    _, order_array, n_predictions = generate_hypothesis(order, n_vars)
    permutations = generate_permutations(n_vars)
    n_perms = permutations.shape[0]

    return RTHORResult(
        results=results_df,
        n_matrices=n_mats,
        n_variables=n_vars,
        order=order_array,
        n_predictions=n_predictions,
        n_permutations=n_perms,
    )


def compare_matrices(
    data: Path | str | list[pd.DataFrame] | np.ndarray,
    order: str | list[int] = "circular6",
    n_matrices: int | None = None,
    n_variables: int | None = None,
) -> ComparisonResult:
    """Pairwise comparison of multiple correlation matrices using RTHOR.

    Tests both individual matrices and pairwise differences between matrices
    to determine which matrices best fit the hypothesized ordering and whether
    matrices differ significantly from each other.

    Args:
        data: Input data (same formats as `rthor_test`).
        order: Hypothesized ordering (same as `rthor_test`).
        n_matrices: Number of matrices (required for file input).
        n_variables: Number of variables (required for file input).

    Returns:
        Result object containing:
            - `rthor_results`: Individual RTHOR tests for each matrix
            - `comparisons`: Pairwise comparison results (matrix1, matrix2,
              both_agree, only1, only2, neither, ci, p_value)
            - `n_matrices`: Number of matrices analyzed
            - `n_variables`: Number of variables per matrix
            - `order`: The hypothesized ordering used
            - `n_predictions`: Number of hypothesized predictions
            - `n_permutations`: Number of permutations tested

    Examples:
        Compare multiple correlation matrices:

        >>> import rthor
        >>> result = pythor.compare_matrices(
        ...     "correlations.txt",
        ...     order="circular6",
        ...     n_matrices=3,
        ...     n_variables=6
        ... )
        >>> print(result.summary())
        >>> result.rthor_results  # Individual matrix results
        >>> result.comparisons   # Pairwise comparisons

        Compare from DataFrames:

        >>> result = pythor.compare_matrices([df1, df2, df3], order="circular6")

    Note:
        This function performs two types of tests:

        **Individual tests**: Each matrix is tested against the hypothesis
        independently (same as `rthor_test`)

        **Pairwise comparisons**: Each pair of matrices is compared to determine
        if they differ in their fit to the hypothesis. The comparison CI indicates
        whether one matrix fits better than the other:

        - CI > 0: Matrix 2 fits better than Matrix 1
        - CI < 0: Matrix 1 fits better than Matrix 2
        - CI ≈ 0: Matrices fit similarly

        The comparison uses a randomization test where both matrices are permuted
        identically to assess whether the observed difference could occur by chance.

    See Also:
        rthor_test: For testing matrices without pairwise comparisons

    """
    # Process input to 3D array
    correlation_matrices, n_vars, n_mats = process_input(data, n_matrices, n_variables)

    if n_mats < 2:
        msg = (
            f"Matrix comparison requires at least 2 matrices, got {n_mats}. "
            f"Use rthor_test() for single matrix analysis."
        )
        raise ValueError(msg)

    # Run comparisons
    rthor_df, comparisons_df = compare_multiple_matrices(correlation_matrices, order)

    # Get metadata
    _, order_array, n_predictions = generate_hypothesis(order, n_vars)
    permutations = generate_permutations(n_vars)
    n_perms = permutations.shape[0]

    return ComparisonResult(
        rthor_results=rthor_df,
        comparisons=comparisons_df,
        n_matrices=n_mats,
        n_variables=n_vars,
        order=order_array,
        n_predictions=n_predictions,
        n_permutations=n_perms,
    )
