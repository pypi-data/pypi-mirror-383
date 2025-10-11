"""
ElectronEx Package
------------------
A Python package for ECE & CSE engineers, including circuits, signals, DSP,
communications, logic, algorithms, ML tools, and visualization utilities.
"""

# Import submodules
from . import circuits
from . import signals
from . import dsp
from . import comms
from . import logic
from . import algorithms
from . import mltools
from . import visualization

# Expose commonly used functions for convenience
# (add your most frequently used functions here)
from .circuits import ohms_law, voltage_divider, impedance_rlc, power


# Package version
__version__ = "0.1.0"

# Optional: define __all__ for "from electronex import *"
__all__ = [
    "circuits",
    "signals",
    "dsp",
    "comms",
    "logic",
    "algorithms",
    "mltools",
    "visualization",
    "ohms_law",
    "voltage_divider",
    "impedance_rlc",
    "power",
    
]
