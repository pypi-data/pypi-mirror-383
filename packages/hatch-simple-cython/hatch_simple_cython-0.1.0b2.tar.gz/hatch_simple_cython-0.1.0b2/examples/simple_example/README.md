# Simple Example

This is a minimal example showing how to use hatch-simple-cython.

## Project Structure

```text
simple_example/
├── pyproject.toml
├── simple_example/
│   ├── __init__.py
│   └── math_ops.pyx
└── test_example.py
```

## Build

```bash
cd simple_example
uv build
```

## Test

```bash
python test_example.py
```
