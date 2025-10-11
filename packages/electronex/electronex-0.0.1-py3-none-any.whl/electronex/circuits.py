"""
EngiX Circuits Module
Provides functions for electrical circuit analysis.
"""

def ohms_law(v=None, i=None, r=None):
    """
    Calculates the missing parameter using Ohm's Law: V = I * R.

    Parameters
    ----------
    v : float, optional
        Voltage in volts. Provide None if unknown.
    i : float, optional
        Current in amperes. Provide None if unknown.
    r : float, optional
        Resistance in ohms. Provide None if unknown.

    Returns
    -------
    float
        The calculated missing value (voltage, current, or resistance).

    Example
    -------
    >>> ohms_law(i=0.02, r=220)
    4.4
    """
    if v is None:
        return i * r
    elif i is None:
        return v / r
    elif r is None:
        return v / i

def voltage_divider(v_in, r1, r2):
    """
    Calculates output voltage of a voltage divider.

    Parameters
    ----------
    v_in : float
        Input voltage.
    r1 : float
        Resistance R1.
    r2 : float
        Resistance R2.

    Returns
    -------
    float
        Output voltage across R2.

    Example
    -------
    >>> voltage_divider(12, 10000, 15000)
    7.2
    """
    return v_in * r2 / (r1 + r2)

def impedance_rlc(r, l, c, f):
    """
    Calculates the impedance of a series RLC circuit.

    Parameters
    ----------
    r : float
        Resistance in ohms.
    l : float
        Inductance in henrys.
    c : float
        Capacitance in farads.
    f : float
        Frequency in Hz.

    Returns
    -------
    complex
        Impedance as a complex number (R + jX).

    Example
    -------
    >>> impedance_rlc(100, 0.1, 1e-6, 50)
    (100+30.35843744974348j)
    """
    import cmath
    w = 2 * 3.14159265359 * f
    return complex(r, w*l - 1/(w*c))

def power(v, i):
    """
    Calculates instantaneous power.

    Parameters
    ----------
    v : float
        Voltage in volts.
    i : float
        Current in amperes.

    Returns
    -------
    float
        Power in watts.

    Example
    -------
    >>> power(12, 0.5)
    6
    """
    return v * i
