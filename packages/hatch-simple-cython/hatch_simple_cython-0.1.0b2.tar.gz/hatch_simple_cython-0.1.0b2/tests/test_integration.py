"""Integration tests for hatch-simple-cython plugin."""

import sys
import subprocess
from pathlib import Path

import pytest


@pytest.fixture
def test_project(tmp_path):
    """Create a simple test project."""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()
    
    pkg_dir = project_dir / "test_pkg"
    pkg_dir.mkdir()
    
    # 创建 __init__.py
    (pkg_dir / "__init__.py").write_text("""
\"\"\"Test package.\"\"\"
from test_pkg.math_ops import add, multiply
__all__ = ["add", "multiply"]
""")
    
    # 创建 Cython 文件
    (pkg_dir / "math_ops.pyx").write_text("""
# cython: language_level=3

cpdef int add(int a, int b):
    \"\"\"Add two integers.\"\"\"
    return a + b

cpdef int multiply(int a, int b):
    \"\"\"Multiply two integers.\"\"\"
    return a * b

cpdef double power(double base, int exp):
    \"\"\"Calculate power.\"\"\"
    cdef double result = 1.0
    cdef int i
    for i in range(exp):
        result *= base
    return result
""")
    
    # 创建 pyproject.toml
    root_path = Path(__file__).parent.parent.absolute()
    pyproject_content = f"""
[project]
name = "test-pkg"
version = "0.1.0"
description = "Test package"
requires-python = ">=3.10"
dependencies = []

[build-system]
requires = ["hatchling", "hatch-simple-cython @ file:///{root_path.as_posix()}", "Cython>=3.0.0", "setuptools"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel.hooks.simple-cython]
directives = {{ language_level = "3", boundscheck = false }}
compile_args = ["-O2"]
"""
    (project_dir / "pyproject.toml").write_text(pyproject_content)
    
    return project_dir


@pytest.fixture
def build_project(test_project):
    """Build project and return wheel path."""
    result = subprocess.run(
        ["uv", "build", "--wheel", str(test_project)],
        capture_output=True,
        text=True,
        cwd=test_project,
    )
    
    assert result.returncode == 0, f"Build failed:\n{result.stderr}"
    
    wheels = list((test_project / "dist").glob("*.whl"))
    assert wheels, "No wheel file found"
    return wheels[0]


def test_project_structure(test_project):
    """Test project structure is correct."""
    assert (test_project / "pyproject.toml").exists()
    assert (test_project / "test_pkg" / "__init__.py").exists()
    assert (test_project / "test_pkg" / "math_ops.pyx").exists()


def test_build_project(test_project, build_project):
    """Test project builds successfully."""
    assert build_project.exists()
    assert build_project.suffix == ".whl"


def test_package_installation(test_project, build_project, tmp_path):
    """Test package installation and functionality."""
    import venv
    
    temp_venv = tmp_path / "test_venv"
    venv.create(temp_venv, with_pip=True)
    
    python_exe = temp_venv / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
    
    # Install wheel
    result = subprocess.run(
        [str(python_exe), "-m", "pip", "install", "--quiet", str(build_project)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Install failed:\n{result.stderr}"
    
    # Test functionality
    test_code = """
from test_pkg import add, multiply
from test_pkg.math_ops import power
assert add(5, 3) == 8
assert multiply(4, 7) == 28
assert power(2.0, 10) == 1024.0
"""
    
    result = subprocess.run(
        [str(python_exe), "-c", test_code],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Test failed:\n{result.stderr}"
