"""Validate hatch-simple-cython project structure."""

import pytest
from pathlib import Path


@pytest.fixture
def project_root():
    """Get project root directory."""
    return Path(__file__).parent.parent


class TestCoreFiles:
    """Test core files exist."""
    
    def test_pyproject_toml(self, project_root):
        assert (project_root / "pyproject.toml").exists()
    
    def test_readme(self, project_root):
        assert (project_root / "README.md").exists()
    
    def test_license(self, project_root):
        assert (project_root / "LICENSE").exists()
    
    def test_src_init(self, project_root):
        assert (project_root / "src/hatch_simple_cython/__init__.py").exists()
    
    def test_plugin_py(self, project_root):
        assert (project_root / "src/hatch_simple_cython/plugin.py").exists()
    
    def test_hooks_py(self, project_root):
        assert (project_root / "src/hatch_simple_cython/hooks.py").exists()
    
    def test_py_typed(self, project_root):
        assert (project_root / "src/hatch_simple_cython/py.typed").exists()


class TestTestFiles:
    """Test test files exist."""
    
    def test_conftest(self, project_root):
        assert (project_root / "tests/conftest.py").exists()
    
    def test_test_plugin(self, project_root):
        assert (project_root / "tests/test_plugin.py").exists()
    
    def test_test_integration(self, project_root):
        assert (project_root / "tests/test_integration.py").exists()
    
    def test_test_examples(self, project_root):
        assert (project_root / "tests/test_examples.py").exists()


class TestExamples:
    """Test example projects exist."""
    
    def test_simple_example(self, project_root):
        base = project_root / "examples/simple_example"
        assert base.exists()
        assert (base / "pyproject.toml").exists()
        assert (base / "README.md").exists()
    
    def test_numpy_example(self, project_root):
        base = project_root / "examples/numpy_example"
        assert base.exists()
        assert (base / "pyproject.toml").exists()
        assert (base / "README.md").exists()


class TestProjectStructure:
    """测试项目整体结构"""
    
    def test_src_directory_exists(self, project_root):
        """检查 src/ 目录"""
        assert (project_root / "src").exists()
        assert (project_root / "src").is_dir()
    
    def test_tests_directory_exists(self, project_root):
        """检查 tests/ 目录"""
        assert (project_root / "tests").exists()
        assert (project_root / "tests").is_dir()
    
    def test_examples_directory_exists(self, project_root):
        """检查 examples/ 目录"""
        assert (project_root / "examples").exists()
        assert (project_root / "examples").is_dir()
