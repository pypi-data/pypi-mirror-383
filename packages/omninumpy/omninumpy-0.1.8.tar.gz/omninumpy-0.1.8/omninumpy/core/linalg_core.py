"""
OmniNumpy - Linear Algebra Core (Safe Version)
Backend-aware linear algebra operations with NumPy fallback.
"""

from typing import Any, Optional
from ..backend import get_backend_module


def _np():
    import numpy
    return numpy


def dot(a: Any, b: Any, *, backend_name: Optional[str] = None) -> Any:
    """Dot product of two arrays."""
    try:
        xp = get_backend_module(backend_name)
        return xp.dot(a, b)
    except Exception:
        return _np().dot(a, b)


def matmul(a: Any, b: Any, *, backend_name: Optional[str] = None) -> Any:
    """Matrix product of two arrays."""
    try:
        xp = get_backend_module(backend_name)
        return xp.matmul(a, b)
    except Exception:
        return _np().matmul(a, b)


def inv(a: Any, *, backend_name: Optional[str] = None) -> Any:
    """Compute the (multiplicative) inverse of a matrix."""
    try:
        xp = get_backend_module(backend_name)
        return xp.linalg.inv(a)
    except Exception:
        return _np().linalg.inv(a)


def solve(a: Any, b: Any, *, backend_name: Optional[str] = None) -> Any:
    """Solve a linear matrix equation, or system of linear scalar equations."""
    try:
        xp = get_backend_module(backend_name)
        return xp.linalg.solve(a, b)
    except Exception:
        return _np().linalg.solve(a, b)


def svd(a: Any, full_matrices: bool = True, *, backend_name: Optional[str] = None) -> Any:
    """Singular Value Decomposition."""
    try:
        xp = get_backend_module(backend_name)
        return xp.linalg.svd(a, full_matrices=full_matrices)
    except Exception:
        return _np().linalg.svd(a, full_matrices=full_matrices)
