"""
Backend detection and management for OmniNumpy (final safe version).
"""

from typing import Any, List, Optional
import importlib
import warnings


class BackendManager:
    """Manages backend modules and automatic selection."""

    def __init__(self) -> None:
        self._backends: dict[str, Any] = {}
        self._current_backend: Optional[str] = None
        self._discovered = False

    def _ensure_numpy(self) -> None:
        """Ensure NumPy is available and lazily loaded."""
        if "numpy" in self._backends:
            return
        try:
            numpy_mod = importlib.import_module("numpy")
            self._backends["numpy"] = numpy_mod
        except ImportError:
            warnings.warn("⚠️ NumPy not installed. Some functionality may be unavailable.")
            class Dummy:
                def __getattr__(self, item): raise ImportError("NumPy required")
            self._backends["numpy"] = Dummy()
        if self._current_backend is None:
            self._current_backend = "numpy"

    def _discover_backends(self) -> None:
        """Discover optional backends safely."""
        if self._discovered:
            return
        self._ensure_numpy()

        # Try CuPy
        try:
            cp = importlib.import_module("cupy")
            self._backends["cupy"] = cp
            self._current_backend = "cupy"
        except ImportError:
            pass

        # Try JAX
        try:
            jnp = importlib.import_module("jax.numpy")
            self._backends["jax"] = jnp
            self._backends["jax_module"] = importlib.import_module("jax")
            if self._current_backend == "numpy":
                self._current_backend = "jax"
        except ImportError:
            pass

        self._discovered = True

    def _get_backend_name(self) -> str:
        if self._current_backend is None:
            self._discover_backends()
        return self._current_backend or "numpy"

    def set_backend(self, backend_name: str) -> None:
        self._discover_backends()
        if backend_name not in self._backends:
            warnings.warn(f"⚠️ Backend '{backend_name}' not found. Falling back to NumPy.")
            self._ensure_numpy()
            backend_name = "numpy"
        self._current_backend = backend_name

    def list_backends(self) -> List[str]:
        self._discover_backends()
        return list(self._backends.keys())

    def get_backend_module(self, backend_name: Optional[str] = None) -> Any:
        self._discover_backends()
        name = backend_name or self._current_backend or "numpy"
        if name not in self._backends:
            self._ensure_numpy()
            name = "numpy"
        return self._backends[name]


# Singleton manager
_manager = BackendManager()

def get_backend() -> str:
    return _manager._get_backend_name()

def set_backend(name: str) -> None:
    return _manager.set_backend(name)

def list_backends() -> List[str]:
    return _manager.list_backends()

def get_backend_module(name: Optional[str] = None) -> Any:
    return _manager.get_backend_module(name)
