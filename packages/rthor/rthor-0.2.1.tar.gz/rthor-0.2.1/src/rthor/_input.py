"""Input processing for RTHOR analyses."""

from __future__ import annotations

from pathlib import Path
from typing import cast

import numpy as np
import pandas as pd

from rthor._validation import (
    validate_correlation_matrices_3d,
    validate_dataframe_list,
    validate_filepath,
)


def process_input(
    data: Path | str | list[pd.DataFrame] | np.ndarray,
    n_matrices: int | None = None,
    n_variables: int | None = None,
) -> tuple[np.ndarray, int, int]:
    """Process various input formats into 3D correlation matrix array.

    Args:
        data: Input data in various formats:

            - Path/str: File path containing correlation matrices
            - list[pd.DataFrame]: List of DataFrames (correlations computed)
            - np.ndarray: Pre-computed correlation matrices (2D or 3D)
        n_matrices: Number of matrices (required for file input if ambiguous)
        n_variables: Number of variables (required for file input if ambiguous)

    Returns:
        correlation_matrices: 3D array of shape (n_variables, n_variables, n_matrices)
        n_variables: Number of variables
        n_matrices: Number of matrices

    Raises:
        ValueError: If input format is invalid or parameters are missing

    """
    # Handle file path input
    if isinstance(data, (str, Path)):
        return _process_file_input(data, n_matrices, n_variables)

    # Handle list of DataFrames
    if isinstance(data, list):
        return _process_dataframe_list(cast("list[pd.DataFrame]", data))

    # Handle numpy array
    if isinstance(data, np.ndarray):
        return _process_array_input(data)

    msg = (
        f"Invalid input type: {type(data)}. "
        f"Expected Path, str, list[pd.DataFrame], or np.ndarray."
    )
    raise TypeError(msg)


def _process_file_input(
    filepath: Path | str,
    n_matrices: int | None,
    n_variables: int | None,
) -> tuple[np.ndarray, int, int]:
    """Process file input."""
    path = validate_filepath(filepath)

    if n_matrices is None or n_variables is None:
        msg = (
            "For file input, both n_matrices and n_variables must be specified. "
            "Cannot auto-infer from file format."
        )
        raise ValueError(msg)

    correlation_matrices = read_correlation_matrices(path, n_variables, n_matrices)
    validate_correlation_matrices_3d(correlation_matrices)

    return correlation_matrices, n_variables, n_matrices


def _process_dataframe_list(
    df_list: list[pd.DataFrame],
) -> tuple[np.ndarray, int, int]:
    """Process list of DataFrames."""
    validate_dataframe_list(df_list)

    n_matrices = len(df_list)
    n_variables = len(df_list[0].columns)

    # Compute correlations for each DataFrame
    # Match R's behavior: reverse list, then prepend correlations
    df_list_reversed = list(reversed(df_list))

    # Build correlation values vector (matching R code)
    correlation_values = []
    for df in df_list_reversed:
        # Compute correlation matrix
        corr_matrix = df.corr().to_numpy()
        lower_tri = extract_lower_triangle(corr_matrix, include_diagonal=True)

        # Prepend to list (R uses: za <- append(lower_tri, za))
        correlation_values = list(lower_tri) + correlation_values

    # Convert to array
    za = np.array(correlation_values)
    correlation_matrices = _build_3d_from_vector(za, n_variables, n_matrices)
    validate_correlation_matrices_3d(correlation_matrices)

    return correlation_matrices, n_variables, n_matrices


def _process_array_input(
    array: np.ndarray,
) -> tuple[np.ndarray, int, int]:
    """Process numpy array input."""
    # Handle 2D array (single matrix)
    if array.ndim == 2:
        if array.shape[0] != array.shape[1]:
            msg = f"Expected square matrix, got shape {array.shape}"
            raise ValueError(msg)

        n_variables = array.shape[0]
        n_matrices = 1

        # Reshape to 3D
        correlation_matrices = array[:, :, np.newaxis]

    # Handle 3D array (multiple matrices)
    elif array.ndim == 3:
        if array.shape[0] != array.shape[1]:
            msg = f"Expected square matrices (nxnxm), got shape {array.shape}"
            raise ValueError(msg)

        n_variables = array.shape[0]
        n_matrices = array.shape[2]
        correlation_matrices = array

    else:
        msg = f"Expected 2D or 3D array, got {array.ndim}D"
        raise ValueError(msg)

    validate_correlation_matrices_3d(correlation_matrices)

    return correlation_matrices, n_variables, n_matrices


