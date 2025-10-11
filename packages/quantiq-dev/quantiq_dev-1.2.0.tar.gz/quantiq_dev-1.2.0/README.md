<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/tony-siqurity-ai/quantiq-brand/main/logos/logo-horizontal-white.png">
    <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/tony-siqurity-ai/quantiq-brand/main/logos/logo-horizontal.png">
    <img src="https://raw.githubusercontent.com/tony-siqurity-ai/quantiq-brand/main/logos/logo-horizontal.png" alt="quantIQ" width="400">
  </picture>

  <p><strong>Quantum circuits, simplified.</strong></p>

  [![PyPI version](https://badge.fury.io/py/quantiq.svg)](https://badge.fury.io/py/quantiq)
  [![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  [![GitHub stars](https://img.shields.io/github/stars/tony-siqurity-ai/quantiq-web?style=social)](https://github.com/tony-siqurity-ai/quantiq-web)

  [Website](https://quantiq.dev) • [Documentation](https://docs.quantiq.dev) • [Examples](./examples)
</div>

---

## 🚀 Quick Start

```bash
pip install quantiq
```

```python
from quantiq import QuantumCircuit

# Create a Bell state (quantum entanglement)
qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)
qc.measure_all()

# Run the circuit
result = qc.run(shots=1000)
print(result)
```

**That's it!** You just created quantum entanglement.

---

## 🎯 What is quantIQ?

**quantIQ** is a Python library for building quantum circuits with a developer-first approach. No quantum physics PhD required.

- 🎯 **Simple API** - Intuitive, Pythonic interface
- ⚡ **Fast** - Optimized quantum circuit simulation
- 📚 **Well Documented** - Clear examples and tutorials
- 🔧 **Extensible** - Easy to add custom gates
- 🌐 **Open Source** - MIT licensed

Perfect for learning, prototyping, and algorithm development.

---

## ✨ Features

### Comprehensive Gate Library

**Single-qubit gates:**
- Pauli gates: `x()`, `y()`, `z()`
- Hadamard: `h()`
- Rotations: `rx()`, `ry()`, `rz()`

**Two-qubit gates:**
- `cx()` - CNOT (controlled-NOT)
- `cz()` - Controlled-Z
- More coming soon!

### Method Chaining

```python
qc = QuantumCircuit(3)
qc.h(0).h(1).h(2).cx(0, 1).cx(1, 2).measure_all()
```

### Circuit Information

```python
print(qc)
# Output: QuantumCircuit(3 qubits, 6 gates)
```

---

## 📖 Examples

### Bell State

```python
from quantiq import QuantumCircuit

qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)
qc.measure_all()

result = qc.run(shots=1000)
# Perfect correlation: ~50% |00⟩ and ~50% |11⟩
```

### GHZ State (3-qubit Entanglement)

```python
from quantiq import QuantumCircuit

qc = QuantumCircuit(3)
qc.h(0)
qc.cx(0, 1)
qc.cx(1, 2)
qc.measure_all()

result = qc.run(shots=1000)
# Result: ~50% |000⟩ and ~50% |111⟩
```

### Superposition

```python
from quantiq import QuantumCircuit

qc = QuantumCircuit(1)
qc.h(0)  # Create superposition
qc.measure_all()

result = qc.run(shots=1000)
# Result: ~50% |0⟩ and ~50% |1⟩
```

**📁 More examples:** [examples/](./examples)

---

## 🛠️ Installation

### Requirements

- Python 3.11 or higher
- NumPy

### Install from PyPI

```bash
pip install quantiq
```

### Install from Source

```bash
git clone https://github.com/tony-siqurity-ai/quantiq-web.git
cd quantiq-web
pip install -e .
```

---

## 📚 Documentation

Full documentation is available at [docs.quantiq.dev](https://docs.quantiq.dev)

- [Getting Started](https://docs.quantiq.dev)
- [API Reference](https://docs.quantiq.dev)
- [Examples](./examples)

---

## 🗺️ Roadmap

### ✅ v1.0 (Current)
- [x] Core quantum gates (H, X, Y, Z, CX)
- [x] Basic statevector simulation
- [x] Method chaining API
- [x] PyPI package

### 🚧 v1.1 (Next)
- [ ] Circuit visualization
- [ ] More quantum gates (CZ, SWAP, Toffoli)
- [ ] Result analysis tools
- [ ] Performance optimizations

### 🔮 Future
- [ ] Advanced quantum algorithms
- [ ] Noise simulation
- [ ] GPU-accelerated simulation
- [ ] Cloud API

**See our [full roadmap](https://github.com/tony-siqurity-ai/quantiq-web/issues) →**

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

- 🐛 Report bugs by [opening an issue](https://github.com/tony-siqurity-ai/quantiq-web/issues)
- ✨ Suggest features in [discussions](https://github.com/tony-siqurity-ai/quantiq-web/discussions)
- 📝 Improve documentation
- 🔧 Submit pull requests

See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/tony-siqurity-ai/quantiq-web.git
cd quantiq-web

# Install in development mode
pip install -e .

# Run tests (if you have them)
python -m pytest tests/
```

---

## 📄 License

quantIQ is released under the [MIT License](./LICENSE).

---

## 🙏 Acknowledgments

Built for the quantum computing community.

Special thanks to early adopters and contributors!

---

## 🗺️ Roadmap

See our [public roadmap](https://github.com/users/tony-siqurity-ai/projects/1) for upcoming features and Cloud API development.

Want to influence what we build? [Open a discussion](https://github.com/tony-siqurity-ai/quantiq-web/discussions)!

---

<div align="center">

**⭐ Star us on GitHub if you find quantIQ useful!**

Made with ⚛️ by the quantIQ team

[Get Started](https://docs.quantiq.dev) • [GitHub](https://github.com/tony-siqurity-ai/quantiq-web) • [PyPI](https://pypi.org/project/quantiq/)

</div>