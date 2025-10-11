"""
EngiX Logic Module
Provides digital logic gate operations and code converters.
"""

def and_gate(a, b):
    """
    Logical AND of two binary inputs.

    Example
    -------
    >>> and_gate(1,0)
    0
    """
    return a & b

def or_gate(a, b):
    """
    Logical OR of two binary inputs.

    Example
    -------
    >>> or_gate(1,0)
    1
    """
    return a | b

def not_gate(a):
    """
    Logical NOT of a binary input.

    Example
    -------
    >>> not_gate(1)
    0
    """
    return 0 if a else 1

def xor_gate(a, b):
    """
    Logical XOR of two binary inputs.

    Example
    -------
    >>> xor_gate(1,1)
    0
    """
    return a ^ b

def binary_to_gray(n):
    """
    Converts binary number to Gray code.

    Parameters
    ----------
    n : int
        Binary number.

    Returns
    -------
    int
        Gray code.

    Example
    -------
    >>> binary_to_gray(7)
    4
    """
    return n ^ (n >> 1)

def gray_to_binary(n):
    """
    Converts Gray code to binary number.

    Parameters
    ----------
    n : int
        Gray code.

    Returns
    -------
    int
        Binary number.

    Example
    -------
    >>> gray_to_binary(4)
    7
    """
    mask = n
    while mask != 0:
        mask >>= 1
        n ^= mask
    return n
