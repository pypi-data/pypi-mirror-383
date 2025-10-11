"""Test the simple_example package."""

import pytest


@pytest.fixture(autouse=True)
def skip_if_not_installed():
    """Skip if simple_example not installed."""
    pytest.importorskip("simple_example")


def test_add():
    """Test add function."""
    from simple_example import add
    assert add(5, 3) == 8


def test_multiply():
    """Test multiply function."""
    from simple_example import multiply
    assert multiply(4, 7) == 28


def test_power():
    """Test power function."""
    from simple_example.math_ops import power
    assert power(2.0, 10) == 1024.0