def _build_3d_from_vector(
    za: np.ndarray,
    n_variables: int,
    n_matrices: int,
) -> np.ndarray:
    """Build 3D correlation matrix array from flat vector.

    Matches logic from io.py read_correlation_matrices().

    Args:
        za: Flat array of correlation values
        n_variables: Number of variables
        n_matrices: Number of matrices

    Returns:
        3D array (n_variables, n_variables, n_matrices)

    """
    dmatm = np.zeros((n_variables, n_variables, n_matrices))
    n_pairs = (n_variables * n_variables - n_variables) // 2

    for m in range(n_matrices):
        ii = m * (n_pairs + n_variables) - 1

        # First pass: fill upper triangle
        for j in range(n_variables):
            for i in range(n_variables):
                if i > j:
                    continue
                ii += 1
                dmatm[i, j, m] = za[ii]

        # Second pass: fill lower triangle (make symmetric)
        ii = m * (n_pairs + n_variables) - 1
        for i in range(n_variables):
            for j in range(n_variables):
                if i < j:
                    continue
                ii += 1
                dmatm[i, j, m] = za[ii]

    return dmatm


def read_correlation_matrices(
    filepath: Path | str,
    n: int,
    nmat: int,
) -> np.ndarray:
    """Read correlation matrices from text file.

    Args:
        filepath: Path to input file containing correlation matrices
        n: Number of variables (matrix dimension)
        nmat: Number of matrices in the file

    Returns:
        3D array of correlation matrices (n x n x nmat)

    Notes:
        Translated from [`RTHORR/R/randall.R`](https://github.com/michaellynnmorris/RTHORR/blob/c3edb36287c77733ec0a23236b478cc53c1cac0f/R/randall.R#L49)
        lines 49-67.

        Input file format:

        - Lower triangular matrices including diagonal
        - Values separated by whitespace
        - Each matrix starts with diagonal element (1.00)
        - Example for n=3:

            1.00
            .62 1.00
            .40 .62 1.00

        The R code reads this using `scan()` and fills the matrix in two passes:

        1. Upper triangle (i <= j)
        2. Lower triangle (i >= j)

        This creates a symmetric matrix.

    """
    filepath = Path(filepath)

    # Read all values from file (R: za <- scan(input))
    with filepath.open() as f:
        values = []
        for line in f:
            # Split on whitespace and convert to float
            line_values = [float(x) for x in line.strip().split() if x]
            values.extend(line_values)

    za = np.array(values)

    # Initialize 3D array for matrices
    dmatm = np.zeros((n, n, nmat))

    # Calculate number of pairs
    np_pairs = (n * n - n) // 2

    # Fill matrices (R code lines 51-67)
    for m in range(nmat):
        ii = m * (np_pairs + n) - 1  # -1 for 0-indexing

        # First pass: fill upper triangle (i <= j)
        # R code: for(j in 1:n) for(i in 1:n) if (i > j) next
        for j in range(n):
            for i in range(n):
                if i > j:
                    continue
                ii += 1
                dmatm[i, j, m] = za[ii]

        # Second pass: fill lower triangle (i >= j)
        # This makes the matrix symmetric
        # R code: for(i in 1:n) for(j in 1:n) if (i < j) next
        ii = m * (np_pairs + n) - 1  # Reset index
        for i in range(n):
            for j in range(n):
                if i < j:
                    continue
                ii += 1
                dmatm[i, j, m] = za[ii]

    return dmatm


def extract_lower_triangle(
    corr_matrix: np.ndarray,
    *,
    include_diagonal: bool = True,
) -> np.ndarray:
    """Extract lower triangular values from correlation matrix.

    Args:
        corr_matrix: Correlation matrix (n x n)
        include_diagonal: Whether to include diagonal values

    Returns:
        Lower triangular values in row-major order

    Notes:
        Used by [`rthor.test`][rthor.test] and
        [`rthor.compare`][rthor.compare] via
        [`process_input`][rthor._input.process_input]
        to convert correlation matrices computed from DataFrames into the
        format expected by the file reading functions.

        Matches R's `gdata::lowerTriangle(cor_df, diag=TRUE, byrow=TRUE)`

    """
    n = corr_matrix.shape[0]
    values = []

    if include_diagonal:
        # Include diagonal: extract full lower triangle
        for i in range(n):
            for j in range(i + 1):
                values.append(corr_matrix[i, j])
    else:
        # Exclude diagonal: only below diagonal
        for i in range(n):
            for j in range(i):
                values.append(corr_matrix[i, j])

    return np.array(values)
