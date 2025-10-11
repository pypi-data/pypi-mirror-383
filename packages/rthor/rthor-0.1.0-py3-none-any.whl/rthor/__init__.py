"""rthor - Python implementation of RTHOR."""

from ._version import __version__
from .api import compare_matrices, rthor_test
from .results import ComparisonResult, RTHORResult

__all__ = [
    "ComparisonResult",
    "RTHORResult",
    "__version__",
    "compare_matrices",
    "rthor_test",
]
