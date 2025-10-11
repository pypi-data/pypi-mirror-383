"""Vectorized operations for RTHOR algorithm.

This module contains high-performance vectorized implementations of core
RTHOR operations, replacing nested loops with NumPy broadcasting.
"""

from __future__ import annotations

import numpy as np


def build_comparison_matrix(correlations_vector: np.ndarray) -> np.ndarray:
    """Build comparison matrix from correlation vector.

    Vectorized replacement for nested loops in calculate_fit().

    Args:
    correlations_vector : np.ndarray
        1D array of correlation values from upper triangle

    Returns:
    comparison_matrix : np.ndarray
        Matrix where:
        - comparison_matrix[i,j] = 1 if correlations_vector[j] > correlations_vector[i]
        - comparison_matrix[i,j] = 2 if correlations_vector[j] == correlations_vector[i]
        - comparison_matrix[i,j] = 0 if correlations_vector[j] < correlations_vector[i]

    Notes:
    Performance: O(1) broadcast vs O(n²) nested loops.
    Original R code (randall.R:135-140) used nested loops.

    Examples:
    >>> corr = np.array([0.8, 0.6, 0.7])
    >>> comp = build_comparison_matrix(corr)
    >>> comp.shape
    (3, 3)

    """
    # Reshape for broadcasting: column vector and row vector
    corr_i = correlations_vector[:, np.newaxis]  # Shape: (n, 1)
    corr_j = correlations_vector[np.newaxis, :]  # Shape: (1, n)

    # Vectorized comparison using np.where
    # This broadcasts to (n, n) automatically
    return np.where(
        corr_j > corr_i,
        1,
        np.where(corr_j == corr_i, 2, 0),
    ).astype(np.int32)


def count_agreements(
    comparison_matrix: np.ndarray,
    hypothesis_matrix: np.ndarray,
) -> tuple[int, int]:
    """Count agreements and ties between comparison and hypothesis matrices.

    Vectorized replacement for nested loops in calculate_fit().

    Args:
    comparison_matrix : np.ndarray
        Comparison matrix from build_comparison_matrix()
    hypothesis_matrix : np.ndarray
        Hypothesis matrix (1 where prediction exists, 0 otherwise)

    Returns:
    n_agreements : int
        Number of agreements (comparison==1 and hypothesis==1)
    n_ties : int
        Number of ties (comparison==2 and hypothesis==1)

    Notes:
    Performance: O(1) boolean indexing vs O(n²) nested loops.
    Original R code (randall.R:143-146) used nested loops.

    Examples:
    >>> comp = np.array([[0, 1, 0], [0, 0, 2], [1, 0, 0]])
    >>> hyp = np.array([[0, 1, 1], [0, 0, 1], [0, 0, 0]])
    >>> n_agr, n_tie = count_agreements(comp, hyp)

    """
    # Create boolean masks for hypothesized predictions
    hypothesis_mask = hypothesis_matrix == 1

    # Count agreements: where both comparison and hypothesis are 1
    n_agreements = int(np.sum((comparison_matrix == 1) & hypothesis_mask))

    # Count ties: where comparison is 2 (tie) and hypothesis is 1
    n_ties = int(np.sum((comparison_matrix == 2) & hypothesis_mask))

    return n_agreements, n_ties


def build_hypothesis_matrix(order_array: np.ndarray) -> np.ndarray:
    """Build hypothesis matrix from order array.

    Vectorized replacement for nested loops in generate_hypothesis_matrix().

    Args:
    order_array : np.ndarray
        1D array specifying hypothesized ordering

    Returns:
    hypothesis_matrix : np.ndarray
        Matrix where hypothesis_matrix[i,j] = 1 if order_array[j] < order_array[i]

    Notes:
    Performance: O(1) broadcast vs O(n²) nested loops.
    Original R code (randall.R:71-79) used nested loops.

    Examples:
    >>> order = np.array([1, 2, 3, 2, 1])
    >>> hyp = build_hypothesis_matrix(order)
    >>> hyp.shape
    (5, 5)

    """
    # Reshape for broadcasting
    order_i = order_array[:, np.newaxis]  # Column vector
    order_j = order_array[np.newaxis, :]  # Row vector

    # Vectorized comparison: 1 where order_j < order_i
    return (order_j < order_i).astype(np.int32)


