"""Core RTHOR algorithm functions."""

from __future__ import annotations

import numpy as np
import pandas as pd

from rthor._validation import validate_labels, validate_order
from rthor._vectorized import (
    build_comparison_matrix,
    build_hypothesis_matrix,
    calculate_comparison_ci,
    count_agreements,
    count_pairwise_agreements,
    extract_upper_triangle_vector,
)
from rthor.permutations import apply_permutation, generate_permutations


def generate_hypothesis(
    order: str | list[int] | np.ndarray,
    n_variables: int,
) -> tuple[np.ndarray, np.ndarray, int]:
    """Generate hypothesis matrix for RTHOR analysis.

    Args:
        order: Order specification (validated by caller)
        n_variables: Number of variables

    Returns:
        hypothesis_matrix: Hypothesis matrix (n_pairs x n_pairs)
        order_array: Processed order array
        n_predictions: Number of hypothesized predictions (count of 1s)

    """
    # Validate and get order array
    order_array = validate_order(order, n_variables)
    hypothesis_matrix = build_hypothesis_matrix(order_array)

    # Count predictions
    n_predictions = int(np.sum(hypothesis_matrix))

    return hypothesis_matrix, order_array, n_predictions


def calculate_fit(
    correlation_matrix: np.ndarray,
    hypothesis_matrix: np.ndarray,
) -> tuple[int, int]:
    """Calculate fit of correlation matrix to hypothesis.

    Args:
        correlation_matrix: Correlation matrix (n x n)
        hypothesis_matrix: Hypothesis matrix (n_pairs x n_pairs)

    Returns:
        n_agreements: Number of predictions satisfied
        n_ties: Number of tied correlations

    """
    correlations_vector = extract_upper_triangle_vector(correlation_matrix)
    comparison_matrix = build_comparison_matrix(correlations_vector)
    n_agreements, n_ties = count_agreements(comparison_matrix, hypothesis_matrix)

    return n_agreements, n_ties


def calculate_ci(n_agreements: int, n_ties: int, n_predictions: int) -> float:
    r"""Calculate Correspondence Index.

    $$
    CI = \frac{ n_{\text{agreements}} - (n_{\text{predictions}} - (n_{\text{agreements}} + n_{\text{ties}})) } { n_{\text{predictions}} }
    $$

    Args:
        n_agreements: Number of agreements
        n_ties: Number of ties
        n_predictions: Number of predictions

    Returns:
        ci: Correspondence Index

    """  # noqa: E501
    return (n_agreements - (n_predictions - (n_agreements + n_ties))) / n_predictions


def run_permutation_test(
    correlation_matrix: np.ndarray,
    hypothesis_matrix: np.ndarray,
    n_agreements: int,
    permutations: np.ndarray,
) -> float:
    """Run randomization test via permutations.

    Args:
        correlation_matrix: Original correlation matrix
        hypothesis_matrix: Hypothesis matrix
        n_agreements: Observed number of agreements
        permutations: Permutation matrix (n_permutations x n_variables)

    Returns:
        p_value: Proportion of permutations with fit >= observed

    """
    n_permutations = permutations.shape[0]
    count = 1  # Count observed data

    # Test each permutation (excluding identity which is first)
    for k in range(n_permutations - 1):
        perm = permutations[k, :]

        # Apply permutation
        permuted_matrix = apply_permutation(correlation_matrix, perm)

        # Calculate fit
        perm_agreements, _ = calculate_fit(permuted_matrix, hypothesis_matrix)

        # Count if equal or greater fit
        if perm_agreements >= n_agreements:
            count += 1

    return count / n_permutations


def test_single_matrix(
    correlation_matrix: np.ndarray,
    hypothesis_matrix: np.ndarray,
    n_predictions: int,
    permutations: np.ndarray,
    matrix_id: int,
    label: str,
) -> dict:
    """Test a single correlation matrix.

    Args:
        correlation_matrix: Correlation matrix to test
        hypothesis_matrix: Hypothesis matrix
        n_predictions: Number of hypothesized predictions
        permutations: Permutation matrix
        matrix_id: Matrix identifier (1-indexed)
        label: Matrix label

    Returns:
        Dictionary with keys: matrix, predictions, agreements, ties, ci, p_value, label

    """
    n_agreements, n_ties = calculate_fit(correlation_matrix, hypothesis_matrix)
    ci = calculate_ci(n_agreements, n_ties, n_predictions)
    p_value = run_permutation_test(
        correlation_matrix, hypothesis_matrix, n_agreements, permutations
    )

    return {
        "matrix": matrix_id,
        "predictions": n_predictions,
        "agreements": n_agreements,
        "ties": n_ties,
        "ci": ci,
        "p_value": p_value,
        "label": label,
    }


def test_multiple_matrices(
    correlation_matrices: np.ndarray,
    order: str | list[int] | np.ndarray,
    labels: list[str] | None,
) -> pd.DataFrame:
    """Test multiple correlation matrices.

    Args:
        correlation_matrices: 3D array (n_variables, n_variables, n_matrices)
        order: Hypothesized ordering
        labels: Matrix labels

    Returns:
        Results table

    """
    n_variables = correlation_matrices.shape[0]
    n_matrices = correlation_matrices.shape[2]

    labels = validate_labels(labels, n_matrices)
    hypothesis_matrix, _, n_predictions = generate_hypothesis(order, n_variables)
    permutations = generate_permutations(n_variables)

    # Test each matrix
    results = []
    for i in range(n_matrices):
        corr_mat = correlation_matrices[:, :, i]
        result = test_single_matrix(
            corr_mat,
            hypothesis_matrix,
            n_predictions,
            permutations,
            matrix_id=i + 1,
            label=labels[i],
        )
        results.append(result)

    # Create DataFrame with proper dtypes
    df = pd.DataFrame(results)
    df["matrix"] = df["matrix"].astype(int)
    df["predictions"] = df["predictions"].astype(int)
    df["agreements"] = df["agreements"].astype(int)
    df["ties"] = df["ties"].astype(int)
    df["ci"] = df["ci"].astype(float)
    df["p_value"] = df["p_value"].astype(float)

    return df


