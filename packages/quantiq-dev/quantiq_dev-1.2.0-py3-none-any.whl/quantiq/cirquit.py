"""
Main QuantumCircuit class for quantIQ
"""
import numpy as np
from typing import List, Tuple, Optional
from .gates import H, X, Y, Z, CX
from .simulator import Simulator
from .results import Result
from .visualization import CircuitDrawer


class QuantumCircuit:
    """A quantum circuit for building and simulating quantum algorithms."""

    def __init__(self, num_qubits: int):
        """
        Initialize a quantum circuit.

        Args:
            num_qubits: Number of qubits in the circuit
        """
        if num_qubits <= 0:
            raise ValueError("Number of qubits must be positive")

        self.num_qubits = num_qubits
        self.gates: List[Tuple] = []
        self._simulator: Optional[Simulator] = None
        self._drawer = CircuitDrawer(num_qubits)

    def h(self, qubit: int) -> 'QuantumCircuit':
        """Apply Hadamard gate to qubit."""
        self._validate_qubit(qubit)
        self.gates.append(('H', qubit))
        self._drawer.add_gate('H', qubit)
        return self

    def x(self, qubit: int) -> 'QuantumCircuit':
        """Apply Pauli-X (NOT) gate to qubit."""
        self._validate_qubit(qubit)
        self.gates.append(('X', qubit))
        self._drawer.add_gate('X', qubit)
        return self

    def y(self, qubit: int) -> 'QuantumCircuit':
        """Apply Pauli-Y gate to qubit."""
        self._validate_qubit(qubit)
        self.gates.append(('Y', qubit))
        self._drawer.add_gate('Y', qubit)
        return self

    def z(self, qubit: int) -> 'QuantumCircuit':
        """Apply Pauli-Z gate to qubit."""
        self._validate_qubit(qubit)
        self.gates.append(('Z', qubit))
        self._drawer.add_gate('Z', qubit)
        return self

    def cx(self, control: int, target: int) -> 'QuantumCircuit':
        """Apply CNOT (Controlled-X) gate."""
        self._validate_qubit(control)
        self._validate_qubit(target)
        if control == target:
            raise ValueError("Control and target qubits must be different")
        self.gates.append(('CX', control, target))
        self._drawer.add_gate('CX', control, target)
        return self

    def measure_all(self) -> 'QuantumCircuit':
        """Measure all qubits in the computational basis."""
        self.gates.append(('MEASURE_ALL',))
        self._drawer.add_gate('MEASURE_ALL')
        return self

    def _validate_qubit(self, qubit: int) -> None:
        """Validate qubit index."""
        if not 0 <= qubit < self.num_qubits:
            raise ValueError(f"Qubit index {qubit} out of range [0, {self.num_qubits})")

    def run(self, shots: int = 1000) -> Result:
        """
        Simulate the circuit and return measurement results.

        Args:
            shots: Number of times to run the circuit

        Returns:
            Result object with measurement outcomes
        """
        if shots <= 0:
            raise ValueError("Number of shots must be positive")

        # Initialize simulator
        simulator = Simulator(self.num_qubits)

        # Apply gates
        for gate in self.gates:
            gate_type = gate[0]

            if gate_type == 'H':
                simulator.apply_gate(H, gate[1])
            elif gate_type == 'X':
                simulator.apply_gate(X, gate[1])
            elif gate_type == 'Y':
                simulator.apply_gate(Y, gate[1])
            elif gate_type == 'Z':
                simulator.apply_gate(Z, gate[1])
            elif gate_type == 'CX':
                simulator.apply_cx(gate[1], gate[2])
            elif gate_type == 'MEASURE_ALL':
                # Measurement is handled after all gates
                pass

        # Perform measurement
        result = simulator.measure_all(shots)

        return result

    def get_statevector(self) -> np.ndarray:
        """
        Get the statevector after applying all gates (no measurement).

        Returns:
            Complex numpy array representing the statevector
        """
        simulator = Simulator(self.num_qubits)

        # Apply gates (excluding measurements)
        for gate in self.gates:
            gate_type = gate[0]

            if gate_type == 'H':
                simulator.apply_gate(H, gate[1])
            elif gate_type == 'X':
                simulator.apply_gate(X, gate[1])
            elif gate_type == 'Y':
                simulator.apply_gate(Y, gate[1])
            elif gate_type == 'Z':
                simulator.apply_gate(Z, gate[1])
            elif gate_type == 'CX':
                simulator.apply_cx(gate[1], gate[2])

        return simulator.get_statevector()

    def draw(self) -> str:
        """
        Draw the circuit as ASCII art.

        Returns:
            String representation of the circuit
        """
        return self._drawer.draw()

    def __repr__(self) -> str:
        return f"QuantumCircuit({self.num_qubits} qubits, {len(self.gates)} gates)"

    def __str__(self) -> str:
        return self.draw()


__all__ = ['QuantumCircuit']