"""
Quantum circuit simulator using statevector representation
"""
import numpy as np
from typing import List, Tuple, Dict
from .results import Result
from .gates import H, X, Y, Z, CX


class Simulator:
    """
    Statevector-based quantum circuit simulator.

    Simulates quantum circuits by maintaining and evolving the full
    statevector representation.
    """

    def __init__(self, num_qubits: int):
        """
        Initialize simulator.

        Args:
            num_qubits: Number of qubits to simulate
        """
        if num_qubits <= 0:
            raise ValueError("Number of qubits must be positive")
        if num_qubits > 25:
            raise ValueError(
                "Cannot simulate more than 25 qubits (memory constraint). "
                f"Requested: {num_qubits}"
            )

        self.num_qubits = num_qubits
        self.num_states = 2 ** num_qubits
        self.statevector = self._initialize_statevector()

    def _initialize_statevector(self) -> np.ndarray:
        """
        Initialize statevector to |00...0⟩ state.

        Returns:
            Statevector array
        """
        statevector = np.zeros(self.num_states, dtype=complex)
        statevector[0] = 1.0  # |00...0⟩ state
        return statevector

    def reset(self) -> None:
        """Reset the statevector to |00...0⟩ state."""
        self.statevector = self._initialize_statevector()

    def apply_gate(self, gate: np.ndarray, target_qubit: int) -> None:
        """
        Apply a single-qubit gate to the statevector.

        Args:
            gate: 2x2 unitary matrix
            target_qubit: Qubit index to apply gate to
        """
        if target_qubit < 0 or target_qubit >= self.num_qubits:
            raise ValueError(f"Invalid qubit index: {target_qubit}")

        # Create identity matrices for all other qubits
        gate_matrix = self._expand_gate_to_full_space(gate, target_qubit)

        # Apply gate to statevector
        self.statevector = gate_matrix @ self.statevector

    def _expand_gate_to_full_space(
        self, gate: np.ndarray, target_qubit: int
    ) -> np.ndarray:
        """
        Expand a single-qubit gate to act on full Hilbert space.

        Args:
            gate: 2x2 gate matrix
            target_qubit: Which qubit the gate acts on

        Returns:
            Full-space gate matrix
        """
        # Create the full matrix by tensor product
        if target_qubit == 0:
            result = gate
        else:
            result = np.eye(2, dtype=complex)

        for i in range(1, self.num_qubits):
            if i == target_qubit:
                result = np.kron(result, gate)
            else:
                result = np.kron(result, np.eye(2, dtype=complex))

        return result

    def apply_cx(self, control: int, target: int) -> None:
        """
        Apply CNOT gate to the statevector.

        Args:
            control: Control qubit index
            target: Target qubit index
        """
        if control == target:
            raise ValueError("Control and target qubits must be different")
        if not (0 <= control < self.num_qubits and 0 <= target < self.num_qubits):
            raise ValueError("Invalid qubit indices")

        # Create full CNOT matrix
        cx_matrix = self._create_cx_matrix(control, target)
        self.statevector = cx_matrix @ self.statevector

    def _create_cx_matrix(self, control: int, target: int) -> np.ndarray:
        """
        Create CNOT gate matrix for arbitrary control and target qubits.

        Args:
            control: Control qubit index
            target: Target qubit index

        Returns:
            Full-space CNOT matrix
        """
        matrix = np.eye(self.num_states, dtype=complex)

        for i in range(self.num_states):
            # Check if control qubit is 1
            if (i >> (self.num_qubits - 1 - control)) & 1:
                # Flip target qubit
                j = i ^ (1 << (self.num_qubits - 1 - target))
                if i != j:
                    # Swap rows i and j
                    matrix[i, i] = 0
                    matrix[j, j] = 0
                    matrix[i, j] = 1
                    matrix[j, i] = 1

        return matrix

    def measure_all(self, shots: int = 1000) -> Result:
        """
        Measure all qubits in computational basis.

        Args:
            shots: Number of measurements to perform

        Returns:
            Result object with measurement outcomes
        """
        if shots <= 0:
            raise ValueError("Number of shots must be positive")

        # Calculate probabilities from statevector
        probabilities = np.abs(self.statevector) ** 2

        # Normalize (in case of numerical errors)
        probabilities /= np.sum(probabilities)

        # Sample from probability distribution
        outcomes = np.random.choice(
            self.num_states,
            size=shots,
            p=probabilities
        )

        # Convert to bitstrings and count
        counts: Dict[str, int] = {}
        for outcome in outcomes:
            bitstring = format(outcome, f'0{self.num_qubits}b')
            counts[bitstring] = counts.get(bitstring, 0) + 1

        return Result(counts=counts, shots=shots, num_qubits=self.num_qubits)

    def get_statevector(self) -> np.ndarray:
        """
        Get current statevector.

        Returns:
            Copy of the current statevector
        """
        return self.statevector.copy()

    def get_probabilities(self) -> np.ndarray:
        """
        Get probability distribution from statevector.

        Returns:
            Array of probabilities for each computational basis state
        """
        return np.abs(self.statevector) ** 2

    def __repr__(self) -> str:
        """String representation."""
        return f"Simulator(num_qubits={self.num_qubits})"


__all__ = ['Simulator']