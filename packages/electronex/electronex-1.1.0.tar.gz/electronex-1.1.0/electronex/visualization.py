"""
EngiX Visualization Module
Provides functions to plot signals and circuit responses.
"""

def plot_signal(n, x, title="Signal"):
    """
    Plots discrete-time signal.

    Parameters
    ----------
    n : list or array-like
        Sample indices.
    x : list or array-like
        Signal values.
    title : str, optional
        Plot title.

    Example
    -------
    >>> n = range(-5,6)
    >>> x = [i**2 for i in n]
    >>> plot_signal(n,x)
    """
    import matplotlib.pyplot as plt
    plt.stem(n, x)
    plt.title(title)
    plt.xlabel("n")
    plt.ylabel("Amplitude")
    plt.show()

def plot_circuit_response(time, voltage):
    """
    Plots voltage vs time for a circuit.

    Example
    -------
    >>> plot_circuit_response([0,1,2,3],[5,3,1.5,0.5])
    """
    import matplotlib.pyplot as plt
    plt.plot(time, voltage)
    plt.title("Circuit Response")
    plt.xlabel("Time (s)")
    plt.ylabel("Voltage (V)")
    plt.grid(True)
    plt.show()
