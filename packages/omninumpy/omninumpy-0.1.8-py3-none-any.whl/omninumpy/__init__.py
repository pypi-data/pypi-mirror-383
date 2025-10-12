"""
OmniNumpy - Safe Frontend
=========================
Exposes safe_* functions alongside normal API for drop-in compatibility.
"""

from . import backend
from . import core
from . import interface
"""
OmniNumpy - Safe Lazy-Import Numpy Wrapper
Boot-safe, backend-flexible array utilities with lazy initialization.
"""

from .backend import (
    get_backend,
    set_backend,
    list_backends,
    get_backend_module
)

# Core API imports (safe versions only)
from .core.array_core import array, zeros, ones
from .core.math_core import (
    add, subtract, multiply, divide, power,
    sqrt, exp, log, sin, cos, tan
)
from .core.reduce_core import (
    sum, mean, max, min, argmax, argmin
)
from .core.shape_core import (
    reshape, transpose, concatenate, stack, vstack, hstack
)
from .core.dtype_core import (
    asarray, astype, promote_types, result_type
)
from .core.linalg_core import (
    dot, matmul, inv, solve, svd
)
from .core.random_core import (
    rand, randint, normal, uniform
)
from .core.compat_core import (
    is_array, is_scalar, ndim, shape
)

__all__ = [
    # backend API
    "get_backend", "set_backend", "list_backends", "get_backend_module",

    # array creation
    "array", "zeros", "ones",

    # math ops
    "add", "subtract", "multiply", "divide", "power", "sqrt", "exp",
    "log", "sin", "cos", "tan",

    # reductions
    "sum", "mean", "max", "min", "argmax", "argmin",

    # shape ops
    "reshape", "transpose", "concatenate", "stack", "vstack", "hstack",

    # dtype handling
    "asarray", "astype", "promote_types", "result_type",

    # linear algebra
    "dot", "matmul", "inv", "solve", "svd",

    # random
    "rand", "randint", "normal", "uniform",

    # compat utils
    "is_array", "is_scalar", "ndim", "shape"
]

# Export safe-aware modules
