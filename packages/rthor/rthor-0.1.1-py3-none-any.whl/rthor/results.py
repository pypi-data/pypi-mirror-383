"""Result classes for RTHOR analyses."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import numpy as np
import pandas as pd

from rthor._utils import is_installed, is_running_in_ipynb, requires

if TYPE_CHECKING:
    from rich.table import Table


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

    def summary(self, *, print_table: bool = False) -> dict[str, Any] | None:
        """Generate formatted summary of RTHOR results.

        Args:
            print_table: If True, print a rich-formatted table to the console and
                return None. If False, return a dictionary with summary information.

        Returns:
            Dictionary containing summary information if print_table=False,
            otherwise None after printing the table.

        Examples:
            >>> result.summary()  # Returns summary dict
            >>> result.summary(print_table=True)  # Prints rich table to console

        """
        summary_dict = {
            "n_matrices": self.n_matrices,
            "n_variables": self.n_variables,
            "n_predictions": self.n_predictions,
            "n_permutations": self.n_permutations,
            "results": self.results.to_dict(orient="records"),
        }

        if not print_table:
            return summary_dict

        _ = self._create_rich_table(prints=True)
        return None

    def _create_text_summary(self) -> str:
        """Generate plain text summary (fallback when rich is not available)."""
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

    def _create_rich_table(self, *, prints: bool = False) -> Table:
        """Create a rich table displaying RTHOR results.

        Args:
            prints: If True, print the table to console before returning.

        Returns:
            Rich Table object with formatted results.

        """
        requires("rich", reason="print_table=True", extras="rich")
        import rich.box  # noqa: PLC0415
        import rich.table  # noqa: PLC0415
        from rich.console import Console  # noqa: PLC0415

        # Create main table
        table = rich.table.Table(
            title="RTHOR Analysis Results",
            box=rich.box.DOUBLE_EDGE,
            show_header=True,
            header_style="bold magenta",
        )

        # Add metadata section at top
        table.add_column("Metric", style="dim")
        table.add_column("Value", style="bold cyan")

        table.add_row("Matrices analyzed", str(self.n_matrices))
        table.add_row("Variables per matrix", str(self.n_variables))
        table.add_row("Hypothesized predictions", str(self.n_predictions))
        table.add_row("Permutations tested", str(self.n_permutations))

        # Create results table
        results_table = rich.table.Table(
            title="Individual Matrix Results",
            box=rich.box.SIMPLE,
            show_header=True,
            header_style="bold yellow",
        )

        results_table.add_column("Matrix", justify="right", style="cyan")
        results_table.add_column("Label", style="white")
        results_table.add_column("CI", justify="right", style="green")
        results_table.add_column("p-value", justify="right", style="yellow")
        results_table.add_column("Sig.", justify="center", style="bold red")
        results_table.add_column("Predictions", justify="right", style="dim")
        results_table.add_column("Agreements", justify="right", style="dim")

        # Add rows for each matrix
        for _, row in self.results.iterrows():
            label = row["label"] if row["label"] else f"Matrix {row['matrix']}"
            ci = row["ci"]
            p_val = row["p_value"]

            # Determine significance
            if p_val < 0.001:
                sig = "***"
                sig_style = "bold red"
            elif p_val < 0.01:
                sig = "**"
                sig_style = "bold yellow"
            elif p_val < 0.05:
                sig = "*"
                sig_style = "bold"
            else:
                sig = ""
                sig_style = "dim"

            results_table.add_row(
                str(row["matrix"]),
                label,
                f"{ci:.4f}",
                f"{p_val:.4f}",
                f"[{sig_style}]{sig}[/]",
                str(row["predictions"]),
                str(row["agreements"]),
            )

        # Add caption
        results_table.caption = "Significance codes: *** p<0.001, ** p<0.01, * p<0.05"
        results_table.caption_style = "dim italic"

        if prints:
            console = Console()
            console.print(table)
            console.print()
            console.print(results_table)

        return results_table

    def _repr_mimebundle_(
        self,
        include: set[str] | None = None,
        exclude: set[str] | None = None,
    ) -> dict[str, str]:
        """Display rich table in Jupyter notebooks automatically."""
        if is_running_in_ipynb() and is_installed("rich"):
            table = self._create_rich_table(prints=False)
            # Convert sets to lists for rich's _repr_mimebundle_
            inc = list(include) if include is not None else []
            exc = list(exclude) if exclude is not None else []
            return table._repr_mimebundle_(  # type: ignore[attr-defined]
                include=inc, exclude=exc
            )
        # Return a plaintext representation
        return {"text/plain": repr(self)}

    def to_dict(self) -> dict[str, Any]:
        """Convert results to dictionary for serialization.

        Returns:
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
        return self._create_text_summary()

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

    Attributes:
        rthor_results: Individual RTHOR test results for each matrix
            (same format as RTHORResult.results)
        comparisons: Pairwise comparison results with columns:

            - `matrix1`: First matrix identifier
            - `matrix2`: Second matrix identifier
            - `both_agree`: Count of predictions both matrices satisfy
            - `only1`: Count satisfied only by matrix 1
            - `only2`: Count satisfied only by matrix 2
            - `neither`: Count satisfied by neither matrix
            - `ci`: Comparison Correspondence Index
            - `p_value`: Randomization test p-value
        n_matrices: Number of matrices analyzed
        n_variables: Number of variables in each matrix
        order: The hypothesized ordering used for analysis
        n_predictions: Total number of hypothesized predictions
        n_permutations: Number of permutations used in randomization test

    Examples:
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

    def summary(self, *, print_table: bool = False) -> dict[str, Any] | None:
        """Generate formatted summary of comparison results.

        Args:
            print_table: If True, print a rich-formatted table to the console and
                return None. If False, return a dictionary with summary information.

        Returns:
            Dictionary containing summary information if print_table=False,
            otherwise None after printing the table.

        Examples:
            >>> result.summary()  # Returns summary dict
            >>> result.summary(print_table=True)  # Prints rich table to console

        """
        summary_dict = {
            "n_matrices": self.n_matrices,
            "n_variables": self.n_variables,
            "n_predictions": self.n_predictions,
            "n_permutations": self.n_permutations,
            "rthor_results": self.rthor_results.to_dict(orient="records"),
            "comparisons": self.comparisons.to_dict(orient="records"),
        }

        if not print_table:
            return summary_dict

        _ = self._create_rich_table(prints=True)
        return None

    def _create_text_summary(self) -> str:
        """Generate plain text summary (fallback when rich is not available)."""
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

    def _create_rich_table(self, *, prints: bool = False) -> Table:
        """Create a rich table displaying comparison results.

        Args:
            prints: If True, print the table to console before returning.

        Returns:
            Rich Table object with formatted results.

        """
        requires("rich", reason="print_table=True", extras="rich")
        from rich.console import Console  # noqa: PLC0415

        meta_table = self._create_metadata_table()
        individual_table = self._create_individual_results_table()
        comparison_table = self._create_pairwise_comparison_table()

        if prints:
            console = Console()
            console.print(meta_table)
            console.print()
            console.print(individual_table)
            console.print()
            console.print(comparison_table)

        return comparison_table

    def _create_metadata_table(self) -> Table:
        """Create metadata table with analysis parameters."""
        import rich.box  # noqa: PLC0415
        import rich.table  # noqa: PLC0415

        table = rich.table.Table(
            title="Matrix Comparison Analysis",
            box=rich.box.DOUBLE_EDGE,
            show_header=True,
            header_style="bold magenta",
        )

        table.add_column("Metric", style="dim")
        table.add_column("Value", style="bold cyan")

        table.add_row("Matrices analyzed", str(self.n_matrices))
        table.add_row("Variables per matrix", str(self.n_variables))
        table.add_row("Hypothesized predictions", str(self.n_predictions))
        table.add_row("Permutations tested", str(self.n_permutations))

        return table

    def _create_individual_results_table(self) -> Table:
        """Create table for individual matrix results."""
        import rich.box  # noqa: PLC0415
        import rich.table  # noqa: PLC0415

        table = rich.table.Table(
            title="Individual Matrix Results",
            box=rich.box.SIMPLE,
            show_header=True,
            header_style="bold yellow",
        )

        table.add_column("Matrix", justify="right", style="cyan")
        table.add_column("CI", justify="right", style="green")
        table.add_column("p-value", justify="right", style="yellow")
        table.add_column("Sig.", justify="center", style="bold red")
        table.add_column("Predictions", justify="right", style="dim")
        table.add_column("Agreements", justify="right", style="dim")

        for _, row in self.rthor_results.iterrows():
            sig, sig_style = self._get_significance(row["p_value"])
            table.add_row(
                str(row["matrix"]),
                f"{row['ci']:.4f}",
                f"{row['p_value']:.4f}",
                f"[{sig_style}]{sig}[/]",
                str(row["predictions"]),
                str(row["agreements"]),
            )

        table.caption = "Significance codes: *** p<0.001, ** p<0.01, * p<0.05"
        table.caption_style = "dim italic"

        return table

    def _create_pairwise_comparison_table(self) -> Table:
        """Create table for pairwise matrix comparisons."""
        import rich.box  # noqa: PLC0415
        import rich.table  # noqa: PLC0415

        table = rich.table.Table(
            title="Pairwise Comparisons",
            box=rich.box.SIMPLE,
            show_header=True,
            header_style="bold yellow",
        )

        table.add_column("Matrix 1", justify="right", style="cyan")
        table.add_column("Matrix 2", justify="right", style="cyan")
        table.add_column("Both", justify="right", style="dim")
        table.add_column("Only 1", justify="right", style="dim")
        table.add_column("Only 2", justify="right", style="dim")
        table.add_column("Neither", justify="right", style="dim")
        table.add_column("CI", justify="right", style="green")
        table.add_column("p-value", justify="right", style="yellow")
        table.add_column("Sig.", justify="center", style="bold red")

        for _, row in self.comparisons.iterrows():
            sig, sig_style = self._get_significance(row["p_value"])
            table.add_row(
                str(int(row["matrix1"])),
                str(int(row["matrix2"])),
                str(row["both_agree"]),
                str(row["only1"]),
                str(row["only2"]),
                str(row["neither"]),
                f"{row['ci']:.4f}",
                f"{row['p_value']:.4f}",
                f"[{sig_style}]{sig}[/]",
            )

        table.caption = "Significance codes: *** p<0.001, ** p<0.01, * p<0.05"
        table.caption_style = "dim italic"

        return table

    @staticmethod
    def _get_significance(p_value: float) -> tuple[str, str]:
        """Get significance symbol and style based on p-value."""
        if p_value < 0.001:
            return "***", "bold red"
        if p_value < 0.01:
            return "**", "bold yellow"
        if p_value < 0.05:
            return "*", "bold"
        return "", "dim"

    def _repr_mimebundle_(
        self,
        include: set[str] | None = None,
        exclude: set[str] | None = None,
    ) -> dict[str, str]:
        """Display rich table in Jupyter notebooks automatically."""
        if is_running_in_ipynb() and is_installed("rich"):
            table = self._create_rich_table(prints=False)
            # Convert sets to lists for rich's _repr_mimebundle_
            inc = list(include) if include is not None else []
            exc = list(exclude) if exclude is not None else []
            return table._repr_mimebundle_(  # type: ignore[attr-defined]
                include=inc, exclude=exc
            )
        # Return a plaintext representation
        return {"text/plain": repr(self)}

    def to_dict(self) -> dict[str, Any]:
        """Convert results to dictionary for serialization.

        Returns:
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
        return self._create_text_summary()

    def __repr__(self) -> str:
        """Return detailed representation."""
        return (
            f"ComparisonResult(n_matrices={self.n_matrices}, "
            f"n_variables={self.n_variables}, "
            f"n_comparisons={len(self.comparisons)})"
        )
