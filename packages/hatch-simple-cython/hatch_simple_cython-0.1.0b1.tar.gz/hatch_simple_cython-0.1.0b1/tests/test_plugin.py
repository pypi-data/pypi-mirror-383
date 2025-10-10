"""Tests for hatch-simple-cython plugin."""

from types import SimpleNamespace

import pytest

from hatch_simple_cython.plugin import SimpleCythonBuildHook


@pytest.fixture
def temp_project(tmp_path):
    """Create a temporary project structure for testing."""
    pkg_dir = tmp_path / "test_pkg"
    pkg_dir.mkdir()
    
    (pkg_dir / "__init__.py").write_text("# Test package")
    (pkg_dir / "math_ops.pyx").write_text("cpdef int add(int a, int b):\n    return a + b")
    
    return tmp_path


@pytest.fixture
def mock_app():
    """Create a mock app object."""
    return SimpleNamespace(
        display_info=lambda x: None,
        display_debug=lambda x: None,
        display_warning=lambda x: None,
        display_error=lambda x: None,
        display_success=lambda x: None,
        display_mini_header=lambda x: None,
    )


@pytest.fixture
def mock_hook(temp_project, mock_app):
    """Create a mock build hook instance."""
    config = {
        "options": {
            "directives": {"language_level": "3"},
            "compile_args": ["-O2"],
        }
    }
    
    return SimpleCythonBuildHook(
        str(temp_project),
        config,
        {},
        SimpleNamespace(name="test-pkg"),
        app=mock_app,
        directory=str(temp_project),
        target_name="wheel",
    )


def test_plugin_name():
    """Test plugin name is correct."""
    assert SimpleCythonBuildHook.PLUGIN_NAME == "simple-cython"


def test_options_parsing(mock_hook):
    """Test options are parsed correctly."""
    opts = mock_hook.options
    assert opts["directives"]["language_level"] == "3"
    assert opts["compile_args"] == ["-O2"]
    assert opts["compile_py"] is False
    assert opts["include_numpy"] is False


def test_is_src_layout(temp_project, mock_app):
    """Test detection of src/ layout."""
    config = {"options": {}}
    metadata = SimpleNamespace(name="test-pkg")
    
    hook = SimpleCythonBuildHook(
        str(temp_project), config, {}, metadata,
        app=mock_app, directory=str(temp_project), target_name="wheel"
    )
    assert not hook.is_src_layout
    
    (temp_project / "src").mkdir()
    hook = SimpleCythonBuildHook(
        str(temp_project), config, {}, metadata,
        app=mock_app, directory=str(temp_project), target_name="wheel"
    )
    assert hook.is_src_layout


def test_find_cython_files(mock_hook):
    """Test finding Cython files."""
    files = mock_hook.find_cython_files()
    assert len(files) == 1
    assert "test_pkg/math_ops.pyx" in files[0]


def test_group_files_by_module(mock_hook):
    """Test grouping files into modules."""
    files = ["test_pkg/math_ops.pyx"]
    extensions = mock_hook.group_files_by_module(files)
    assert len(extensions) == 1
    assert extensions[0]["name"] == "test_pkg.math_ops"
    assert extensions[0]["sources"] == ["test_pkg/math_ops.pyx"]


def test_generate_setup_script(mock_hook, temp_project):
    """Test setup.py generation."""
    extensions = [{"name": "test_pkg.math_ops", "sources": ["test_pkg/math_ops.pyx"]}]
    output_file = temp_project / "setup.py"
    mock_hook.generate_setup_script(extensions, str(output_file))
    
    assert output_file.exists()
    content = output_file.read_text()
    assert "from setuptools import Extension" in content
    assert "from Cython.Build import cythonize" in content
    assert "test_pkg.math_ops" in content


def test_numpy_include(temp_project, mock_app):
    """Test numpy include directory is added."""
    np = pytest.importorskip("numpy")
    
    config = {"options": {"include_numpy": True}}
    hook = SimpleCythonBuildHook(
        str(temp_project), config, {}, SimpleNamespace(name="test-pkg"),
        app=mock_app, directory=str(temp_project), target_name="wheel"
    )
    
    assert hook.options["include_numpy"]
    assert np.get_include() in hook.options["include_dirs"]


def test_compile_py_option(temp_project, mock_app):
    """Test compile_py option includes .py files."""
    (temp_project / "test_pkg" / "helper.py").write_text("def helper(): pass")
    
    config = {"options": {"compile_py": True}}
    hook = SimpleCythonBuildHook(
        str(temp_project), config, {}, SimpleNamespace(name="test-pkg"),
        app=mock_app, directory=str(temp_project), target_name="wheel"
    )
    
    files = hook.find_cython_files()
    pyx_files = [f for f in files if f.endswith(".pyx")]
    py_files = [f for f in files if f.endswith(".py") and "helper" in f]
    
    assert len(pyx_files) >= 1
    assert len(py_files) >= 1
