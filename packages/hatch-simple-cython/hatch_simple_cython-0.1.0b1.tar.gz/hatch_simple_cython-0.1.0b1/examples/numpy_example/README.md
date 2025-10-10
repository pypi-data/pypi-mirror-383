# NumPy Example

This example demonstrates using hatch-simple-cython with NumPy arrays.

## Features

- Fast array operations using Cython and NumPy C API
- Type-safe array processing
- Performance benchmarks

## Project Structure

```text
numpy_example/
├── pyproject.toml
├── numpy_example/
│   ├── __init__.py
│   └── array_ops.pyx
└── test_numpy.py
```

## Build

```bash
cd numpy_example
uv build
```

## Install and Test

```bash
uv pip install numpy
uv pip install dist/*.whl
python test_numpy.py
```

## Performance

The Cython implementation provides significant speedups for array operations compared to pure Python, especially for element-wise operations and custom algorithms.

See `test_numpy.py` for benchmark comparisons.
