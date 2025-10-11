# Pure Python to Binary Example

Demonstrates compiling `.py` files to binary extensions using Cython.

## Key Configuration

```toml
[tool.hatch.build.targets.wheel.hooks.simple-cython]
compile_py = true  # Compile .py files, not just .pyx
```

## Build

```bash
uv build
uv pip install dist/*.whl
```

## Test

```bash
python test_example.py
```
