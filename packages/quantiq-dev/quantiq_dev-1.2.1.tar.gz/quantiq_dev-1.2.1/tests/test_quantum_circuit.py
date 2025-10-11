"""Tests for QuantumCircuit class."""

import pytest

from quantiq import QuantumCircuit


class TestQuantumCircuitBasics:
    """Test basic circuit creation and properties."""

    def test_circuit_creation(self):
        """Test creating a quantum circuit."""
        circuit = QuantumCircuit(2)
        assert circuit.num_qubits == 2

    def test_circuit_with_zero_qubits_raises_error(self):
        """Test that creating a circuit with 0 qubits raises an error."""
        with pytest.raises(ValueError):
            QuantumCircuit(0)

    def test_circuit_with_negative_qubits_raises_error(self):
        """Test that creating a circuit with negative qubits raises an error."""
        with pytest.raises(ValueError):
            QuantumCircuit(-1)


class TestQuantumGates:
    """Test quantum gate operations."""

    def test_hadamard_gate(self):
        """Test applying Hadamard gate."""
        circuit = QuantumCircuit(1)
        circuit.h(0)
        assert len(circuit.gates) == 1
        assert circuit.gates[0] == ("H", 0)

    def test_cnot_gate(self):
        """Test applying CNOT gate."""
        circuit = QuantumCircuit(2)
        circuit.cx(0, 1)
        assert len(circuit.gates) == 1

    def test_pauli_gates(self):
        """Test Pauli X, Y, Z gates."""
        circuit = QuantumCircuit(1)
        circuit.x(0)
        circuit.y(0)
        circuit.z(0)
        assert len(circuit.gates) == 3

    def test_gate_chaining(self):
        """Test that gates can be chained."""
        circuit = QuantumCircuit(2)
        result = circuit.h(0).x(1)
        assert result is circuit  # Should return self for chaining
        assert len(circuit.gates) == 2


def test_package_import():
    """Test that the package can be imported."""
    from quantiq import QuantumCircuit

    assert QuantumCircuit is not None
