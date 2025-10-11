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
from rthor.io import extract_lower_triangle, read_correlation_matrices


def process_input(
    data: Path | str | list[pd.DataFrame] | np.ndarray,
    n_matrices: int | None = None,
    n_variables: int | None = None,
) -> tuple[np.ndarray, int, int]:
    """Process various input formats into 3D correlation matrix array.

    Args:
    data : Path, str, list[pd.DataFrame], or np.ndarray
        Input data in various formats:
        - Path/str: File path containing correlation matrices
        - list[pd.DataFrame]: List of DataFrames (correlations computed)
        - np.ndarray: Pre-computed correlation matrices (2D or 3D)
    n_matrices : int, optional
        Number of matrices (required for file input if ambiguous)
    n_variables : int, optional
        Number of variables (required for file input if ambiguous)

    Returns:
    correlation_matrices : np.ndarray
        3D array of shape (n_variables, n_variables, n_matrices)
    n_variables : int
        Number of variables
    n_matrices : int
        Number of matrices

    Raises:
    ValueError
        If input format is invalid or parameters are missing

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

    # Read matrices from file
    correlation_matrices = read_correlation_matrices(path, n_variables, n_matrices)

    # Validate
    validate_correlation_matrices_3d(correlation_matrices)

    return correlation_matrices, n_variables, n_matrices


def _process_dataframe_list(
    df_list: list[pd.DataFrame],
) -> tuple[np.ndarray, int, int]:
    """Process list of DataFrames."""
    # Validate
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

        # Extract lower triangle with diagonal
        lower_tri = extract_lower_triangle(corr_matrix, include_diagonal=True)

        # Prepend to list (R uses: za <- append(lower_tri, za))
        correlation_values = list(lower_tri) + correlation_values

    # Convert to array
    za = np.array(correlation_values)

    # Build 3D array from flat vector (matching io.py logic)
    correlation_matrices = _build_3d_from_vector(za, n_variables, n_matrices)

    # Validate
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

    # Validate
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
    za : np.ndarray
        Flat array of correlation values
    n_variables : int
        Number of variables
    n_matrices : int
        Number of matrices

    Returns:
    correlation_matrices : np.ndarray
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
