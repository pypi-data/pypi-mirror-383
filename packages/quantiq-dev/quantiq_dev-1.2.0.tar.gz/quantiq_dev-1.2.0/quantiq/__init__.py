"""
quantIQ - Quantum circuits, simplified.
A developer-first quantum computing platform.
"""

__version__ = "1.0.1"

from .quantiq import QuantumCircuit
from .results import Result
from .simulator import Simulator
from .visualization import draw_circuit, plot_results

__all__ = [
    'QuantumCircuit',
    'Result',
    'Simulator',
    'draw_circuit',
    'plot_results',
    '__version__'
]