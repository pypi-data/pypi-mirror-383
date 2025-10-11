from __future__ import annotations

from concurrent.futures import (
    ThreadPoolExecutor,
    as_completed,
    Future,
    TimeoutError as FuturesTimeoutError,
)
from typing import Any, Literal, TypeVar, overload

from paravalid.core import auto_workers, is_nogil_active, should_parallelize

try:
    from pydantic import BaseModel, TypeAdapter
except ImportError:
    BaseModel = None  # type: ignore
    TypeAdapter = None  # type: ignore

T = TypeVar("T")


@overload
def parallel_validate(
    model_or_type: type[BaseModel],
    data_list: list[Any],
    *,
    workers: Literal["auto"] | int = "auto",
    min_size: int = 100,
    chunk_size: Literal["auto"] | int | None = "auto",
    errors: Literal["raise", "collect"] = "raise",
    timeout: float | None = None,
    **opts: Any,
) -> list[BaseModel | Exception]: ...


@overload
def parallel_validate(
    model_or_type: type[T],
    data_list: list[Any],
    *,
    workers: Literal["auto"] | int = "auto",
    min_size: int = 100,
    chunk_size: Literal["auto"] | int | None = "auto",
    errors: Literal["raise", "collect"] = "raise",
    timeout: float | None = None,
    **opts: Any,
) -> list[T | Exception]: ...


def parallel_validate(
    model_or_type: type[T],
    data_list: list[Any],
    *,
    workers: Literal["auto"] | int = "auto",
    min_size: int = 100,
    chunk_size: Literal["auto"] | int | None = "auto",
    errors: Literal["raise", "collect"] = "raise",
    timeout: float | None = None,
    **opts: Any,
) -> list[T | Exception]:
    """
    Validate a list of data against a Pydantic model or type in parallel.

    Args:
        model_or_type: A Pydantic BaseModel subclass or any type for TypeAdapter.
        data_list: List of data to validate.
        workers: Number of workers ('auto' or positive int).
        min_size: Minimum list size to trigger parallelization.
        chunk_size: Size of chunks for parallel processing ('auto', int, or None).
                   'auto' = conservative default (len(data)//(workers*6) with min 1).
                   None = no chunking (one item per task).
        errors: 'raise' to raise on first error, 'collect' to return exceptions in results.
        timeout: Global timeout in seconds for all operations.
        **opts: Additional options (currently unused, reserved for future).

    Returns:
        List of validated objects or exceptions (in original order).

    Raises:
        Exception: If errors='raise' and any validation fails.
        TimeoutError: If timeout is exceeded.
        ImportError: If pydantic is not installed.
    """
    if BaseModel is None or TypeAdapter is None:
        raise ImportError(
            "pydantic is required for parallel_validate. "
            "Install it with: pip install paravalid[pydantic]"
        )

    # Materialize as list and check if we should parallelize
    items = list(data_list)
    n_items = len(items)
    nogil = is_nogil_active()

    # Determine if we're using BaseModel or TypeAdapter
    is_base_model = isinstance(model_or_type, type) and issubclass(
        model_or_type, BaseModel
    )

    def validate_one(data: Any) -> T:
        """Validate a single item."""
        if is_base_model:
            return model_or_type.model_validate(data)  # type: ignore
        else:
            adapter = TypeAdapter(model_or_type)
            return adapter.validate_python(data)

    # Sequential fast path
    if not should_parallelize(n_items, min_size, nogil):
        results: list[T | Exception] = []
        for data in items:
            try:
                results.append(validate_one(data))
            except Exception as e:
                if errors == "raise":
                    raise
                results.append(e)
        return results

    # Parallel path with chunking
    num_workers = auto_workers(workers)

    # Calculate chunk size
    if chunk_size == "auto":
        # Conservative default: divide data among workers with some overhead
        calculated_chunk_size = max(1, n_items // (num_workers * 6))
    elif chunk_size is None:
        calculated_chunk_size = 1
    else:
        calculated_chunk_size = max(1, chunk_size)

    # Create chunks
    chunks: list[tuple[int, list[Any]]] = []
    for i in range(0, n_items, calculated_chunk_size):
        chunk_data = items[i : i + calculated_chunk_size]
        chunks.append((i, chunk_data))

    results_dict: dict[int, T | Exception] = {}

    def validate_chunk(
        start_idx: int, chunk_data: list[Any]
    ) -> dict[int, T | Exception]:
        """Validate a chunk of items and return results indexed from start_idx."""
        chunk_results: dict[int, T | Exception] = {}
        for offset, data in enumerate(chunk_data):
            idx = start_idx + offset
            try:
                chunk_results[idx] = validate_one(data)
            except Exception as e:
                if errors == "raise":
                    raise
                chunk_results[idx] = e
        return chunk_results

    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        # Submit all chunks
        futures: dict[Future, int] = {
            executor.submit(validate_chunk, start_idx, chunk_data): start_idx
            for start_idx, chunk_data in chunks
        }

        try:
            # Collect results as they complete
            for future in as_completed(futures, timeout=timeout):
                try:
                    chunk_results = future.result()
                    results_dict.update(chunk_results)
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
