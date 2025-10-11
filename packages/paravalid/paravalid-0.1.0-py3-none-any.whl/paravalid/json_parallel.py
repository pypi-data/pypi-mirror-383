from __future__ import annotations

import json
from concurrent.futures import (
    ThreadPoolExecutor,
    as_completed,
    Future,
    TimeoutError as FuturesTimeoutError,
)
from typing import Any, Literal

from paravalid.core import auto_workers, is_nogil_active, should_parallelize


def parallel_json_dumps(
    obj_list: list[Any],
    *,
    workers: Literal["auto"] | int = "auto",
    min_size: int = 100,
    errors: Literal["raise", "collect"] = "raise",
    timeout: float | None = None,
    **json_kwargs: Any,
) -> list[str | Exception]:
    """
    Serialize a list of objects to JSON strings in parallel.

    Args:
        obj_list: List of objects to serialize.
        workers: Number of workers ('auto' or positive int).
        min_size: Minimum list size to trigger parallelization.
        errors: 'raise' to raise on first error, 'collect' to return exceptions in results.
        timeout: Global timeout in seconds for all operations.
        **json_kwargs: Additional arguments passed to json.dumps (indent, ensure_ascii, default, etc.).

    Returns:
        List of JSON strings or exceptions (in original order).

    Raises:
        Exception: If errors='raise' and any serialization fails.
        TimeoutError: If timeout is exceeded.

    Note:
        If you provide a custom 'default' function in json_kwargs, ensure it is thread-safe.
    """
    # Materialize as list and check if we should parallelize
    items = list(obj_list)
    n_items = len(items)
    nogil = is_nogil_active()

    # Sequential fast path
    if not should_parallelize(n_items, min_size, nogil):
        results: list[str | Exception] = []
        for obj in items:
            try:
                results.append(json.dumps(obj, **json_kwargs))
            except Exception as e:
                if errors == "raise":
                    raise
                results.append(e)
        return results

    # Parallel path
    num_workers = auto_workers(workers)
    results_dict: dict[int, str | Exception] = {}

    def serialize_one(index: int, obj: Any) -> tuple[int, str | Exception]:
        """Serialize a single object and return (index, result)."""
        try:
            return (index, json.dumps(obj, **json_kwargs))
        except Exception as e:
            if errors == "raise":
                raise
            return (index, e)

    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        # Submit all tasks
        futures: dict[Future, int] = {
            executor.submit(serialize_one, i, obj): i for i, obj in enumerate(items)
        }

        try:
            # Collect results as they complete
            for future in as_completed(futures, timeout=timeout):
                try:
                    idx, result = future.result()
                    results_dict[idx] = result
                except Exception:
                    # If errors='raise', cancel remaining tasks and re-raise
                    if errors == "raise":
                        for f in futures:
                            f.cancel()
                        raise
                    # Otherwise this shouldn't happen (errors already caught in worker)
                    raise
        except FuturesTimeoutError:
            # Cancel remaining futures on timeout
            for future in futures:
                future.cancel()
            raise TimeoutError("Operation timed out")

    # Return results in original order
    return [results_dict[i] for i in range(n_items)]


def parallel_json_loads(
    json_list: list[str],
    *,
    workers: Literal["auto"] | int = "auto",
    min_size: int = 100,
    errors: Literal["raise", "collect"] = "raise",
    timeout: float | None = None,
    **json_kwargs: Any,
) -> list[Any | Exception]:
    """
    Deserialize a list of JSON strings to Python objects in parallel.

    Args:
        json_list: List of JSON strings to deserialize.
        workers: Number of workers ('auto' or positive int).
        min_size: Minimum list size to trigger parallelization.
        errors: 'raise' to raise on first error, 'collect' to return exceptions in results.
        timeout: Global timeout in seconds for all operations.
        **json_kwargs: Additional arguments passed to json.loads.

    Returns:
        List of deserialized objects or exceptions (in original order).

    Raises:
        Exception: If errors='raise' and any deserialization fails.
        TimeoutError: If timeout is exceeded.
    """
    # Materialize as list and check if we should parallelize
    items = list(json_list)
    n_items = len(items)
    nogil = is_nogil_active()

    # Sequential fast path
    if not should_parallelize(n_items, min_size, nogil):
        results: list[Any | Exception] = []
        for json_str in items:
            try:
                results.append(json.loads(json_str, **json_kwargs))
            except Exception as e:
                if errors == "raise":
                    raise
                results.append(e)
        return results

    # Parallel path
    num_workers = auto_workers(workers)
    results_dict: dict[int, Any | Exception] = {}

    def deserialize_one(index: int, json_str: str) -> tuple[int, Any | Exception]:
        """Deserialize a single JSON string and return (index, result)."""
        try:
            return (index, json.loads(json_str, **json_kwargs))
        except Exception as e:
            if errors == "raise":
                raise
            return (index, e)

    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        # Submit all tasks
        futures: dict[Future, int] = {
            executor.submit(deserialize_one, i, json_str): i
            for i, json_str in enumerate(items)
        }

        try:
            # Collect results as they complete
            for future in as_completed(futures, timeout=timeout):
                try:
                    idx, result = future.result()
                    results_dict[idx] = result
                except Exception:
                    # If errors='raise', cancel remaining tasks and re-raise
                    if errors == "raise":
                        for f in futures:
                            f.cancel()
                        raise
                    # Otherwise this shouldn't happen (errors already caught in worker)
                    raise
        except FuturesTimeoutError:
            # Cancel remaining futures on timeout
            for future in futures:
                future.cancel()
            raise TimeoutError("Operation timed out")

    # Return results in original order
    return [results_dict[i] for i in range(n_items)]
