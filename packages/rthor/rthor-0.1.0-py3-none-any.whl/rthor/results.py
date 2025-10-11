"""Result classes for RTHOR analyses."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd


@dataclass
class RTHORResult:
    """Results from RTHOR (Randomization Test of Hypothesized Order Relations) analysis.

    This class encapsulates the results of testing whether correlation matrices
    conform to a hypothesized ordering of variables.

    Attributes:
        results: Main results table with columns (matrix, predictions, agreements,
            ties, ci, p_value, label).
        n_matrices: Number of matrices analyzed.
        n_variables: Number of variables in each matrix.
        order: The hypothesized ordering used for analysis.
        n_predictions: Total number of hypothesized predictions.
        n_permutations: Number of permutations used in randomization test.

    Examples:
        >>> import rthor
        >>> result = pythor.rthor_test("correlations.txt", order="circular6")
        >>> print(result.summary())
        >>> result.results  # Access results DataFrame

    """

    results: pd.DataFrame
    n_matrices: int
    n_variables: int
    order: np.ndarray
    n_predictions: int
    n_permutations: int

    def summary(self) -> str:
        """Generate formatted summary of results.

        Returns:
            Multi-line summary string with key statistics.

        """
        lines = [
            "RTHOR Analysis Summary",
            "=" * 50,
            f"Matrices analyzed: {self.n_matrices}",
            f"Variables per matrix: {self.n_variables}",
            f"Hypothesized predictions: {self.n_predictions}",
            f"Permutations tested: {self.n_permutations}",
            "",
            "Results:",
            "-" * 50,
        ]

        # Add key statistics
        for _, row in self.results.iterrows():
            label = row["label"] if row["label"] else f"Matrix {row['matrix']}"
            ci = row["ci"]
            p_val = row["p_value"]
            sig = (
                "***"
                if p_val < 0.001
                else "**"
                if p_val < 0.01
                else "*"
                if p_val < 0.05
                else ""
            )
            lines.append(f"{label:30s} CI={ci:7.4f}  p={p_val:.4f} {sig}")

        lines.extend(
            [
                "",
                "Significance codes: *** p<0.001, ** p<0.01, * p<0.05",
            ]
        )

        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        """Convert results to dictionary for serialization.

        Returns
        -------
        dict
            Dictionary containing all result data

        """
        return {
            "results": self.results.to_dict(orient="records"),
            "n_matrices": self.n_matrices,
            "n_variables": self.n_variables,
            "order": self.order.tolist(),
            "n_predictions": self.n_predictions,
            "n_permutations": self.n_permutations,
        }

    def __str__(self) -> str:
        """Return summary string representation."""
        return self.summary()

    def __repr__(self) -> str:
        """Return detailed representation."""
        return (
            f"RTHORResult(n_matrices={self.n_matrices}, "
            f"n_variables={self.n_variables}, "
            f"n_predictions={self.n_predictions})"
        )


@dataclass
class ComparisonResult:
    """Results from pairwise matrix comparison analysis.

    This class encapsulates both individual matrix RTHOR tests and pairwise
    comparisons between matrices.

    Attributes
    ----------
    rthor_results : pd.DataFrame
        Individual RTHOR test results for each matrix
        (same format as RTHORResult.results)
    comparisons : pd.DataFrame
        Pairwise comparison results with columns:
        - matrix1: First matrix identifier
        - matrix2: Second matrix identifier
        - both_agree: Count of predictions both matrices satisfy
        - only1: Count satisfied only by matrix 1
        - only2: Count satisfied only by matrix 2
        - neither: Count satisfied by neither matrix
        - ci: Comparison Correspondence Index
        - p_value: Randomization test p-value
    n_matrices : int
        Number of matrices analyzed
    n_variables : int
        Number of variables in each matrix
    order : np.ndarray
        The hypothesized ordering used for analysis
    n_predictions : int
        Total number of hypothesized predictions
    n_permutations : int
        Number of permutations used in randomization test

    Examples
    --------
    >>> import rthor
    >>> result = pythor.compare_matrices("correlations.txt", order="circular6")
    >>> print(result.summary())
    >>> result.rthor_results  # Individual matrix results
    >>> result.comparisons  # Pairwise comparison results

    """

    rthor_results: pd.DataFrame
    comparisons: pd.DataFrame
    n_matrices: int
    n_variables: int
    order: np.ndarray
    n_predictions: int
    n_permutations: int

    def summary(self) -> str:
        """Generate formatted summary of results.

        Returns
        -------
        str
            Multi-line summary string with key statistics

        """
        lines = [
            "Matrix Comparison Analysis Summary",
            "=" * 60,
            f"Matrices analyzed: {self.n_matrices}",
            f"Variables per matrix: {self.n_variables}",
            f"Hypothesized predictions: {self.n_predictions}",
            f"Permutations tested: {self.n_permutations}",
            "",
            "Individual Matrix Results:",
            "-" * 60,
        ]

        # Individual results
        for _, row in self.rthor_results.iterrows():
            mat_id = row["matrix"]
            ci = row["ci"]
            p_val = row["p_value"]
            sig = (
                "***"
                if p_val < 0.001
                else "**"
                if p_val < 0.01
                else "*"
                if p_val < 0.05
                else ""
            )
            lines.append(f"Matrix {mat_id:2d}  CI={ci:7.4f}  p={p_val:.4f} {sig}")

        lines.extend(
            [
                "",
                "Pairwise Comparisons:",
                "-" * 60,
            ]
        )

        # Pairwise comparisons
        for _, row in self.comparisons.iterrows():
            m1 = int(row["matrix1"])
            m2 = int(row["matrix2"])
            ci = row["ci"]
            p_val = row["p_value"]
            sig = (
                "***"
                if p_val < 0.001
                else "**"
                if p_val < 0.01
                else "*"
                if p_val < 0.05
                else ""
            )
            lines.append(f"Matrix {m1} vs {m2}  CI={ci:7.4f}  p={p_val:.4f} {sig}")

        lines.extend(
            [
                "",
                "Significance codes: *** p<0.001, ** p<0.01, * p<0.05",
            ]
        )

        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        """Convert results to dictionary for serialization.

        Returns
        -------
        dict
            Dictionary containing all result data

        """
        return {
            "rthor_results": self.rthor_results.to_dict(orient="records"),
            "comparisons": self.comparisons.to_dict(orient="records"),
            "n_matrices": self.n_matrices,
            "n_variables": self.n_variables,
            "order": self.order.tolist(),
            "n_predictions": self.n_predictions,
            "n_permutations": self.n_permutations,
        }

    def __str__(self) -> str:
        """Return summary string representation."""
        return self.summary()

    def __repr__(self) -> str:
        """Return detailed representation."""
        return (
            f"ComparisonResult(n_matrices={self.n_matrices}, "
            f"n_variables={self.n_variables}, "
            f"n_comparisons={len(self.comparisons)})"
        )