def extract_upper_triangle_vector(matrix: np.ndarray) -> np.ndarray:
    """Extract upper triangle of matrix as vector (row-major order).

    This matches R's row-major ordering for consistency with original implementation.

    Args:
    matrix : np.ndarray
        2D square matrix (n x n)

    Returns:
    vector : np.ndarray
        1D array of upper triangle values (length = n*(n-1)/2)

    Notes:
    Extracts in the same order as R code (randall.R:126-131) for exact parity.
    Uses row-major traversal: (0,1), (0,2), ..., (0,n-1), (1,2), ..., (n-2,n-1)

    Examples:
    >>> mat = np.array([[1.0, 0.8, 0.6],
    ...                 [0.8, 1.0, 0.7],
    ...                 [0.6, 0.7, 1.0]])
    >>> vec = extract_upper_triangle_vector(mat)
    >>> vec
    array([0.8, 0.6, 0.7])

    """
    n = matrix.shape[0]
    n_pairs = (n * (n - 1)) // 2

    vector = np.zeros(n_pairs, dtype=matrix.dtype)
    idx = 0

    # Row-major order to match R
    for i in range(n):
        for j in range(n):
            if i >= j:
                continue
            vector[idx] = matrix[i, j]
            idx += 1

    return vector


def build_pairwise_comparison_matrices(
    corr_vec1: np.ndarray,
    corr_vec2: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Build comparison matrices for two correlation vectors.

    Used in pairwise matrix comparison (randmf).

    Args:
    corr_vec1 : np.ndarray
        Correlation vector from first matrix
    corr_vec2 : np.ndarray
        Correlation vector from second matrix

    Returns:
    comp_mat1 : np.ndarray
        Comparison matrix for first vector
    comp_mat2 : np.ndarray
        Comparison matrix for second vector

    Notes:
    Vectorized version of R code (randmf.R:244-254).

    """
    comp_mat1 = build_comparison_matrix(corr_vec1)
    comp_mat2 = build_comparison_matrix(corr_vec2)

    return comp_mat1, comp_mat2


def count_pairwise_agreements(
    comp_mat1: np.ndarray,
    comp_mat2: np.ndarray,
    hypothesis_matrix: np.ndarray,
) -> tuple[int, int, int, int]:
    """Count agreement patterns between two matrices.

    Vectorized replacement for quadruple nested loops in randmf().

    Args:
    comp_mat1 : np.ndarray
        Comparison matrix for first correlation matrix
    comp_mat2 : np.ndarray
        Comparison matrix for second correlation matrix
    hypothesis_matrix : np.ndarray
        Hypothesis matrix

    Returns:
    both_agree : int
        Count where both matrices satisfy hypothesis
    only1 : int
        Count where only matrix 1 satisfies hypothesis
    only2 : int
        Count where only matrix 2 satisfies hypothesis
    neither : int
        Count where neither matrix satisfies hypothesis

    Notes:
    Performance: O(1) vs O(n⁴) nested loops.
    Original R code (randmf.R:256-280) used 4 nested loops.

    The logic checks for each hypothesized prediction (hypothesis_matrix==1):
    - m1 = 1 if comp_mat1 agrees (==1)
    - m2 = 1 if comp_mat2 agrees (==1)
    Then counts: (m1=1,m2=1), (m1=1,m2=0), (m1=0,m2=1), (m1=0,m2=0)

    """
    # Create masks for hypothesized predictions
    hypothesis_mask = hypothesis_matrix == 1

    # For hypothesized predictions, check if each matrix agrees (==1) or disagrees (==0)
    # Note: ties (==2) are NOT counted as either agreement or disagreement
    m1_agrees = (comp_mat1 == 1) & hypothesis_mask
    m1_disagrees = (comp_mat1 == 0) & hypothesis_mask
    m2_agrees = (comp_mat2 == 1) & hypothesis_mask
    m2_disagrees = (comp_mat2 == 0) & hypothesis_mask

    # Count patterns using boolean operations
    # Both agree: m1==1 AND m2==1
    both_agree = int(np.sum(m1_agrees & m2_agrees))
    # Only1 agrees: m1==1 AND m2==0 (not m2==1 or m2==2)
    only1 = int(np.sum(m1_agrees & m2_disagrees))
    # Only2 agrees: m1==0 AND m2==1
    only2 = int(np.sum(m1_disagrees & m2_agrees))
    # Neither agrees: m1==0 AND m2==0
    neither = int(np.sum(m1_disagrees & m2_disagrees))

    return both_agree, only1, only2, neither


def calculate_comparison_ci(
    only1: int,
    only2: int,
    both_agree: int,
    neither: int,
) -> float:
    """Calculate Correspondence Index for pairwise comparison.

    Args:
    only1 : int
        Count where only matrix 1 agrees
    only2 : int
        Count where only matrix 2 agrees
    both_agree : int
        Count where both agree
    neither : int
        Count where neither agrees

    Returns:
    ci : float
        Comparison CI

    Notes:
    Formula from R code (randmf.R:205):
    CI = (only2 - only1) / (both + only1 + only2 + neither)

    """
    denominator = both_agree + only1 + only2 + neither
    if denominator == 0:
        return 0.0

    return (only2 - only1) / denominator
