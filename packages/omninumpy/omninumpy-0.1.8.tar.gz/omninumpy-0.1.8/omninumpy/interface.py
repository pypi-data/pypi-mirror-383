"""
OmniNumpy interface - safe, backend-aware
"""

from typing import Any, Optional
import sys
import types

from . import core
from . import backend
from .core.array_core import array as _array
from .core.dtype_core import astype as _astype


class OmniModule(types.ModuleType):
    """Dynamic module proxy that resolves attributes from core, backend, or NumPy."""

    def __getattr__(self, name: str) -> Any:
        if hasattr(core, name):
            return getattr(core, name)
        if hasattr(backend, name):
            return getattr(backend, name)

        # Fallback: try NumPy directly
        import numpy as np
        if hasattr(np, name):
            return getattr(np, name)

        raise AttributeError(f"omninumpy has no attribute '{name}'")

    def __dir__(self) -> list[str]:
        """List all available symbols dynamically."""
        return sorted(set(dir(core) + dir(backend)))

    # --- Public API functions (defined as static methods for clarity) ---

    @staticmethod
    def array(obj: Any, *, backend_name: Optional[str] = None) -> Any:
        """Create an array from input (safe, backend-aware)."""
        return _array(obj, backend_name=backend_name)

    @staticmethod
    def as_dtype(obj: Any, dtype: Any, *, backend_name: Optional[str] = None) -> Any:
        """Convert an array to a given dtype (safe, backend-aware)."""
        return _astype(obj, dtype, backend_name=backend_name)


# Register this dynamic module proxy
sys.modules[__name__] = OmniModule(__name__)  # type: ignore[assignment]
