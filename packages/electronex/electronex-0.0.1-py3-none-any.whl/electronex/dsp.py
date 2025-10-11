"""
EngiX DSP Module
Provides digital signal processing utilities.
"""

def fourier_transform(x):
    """
    Computes the Fast Fourier Transform (FFT) of a sequence.

    Parameters
    ----------
    x : list or array-like
        Input discrete-time signal.

    Returns
    -------
    list of complex
        FFT of the input signal.

    Example
    -------
    >>> fourier_transform([1,0,-1,0])
    [(0+0j), (2+0j), (0+0j), (2+0j)]
    """
    import numpy as np
    return np.fft.fft(x).tolist()

def inverse_fourier(X):
    """
    Computes the inverse FFT of a sequence.

    Parameters
    ----------
    X : list or array-like
        Frequency domain signal.

    Returns
    -------
    list of complex
        Time-domain signal.

    Example
    -------
    >>> inverse_fourier([1, 2, 3, 4])
    [(2.5+0j), (-0.5+0.5j), (-0.5+0j), (-0.5-0.5j)]
    """
    import numpy as np
    return np.fft.ifft(X).tolist()

def filter_signal(x, threshold):
    """
    Simple low-pass filter that zeroes out elements above threshold.

    Parameters
    ----------
    x : list
        Input signal.
    threshold : float
        Threshold for filtering.

    Returns
    -------
    list
        Filtered signal.

    Example
    -------
    >>> filter_signal([1.2, 0.5, -2, 0.3], 1.0)
    [1.0, 0.5, -1.0, 0.3]
    """
    return [max(min(val, threshold), -threshold) for val in x]
