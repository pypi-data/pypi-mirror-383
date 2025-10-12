"""
OmniNumpy - Compat Core (Safe Version)
Compatibility and utility helpers for backend-agnostic code.
"""

from typing import Any, Optional
from ..backend import get_backend_module


def _np():
    import numpy
    return numpy


def is_array(obj: Any, *, backend_name: Optional[str] = None) -> bool:
    """Return True if the object is an array-like structure."""
    try:
        xp = get_backend_module(backend_name)
        return xp.asarray(obj).shape is not None
    except Exception:
        try:
            return _np().asarray(obj).shape is not None
        except Exception:
            return False


def is_scalar(obj: Any, *, backend_name: Optional[str] = None) -> bool:
    """Return True if the object is a scalar value."""
    try:
        xp = get_backend_module(backend_name)
        return xp.isscalar(obj)
    except Exception:
        return _np().isscalar(obj)


def ndim(obj: Any, *, backend_name: Optional[str] = None) -> int:
    """Return the number of dimensions of an array."""
    try:
        xp = get_backend_module(backend_name)
        return xp.asarray(obj).ndim
    except Exception:
        return _np().asarray(obj).ndim


def shape(obj: Any, *, backend_name: Optional[str] = None):
    """Return the shape of an array."""
    try:
        xp = get_backend_module(backend_name)
        return xp.asarray(obj).shape
    except Exception:
        return _np().asarray(obj).shape
