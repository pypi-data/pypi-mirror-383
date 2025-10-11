"""Regression tests against R RTHORR package outputs.

These tests ensure that the Python implementation produces identical results
to the original R implementation.
"""

from pathlib import Path

import pandas as pd
import pytest

from rthor import compare_matrices, rthor_test


class TestRthorTestRegression:
    """Test rthor_test() function against R outputs."""

    def test_rthor_test_from_file_matches_r(
        self,
        input_matrix_file: Path,
        expected_randall_output: pd.DataFrame,
    ) -> None:
        """Test that rthor_test() with file input matches R randall() output."""
        result = rthor_test(
            data=input_matrix_file,
            n_matrices=3,
            n_variables=6,
            order="circular6",
            labels=["sample_one", "sample_two", "sample_three"],
        )

        # Check result type
        assert result.__class__.__name__ == "RTHORResult"
        assert isinstance(result.results, pd.DataFrame)

        # Check metadata
        assert result.n_matrices == 3
        assert result.n_variables == 6
        assert result.n_predictions == 72

        # Check DataFrame structure
        assert result.results.shape == expected_randall_output.shape

        # Map new column names to old for comparison
        results_mapped = result.results.rename(
            columns={
                "matrix": "mat",
                "predictions": "pred",
                "agreements": "met",
                "ties": "tie",
                "ci": "CI",
                "p_value": "p",
                "label": "description",
            }
        )

        # Check numerical columns match R output
        numerical_cols = ["mat", "pred", "met", "tie", "CI", "p"]
        for col in numerical_cols:
            pd.testing.assert_series_equal(
                results_mapped[col].astype(float),
                expected_randall_output[col].astype(float),
                rtol=1e-10,
                atol=1e-12,
                check_names=False,
            )

        # Check description column
        pd.testing.assert_series_equal(
            results_mapped["description"],
            expected_randall_output["description"],
            check_names=False,
        )

    def test_rthor_test_from_dataframes_matches_r(
        self,
        df_list: list[pd.DataFrame],
        expected_randall_from_df_output: pd.DataFrame,
    ) -> None:
        """Test rthor_test() with DataFrame input matches R randall_from_df()."""
        result = rthor_test(
            data=df_list,
            order="circular6",
            labels=["whole sample", "t1", "t2", "t3", "t4"],
        )

        # Check result type and metadata
        assert result.__class__.__name__ == "RTHORResult"
        assert result.n_matrices == 5
        assert result.n_variables == 6

        # Map column names
        results_mapped = result.results.rename(
            columns={
                "matrix": "mat",
                "predictions": "pred",
                "agreements": "met",
                "ties": "tie",
                "ci": "CI",
                "p_value": "p",
                "label": "description",
            }
        )

        # Check numerical columns
        numerical_cols = ["mat", "pred", "met", "tie", "CI", "p"]
        for col in numerical_cols:
            pd.testing.assert_series_equal(
                results_mapped[col].astype(float),
                expected_randall_from_df_output[col].astype(float),
                rtol=1e-10,
                atol=1e-12,
                check_names=False,
            )

        # Check labels
        pd.testing.assert_series_equal(
            results_mapped["description"],
            expected_randall_from_df_output["description"],
            check_names=False,
        )


class TestCompareMatricesRegression:
    """Test compare_matrices() function against R outputs."""

    def test_compare_matrices_from_file_matches_r(
        self,
        input_matrix_file: Path,
        expected_randmf_output: dict[str, pd.DataFrame],
    ) -> None:
        """Test that compare_matrices() with file input matches R randmf() output."""
        result = compare_matrices(
            data=input_matrix_file,
            n_matrices=3,
            n_variables=6,
            order="circular6",
        )

        # Check result type
        assert result.__class__.__name__ == "ComparisonResult"
        assert isinstance(result.rthor_results, pd.DataFrame)
        assert isinstance(result.comparisons, pd.DataFrame)

        # Check metadata
        assert result.n_matrices == 3
        assert result.n_variables == 6

        # Test RTHOR results (individual matrix tests)
        rthor_mapped = result.rthor_results.rename(
            columns={
                "matrix": "mat",
                "predictions": "pred",
                "agreements": "met",
                "ties": "tie",
                "ci": "CI",
                "p_value": "p",
            }
        )

        rthor_expected = expected_randmf_output["RTHOR"]
        # Note: rthor_mapped has 7 columns (includes label), rthor_expected has 6
        assert (
            rthor_mapped.shape[0] == rthor_expected.shape[0]
        )  # Same number of matrices

        # Compare only the numerical columns that R outputs
        numerical_cols = ["mat", "pred", "met", "tie", "CI", "p"]
        for col in numerical_cols:
            pd.testing.assert_series_equal(
                rthor_mapped[col].astype(float),
                rthor_expected[col].astype(float),
                rtol=1e-10,
                atol=1e-12,
                check_names=False,
            )

        # Test comparisons results
        comp_mapped = result.comparisons.rename(
            columns={
                "matrix1": "mat1",
                "matrix2": "mat2",
                "both_agree": "bothmet",
                "only1": "1met2not",
                "only2": "2met1not",
                "neither": "neither",
                "ci": "CI",
                "p_value": "p",
            }
        )

        comp_expected = expected_randmf_output["comparisons"]
        # Note: comp_mapped has 8 columns (includes p_value separately),
        # comp_expected may have 6 (p combined with CI in some formats)
        assert (
            comp_mapped.shape[0] == comp_expected.shape[0]
        )  # Same number of comparisons

        numerical_cols = [
            "mat1",
            "mat2",
            "bothmet",
            "1met2not",
            "2met1not",
            "neither",
            "CI",
            "p",
        ]
        for col in numerical_cols:
            pd.testing.assert_series_equal(
                comp_mapped[col].astype(float),
                comp_expected[col].astype(float),
                rtol=1e-10,
                atol=1e-12,
                check_names=False,
            )

    def test_compare_matrices_from_dataframes_matches_r(
        self,
        df_list: list[pd.DataFrame],
        expected_randmf_from_df_output: dict[str, pd.DataFrame],
    ) -> None:
        """Test compare_matrices() with DataFrame input matches R randmf_from_df()."""
        result = compare_matrices(
            data=df_list,
            order="circular6",
        )

        # Check result type
        assert result.__class__.__name__ == "ComparisonResult"
        assert result.n_matrices == 5
        assert result.n_variables == 6

        # Test RTHOR results
        rthor_mapped = result.rthor_results.rename(
            columns={
                "matrix": "mat",
                "predictions": "pred",
                "agreements": "met",
                "ties": "tie",
                "ci": "CI",
                "p_value": "p",
            }
        )

        rthor_expected = expected_randmf_from_df_output["RTHOR"]

        numerical_cols = ["mat", "pred", "met", "tie", "CI", "p"]
        for col in numerical_cols:
            pd.testing.assert_series_equal(
                rthor_mapped[col].astype(float),
                rthor_expected[col].astype(float),
                rtol=1e-10,
                atol=1e-12,
                check_names=False,
            )

        # Test comparisons
        comp_mapped = result.comparisons.rename(
            columns={
                "matrix1": "mat1",
                "matrix2": "mat2",
                "both_agree": "bothmet",
                "only1": "1met2not",
                "only2": "2met1not",
                "neither": "neither",
                "ci": "CI",
                "p_value": "p",
            }
        )

        comp_expected = expected_randmf_from_df_output["comparisons"]

        numerical_cols = [
            "mat1",
            "mat2",
            "bothmet",
            "1met2not",
            "2met1not",
            "neither",
            "CI",
            "p",
        ]
        for col in numerical_cols:
            pd.testing.assert_series_equal(
                comp_mapped[col].astype(float),
                comp_expected[col].astype(float),
                rtol=1e-10,
                atol=1e-12,
                check_names=False,
            )


