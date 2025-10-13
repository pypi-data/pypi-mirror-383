"""Compact formatting utilities for displaying RTHOR results."""

from __future__ import annotations

import pandas as pd

from rthor._utils import is_installed, requires


def print_results(results: pd.DataFrame, *, use_rich: bool = True) -> None:
    """Print RTHOR test results in a compact, interpretable format."""
    if use_rich and is_installed("rich"):
        _print_results_rich(results)
    else:
        _print_results_plain(results)


def _interpret_ci(ci: float) -> tuple[str, str, str]:
    """Interpret CI value and return (interpretation, quality, symbol)."""
    if ci >= 0.7:
        return "Excellent fit", "excellent", "✓"
    if ci >= 0.5:
        return "Good fit", "good", "↗"
    if ci >= 0.3:
        return "Moderate fit", "moderate", "→"
    if ci >= 0.1:
        return "Weak fit", "weak", "↘"
    if ci >= 0:
        return "Minimal fit", "minimal", "⚠"
    return "Poor fit", "poor", "✗"


def _print_results_plain(results: pd.DataFrame) -> None:
    """Generate concise plain text output of RTHOR results."""
    n_mats = len(results)
    n_vars = int(results["n_variables"].iloc[0])
    n_preds = int(results["predictions"].iloc[0])
    n_perms = int(results["n_permutations"].iloc[0])

    print("=" * 70)  # noqa: T201
    print("RTHOR TEST RESULTS")  # noqa: T201
    print("=" * 70)  # noqa: T201
    print(  # noqa: T201
        f"{n_mats} {'matrix' if n_mats == 1 else 'matrices'} • {n_vars} variables • {n_preds} predictions • {n_perms:,} permutations"
    )
    print()  # noqa: T201

    # Results for each matrix
    for idx, (_, row) in enumerate(results.iterrows(), 1):
        label = row["label"] if row["label"] else f"Matrix {row['matrix']}"
        ci = row["ci"]
        p_val = row["p_value"]
        agreements = int(row["agreements"])
        violations = n_preds - agreements - int(row["ties"])

        # Interpretation
        interpretation, _, symbol = _interpret_ci(ci)

        # Significance
        if p_val < 0.001:
            sig = "p < .001 ***"
        elif p_val < 0.01:
            sig = "p < .01 **"
        elif p_val < 0.05:
            sig = "p < .05 *"
        else:
            sig = f"p = {p_val:.3f} ns"

        print(f"[{idx}] {label}")  # noqa: T201
        print(f"    {symbol} CI = {ci:.3f} ({interpretation}) • {sig}")  # noqa: T201
        print(  # noqa: T201
            f"    {agreements}/{n_preds} satisfied ({agreements / n_preds * 100:.0f}%), {violations}/{n_preds} violated ({violations / n_preds * 100:.0f}%)"
        )
        print()  # noqa: T201

    print("=" * 70)  # noqa: T201


