"""
Circuit and result visualization utilities
"""
from typing import List, Tuple, Dict, Optional
from .results import Result


class CircuitDrawer:
    """
    Draws quantum circuits as ASCII art.
    """

    def __init__(self, num_qubits: int):
        """
        Initialize circuit drawer.

        Args:
            num_qubits: Number of qubits in the circuit
        """
        self.num_qubits = num_qubits
        self.gates: List[Tuple] = []

    def add_gate(self, gate_type: str, *qubits: int) -> None:
        """
        Add a gate to the circuit diagram.

        Args:
            gate_type: Type of gate (H, X, Y, Z, CX, etc.)
            *qubits: Qubit indices the gate acts on
        """
        self.gates.append((gate_type, *qubits))

    def draw(self) -> str:
        """
        Draw the circuit as ASCII art.

        Returns:
            String representation of the circuit
        """
        if not self.gates:
            return self._empty_circuit()

        # Initialize wire strings for each qubit
        wires = [f"q{i}: ─" for i in range(self.num_qubits)]

        # Process each gate
        for gate in self.gates:
            gate_type = gate[0]

            if gate_type in ['H', 'X', 'Y', 'Z']:
                # Single-qubit gates
                qubit = gate[1]
                self._add_single_qubit_gate(wires, gate_type, qubit)

            elif gate_type == 'CX':
                # Two-qubit gate
                control, target = gate[1], gate[2]
                self._add_cx_gate(wires, control, target)

            elif gate_type == 'MEASURE_ALL':
                # Measurement
                self._add_measurement(wires)

        # Add final connections
        for i in range(self.num_qubits):
            wires[i] += "─"

        return '\n'.join(wires)

    def _empty_circuit(self) -> str:
        """Draw empty circuit."""
        return '\n'.join([f"q{i}: ─────" for i in range(self.num_qubits)])

    def _add_single_qubit_gate(
        self, wires: List[str], gate_type: str, qubit: int
    ) -> None:
        """Add single-qubit gate to diagram."""
        # Pad other wires to align
        max_len = max(len(w) for w in wires)
        for i in range(self.num_qubits):
            while len(wires[i]) < max_len:
                wires[i] += "─"

        # Add gate
        wires[qubit] += f"[{gate_type}]─"

        # Extend other wires
        gate_len = len(f"[{gate_type}]─")
        for i in range(self.num_qubits):
            if i != qubit:
                wires[i] += "─" * gate_len

    def _add_cx_gate(
        self, wires: List[str], control: int, target: int
    ) -> None:
        """Add CNOT gate to diagram."""
        # Pad all wires to align
        max_len = max(len(w) for w in wires)
        for i in range(self.num_qubits):
            while len(wires[i]) < max_len:
                wires[i] += "─"

        # Add control and target symbols
        wires[control] += "●─"
        wires[target] += "⊕─"

        # Add vertical connections
        min_qubit = min(control, target)
        max_qubit = max(control, target)

        for i in range(self.num_qubits):
            if min_qubit < i < max_qubit:
                wires[i] += "│─"
            elif i not in [control, target]:
                wires[i] += "──"

    def _add_measurement(self, wires: List[str]) -> None:
        """Add measurement symbols to diagram."""
        max_len = max(len(w) for w in wires)
        for i in range(self.num_qubits):
            while len(wires[i]) < max_len:
                wires[i] += "─"
            wires[i] += "[M]"


class ResultVisualizer:
    """
    Visualizes quantum circuit execution results.
    """

    @staticmethod
    def plot_histogram(result: Result, max_outcomes: int = 10) -> str:
        """
        Create ASCII histogram of measurement results.

        Args:
            result: Result object to visualize
            max_outcomes: Maximum number of outcomes to display

        Returns:
            String representation of histogram
        """
        lines = [
            f"Measurement Results ({result.shots} shots)",
            "=" * 60
        ]

        # Get top outcomes
        top_outcomes = result.most_common(max_outcomes)

        # Find max count for scaling
        max_count = max(count for _, count in top_outcomes)

        # Create bars
        for outcome, count in top_outcomes:
            prob = count / result.shots

            # Scale bar to 40 characters max
            bar_length = int((count / max_count) * 40)
            bar = '█' * bar_length

            # Format line
            line = f"|{outcome}⟩: {count:5d} ({prob:6.2%}) {bar}"
            lines.append(line)

        # Add summary if there are more outcomes
        if len(result.counts) > max_outcomes:
            remaining = len(result.counts) - max_outcomes
            lines.append(f"\n... and {remaining} more outcomes")

        lines.append("=" * 60)

        return '\n'.join(lines)

    @staticmethod
    def plot_probabilities(result: Result, max_outcomes: int = 10) -> str:
        """
        Create probability distribution plot.

        Args:
            result: Result object to visualize
            max_outcomes: Maximum number of outcomes to display

        Returns:
            String representation of probability plot
        """
        lines = [
            f"Probability Distribution",
            "=" * 60
        ]

        probabilities = result.probabilities()

        # Sort by probability
        sorted_probs = sorted(
            probabilities.items(),
            key=lambda x: x[1],
            reverse=True
        )[:max_outcomes]

        # Create bars
        for outcome, prob in sorted_probs:
            # Scale bar to 50 characters
            bar_length = int(prob * 50)
            bar = '▓' * bar_length

            line = f"|{outcome}⟩: {prob:6.2%} {bar}"
            lines.append(line)

        lines.append("=" * 60)

        return '\n'.join(lines)

    @staticmethod
    def show_state_vector(
        statevector: 'np.ndarray',  # type: ignore
        num_qubits: int,
        threshold: float = 0.01
    ) -> str:
        """
        Display statevector amplitudes.

        Args:
            statevector: Quantum statevector
            num_qubits: Number of qubits
            threshold: Minimum probability to display

        Returns:
            String representation of statevector
        """
        lines = [
            "Statevector Amplitudes",
            "=" * 60
        ]

        for i, amplitude in enumerate(statevector):
            prob = abs(amplitude) ** 2

            if prob >= threshold:
                bitstring = format(i, f'0{num_qubits}b')
                phase = 0 if amplitude.real >= 0 else 180

                # Format amplitude
                real = amplitude.real
                imag = amplitude.imag

                if abs(imag) < 1e-10:
                    amp_str = f"{real:+.4f}"
                else:
                    amp_str = f"{real:+.4f}{imag:+.4f}j"

                line = f"|{bitstring}⟩: {amp_str} (p={prob:.4f})"
                lines.append(line)

        lines.append("=" * 60)

        return '\n'.join(lines)


def draw_circuit(num_qubits: int, gates: List[Tuple]) -> str:
    """
    Convenience function to draw a circuit.

    Args:
        num_qubits: Number of qubits
        gates: List of gate tuples (gate_type, *qubits)

    Returns:
        ASCII art representation of circuit
    """
    drawer = CircuitDrawer(num_qubits)
    for gate in gates:
        drawer.add_gate(*gate)
    return drawer.draw()


def plot_results(result: Result, style: str = 'histogram') -> str:
    """
    Plot measurement results.

    Args:
        result: Result object to plot
        style: Plot style ('histogram' or 'probability')

    Returns:
        String representation of plot
    """
    visualizer = ResultVisualizer()

    if style == 'histogram':
        return visualizer.plot_histogram(result)
    elif style == 'probability':
        return visualizer.plot_probabilities(result)
    else:
        raise ValueError(f"Unknown style: {style}")


__all__ = [
    'CircuitDrawer',
    'ResultVisualizer',
    'draw_circuit',
    'plot_results'
]