# cython: language_level=3
"""Basic math operations in Cython."""


cpdef int add(int a, int b):
    """Add two integers using Cython.
    
    Args:
        a: First integer
        b: Second integer
        
    Returns:
        Sum of a and b
    """
    return a + b


cpdef int multiply(int a, int b):
    """Multiply two integers using Cython.
    
    Args:
        a: First integer
        b: Second integer
        
    Returns:
        Product of a and b
    """
    return a * b


cpdef double power(double base, int exponent):
    """Calculate base raised to the power of exponent.
    
    Args:
        base: Base number
        exponent: Exponent
        
    Returns:
        base ** exponent
    """
    cdef double result = 1.0
    cdef int i
    
    for i in range(exponent):
        result *= base
    
    return result
