"""
Quantum gate definitions for quantIQ
"""

import numpy as np

# Single-qubit gates
# Hadamard gate
H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)

# Pauli-X gate (NOT gate)
X = np.array([[0, 1], [1, 0]], dtype=complex)

# Pauli-Y gate
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)

# Pauli-Z gate
Z = np.array([[1, 0], [0, -1]], dtype=complex)

# S gate (Phase gate, sqrt(Z))
S = np.array([[1, 0], [0, 1j]], dtype=complex)

# T gate (π/8 gate)
T = np.array([[1, 0], [0, np.exp(1j * np.pi / 4)]], dtype=complex)

# Identity gate
I = np.array([[1, 0], [0, 1]], dtype=complex)

# Two-qubit gates
# CNOT gate (controlled-NOT)
# Basis order: |00⟩, |01⟩, |10⟩, |11⟩
CX = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]], dtype=complex)

# Controlled-Z gate
CZ = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, -1]], dtype=complex)

# SWAP gate
SWAP = np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1]], dtype=complex)


# Rotation gates
def rx(theta: float) -> np.ndarray:
    """
    Rotation around X-axis.

    Args:
        theta: Rotation angle in radians

    Returns:
        2x2 unitary matrix
    """
    c = np.cos(theta / 2)
    s = np.sin(theta / 2)
    return np.array([[c, -1j * s], [-1j * s, c]], dtype=complex)


def ry(theta: float) -> np.ndarray:
    """
    Rotation around Y-axis.

    Args:
        theta: Rotation angle in radians

    Returns:
        2x2 unitary matrix
    """
    c = np.cos(theta / 2)
    s = np.sin(theta / 2)
    return np.array([[c, -s], [s, c]], dtype=complex)


def rz(theta: float) -> np.ndarray:
    """
    Rotation around Z-axis.

    Args:
        theta: Rotation angle in radians

    Returns:
        2x2 unitary matrix
    """
    return np.array(
        [[np.exp(-1j * theta / 2), 0], [0, np.exp(1j * theta / 2)]], dtype=complex
    )
