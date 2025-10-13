"""Pytest configuration and fixtures for rthor tests."""

import json
from pathlib import Path

import pandas as pd
import pytest


@pytest.fixture(scope="session")
def fixtures_dir() -> Path:
    """Return path to test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def input_matrix_file(fixtures_dir: Path) -> Path:
    """Return path to input.txt correlation matrix file."""
    return fixtures_dir / "input.txt"


@pytest.fixture(scope="session")
def df_list(fixtures_dir: Path) -> list[pd.DataFrame]:
    """Load the list of test DataFrames."""
    dfs = []
    for i in range(1, 6):  # 5 dataframes
        df = pd.read_csv(fixtures_dir / f"df_list_{i}.csv")
        dfs.append(df)
    return dfs


@pytest.fixture(scope="session")
def expected_randall_output(fixtures_dir: Path) -> pd.DataFrame:
    """Load expected output from R's randall() function."""
    with (fixtures_dir / "randall_output_test.json").open() as f:
        data = json.load(f)
    return pd.DataFrame(data)


@pytest.fixture(scope="session")
def expected_randmf_output(fixtures_dir: Path) -> dict[str, pd.DataFrame]:
    """Load expected output from R's randmf() function."""
    with (fixtures_dir / "randmf_output_rthor.json").open() as f:
        rthor_data = json.load(f)
    with (fixtures_dir / "randmf_output_comparisons.json").open() as f:
        comp_data = json.load(f)
    return {
        "RTHOR": pd.DataFrame(rthor_data),
        "comparisons": pd.DataFrame(comp_data),
    }


@pytest.fixture(scope="session")
def expected_randall_from_df_output(fixtures_dir: Path) -> pd.DataFrame:
    """Load expected output from R's randall_from_df() function."""
    with (fixtures_dir / "randall_from_df_output.json").open() as f:
        data = json.load(f)
    return pd.DataFrame(data)


@pytest.fixture(scope="session")
def expected_randmf_from_df_output(fixtures_dir: Path) -> dict[str, pd.DataFrame]:
    """Load expected output from R's randmf_from_df() function."""
    with (fixtures_dir / "randmf_from_df_output_rthor.json").open() as f:
        rthor_data = json.load(f)
    with (fixtures_dir / "randmf_from_df_output_comparisons.json").open() as f:
        comp_data = json.load(f)
    return {
        "RTHOR": pd.DataFrame(rthor_data),
        "comparisons": pd.DataFrame(comp_data),
    }
