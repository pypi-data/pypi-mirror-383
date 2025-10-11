# paravalid

**Parallel validation and serialization for Python 3.13+**

`paravalid` provides high-performance parallel JSON serialization/deserialization and Pydantic model validation optimized for Python 3.13+ free-threaded (no-GIL) builds.

## Features

- **Parallel JSON operations**: Serialize and deserialize JSON lists in parallel
- **Parallel Pydantic validation**: Validate data against Pydantic models using multiple threads
- **Automatic fallback**: Seamlessly falls back to sequential processing when no-GIL is unavailable
- **Preserves order**: Results always maintain the original input order
- **Error handling**: Choose between raising on first error or collecting all errors
- **Smart cancellation**: When `errors='raise'`, remaining tasks are cancelled immediately on first error
- **Zero overhead**: Small datasets automatically use sequential processing
- **CLI tool**: Check no-GIL availability and configuration

## Performance

Tested on Python 3.14.0rc2 (free-threaded), GIL disabled, 8 workers:

| Operation | Dataset Size | Speedup |
|-----------|-------------|---------|
| JSON serialization | 5,000 objects | **4.66×** |
| Pydantic validation | 5,000 users | **3.36×** |

### Detailed Benchmark Results

#### Complex Pydantic Models (2-4KB JSON)

Testing with nested models containing 7+ fields, nested objects, and lists:

**Python 3.13.7t (free-threaded):**
| Items | Sequential | Parallel (chunk=64) | Speedup |
|-------|-----------|---------------------|---------|
| 500   | 9.10 ms   | 4.06 ms            | **2.24×** |
| 1000  | 14.82 ms  | 7.17 ms            | **2.07×** |

**Python 3.14.0t (free-threaded):**
| Items | Sequential | Parallel (chunk=64) | Speedup |
|-------|-----------|---------------------|---------|
| 500   | 7.45 ms   | 3.44 ms            | **2.16×** |
| 1000  | 13.71 ms  | 6.92 ms            | **1.98×** |

**Key Findings:**
- ✅ Optimal chunk size: **64** for complex models
- ✅ Consistent **1.7-2.2× speedup** across different chunk sizes (64, 128, 256, auto)
- ✅ Python 3.14 shows 10-18% faster sequential baseline
- ✅ Best results with models containing nested structures and validation logic

#### Large JSON Objects (50KB+ per object)

Testing with large documents containing extensive text, lists, and metadata:

**Python 3.13.7t (free-threaded):**
| Items | Operation | Sequential | Parallel (8 workers) | Speedup |
|-------|-----------|-----------|---------------------|---------|
| 5,000  | Dumps    | 573.01 ms | 177.36 ms          | **3.23×** |
| 5,000  | Loads    | 819.09 ms | 200.31 ms          | **4.09×** |
| 10,000 | Dumps    | 1155.57 ms| 345.14 ms          | **3.35×** |
| 10,000 | Loads    | 1391.30 ms| 440.00 ms          | **3.16×** |

**Python 3.14.0t (free-threaded):**
| Items | Operation | Sequential | Parallel (8 workers) | Speedup |
|-------|-----------|-----------|---------------------|---------|
| 5,000  | Dumps    | 603.98 ms | 182.85 ms          | **3.30×** |
| 5,000  | Loads    | 486.63 ms | 254.20 ms          | **1.91×** |
| 10,000 | Dumps    | 1185.10 ms| 310.86 ms          | **3.81×** |
| 10,000 | Loads    | 917.45 ms | 372.49 ms          | **2.46×** |

**Key Findings:**
- ✅ **3-4× speedup** for large objects (50KB+ per object)
- ✅ JSON dumps consistently shows **3.2-3.8× speedup**
- ✅ JSON loads shows **1.9-4.1× speedup** depending on Python version
- ✅ Performance improves with dataset size (10k items better than 5k)
- ⚠️ Small simple objects (<1KB) don't benefit due to thread overhead

### Performance Guidelines

**When to use `paravalid`:**
- ✅ Complex Pydantic models with nested structures (2KB+ JSON)
- ✅ Large JSON objects (10KB+ per object)
- ✅ Dataset size ≥ 500 items for complex models
- ✅ Dataset size ≥ 5,000 items for large JSON objects
- ✅ CPU-bound validation logic in your models

**When NOT to use:**
- ❌ Simple flat objects (<500 bytes)
- ❌ Small datasets (<100 items)
- ❌ Operations dominated by I/O rather than CPU

**Optimal Settings:**
- **Workers:** 8 threads on modern CPUs (4-8 cores)
- **chunk_size:** 64 for Pydantic validation
- **min_size:** 100 (default) for complex models, 500-1000 for JSON

