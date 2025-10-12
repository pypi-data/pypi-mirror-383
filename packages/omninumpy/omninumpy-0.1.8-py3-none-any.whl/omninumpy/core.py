"""
OmniNumpy Public Interface Layer.

Provides unified entry points for core array operations and backend control.
All functions here are boot-safe and backend-aware.
"""

from typing import Any, Optional
from .backend import (
    get_backend,
    set_backend,
    list_backends,
    get_backend_module,
)


from .core.array_core import array as ensure_array
from .core.dtype_core import astype as ensure_dtype




# --- Backend API ---

def backend() -> str:
    """Return the current backend name."""
    return get_backend()

def switch_backend(name: str) -> None:
    """Switch the current backend."""
    return set_backend(name)

def available_backends() -> list[str]:
    """List available backends."""
    return list_backends()

def backend_module(name: Optional[str] = None) -> Any:
    """Return the backend module (NumPy, CuPy, etc.)."""
    return get_backend_module(name)


# --- Array Interface API ---

def array(obj: Any, *, backend_name: Optional[str] = None) -> Any:
    """Create an array from input."""
    return ensure_array(obj, backend_name=backend_name)

def as_dtype(obj: Any, dtype: Any, *, backend_name: Optional[str] = None) -> Any:
    """Convert an array to a given dtype."""
    return ensure_dtype(obj, dtype=dtype, backend_name=backend_name)
