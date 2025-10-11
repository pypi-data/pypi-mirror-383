"""Basic math operations - regular .py file compiled to binary."""


def add(a: int, b: int) -> int:
    """Add two integers."""
    return a + b


def multiply(a: int, b: int) -> int:
    """Multiply two integers."""
    return a * b


def power(base: float, exponent: int) -> float:
    """Calculate base^exponent."""
    result = 1.0
    for i in range(exponent):
        result *= base
    return result