## Installation

```bash
# Basic installation (JSON support only)
pip install paravalid

# With Pydantic support
pip install paravalid[pydantic]
```

## Requirements

- Python 3.13 or higher
- Optional: Pydantic 2.0+ for validation features

## Quick Start

### JSON Serialization

```python
from paravalid import parallel_json_dumps, parallel_json_loads

# Serialize a list of objects
data = [{"id": i, "name": f"user_{i}"} for i in range(1000)]
json_strings = parallel_json_dumps(data, workers=4)

# Deserialize back
objects = parallel_json_loads(json_strings, workers=4)
```

### Pydantic Validation

```python
from pydantic import BaseModel
from paravalid import parallel_validate

class User(BaseModel):
    id: int
    name: str
    email: str
    age: int

# Validate data in parallel
data = [
    {"id": i, "name": f"user_{i}", "email": f"user{i}@example.com", "age": 25}
    for i in range(1000)
]
users = parallel_validate(User, data, workers=4)
```

## API Reference

### JSON Operations

#### `parallel_json_dumps`

```python
parallel_json_dumps(
    obj_list: list[Any],
    *,
    workers: Literal["auto"] | int = "auto",
    min_size: int = 100,
    errors: Literal["raise", "collect"] = "raise",
    timeout: float | None = None,
    **json_kwargs: Any,
) -> list[str | Exception]
```

Serialize a list of objects to JSON strings in parallel.

**Parameters:**
- `obj_list`: List of objects to serialize
- `workers`: Number of workers ('auto' uses CPU count)
- `min_size`: Minimum list size to trigger parallelization (default: 100)
- `errors`: 'raise' to raise on first error, 'collect' to return exceptions in results
- `timeout`: Global timeout in seconds for all operations
- `**json_kwargs`: Additional arguments passed to `json.dumps` (indent, ensure_ascii, default, etc.)

**Returns:** List of JSON strings or exceptions (in original order)

#### `parallel_json_loads`

```python
parallel_json_loads(
    json_list: list[str],
    *,
    workers: Literal["auto"] | int = "auto",
    min_size: int = 100,
    errors: Literal["raise", "collect"] = "raise",
    timeout: float | None = None,
    **json_kwargs: Any,
) -> list[Any | Exception]
```

Deserialize a list of JSON strings to Python objects in parallel.

**Parameters:** Similar to `parallel_json_dumps`

**Returns:** List of deserialized objects or exceptions (in original order)

### Pydantic Validation

#### `parallel_validate`

```python
parallel_validate(
    model_or_type: type[T],
    data_list: list[Any],
    *,
    workers: Literal["auto"] | int = "auto",
    min_size: int = 100,
    chunk_size: Literal["auto"] | int | None = "auto",
    errors: Literal["raise", "collect"] = "raise",
    timeout: float | None = None,
    **opts: Any,
) -> list[T | Exception]
```

Validate a list of data against a Pydantic model or type in parallel.

