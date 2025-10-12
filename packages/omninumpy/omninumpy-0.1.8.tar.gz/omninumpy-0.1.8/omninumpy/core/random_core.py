"""
OmniNumpy - Random Core (Safe Version)
Backend-aware random number generation with NumPy fallback.
"""

from typing import Any, Optional, Sequence
from ..backend import get_backend_module


def _np():
    import numpy
    return numpy


def rand(*shape: int, backend_name: Optional[str] = None) -> Any:
    """Random values in a given shape [0, 1)."""
    try:
        xp = get_backend_module(backend_name)
        return xp.random.rand(*shape)
    except Exception:
        return _np().random.rand(*shape)


def randint(low: int, high: Optional[int] = None, size: Optional[Sequence[int]] = None, *, backend_name: Optional[str] = None) -> Any:
    """Return random integers from low (inclusive) to high (exclusive)."""
    try:
        xp = get_backend_module(backend_name)
        return xp.random.randint(low, high, size)
    except Exception:
        return _np().random.randint(low, high, size)


def normal(loc: float = 0.0, scale: float = 1.0, size: Optional[Sequence[int]] = None, *, backend_name: Optional[str] = None) -> Any:
    """Draw random samples from a normal (Gaussian) distribution."""
    try:
        xp = get_backend_module(backend_name)
        return xp.random.normal(loc, scale, size)
    except Exception:
        return _np().random.normal(loc, scale, size)


def uniform(low: float = 0.0, high: float = 1.0, size: Optional[Sequence[int]] = None, *, backend_name: Optional[str] = None) -> Any:
    """Draw samples from a uniform distribution."""
    try:
        xp = get_backend_module(backend_name)
        return xp.random.uniform(low, high, size)
    except Exception:
        return _np().random.uniform(low, high, size)
