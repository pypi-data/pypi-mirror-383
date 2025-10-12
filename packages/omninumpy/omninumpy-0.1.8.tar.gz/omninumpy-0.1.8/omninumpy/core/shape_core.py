"""
OmniNumpy - Shape Core (Safe Version)
Safe shape transformation utilities with backend awareness.
"""

from typing import Any, Optional, Sequence
from ..backend import get_backend_module


def _np():
    import numpy
    return numpy


def reshape(a: Any, newshape: Sequence[int], *, backend_name: Optional[str] = None) -> Any:
    """Give a new shape to an array without changing its data."""
    try:
        xp = get_backend_module(backend_name)
        return xp.reshape(a, newshape)
    except Exception:
        return _np().reshape(a, newshape)


def transpose(a: Any, axes: Optional[Sequence[int]] = None, *, backend_name: Optional[str] = None) -> Any:
    """Permute the dimensions of an array."""
    try:
        xp = get_backend_module(backend_name)
        return xp.transpose(a, axes=axes)
    except Exception:
        return _np().transpose(a, axes=axes)


def concatenate(arrays: Sequence[Any], axis: int = 0, *, backend_name: Optional[str] = None) -> Any:
    """Join a sequence of arrays along an existing axis."""
    try:
        xp = get_backend_module(backend_name)
        return xp.concatenate(arrays, axis=axis)
    except Exception:
        return _np().concatenate(arrays, axis=axis)


def stack(arrays: Sequence[Any], axis: int = 0, *, backend_name: Optional[str] = None) -> Any:
    """Join a sequence of arrays along a new axis."""
    try:
        xp = get_backend_module(backend_name)
        return xp.stack(arrays, axis=axis)
    except Exception:
        return _np().stack(arrays, axis=axis)


def vstack(arrays: Sequence[Any], *, backend_name: Optional[str] = None) -> Any:
    """Stack arrays vertically (row-wise)."""
    try:
        xp = get_backend_module(backend_name)
        return xp.vstack(arrays)
    except Exception:
        return _np().vstack(arrays)


def hstack(arrays: Sequence[Any], *, backend_name: Optional[str] = None) -> Any:
    """Stack arrays horizontally (column-wise)."""
    try:
        xp = get_backend_module(backend_name)
        return xp.hstack(arrays)
    except Exception:
        return _np().hstack(arrays)
