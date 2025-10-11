"""Test the numpy_example package."""

import pytest


@pytest.fixture(autouse=True)
def skip_if_not_installed():
    """Skip if numpy_example not installed."""
    pytest.importorskip("numpy")
    pytest.importorskip("numpy_example")


def test_sum_array():
    """Test sum_array function."""
    import numpy as np
    from numpy_example import sum_array
    
    arr = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    assert np.isclose(sum_array(arr), 15.0)


def test_multiply_arrays():
    """Test multiply_arrays function."""
    import numpy as np
    from numpy_example import multiply_arrays
    
    a = np.array([1.0, 2.0, 3.0])
    b = np.array([4.0, 5.0, 6.0])
    expected = np.array([4.0, 10.0, 18.0])
    assert np.allclose(multiply_arrays(a, b), expected)


def test_matrix_multiply():
    """Test matrix_multiply function."""
    import numpy as np
    from numpy_example.array_ops import matrix_multiply
    
    A = np.array([[1.0, 2.0], [3.0, 4.0]])
    B = np.array([[5.0, 6.0], [7.0, 8.0]])
    expected = np.array([[19.0, 22.0], [43.0, 50.0]])
    assert np.allclose(matrix_multiply(A, B), expected)