def compare_two_matrices(
    corr_mat1: np.ndarray,
    corr_mat2: np.ndarray,
    hypothesis_matrix: np.ndarray,
    permutations: np.ndarray,
    matrix1_id: int,
    matrix2_id: int,
) -> dict:
    """Compare two correlation matrices.

    Notes:
        Vectorized version of R code (`randmf.R:244-254`).

    Args:
        corr_mat1: First correlation matrix
        corr_mat2: Second correlation matrix
        hypothesis_matrix: Hypothesis matrix
        permutations: Permutation matrix
        matrix1_id: First matrix ID
        matrix2_id: Second matrix ID

    Returns:
        Comparison result with keys: `matrix1, matrix2, both_agree, only1, only2,
            neither, ci, p_value`

    """
    # Extract correlation vectors
    corr_vec1 = extract_upper_triangle_vector(corr_mat1)
    corr_vec2 = extract_upper_triangle_vector(corr_mat2)

    comp_mat1 = build_comparison_matrix(corr_vec1)
    comp_mat2 = build_comparison_matrix(corr_vec2)
    both_agree, only1, only2, neither = count_pairwise_agreements(
        comp_mat1, comp_mat2, hypothesis_matrix
    )
    ci = calculate_comparison_ci(only1, only2, both_agree, neither)

    # Run permutation test
    n_permutations = permutations.shape[0]
    count = 1  # Count observed

    for k in range(n_permutations - 1):
        perm = permutations[k, :]

        # Apply same permutation to both matrices
        perm_mat1 = apply_permutation(corr_mat1, perm)
        perm_mat2 = apply_permutation(corr_mat2, perm)

        perm_vec1 = extract_upper_triangle_vector(perm_mat1)
        perm_vec2 = extract_upper_triangle_vector(perm_mat2)

        perm_comp1 = build_comparison_matrix(perm_vec1)
        perm_comp2 = build_comparison_matrix(perm_vec2)
        perm_both, perm_only1, perm_only2, perm_neither = count_pairwise_agreements(
            perm_comp1, perm_comp2, hypothesis_matrix
        )
        perm_ci = calculate_comparison_ci(
            perm_only1, perm_only2, perm_both, perm_neither
        )

        # Count if permuted CI is equal or greater than observed
        # (matches R code line 298 in randmf.R)
        if perm_ci >= ci:
            count += 1

    p_value = count / n_permutations

    return {
        "matrix1": matrix1_id,
        "matrix2": matrix2_id,
        "both_agree": both_agree,
        "only1": only1,
        "only2": only2,
        "neither": neither,
        "ci": ci,
        "p_value": p_value,
    }


def compare_multiple_matrices(
    correlation_matrices: np.ndarray,
    order: str | list[int] | np.ndarray,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Compare all pairs of correlation matrices.

    Args:
        correlation_matrices: 3D array (n_variables, n_variables, n_matrices)
        order: Hypothesized ordering

    Returns:
        rthor_df: Individual matrix test results
        comparisons: Pairwise comparison results

    """
    n_variables = correlation_matrices.shape[0]
    n_matrices = correlation_matrices.shape[2]

    hypothesis_matrix, _, n_predictions = generate_hypothesis(order, n_variables)
    permutations = generate_permutations(n_variables)

    # Test each matrix individually
    rthor_results = []
    for i in range(n_matrices):
        corr_mat = correlation_matrices[:, :, i]
        result = test_single_matrix(
            corr_mat,
            hypothesis_matrix,
            n_predictions,
            permutations,
            matrix_id=i + 1,
            label="",
        )
        rthor_results.append(result)

    # Compare all pairs
    comparison_results = []
    for i in range(n_matrices):
        for j in range(i + 1, n_matrices):
            corr_mat1 = correlation_matrices[:, :, i]
            corr_mat2 = correlation_matrices[:, :, j]

            comp_result = compare_two_matrices(
                corr_mat1,
                corr_mat2,
                hypothesis_matrix,
                permutations,
                matrix1_id=i + 1,
                matrix2_id=j + 1,
            )
            comparison_results.append(comp_result)

    # Create DataFrames
    rthor_df = pd.DataFrame(rthor_results)
    rthor_df["matrix"] = rthor_df["matrix"].astype(int)
    rthor_df["predictions"] = rthor_df["predictions"].astype(int)
    rthor_df["agreements"] = rthor_df["agreements"].astype(int)
    rthor_df["ties"] = rthor_df["ties"].astype(int)
    rthor_df["ci"] = rthor_df["ci"].astype(float)
    rthor_df["p_value"] = rthor_df["p_value"].astype(float)

    comp_df = pd.DataFrame(comparison_results)
    comp_df["matrix1"] = comp_df["matrix1"].astype(int)
    comp_df["matrix2"] = comp_df["matrix2"].astype(int)
    comp_df["both_agree"] = comp_df["both_agree"].astype(int)
    comp_df["only1"] = comp_df["only1"].astype(int)
    comp_df["only2"] = comp_df["only2"].astype(int)
    comp_df["neither"] = comp_df["neither"].astype(int)
    comp_df["ci"] = comp_df["ci"].astype(float)
    comp_df["p_value"] = comp_df["p_value"].astype(float)

    return rthor_df, comp_df
