"""
OmniNumpy - Reduce Core (Safe Version)
Backend-aware reductions and aggregation functions with NumPy fallback.
"""

from typing import Any, Optional
from ..backend import get_backend_module


def _np():
    import numpy
    return numpy


def sum(a: Any, axis: Optional[int] = None, *, backend_name: Optional[str] = None) -> Any:
    """Compute the sum over the given axis."""
    try:
        xp = get_backend_module(backend_name)
        return xp.sum(a, axis=axis)
    except Exception:
        return _np().sum(a, axis=axis)


def mean(a: Any, axis: Optional[int] = None, *, backend_name: Optional[str] = None) -> Any:
    """Compute the mean over the given axis."""
    try:
        xp = get_backend_module(backend_name)
        return xp.mean(a, axis=axis)
    except Exception:
        return _np().mean(a, axis=axis)


def max(a: Any, axis: Optional[int] = None, *, backend_name: Optional[str] = None) -> Any:
    """Compute the maximum over the given axis."""
    try:
        xp = get_backend_module(backend_name)
        return xp.max(a, axis=axis)
    except Exception:
        return _np().max(a, axis=axis)


def min(a: Any, axis: Optional[int] = None, *, backend_name: Optional[str] = None) -> Any:
    """Compute the minimum over the given axis."""
    try:
        xp = get_backend_module(backend_name)
        return xp.min(a, axis=axis)
    except Exception:
        return _np().min(a, axis=axis)


def argmax(a: Any, axis: Optional[int] = None, *, backend_name: Optional[str] = None) -> Any:
    """Indices of the maximum values along an axis."""
    try:
        xp = get_backend_module(backend_name)
        return xp.argmax(a, axis=axis)
    except Exception:
        return _np().argmax(a, axis=axis)


def argmin(a: Any, axis: Optional[int] = None, *, backend_name: Optional[str] = None) -> Any:
    """Indices of the minimum values along an axis."""
    try:
        xp = get_backend_module(backend_name)
        return xp.argmin(a, axis=axis)
    except Exception:
        return _np().argmin(a, axis=axis)
