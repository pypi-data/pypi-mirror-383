"""Input validation functions for RTHOR analyses."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import numpy as np
import pandas as pd

OrderPreset = Literal["circular6", "circular8"]

# Preset order arrays (from R package)
_PRESET_ORDERS = {
    "circular6": np.array(
        [1, 2, 3, 2, 1, 1, 2, 3, 2, 1, 2, 3, 1, 2, 1], dtype=np.int32
    ),
    "circular8": np.array(
        [
            1,
            2,
            3,
            4,
            3,
            2,
            1,
            1,
            2,
            3,
            4,
            3,
            2,
            1,
            2,
            3,
            4,
            3,
            1,
            2,
            3,
            4,
            1,
            2,
            3,
            1,
            2,
            1,
        ],
        dtype=np.int32,
    ),
}


def validate_correlation_matrix(
    matrix: np.ndarray, *, matrix_id: int | None = None
) -> None:
    """Validate that a matrix is a valid correlation matrix.

    Args:
    matrix : np.ndarray
        Matrix to validate
    matrix_id : int, optional
        Matrix identifier for error messages

    Raises:
    ValueError
        If matrix is not a valid correlation matrix

    """
    prefix = f"Matrix {matrix_id}: " if matrix_id is not None else ""

    if matrix.ndim != 2:
        msg = f"{prefix}Expected 2D array, got {matrix.ndim}D"
        raise ValueError(msg)

    if matrix.shape[0] != matrix.shape[1]:
        msg = f"{prefix}Expected square matrix, got shape {matrix.shape}"
        raise ValueError(msg)

    if matrix.shape[0] < 2:
        msg = (
            f"{prefix}Matrix must be at least 2x2, "
            f"got {matrix.shape[0]}x{matrix.shape[0]}"
        )
        raise ValueError(msg)

    # Check symmetry
    if not np.allclose(matrix, matrix.T, rtol=1e-10, atol=1e-12):
        msg = f"{prefix}Matrix is not symmetric"
        raise ValueError(msg)

    # Check diagonal is all 1.0
    if not np.allclose(np.diag(matrix), 1.0, rtol=1e-10, atol=1e-12):
        msg = f"{prefix}Correlation matrix diagonal must be 1.0"
        raise ValueError(msg)

    # Check values in valid range
    if not np.all((matrix >= -1 - 1e-10) & (matrix <= 1 + 1e-10)):
        msg = f"{prefix}Correlation values must be in [-1, 1]"
        raise ValueError(msg)


def validate_order(
    order: str | list[int] | np.ndarray,
    n_variables: int,
) -> np.ndarray:
    """Validate and process order specification.

    Args:
    order : str or list[int] or np.ndarray
        Order specification. Can be:
        - "circular6": Preset for 6-variable circular model
        - "circular8": Preset for 8-variable circular model
        - Custom array/list of integers
    n_variables : int
        Number of variables in correlation matrices

    Returns:
    order_array : np.ndarray
        Processed order array (int32)

    Raises:
    ValueError
        If order specification is invalid

    """
    # Handle preset strings
    if isinstance(order, str):
        if order not in _PRESET_ORDERS:
            msg = (
                f"Unknown order preset: '{order}'. "
                f"Valid presets: {', '.join(_PRESET_ORDERS.keys())}"
            )
            raise ValueError(msg)

        order_array = _PRESET_ORDERS[order]

        # Verify preset matches n_variables
        expected_length = (n_variables * (n_variables - 1)) // 2
        if len(order_array) != expected_length:
            # Give helpful error for common case
            if order == "circular6" and n_variables != 6:
                msg = (
                    f"Order preset 'circular6' is for 6 variables, "
                    f"but data has {n_variables} variables"
                )
            elif order == "circular8" and n_variables != 8:
                msg = (
                    f"Order preset 'circular8' is for 8 variables, "
                    f"but data has {n_variables} variables"
                )
            else:
                msg = (
                    f"Order preset '{order}' length {len(order_array)} "
                    f"doesn't match data ({n_variables} variables requires "
                    f"length {expected_length})"
                )
            raise ValueError(msg)

        return order_array

    # Handle custom order
    order_array = np.asarray(order, dtype=np.int32)

    if order_array.ndim != 1:
        msg = f"Order must be 1D array, got {order_array.ndim}D"
        raise ValueError(msg)

    expected_length = (n_variables * (n_variables - 1)) // 2
    if len(order_array) != expected_length:
        msg = (
            f"Order length {len(order_array)} doesn't match expected length "
            f"{expected_length} for {n_variables} variables. "
            f"Order must have length n*(n-1)/2 where n is number of variables."
        )
        raise ValueError(msg)

    return order_array


def validate_labels(
    labels: list[str] | None,
    n_matrices: int,
) -> list[str]:
    """Validate and process matrix labels.

    Args:
    labels : list[str] or None
        Matrix labels, or None to auto-generate
    n_matrices : int
        Number of matrices

    Returns:
    labels : list[str]
        Processed labels (auto-generated if input was None)

    Raises:
    ValueError
        If number of labels doesn't match number of matrices

    """
    if labels is None:
        return ["" for _ in range(n_matrices)]

    if len(labels) != n_matrices:
        msg = (
            f"Number of labels ({len(labels)}) doesn't match "
            f"number of matrices ({n_matrices})"
        )
        raise ValueError(msg)

    return labels


def validate_filepath(filepath: Path | str) -> Path:
    """Validate filepath exists and is readable.

    Args:
    filepath : Path or str
        Path to file

    Returns:
    path : Path
        Validated Path object

    Raises:
    FileNotFoundError
        If file doesn't exist
    ValueError
        If path is not a file

    """
    path = Path(filepath)

    if not path.exists():
        msg = f"File not found: {path}"
        raise FileNotFoundError(msg)

    if not path.is_file():
        msg = f"Path is not a file: {path}"
        raise ValueError(msg)

    return path


def validate_dataframe_list(df_list: list[pd.DataFrame]) -> None:
    """Validate list of DataFrames for RTHOR analysis.

    Args:
    df_list : list[pd.DataFrame]
        List of DataFrames

    Raises:
    ValueError
        If DataFrames are invalid or inconsistent

    """
    if not df_list:
        msg = "DataFrame list is empty"
        raise ValueError(msg)

    if not all(isinstance(df, pd.DataFrame) for df in df_list):
        msg = "All elements must be pandas DataFrames"
        raise ValueError(msg)

    # Check all have same number of columns
    n_cols = len(df_list[0].columns)
    if not all(len(df.columns) == n_cols for df in df_list):
        msg = "All DataFrames must have the same number of columns"
        raise ValueError(msg)

    if n_cols < 2:
        msg = f"DataFrames must have at least 2 columns, got {n_cols}"
        raise ValueError(msg)

    # Check each DataFrame has enough rows for correlation
    for i, df in enumerate(df_list, 1):
        if len(df) < 2:
            msg = (
                f"DataFrame {i} has insufficient rows ({len(df)}) "
                f"for correlation analysis"
            )
            raise ValueError(msg)

        # Check for non-numeric columns
        non_numeric = df.select_dtypes(exclude=[np.number]).columns.tolist()
        if non_numeric:
            msg = (
                f"DataFrame {i} has non-numeric columns: {non_numeric}. "
                f"All columns must be numeric for correlation analysis."
            )
            raise ValueError(msg)


def validate_correlation_matrices_3d(
    matrices: np.ndarray,
) -> None:
    """Validate 3D array of correlation matrices.

    Args:
    matrices : np.ndarray
        3D array of shape (n, n, n_matrices)

    Raises:
    ValueError
        If array is invalid

    """
    if matrices.ndim != 3:
        msg = f"Expected 3D array, got {matrices.ndim}D"
        raise ValueError(msg)

    if matrices.shape[0] != matrices.shape[1]:
        msg = (
            f"Expected square matrices (nxnxm), "
            f"got {matrices.shape[0]}x{matrices.shape[1]}x{matrices.shape[2]}"
        )
        raise ValueError(msg)

    n_matrices = matrices.shape[2]

    # Validate each matrix
    for i in range(n_matrices):
        validate_correlation_matrix(matrices[:, :, i], matrix_id=i + 1)
