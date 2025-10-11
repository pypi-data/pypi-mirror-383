"""
Quantum circuit execution results
"""

from collections import Counter
from typing import Dict, List, Tuple


class Result:
    """
    Stores and analyzes quantum circuit execution results.

    Attributes:
        counts: Dictionary mapping measurement outcomes to counts
        shots: Total number of circuit executions
        num_qubits: Number of qubits measured
    """

    def __init__(self, counts: Dict[str, int], shots: int, num_qubits: int):
        """
        Initialize a Result object.

        Args:
            counts: Dictionary of measurement outcomes and their counts
            shots: Total number of shots executed
            num_qubits: Number of qubits in the circuit
        """
        self.counts = counts
        self.shots = shots
        self.num_qubits = num_qubits
        self._validate()

    def _validate(self) -> None:
        """Validate result data."""
        total_counts = sum(self.counts.values())
        if total_counts != self.shots:
            raise ValueError(
                f"Sum of counts ({total_counts}) doesn't match shots ({self.shots})"
            )

        # Validate bitstring lengths
        for bitstring in self.counts.keys():
            if len(bitstring) != self.num_qubits:
                raise ValueError(
                    f"Bitstring '{bitstring}' length doesn't match num_qubits ({self.num_qubits})"
                )

    def probabilities(self) -> Dict[str, float]:
        """
        Calculate probability distribution from counts.

        Returns:
            Dictionary mapping outcomes to probabilities
        """
        return {outcome: count / self.shots for outcome, count in self.counts.items()}

    def most_common(self, n: int = 5) -> List[Tuple[str, int]]:
        """
        Get the n most common measurement outcomes.

        Args:
            n: Number of outcomes to return

        Returns:
            List of (outcome, count) tuples sorted by count
        """
        counter = Counter(self.counts)
        return counter.most_common(n)

    def get_counts(self, outcome: str) -> int:
        """
        Get count for a specific outcome.

        Args:
            outcome: Bitstring outcome (e.g., '00', '11')

        Returns:
            Number of times this outcome was measured
        """
        return self.counts.get(outcome, 0)

    def expectation_value(self, observable: str = "Z") -> float:
        """
        Calculate expectation value for a given observable.

        Args:
            observable: Observable to measure ('Z' for computational basis)

        Returns:
            Expectation value
        """
        if observable != "Z":
            raise NotImplementedError("Only Z observable supported currently")

        expectation = 0.0
        for outcome, count in self.counts.items():
            # Count number of 1s in outcome
            parity = sum(int(bit) for bit in outcome) % 2
            # (-1)^parity gives +1 for even, -1 for odd
            sign = 1 if parity == 0 else -1
            expectation += sign * (count / self.shots)

        return expectation

    def to_dict(self) -> Dict:
        """
        Convert result to dictionary format.

        Returns:
            Dictionary representation of the result
        """
        return {
            "counts": self.counts,
            "shots": self.shots,
            "num_qubits": self.num_qubits,
            "probabilities": self.probabilities(),
        }

    def __repr__(self) -> str:
        """String representation of Result."""
        top_outcomes = self.most_common(3)
        outcomes_str = ", ".join(
            f"'{outcome}': {count}" for outcome, count in top_outcomes
        )
        return f"Result(shots={self.shots}, top_outcomes={{{outcomes_str}, ...}})"

    def __str__(self) -> str:
        """Pretty string representation."""
        lines = [f"Quantum Circuit Results ({self.shots} shots):"]
        lines.append("-" * 50)

        for outcome, count in self.most_common(10):
            prob = count / self.shots
            bar_length = int(prob * 40)
            bar = "█" * bar_length
            lines.append(f"|{outcome}⟩: {count:4d} ({prob:6.2%}) {bar}")

        if len(self.counts) > 10:
            lines.append(f"... and {len(self.counts) - 10} more outcomes")

        return "\n".join(lines)


__all__ = ["Result"]