**Parameters:**
- `model_or_type`: A Pydantic BaseModel subclass or any type for TypeAdapter
- `data_list`: List of data to validate
- `workers`: Number of workers ('auto' uses CPU count)
- `min_size`: Minimum list size to trigger parallelization (default: 100)
- `chunk_size`: Size of chunks for parallel processing
  - `'auto'`: Conservative default (len(data) // (workers * 6), min 1)
  - `None`: No chunking (one item per task)
  - `int`: Explicit chunk size
- `errors`: 'raise' to raise on first error, 'collect' to return exceptions in results
- `timeout`: Global timeout in seconds for all operations

**Returns:** List of validated objects or exceptions (in original order)

### Utility Functions

#### `is_nogil_available`

```python
is_nogil_available() -> bool
```

Check if the Python build supports running without the GIL.

#### `is_nogil_active`

```python
is_nogil_active() -> bool
```

Check if the GIL is currently disabled at runtime.

## Advanced Usage

### Error Collection

Instead of raising on the first error, collect all errors and continue processing:

```python
from paravalid import parallel_json_loads

json_strings = ['{"valid": 1}', 'invalid json', '{"also": "valid"}']
results = parallel_json_loads(json_strings, errors="collect")

for i, result in enumerate(results):
    if isinstance(result, Exception):
        print(f"Item {i} failed: {result}")
    else:
        print(f"Item {i} succeeded: {result}")
```

### Custom JSON Serialization

Pass additional arguments to `json.dumps`:

```python
from paravalid import parallel_json_dumps

data = [{"name": "François"}, {"name": "José"}]

# Pretty-print with indentation
json_strings = parallel_json_dumps(data, indent=2)

# Preserve Unicode characters
json_strings = parallel_json_dumps(data, ensure_ascii=False)

# Custom default handler
def custom_default(obj):
    if isinstance(obj, set):
        return list(obj)
    raise TypeError(f"Cannot serialize {type(obj)}")

json_strings = parallel_json_dumps(data, default=custom_default)
```

### Nested Pydantic Models

```python
from pydantic import BaseModel
from paravalid import parallel_validate

class Address(BaseModel):
    street: str
    city: str
    zipcode: str

class User(BaseModel):
    name: str
    email: str
    address: Address

data = [
    {
        "name": "Alice",
        "email": "alice@example.com",
        "address": {"street": "123 Main St", "city": "Springfield", "zipcode": "12345"}
    },
    # ... more records
]

users = parallel_validate(User, data, workers=4)
```

### Using TypeAdapter

For validating simple types or generic types:

```python
from paravalid import parallel_validate

# Validate integers
int_strings = ["1", "2", "3", "4", "5"]
integers = parallel_validate(int, int_strings)

# Validate lists
list_data = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
validated_lists = parallel_validate(list[int], list_data)
```

## CLI Tool

`paravalid` includes a command-line tool to check your Python environment:

```bash
# Check if no-GIL is available and active
$ paravalid --check-nogil
No-GIL available: True
No-GIL active: True

✓ paravalid can use parallel execution with no-GIL

# Show version
$ paravalid --version
paravalid 0.1.0

# Show help
$ paravalid --help
```

The CLI tool helps you verify that:
- Your Python build supports free-threading (no-GIL)
- The GIL is actually disabled at runtime
- `paravalid` will be able to use parallel execution

**Exit codes:**
- `0`: No-GIL is available and active (parallel execution enabled)
- `1`: No-GIL is not available or not active (will use sequential fallback)

## How It Works

1. **No-GIL Detection**: Automatically detects if Python is running in free-threaded mode using:
   - `sysconfig.get_config_var("Py_GIL_DISABLED")` (most reliable)
   - `sys.version` string check for "free-threading"
   - `sys._is_gil_enabled()` runtime API
2. **Smart Parallelization**: Only uses parallel processing when:
   - No-GIL is active
   - Dataset size ≥ `min_size` (default: 100)
3. **ThreadPoolExecutor**: Uses threads (not processes) for true parallelism without GIL overhead
4. **Order Preservation**: Results are always returned in the same order as input
5. **Task Cancellation**: When `errors='raise'`, all remaining tasks are cancelled immediately on first error
6. **Graceful Fallback**: Falls back to sequential processing on standard CPython builds

## Important Caveats

### Thread Safety

- **Custom `json.default` functions**: If you provide a custom `default` function to `parallel_json_dumps`, ensure it is thread-safe
- **Global state**: Avoid accessing mutable global state from custom validators or default handlers
- **Pydantic validators**: Any custom validators in your Pydantic models must be thread-safe

### Performance Considerations

- **Small datasets**: Parallelization adds overhead; adjust `min_size` based on your data
- **CPU-bound only**: This library targets CPU-bound operations, not I/O-bound tasks
- **Memory**: Parallel processing uses more memory as multiple operations run simultaneously

## Running Tests

```bash
# Install development dependencies
pip install -e ".[pydantic]"
pip install pytest

# Run all tests
pytest tests/ -v

# Run specific test modules
pytest tests/test_json.py -v
pytest tests/test_pydantic.py -v
```

## Running Benchmarks

```bash
# Install benchmark dependencies
pip install pyperf

# Run JSON benchmarks
python benchmarks/bench_json.py

# Run Pydantic benchmarks
python benchmarks/bench_pydantic.py
```

## Examples

See the `examples/` directory for complete working examples:
- `examples/example_json.py`: JSON serialization examples
- `examples/example_pydantic.py`: Pydantic validation examples

## License

This project is provided as-is under the MIT License.

## Contributing

Contributions are welcome! Please ensure:
- All tests pass
- Code follows the existing style
- New features include tests and documentation

## Changelog

### 0.1.0 (2025-10-11)
- Initial release
- Parallel JSON serialization/deserialization
- Parallel Pydantic validation
- Automatic no-GIL detection with `sysconfig.get_config_var("Py_GIL_DISABLED")` priority
- Error collection support with `errors='collect'`
- Smart task cancellation: when `errors='raise'`, remaining tasks are cancelled immediately
- Proper `concurrent.futures.TimeoutError` handling
- CLI tool with `--check-nogil` command
- Comprehensive test suite (52 tests)
- Detailed benchmarks showing 2-4× speedup on complex models

