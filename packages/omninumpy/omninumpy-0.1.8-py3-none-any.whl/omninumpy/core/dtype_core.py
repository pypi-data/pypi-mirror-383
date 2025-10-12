"""
OmniNumpy - Dtype Core (Safe Version)
Safe dtype handling and type promotion utilities.
"""

from typing import Any, Optional
from ..backend import get_backend_module


def _np():
    import numpy
    return numpy


def asarray(obj: Any, *, backend_name: Optional[str] = None) -> Any:
    """Convert input to an array."""
    try:
        xp = get_backend_module(backend_name)
        return xp.asarray(obj)
    except Exception:
        return _np().asarray(obj)


def astype(obj: Any, dtype: Any, *, backend_name: Optional[str] = None) -> Any:
    """Copy of the array, cast to a specified dtype."""
    try:
        xp = get_backend_module(backend_name)
        return xp.asarray(obj).astype(dtype)
    except Exception:
        return _np().asarray(obj).astype(dtype)


def promote_types(type1: Any, type2: Any, *, backend_name: Optional[str] = None) -> Any:
    """Return the promoted dtype that can represent both input types."""
    try:
        xp = get_backend_module(backend_name)
        return xp.promote_types(type1, type2)
    except Exception:
        return _np().promote_types(type1, type2)


def result_type(*arrays_and_dtypes: Any, backend_name: Optional[str] = None) -> Any:
    """Return the dtype that results from applying the type promotion rules."""
    try:
        xp = get_backend_module(backend_name)
        return xp.result_type(*arrays_and_dtypes)
    except Exception:
        return _np().result_type(*arrays_and_dtypes)
