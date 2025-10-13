"""Unit tests for I/O functions."""

from pathlib import Path

import numpy as np

from rthor.io import extract_lower_triangle, read_correlation_matrices


class TestReadCorrelationMatrices:
    """Test read_correlation_matrices function."""

    def test_read_input_txt(self, fixtures_dir: Path) -> None:
        """Test reading the test input.txt file."""
        input_file = fixtures_dir / "input.txt"
        dmatm = read_correlation_matrices(input_file, n=6, nmat=3)

        # Should be 3D array with correct shape
        assert dmatm.shape == (6, 6, 3)

        # Check that matrices are symmetric
        for m in range(3):
            np.testing.assert_array_almost_equal(
                dmatm[:, :, m],
                dmatm[:, :, m].T,
                err_msg=f"Matrix {m} is not symmetric",
            )

        # Check diagonal is all 1.0
        for m in range(3):
            np.testing.assert_array_almost_equal(
                np.diag(dmatm[:, :, m]),
                np.ones(6),
                err_msg=f"Matrix {m} diagonal is not all 1.0",
            )

    def test_first_matrix_values(self, fixtures_dir: Path) -> None:
        """Test specific values from first matrix."""
        input_file = fixtures_dir / "input.txt"
        dmatm = read_correlation_matrices(input_file, n=6, nmat=3)

        # Check some specific values from first matrix
        # Based on input.txt lines 1-6
        mat0 = dmatm[:, :, 0]

        assert abs(mat0[0, 0] - 1.00) < 1e-6
        assert abs(mat0[1, 0] - 0.62) < 1e-6
        assert abs(mat0[0, 1] - 0.62) < 1e-6  # Symmetric
        assert abs(mat0[2, 0] - 0.40) < 1e-6
        assert abs(mat0[2, 1] - 0.62) < 1e-6
        assert abs(mat0[5, 4] - 0.74) < 1e-6

    def test_matrices_are_different(self, fixtures_dir: Path) -> None:
        """Test that the three matrices are different."""
        input_file = fixtures_dir / "input.txt"
        dmatm = read_correlation_matrices(input_file, n=6, nmat=3)

        # Matrices should not all be the same
        assert not np.array_equal(dmatm[:, :, 0], dmatm[:, :, 1])
        assert not np.array_equal(dmatm[:, :, 1], dmatm[:, :, 2])
        assert not np.array_equal(dmatm[:, :, 0], dmatm[:, :, 2])


class TestExtractLowerTriangle:
    """Test extract_lower_triangle function."""

    def test_extract_with_diagonal(self) -> None:
        """Test extracting lower triangle with diagonal."""
        mat = np.array(
            [
                [1.0, 0.8, 0.6],
                [0.8, 1.0, 0.7],
                [0.6, 0.7, 1.0],
            ]
        )

        values = extract_lower_triangle(mat, include_diagonal=True)

        # Should be: [1.0, 0.8, 1.0, 0.6, 0.7, 1.0]
        expected = np.array([1.0, 0.8, 1.0, 0.6, 0.7, 1.0])
        np.testing.assert_array_almost_equal(values, expected)

    def test_extract_without_diagonal(self) -> None:
        """Test extracting lower triangle without diagonal."""
        mat = np.array(
            [
                [1.0, 0.8, 0.6],
                [0.8, 1.0, 0.7],
                [0.6, 0.7, 1.0],
            ]
        )

        values = extract_lower_triangle(mat, include_diagonal=False)

        # Should be: [0.8, 0.6, 0.7]
        expected = np.array([0.8, 0.6, 0.7])
        np.testing.assert_array_almost_equal(values, expected)

    def test_extract_length(self) -> None:
        """Test that extracted vector has correct length."""
        n = 5
        mat = np.eye(n)

        with_diag = extract_lower_triangle(mat, include_diagonal=True)
        without_diag = extract_lower_triangle(mat, include_diagonal=False)

        # With diagonal: n + (n-1) + (n-2) + ... + 1 = n(n+1)/2
        assert len(with_diag) == n * (n + 1) // 2

        # Without diagonal: n(n-1)/2
        assert len(without_diag) == n * (n - 1) // 2