def _print_results_rich(results: pd.DataFrame) -> None:
    """Create compact rich formatted output of RTHOR results."""
    requires("rich", reason="use_rich=True", extras="rich")
    from rich import box
    from rich.console import Console

    n_mats = len(results)
    n_vars = int(results["n_variables"].iloc[0])
    n_preds = int(results["predictions"].iloc[0])
    n_perms = int(results["n_permutations"].iloc[0])

    console = Console()

    # Create a single comprehensive table
    from rich.table import Table

    table = Table(
        title=f"[bold cyan]RTHOR Test Results[/]\n[dim]{n_mats} {'matrix' if n_mats == 1 else 'matrices'} • {n_vars} variables • {n_preds} predictions • {n_perms:,} permutations[/]",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan",
        caption="[dim italic]ℹ️  Higher CI values indicate better fit (range: -1 to +1)[/]",  # noqa: RUF001
        caption_style="dim italic",
    )

    table.add_column("Matrix", justify="left", style="bold white", no_wrap=True)
    table.add_column("", justify="center", width=2)  # Symbol
    table.add_column("CI", justify="right", style="bold")
    table.add_column("Interpretation", justify="left")
    table.add_column("Significance", justify="center")
    table.add_column("Satisfied", justify="right", style="green")
    table.add_column("Violated", justify="right", style="red")

    # Add rows for each matrix
    for idx, (_, row) in enumerate(results.iterrows(), 1):
        label = row["label"] if row["label"] else f"Matrix {row['matrix']}"
        ci = row["ci"]
        p_val = row["p_value"]
        agreements = int(row["agreements"])
        violations = n_preds - agreements - int(row["ties"])

        # Interpretation
        interpretation, quality, symbol = _interpret_ci(ci)

        # Color based on quality
        if quality in ("excellent", "good"):
            ci_color = "bright_green"
        elif quality == "moderate":
            ci_color = "yellow"
        else:
            ci_color = "red"

        # Significance
        if p_val < 0.001:
            sig_text = "p<.001 ***"
            sig_color = "bright_red"
        elif p_val < 0.01:
            sig_text = "p<.01 **"
            sig_color = "yellow"
        elif p_val < 0.05:
            sig_text = "p<.05 *"
            sig_color = "green"
        else:
            sig_text = f"p={p_val:.3f}"
            sig_color = "dim"

        table.add_row(
            f"[{idx}] {label}",
            f"[{ci_color}]{symbol}[/]",
            f"[{ci_color}]{ci:.3f}[/]",
            interpretation,
            f"[{sig_color}]{sig_text}[/]",
            f"{agreements}/{n_preds} ({agreements / n_preds * 100:.0f}%)",
            f"{violations}/{n_preds} ({violations / n_preds * 100:.0f}%)",
        )

    console.print(table)


def print_comparison(
    individual: pd.DataFrame,
    pairwise: pd.DataFrame,
    *,
    use_rich: bool = True,
) -> None:
    """Print comparison results in a compact, interpretable format."""
    if use_rich and is_installed("rich"):
        _print_comparison_rich(individual, pairwise)
    else:
        _print_comparison_plain(individual, pairwise)


def _print_comparison_plain(individual: pd.DataFrame, pairwise: pd.DataFrame) -> None:
    """Generate concise plain text output of comparison results."""
    n_mats = len(individual)
    n_vars = int(individual["n_variables"].iloc[0])
    n_preds = int(individual["predictions"].iloc[0])
    n_perms = int(individual["n_permutations"].iloc[0])

    print("=" * 70)  # noqa: T201
    print("RTHOR MATRIX COMPARISON")  # noqa: T201
    print("=" * 70)  # noqa: T201
    print(  # noqa: T201
        f"{n_mats} matrices • {n_vars} variables • {n_preds} predictions • {n_perms:,} permutations"
    )
    print()  # noqa: T201

    # Individual results
    print("INDIVIDUAL FIT:")  # noqa: T201
    for _, row in individual.iterrows():
        mat_id = int(row["matrix"])
        ci = row["ci"]
        p_val = row["p_value"]
        interpretation, _, symbol = _interpret_ci(ci)

        sig = (
            "***"
            if p_val < 0.001
            else "**"
            if p_val < 0.01
            else "*"
            if p_val < 0.05
            else "ns"
        )
        print(f"  Matrix {mat_id}: {symbol} CI = {ci:.3f} ({interpretation}) [{sig}]")  # noqa: T201
    print()  # noqa: T201

    # Pairwise comparisons
    print("PAIRWISE COMPARISONS:")  # noqa: T201
    for _, row in pairwise.iterrows():
        m1 = int(row["matrix1"])
        m2 = int(row["matrix2"])
        ci = row["ci"]
        p_val = row["p_value"]
        both = int(row["both_agree"])
        only1 = int(row["only1"])
        only2 = int(row["only2"])

        # Interpret the comparison
        if abs(ci) < 0.05:
            winner = "Similar fit"
            symbol = "="
        elif ci > 0:
            winner = f"Matrix {m2} better"
            symbol = "↑"
        else:
            winner = f"Matrix {m1} better"
            symbol = "↓"

        sig = (
            "***"
            if p_val < 0.001
            else "**"
            if p_val < 0.01
            else "*"
            if p_val < 0.05
            else "ns"
        )

        print(  # noqa: T201
            f"  {m1} vs {m2}: {symbol} {winner} (CI = {ci:+.3f}) [{sig}] | Both: {both}, Only {m1}: {only1}, Only {m2}: {only2}"
        )

    print()  # noqa: T201
    print("=" * 70)  # noqa: T201


