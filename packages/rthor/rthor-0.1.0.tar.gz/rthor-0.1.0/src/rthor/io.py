"""Input/output utilities for RTHOR analysis."""

from pathlib import Path

import numpy as np


def read_correlation_matrices(
    filepath: Path | str,
    n: int,
    nmat: int,
) -> np.ndarray:
    """Read correlation matrices from text file.

    Args:
    filepath : Path or str
        Path to input file containing correlation matrices
    n : int
        Number of variables (matrix dimension)
    nmat : int
        Number of matrices in the file

    Returns:
    dmatm : np.ndarray
        3D array of correlation matrices (n x n x nmat)

    Notes:
    Translated from RTHORR/R/randall.R lines 49-67.

    Input file format:
    - Lower triangular matrices including diagonal
    - Values separated by whitespace
    - Each matrix starts with diagonal element (1.00)
    - Example for n=3:
        1.00
         .62 1.00
         .40 .62 1.00

    The R code reads this using scan() and fills the matrix in two passes:
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
    include_diagonal: bool = True,  # noqa: FBT001, FBT002
) -> np.ndarray:
    """Extract lower triangular values from correlation matrix.

    Args:
    corr_matrix : np.ndarray
        Correlation matrix (n x n)
    include_diagonal : bool, default=True
        Whether to include diagonal values

    Returns:
    values : np.ndarray
        Lower triangular values in row-major order

    Notes:
    Used by randall_from_df and randmf_from_df to convert
    correlation matrices computed from DataFrames into the
    format expected by the file reading functions.

    Matches R's gdata::lowerTriangle(cor_df, diag=TRUE, byrow=TRUE)

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
