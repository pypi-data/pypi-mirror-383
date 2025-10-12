"""
OmniNumpy - Math Core (Safe Version)
Safe, backend-aware universal math functions with NumPy fallback.
"""

from typing import Any, Optional
from ..backend import get_backend_module


def _np():
    import numpy
    return numpy


def _binary_op(op: str, a: Any, b: Any, *, backend_name: Optional[str] = None) -> Any:
    """Helper for binary operations."""
    try:
        xp = get_backend_module(backend_name)
        return getattr(xp, op)(a, b)
    except Exception:
        return getattr(_np(), op)(a, b)


def add(a: Any, b: Any, *, backend_name: Optional[str] = None) -> Any:
    """Element-wise addition."""
    return _binary_op("add", a, b, backend_name=backend_name)


def subtract(a: Any, b: Any, *, backend_name: Optional[str] = None) -> Any:
    """Element-wise subtraction."""
    return _binary_op("subtract", a, b, backend_name=backend_name)


def multiply(a: Any, b: Any, *, backend_name: Optional[str] = None) -> Any:
    """Element-wise multiplication."""
    return _binary_op("multiply", a, b, backend_name=backend_name)


def divide(a: Any, b: Any, *, backend_name: Optional[str] = None) -> Any:
    """Element-wise division."""
    return _binary_op("divide", a, b, backend_name=backend_name)


def power(a: Any, b: Any, *, backend_name: Optional[str] = None) -> Any:
    """Element-wise power."""
    return _binary_op("power", a, b, backend_name=backend_name)


# --- Unary Ops ---

def sqrt(a: Any, *, backend_name: Optional[str] = None) -> Any:
    """Element-wise square root."""
    try:
        xp = get_backend_module(backend_name)
        return xp.sqrt(a)
    except Exception:
        return _np().sqrt(a)


def exp(a: Any, *, backend_name: Optional[str] = None) -> Any:
    """Element-wise exponential."""
    try:
        xp = get_backend_module(backend_name)
        return xp.exp(a)
    except Exception:
        return _np().exp(a)


def log(a: Any, *, backend_name: Optional[str] = None) -> Any:
    """Element-wise natural log."""
    try:
        xp = get_backend_module(backend_name)
        return xp.log(a)
    except Exception:
        return _np().log(a)


def sin(a: Any, *, backend_name: Optional[str] = None) -> Any:
    """Element-wise sine."""
    try:
        xp = get_backend_module(backend_name)
        return xp.sin(a)
    except Exception:
        return _np().sin(a)


def cos(a: Any, *, backend_name: Optional[str] = None) -> Any:
    """Element-wise cosine."""
    try:
        xp = get_backend_module(backend_name)
        return xp.cos(a)
    except Exception:
        return _np().cos(a)


def tan(a: Any, *, backend_name: Optional[str] = None) -> Any:
    """Element-wise tangent."""
    try:
        xp = get_backend_module(backend_name)
        return xp.tan(a)
    except Exception:
        return _np().tan(a)