def _print_comparison_rich(individual: pd.DataFrame, pairwise: pd.DataFrame) -> None:
    """Create compact rich formatted output of comparison results."""
    requires("rich", reason="use_rich=True", extras="rich")
    from rich import box
    from rich.console import Console
    from rich.table import Table

    n_mats = len(individual)
    n_vars = int(individual["n_variables"].iloc[0])
    n_preds = int(individual["predictions"].iloc[0])
    n_perms = int(individual["n_permutations"].iloc[0])

    console = Console()

    # Create main table with sections
    table = Table(
        title=f"[bold cyan]RTHOR Matrix Comparison[/]\n[dim]{n_mats} matrices • {n_vars} variables • {n_preds} predictions • {n_perms:,} permutations[/]",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan",
        caption="[dim italic]Info: Positive CI means matrix 2 fits better, negative means matrix 1 fits better[/]",
        caption_style="dim italic",
    )

    table.add_column("Comparison", justify="left", style="bold white")
    table.add_column("", justify="center", width=2)  # Symbol
    table.add_column("CI", justify="right", style="bold")
    table.add_column("Result", justify="left")
    table.add_column("Significance", justify="center")
    table.add_column("Both", justify="right", style="dim")
    table.add_column("Only 1", justify="right", style="dim")
    table.add_column("Only 2", justify="right", style="dim")

    # Add individual results first
    for _, row in individual.iterrows():
        mat_id = int(row["matrix"])
        ci = row["ci"]
        p_val = row["p_value"]
        agreements = int(row["agreements"])
        interpretation, quality, symbol = _interpret_ci(ci)

        ci_color = (
            "bright_green"
            if quality in ("excellent", "good")
            else "yellow"
            if quality == "moderate"
            else "red"
        )
        sig = (
            "p<.001 ***"
            if p_val < 0.001
            else "p<.01 **"
            if p_val < 0.01
            else "p<.05 *"
            if p_val < 0.05
            else f"p={p_val:.3f}"
        )
        sig_color = (
            "bright_red"
            if p_val < 0.001
            else "yellow"
            if p_val < 0.01
            else "green"
            if p_val < 0.05
            else "dim"
        )

        table.add_row(
            f"Matrix {mat_id}",
            f"[{ci_color}]{symbol}[/]",
            f"[{ci_color}]{ci:.3f}[/]",
            interpretation,
            f"[{sig_color}]{sig}[/]",
            f"{agreements}/{n_preds}",
            "—",
            "—",
        )

    # Add separator
    table.add_section()

    # Add pairwise comparisons
    for _, row in pairwise.iterrows():
        m1 = int(row["matrix1"])
        m2 = int(row["matrix2"])
        ci = row["ci"]
        p_val = row["p_value"]
        both = int(row["both_agree"])
        only1 = int(row["only1"])
        only2 = int(row["only2"])

        # Interpret the comparison
        if abs(ci) < 0.05:
            winner = "Similar fit"
            ci_color = "yellow"
            symbol = "="
        elif ci > 0:
            winner = f"Matrix {m2} better"
            ci_color = "green"
            symbol = "↑"
        else:
            winner = f"Matrix {m1} better"
            ci_color = "green"
            symbol = "↓"

        sig = (
            "p<.001 ***"
            if p_val < 0.001
            else "p<.01 **"
            if p_val < 0.01
            else "p<.05 *"
            if p_val < 0.05
            else f"p={p_val:.3f}"
        )
        sig_color = (
            "bright_red"
            if p_val < 0.001
            else "yellow"
            if p_val < 0.01
            else "green"
            if p_val < 0.05
            else "dim"
        )

        table.add_row(
            f"{m1} vs {m2}",
            f"[{ci_color}]{symbol}[/]",
            f"[{ci_color}]{ci:+.3f}[/]",
            winner,
            f"[{sig_color}]{sig}[/]",
            str(both),
            str(only1),
            str(only2),
        )

    console.print(table)
