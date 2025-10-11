# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
"""Fast array operations using Cython and NumPy."""

import numpy as np
cimport numpy as cnp
cimport cython

# Initialize NumPy C API
cnp.import_array()


@cython.boundscheck(False)
@cython.wraparound(False)
def sum_array(cnp.ndarray[cnp.float64_t, ndim=1] arr):
    """Sum all elements in a 1D array using Cython.
    
    Args:
        arr: 1D NumPy array of float64
        
    Returns:
        Sum of all elements
    """
    cdef double total = 0.0
    cdef Py_ssize_t i
    cdef Py_ssize_t n = arr.shape[0]
    
    for i in range(n):
        total += arr[i]
    
    return total


@cython.boundscheck(False)
@cython.wraparound(False)
def multiply_arrays(
    cnp.ndarray[cnp.float64_t, ndim=1] a,
    cnp.ndarray[cnp.float64_t, ndim=1] b
):
    """Element-wise multiplication of two 1D arrays.
    
    Args:
        a: First 1D NumPy array
        b: Second 1D NumPy array
        
    Returns:
        New array with element-wise product
    """
    if a.shape[0] != b.shape[0]:
        raise ValueError("Arrays must have the same length")
    
    cdef Py_ssize_t n = a.shape[0]
    cdef cnp.ndarray[cnp.float64_t, ndim=1] result = np.empty(n, dtype=np.float64)
    cdef Py_ssize_t i
    
    for i in range(n):
        result[i] = a[i] * b[i]
    
    return result


@cython.boundscheck(False)
@cython.wraparound(False)
def matrix_multiply(
    cnp.ndarray[cnp.float64_t, ndim=2] A,
    cnp.ndarray[cnp.float64_t, ndim=2] B
):
    """Matrix multiplication using Cython.
    
    Args:
        A: First matrix (m x n)
        B: Second matrix (n x p)
        
    Returns:
        Result matrix (m x p)
    """
    cdef Py_ssize_t m = A.shape[0]
    cdef Py_ssize_t n = A.shape[1]
    cdef Py_ssize_t p = B.shape[1]
    
    if B.shape[0] != n:
        raise ValueError("Incompatible matrix dimensions")
    
    cdef cnp.ndarray[cnp.float64_t, ndim=2] C = np.zeros((m, p), dtype=np.float64)
    cdef Py_ssize_t i, j, k
    
    for i in range(m):
        for j in range(p):
            for k in range(n):
                C[i, j] += A[i, k] * B[k, j]
    
    return C
