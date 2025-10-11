from __future__ import annotations

import os
import sys
import sysconfig
from typing import Literal


def is_nogil_available() -> bool:
    """
    Check if the Python build supports running without the GIL.

    Only returns True if the build was compiled with free-threading support.
    Standard CPython builds return False even if they have sys._is_gil_enabled().

    Priority order:
    1. PARAVALID_ASSUME_NOGIL=1 env var (for testing)
    2. sysconfig.get_config_var("Py_GIL_DISABLED") == 1 (most reliable)
    3. 'free-threading' in sys.version (build-time indicator)

    Returns:
        True if no-GIL build (free-threaded), False otherwise.
    """
    # Allow override for testing
    if os.getenv("PARAVALID_ASSUME_NOGIL") == "1":
        return True

    # Prioritize sysconfig - most reliable way to detect no-GIL build
    try:
        py_gil_disabled = sysconfig.get_config_var("Py_GIL_DISABLED")
        if py_gil_disabled == 1:
            return True
    except Exception:
        # sysconfig might not have this var in older builds
        pass

    # Check if this is a free-threaded build by examining sys.version
    if "free-threading" in sys.version.lower():
        return True

    # Standard CPython builds (even 3.13+) return False
    return False


def is_nogil_active() -> bool:
    """
    Check if the GIL is currently disabled at runtime.

    Returns:
        True if GIL is disabled, False if GIL is enabled or unavailable.
    """
    # Allow override for testing
    if os.getenv("PARAVALID_ASSUME_NOGIL") == "1":
        return True

    # Check runtime GIL state
    if hasattr(sys, "_is_gil_enabled"):
        try:
            return not sys._is_gil_enabled()
        except Exception:
            pass

    # Check if this is a free-threaded build
    if "free-threading" in sys.version.lower():
        return True

    return False


def auto_workers(workers: Literal["auto"] | int) -> int:
    """
    Convert 'auto' to the number of CPU cores, or validate/return the provided int.

    Args:
        workers: Either 'auto' or a positive integer.

    Returns:
        Number of workers to use.

    Raises:
        ValueError: If workers is not 'auto' or a positive integer.
    """
    if workers == "auto":
        cpu_count = os.cpu_count()
        return cpu_count if cpu_count is not None else 1

    if isinstance(workers, int) and workers > 0:
        return workers

    raise ValueError(f"workers must be 'auto' or a positive integer, got: {workers}")


def should_parallelize(n_items: int, min_size: int, nogil: bool) -> bool:
    """
    Determine if parallelization should be used.

    Args:
        n_items: Number of items to process.
        min_size: Minimum number of items required for parallelization.
        nogil: Whether no-GIL is active.

    Returns:
        True if parallelization should be used, False for sequential fallback.
    """
    return nogil and n_items >= min_size
