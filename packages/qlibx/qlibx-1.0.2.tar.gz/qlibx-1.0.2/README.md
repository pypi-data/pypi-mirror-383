# Qlibx: A Quantum Computing Library

Qlibx is a Python library designed to provide foundational tools for quantum computing. It offers classes and methods to represent and manipulate quantum states, operators, and their interactions. The library is lightweight and focuses on the mathematical foundations of quantum mechanics, making it an excellent choice for learning and experimentation.

---

## Features

- **Quantum States**:
    - `Ket` and `Bra` classes to represent quantum states.
    - Support for operations like addition, subtraction, scalar multiplication, tensor products, and inner/outer products.

- **Quantum Operators**:
    - `Operator` class to represent quantum operators.
    - Methods for Hermitian, unitary, and normality checks.
    - Commutator and anti-commutator calculations.
    - Spectral decomposition and partial trace.
    - Von Neumann entropy calculation.

- **Predefined Operators**:
    - Pauli matrices (`pauli_x`, `pauli_y`, `pauli_z`) and the identity matrix.

---

## Installation

pip install qlibx

or

Clone the repository and include the library in your Python project:

```bash
git clone https://github.com/Suraj52721/qc_lib/tree/master
cd qlibx
```

Ensure the `qlibx` directory is in your Python path.

---

## Usage

### Importing the Library

```python
from qlibx import Ket, Bra, Operator
```

### Creating Quantum States

```python
# Create a Ket vector
ket = Ket([1, 0])

# Create a Bra vector
bra = Bra([1, 0])
```

### Quantum Operations

#### Addition and Subtraction

```python
ket1 = Ket([1, 0])
ket2 = Ket([0, 1])

# Addition
result_add = ket1 + ket2
print(result_add)

# Subtraction
result_sub = ket1 - ket2
print(result_sub)
```

#### Scalar Multiplication

```python
ket = Ket([1, 0])

# Scalar multiplication
result_scalar = 2 * ket
print(result_scalar)
```

#### Tensor Product

```python
ket1 = Ket([1, 0])
ket2 = Ket([0, 1])

# Tensor product
result_tensor = ket1.tensor(ket2)
print(result_tensor)
```

#### Inner and Outer Products

```python
ket = Ket([1, 0])
bra = Bra([1, 0])

# Inner product
inner = ket.inner_product(bra)
print(inner)

# Outer product
outer = ket.outer_product(bra)
print(outer)
```

### Working with Operators

#### Defining and Applying Operators

```python
# Define an operator
op = Operator([[0, 1], [1, 0]])

# Apply operator to a Ket
ket = Ket([1, 0])
result = op.op(ket)
print(result)
```

#### Hermitian, Unitary, and Normality Checks

```python
op = Operator([[0, 1], [1, 0]])

# Check if the operator is Hermitian
print(op.hermitian())

# Check if the operator is Unitary
print(op.unitary())

# Check if the operator is Normal
print(op.normal())
```

#### Commutator and Anti-Commutator

```python
op1 = Operator([[0, 1], [1, 0]])
op2 = Operator([[1, 0], [0, -1]])

# Commutator
commutator = op1.commutator(op2)
print(commutator)

# Anti-commutator
anti_commutator = op1.anti_commutator(op2)
print(anti_commutator)
```

#### Spectral Decomposition

```python
op = Operator([[2, 1], [1, 2]])

# Spectral decomposition
spectral_decomp = op.spectral_decom()
print(spectral_decomp)
```

#### Partial Trace

```python
op = Operator([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])

# Partial trace over the first subsystem
partial_trace_result = op.partial_trace([2, 2], 0)
print(partial_trace_result)
```

#### Von Neumann Entropy

```python
op = Operator([[0.5, 0], [0, 0.5]])

# Von Neumann entropy
entropy = op.von_neumann_entropy()
print(entropy)
```

---

## Example: Quantum Circuit Simulation

```python
from qlibx import Ket, Operator

# Define a quantum state |ψ⟩
psi = Ket([1, 0])

# Define a Pauli-X gate
pauli_x = Operator(Operator.pauli_x)

# Apply the gate
new_state = pauli_x.op(psi)

print(new_state)
```

---

## Contributing

Contributions are welcome! If you find a bug or have a feature request, please open an issue or submit a pull request.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Acknowledgments

Qlibx is inspired by the mathematical foundations of quantum mechanics and aims to provide an intuitive interface for quantum computing enthusiasts.
