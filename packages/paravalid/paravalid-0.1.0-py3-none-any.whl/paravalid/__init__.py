"""
paravalid - Parallel validation and serialization for Python 3.13+

Provides parallel JSON serialization/deserialization and Pydantic validation
optimized for Python 3.13+ free-threaded (no-GIL) builds.
"""

from __future__ import annotations

from paravalid.core import is_nogil_active, is_nogil_available
from paravalid.json_parallel import parallel_json_dumps, parallel_json_loads
from paravalid.pydantic_parallel import parallel_validate

__version__ = "0.1.0"

__all__ = [
    # Core utilities
    "is_nogil_available",
    "is_nogil_active",
    # JSON operations
    "parallel_json_dumps",
    "parallel_json_loads",
    # Pydantic validation
    "parallel_validate",
]
