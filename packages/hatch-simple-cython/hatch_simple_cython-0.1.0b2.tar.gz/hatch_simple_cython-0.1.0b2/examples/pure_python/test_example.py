"""Test the pure_python package."""

import pytest


@pytest.fixture(autouse=True)
def skip_if_not_installed():
    """Skip if pure_python not installed."""
    pytest.importorskip("pure_python")


def test_add():
    """Test add function."""
    from pure_python import add
    assert add(5, 3) == 8


def test_multiply():
    """Test multiply function."""
    from pure_python import multiply
    assert multiply(4, 7) == 28


def test_power():
    """Test power function."""
    from pure_python import power
    assert power(2.0, 10) == 1024.0
