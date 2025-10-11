"""
EngiX Communication Module
Provides basic tools for communication system analysis.
"""

def amplitude_modulation(carrier, message, mod_index=0.5):
    """
    Performs amplitude modulation (AM) on a carrier signal.

    Parameters
    ----------
    carrier : list or array-like
        Carrier signal samples.
    message : list or array-like
        Message signal samples.
    mod_index : float, optional
        Modulation index (default is 0.5).

    Returns
    -------
    list
        AM modulated signal.

    Example
    -------
    >>> amplitude_modulation([1,1,1,1], [0.1,0.2,0.1,0], 0.5)
    [1.05, 1.1, 1.05, 1.0]
    """
    return [(1 + mod_index*m)*c for c, m in zip(carrier, message)]

def snr_db(signal_power, noise_power):
    """
    Computes Signal-to-Noise Ratio (SNR) in dB.

    Parameters
    ----------
    signal_power : float
        Power of signal.
    noise_power : float
        Power of noise.

    Returns
    -------
    float
        SNR in decibels.

    Example
    -------
    >>> snr_db(10, 0.1)
    20.0
    """
    import math
    return 10 * math.log10(signal_power / noise_power)

def bit_error_rate(num_errors, total_bits):
    """
    Computes Bit Error Rate (BER).

    Parameters
    ----------
    num_errors : int
        Number of erroneous bits.
    total_bits : int
        Total bits transmitted.

    Returns
    -------
    float
        BER.

    Example
    -------
    >>> bit_error_rate(5, 1000)
    0.005
    """
    return num_errors / total_bits
