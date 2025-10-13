"""Permutation generation for RTHOR randomization tests."""

import itertools
import math

import numpy as np


def generate_permutations(
    n: int, max_perm: int = 50000, seed: int | None = None
) -> np.ndarray:
    r"""Generate permutations for randomization test.

    ??? info "Note"
        Translated from [`RTHORR/R/randall.R` lines 92-107](https://github.com/michaellynnmorris/RTHORR/blob/c3edb36287c77733ec0a23236b478cc53c1cac0f/R/randall.R#L92).

        Critical for parity with RTHORR: Permutation order must match R exactly.
        R uses `permute::allPerms()` which generates permutations in
        lexicographic order. Python's `itertools.permutations()` also uses
        lexicographic order, so they should match.

        When `n! > max_perm`, uses random sampling instead of all permutations.

    Args:
        n: Number of variables to permute
        max_perm: Maximum number of permutations to generate
        seed: Random seed for reproducibility when using random sampling

    Returns:
        Permutation matrix (nper x n) where each row is a permutation.
            Values are 0-indexed (unlike R which is 1-indexed).

    """
    nper = math.factorial(n)

    if nper > max_perm:
        nper = max_perm
        # Generate random permutations
        # R code: sample.int(n, n, replace=FALSE)
        if seed is not None:
            np.random.seed(seed)

        permat = np.zeros((nper, n), dtype=np.int32)
        for i in range(nper):
            permat[i, :] = np.random.permutation(n)

    else:
        # Generate all permutations
        # R uses permute::allPerms() which is lexicographic order
        # Python's itertools.permutations is also lexicographic
        permat = np.array(list(itertools.permutations(range(n))), dtype=np.int32)

    return permat


def apply_permutation(dmat: np.ndarray, perm: np.ndarray) -> np.ndarray:
    """Apply permutation to correlation matrix.

    ??? info "Note"
        Translated from [`RTHORR/R/randall.R` lines 162-165](https://github.com/michaellynnmorris/RTHORR/blob/c3edb36287c77733ec0a23236b478cc53c1cac0f/R/randall.R#L162).
        R code: `dmatp[i,j] <- dmat[pp[i], pp[j]]`

        This permutes both rows and columns simultaneously.

    Args:
        dmat: Original correlation matrix (n x n)
        perm: Permutation vector (length n), 0-indexed

    Returns:
        Permuted correlation matrix (n x n)

    """
    n = len(perm)
    dmatp = np.zeros((n, n))

    for i in range(n):
        for j in range(n):
            # R is 1-indexed, we're 0-indexed
            dmatp[i, j] = dmat[perm[i], perm[j]]

    return dmatp
