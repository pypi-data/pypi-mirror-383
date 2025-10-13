"""Unit tests for permutation generation."""

import numpy as np

from rthor.permutations import apply_permutation, generate_permutations


class TestGeneratePermutations:
    """Test generate_permutations function."""

    def test_small_n_all_permutations(self) -> None:
        """Test that all permutations are generated for small n."""
        n = 3
        permat = generate_permutations(n)

        # Should generate 3! = 6 permutations
        assert permat.shape == (6, 3)

        # All values should be 0-indexed (0, 1, 2)
        assert set(permat.flatten()) == {0, 1, 2}

    def test_n6_generates_720_permutations(self) -> None:
        """Test that n=6 generates 720 permutations."""
        n = 6
        permat = generate_permutations(n)

        # Should generate 6! = 720 permutations
        assert permat.shape == (720, 6)

    def test_large_n_caps_at_max_perm(self) -> None:
        """Test that large n is capped at max_perm."""
        n = 10  # 10! = 3,628,800 > 50,000
        permat = generate_permutations(n, max_perm=50000)

        # Should cap at 50,000
        assert permat.shape == (50000, 10)

    def test_lexicographic_order_n3(self) -> None:
        """Test that permutations are in lexicographic order for n=3."""
        permat = generate_permutations(3)

        # Lexicographic order for [0, 1, 2]:
        expected = np.array(
            [
                [0, 1, 2],
                [0, 2, 1],
                [1, 0, 2],
                [1, 2, 0],
                [2, 0, 1],
                [2, 1, 0],
            ]
        )

        np.testing.assert_array_equal(permat, expected)

    def test_each_row_is_valid_permutation(self) -> None:
        """Test that each row contains all values exactly once."""
        n = 5
        permat = generate_permutations(n)

        for row in permat:
            # Each row should contain 0 through n-1 exactly once
            assert set(row) == set(range(n))
            assert len(row) == n

    def test_random_sampling_reproducible(self) -> None:
        """Test that random sampling is reproducible with seed."""
        n = 10
        permat1 = generate_permutations(n, max_perm=100, seed=42)
        permat2 = generate_permutations(n, max_perm=100, seed=42)

        np.testing.assert_array_equal(permat1, permat2)

    def test_random_sampling_different_seeds(self) -> None:
        """Test that different seeds produce different permutations."""
        n = 10
        permat1 = generate_permutations(n, max_perm=100, seed=42)
        permat2 = generate_permutations(n, max_perm=100, seed=43)

        # Should be different (very high probability)
        assert not np.array_equal(permat1, permat2)


class TestApplyPermutation:
    """Test apply_permutation function."""

    def test_identity_permutation(self) -> None:
        """Test that identity permutation returns original matrix."""
        dmat = np.array(
            [
                [1.0, 0.8, 0.6],
                [0.8, 1.0, 0.7],
                [0.6, 0.7, 1.0],
            ]
        )

        perm = np.array([0, 1, 2])  # Identity
        dmatp = apply_permutation(dmat, perm)

        np.testing.assert_array_equal(dmatp, dmat)

    def test_reverse_permutation(self) -> None:
        """Test reversing order."""
        dmat = np.array(
            [
                [1.0, 0.8, 0.6],
                [0.8, 1.0, 0.7],
                [0.6, 0.7, 1.0],
            ]
        )

        perm = np.array([2, 1, 0])  # Reverse
        dmatp = apply_permutation(dmat, perm)

        expected = np.array(
            [
                [1.0, 0.7, 0.6],
                [0.7, 1.0, 0.8],
                [0.6, 0.8, 1.0],
            ]
        )

        np.testing.assert_array_almost_equal(dmatp, expected)

    def test_permutation_preserves_symmetry(self) -> None:
        """Test that permutation preserves correlation matrix symmetry."""
        dmat = np.array(
            [
                [1.0, 0.8, 0.6],
                [0.8, 1.0, 0.7],
                [0.6, 0.7, 1.0],
            ]
        )

        perm = np.array([1, 2, 0])
        dmatp = apply_permutation(dmat, perm)

        # Permuted matrix should still be symmetric
        np.testing.assert_array_almost_equal(dmatp, dmatp.T)

    def test_permutation_preserves_diagonal(self) -> None:
        """Test that diagonal remains 1.0 (for correlation matrices)."""
        dmat = np.array(
            [
                [1.0, 0.8, 0.6, 0.5],
                [0.8, 1.0, 0.7, 0.4],
                [0.6, 0.7, 1.0, 0.3],
                [0.5, 0.4, 0.3, 1.0],
            ]
        )

        perm = np.array([2, 0, 3, 1])
        dmatp = apply_permutation(dmat, perm)

        # Diagonal should all be 1.0
        np.testing.assert_array_almost_equal(np.diag(dmatp), np.ones(4))
