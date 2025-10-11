"""
EngiX Signals Module
Provides signal generation and basic signal operations.
"""

def unit_step(n):
    """
    Generates a unit step signal.

    Parameters
    ----------
    n : list or array-like
        Sample indices.

    Returns
    -------
    list
        Unit step signal.

    Example
    -------
    >>> unit_step(range(-3,4))
    [0, 0, 0, 1, 1, 1, 1]
    """
    return [1 if i >= 0 else 0 for i in n]

def ramp(n):
    """
    Generates a ramp signal.

    Parameters
    ----------
    n : list or array-like
        Sample indices.

    Returns
    -------
    list
        Ramp signal.

    Example
    -------
    >>> ramp(range(-2,3))
    [0, 0, 0, 1, 2]
    """
    return [i if i > 0 else 0 for i in n]

def convolution(x, h):
    """
    Computes linear convolution of two sequences.

    Parameters
    ----------
    x : list
        First sequence.
    h : list
        Second sequence.

    Returns
    -------
    list
        Convolved sequence.

    Example
    -------
    >>> convolution([1,2,3], [0,1,0.5])
    [0.0, 1.0, 2.5, 4.0, 1.5]
    """
    import numpy as np
    return np.convolve(x, h).tolist()

def correlation(x, y):
    """
    Computes cross-correlation between two sequences.

    Parameters
    ----------
    x : list
        First sequence.
    y : list
        Second sequence.

    Returns
    -------
    list
        Cross-correlated sequence.

    Example
    -------
    >>> correlation([1,2,3],[3,2,1])
    [3, 8, 14, 8, 3]
    """
    import numpy as np
    return np.correlate(x, y, mode='full').tolist()
