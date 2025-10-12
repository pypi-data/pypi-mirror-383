"""
OmniNumpy - Array Core (Safe Version)
Lazy-import, boot-safe array creation utilities.
"""

from typing import Any, Optional, Sequence
from ..backend import get_backend_module


def _np():
    """Lazily import numpy for fallback use."""
    import numpy
    return numpy

def array(
    obj: Any,
    dtype: Optional[Any] = None,
    *,
    backend_name: Optional[str] = None,
    **kwargs
) -> Any:
    """
    Create an array from any Python object.

    Parameters
    ----------
    obj : Any
        Input data to convert into an array.
    dtype : Optional[Any], default=None
        Desired data type of the output array.
    backend_name : Optional[str], default=None
        Override backend (e.g. 'numpy', 'cupy', 'jax').
    **kwargs
        Extra keyword arguments passed to the backend's array function.

    Returns
    -------
    Any
        Backend-specific array object.
    """
    try:
        xp = get_backend_module(backend_name)
        return xp.array(obj, dtype=dtype, **kwargs)
    except Exception:
        return _np().array(obj, dtype=dtype, **kwargs)


def zeros(
    shape: Sequence[int],
    dtype: Optional[Any] = None,
    *,
    backend_name: Optional[str] = None
) -> Any:
    """Create a zero-initialized array."""
    try:
        xp = get_backend_module(backend_name)
        return xp.zeros(shape, dtype=dtype)
    except Exception:
        return _np().zeros(shape, dtype=dtype)


def ones(
    shape: Sequence[int],
    dtype: Optional[Any] = None,
    *,
    backend_name: Optional[str] = None
) -> Any:
    """Create a one-initialized array."""
    try:
        xp = get_backend_module(backend_name)
        return xp.ones(shape, dtype=dtype)
    except Exception:
        return _np().ones(shape, dtype=dtype)