class TestResultObjectMethods:
    """Test result object methods work correctly."""

    def test_rthor_result_summary(
        self,
        input_matrix_file: Path,
    ) -> None:
        """Test that RTHORResult.summary() generates output."""
        result = rthor_test(
            data=input_matrix_file,
            n_matrices=3,
            n_variables=6,
            order="circular6",
            labels=["A", "B", "C"],
        )

        summary = result.summary()
        assert isinstance(summary, str)
        assert "RTHOR Analysis Summary" in summary
        assert "Matrices analyzed: 3" in summary
        assert "Variables per matrix: 6" in summary

    def test_comparison_result_summary(
        self,
        input_matrix_file: Path,
    ) -> None:
        """Test that ComparisonResult.summary() generates output."""
        result = compare_matrices(
            data=input_matrix_file,
            n_matrices=3,
            n_variables=6,
            order="circular6",
        )

        summary = result.summary()
        assert isinstance(summary, str)
        assert "Matrix Comparison Analysis Summary" in summary
        assert "Matrices analyzed: 3" in summary

    def test_rthor_result_to_dict(
        self,
        input_matrix_file: Path,
    ) -> None:
        """Test that RTHORResult.to_dict() works."""
        result = rthor_test(
            data=input_matrix_file,
            n_matrices=3,
            n_variables=6,
            order="circular6",
        )

        result_dict = result.to_dict()
        assert isinstance(result_dict, dict)
        assert "results" in result_dict
        assert "n_matrices" in result_dict
        assert result_dict["n_matrices"] == 3


class TestInputValidation:
    """Test that input validation works correctly."""

    def test_invalid_order_preset(
        self,
        input_matrix_file: Path,
    ) -> None:
        """Test that invalid order preset raises error."""
        with pytest.raises(ValueError, match="Unknown order preset"):
            rthor_test(
                data=input_matrix_file,
                n_matrices=3,
                n_variables=6,
                order="invalid_order",
            )

    def test_order_mismatch_n_variables(
        self,
        df_list: list[pd.DataFrame],
    ) -> None:
        """Test that order/n_variables mismatch raises error."""
        # Use DataFrame list with 5 columns instead of 6
        df_5col = [df.iloc[:, :5] for df in df_list]

        with pytest.raises(ValueError, match=r"circular6.*6 variables"):
            rthor_test(
                data=df_5col,
                order="circular6",  # Wrong! This requires 6 variables, but we have 5
            )

    def test_file_input_requires_dimensions(
        self,
        input_matrix_file: Path,
    ) -> None:
        """Test that file input requires n_matrices and n_variables."""
        with pytest.raises(
            ValueError, match="n_matrices and n_variables must be specified"
        ):
            rthor_test(data=input_matrix_file, order="circular6")

    def test_labels_length_mismatch(
        self,
        input_matrix_file: Path,
    ) -> None:
        """Test that wrong number of labels raises error."""
        with pytest.raises(ValueError, match=r"Number of labels.*doesn't match"):
            rthor_test(
                data=input_matrix_file,
                n_matrices=3,
                n_variables=6,
                order="circular6",
                labels=["A", "B"],  # Wrong! Should be 3 labels
            )

    def test_compare_matrices_requires_multiple(
        self,
        df_list: list[pd.DataFrame],
    ) -> None:
        """Test that compare_matrices requires at least 2 matrices."""
        with pytest.raises(ValueError, match="requires at least 2 matrices"):
            compare_matrices(data=[df_list[0]], order="circular6")
