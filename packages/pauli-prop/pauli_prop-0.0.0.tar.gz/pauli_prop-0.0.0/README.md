# Pauli Prop

### About

Pauli propagation, also known as sparse Pauli dynamics (SPD), is a framework for approximating the
evolution of operators in the Pauli basis under the action of other operators, such as quantum
circuit gates and noise channels [1] - [5]. This approach can be effective when the operators
involved are expected to remain sparse in the Pauli basis. The technique has been used to classically
estimate expectation values of quantum systems and also to reduce the depths of quantum circuits to
be run on a quantum processor [6]. To learn how to use this package to simulate expectation values of
quantum systems, check out the [tutorial](https://github.com/Qiskit/pauli-prop/tree/main/docs/tutorials/simulate_kicked_ising.ipynb).

This package provides a Rust-accelerated Python interface for performing the most common Pauli
propagation routines.

##### Technical details

- Rust-accelerated Python interface
- Ability to truncate operator terms during evolution based on an absolute coefficient
tolerance, a fixed number of terms in the evolving operator, or a combination of both.
- Ability to perform Pauli propagation in both the Schrödinger and Heisenberg frameworks.
- Novel technique for approximating the conjugation of two Pauli-sum operators. This heuristic
implementation greedily generates contributions to the product expected to be most significant.

##### Computational requirements

Both the memory and time cost for Pauli propagation routines generally scale with the size to which
the evolved operator is allowed to grow.

``propagate_through_rotation_gates``: As the Pauli operator is propagated in the Pauli basis under
the action of a sequence of $N$ Pauli rotation gates of an $M$-qubit circuit, the number of terms
will grow as $\mathcal{O}(2^{N})$ towards a maximum of $4^M$ unique Pauli components. To control
the memory usage, the operator is truncated after application of each gate, which introduces some
error proportional to the magnitudes of the truncated terms' coefficients. The memory requirements
are generally linear in the size of the evolved operator and runtime scales linearly in both the
operator size and the number of gates.

``propagate_through_operator``: Conjugates one operator in the Pauli basis by another by greedily
accumulating terms in the sum, $\sum_{i,j,k}G^{\dagger}_iO_jG_k$, where $i,j,k$ are sparse indices
over the Pauli basis. This implementation sorts the coefficients in each operator by descending
magnitude then searches the 3D index space for the terms with the largest coefficients, starting
with the origin, $(0, 0, 0)$, and accumulating $(i,j,k)$ triplets up to a specified cutoff. The time
spent searching can often be made negligible by increasing the search step size in $(i,j,k)$ space,
which provides a cubic speedup for this subroutine. In our profiling, significant time can be spent
sorting the operators and performing Pauli multiplication to generate the terms in the new operator.

----------------------------------------------------------------------------------------------------

### Documentation

All documentation is available at https://qiskit.github.io/pauli-prop/.

----------------------------------------------------------------------------------------------------

### Installation

We encourage installing this package via `pip`, when possible:

```bash
pip install 'pauli-prop'
```

For more installation information refer to these [installation instructions](docs/install.rst).

----------------------------------------------------------------------------------------------------

### Deprecation Policy

We follow [semantic versioning](https://semver.org/) and are guided by the principles in
[Qiskit's deprecation policy](https://github.com/Qiskit/qiskit/blob/main/DEPRECATION.md).
We may occasionally make breaking changes in order to improve the user experience.
When possible, we will keep old interfaces and mark them as deprecated, as long as they can co-exist with the
new ones.
Each substantial improvement, breaking change, or deprecation will be documented in the
[release notes](https://qiskit.github.io/pauli-prop/release-notes.html).

----------------------------------------------------------------------------------------------------

### Contributing

The source code is available [on GitHub](https://github.com/Qiskit/pauli-prop).

The developer guide is located at [CONTRIBUTING.md](https://github.com/Qiskit/pauli-prop/blob/main/CONTRIBUTING.md)
in the root of this project's repository.
By participating, you are expected to uphold Qiskit's [code of conduct](https://github.com/Qiskit/qiskit/blob/main/CODE_OF_CONDUCT.md).

----------------------------------------------------------------------------------------------------

### License

[Apache License 2.0](LICENSE.txt)

----------------------------------------------------------------------------------------------------

### References

[1] Tomislav Begušić, Johnnie Gray, Garnet Kin-Lic Chan, [Fast and converged classical simulations of evidence for the utility of quantum computing before fault tolerance](https://arxiv.org/abs/2308.05077), arXiv:2308.05077 [quant-ph].

[2] Nicolas Loizeau, et al., [Quantum many-body simulations with PauliStrings.jl](https://arxiv.org/abs/2410.09654), arXiv:2410.09654 [quant-ph].

[3] Manuel S. Rudolph, et al., [Pauli Propagation: A Computational Framework for Simulating Quantum Systems](https://arxiv.org/abs/2505.21606), arXiv:2505.21606 [quant-ph].

[4] Hrant Gharibyan, et al., [A Practical Guide to using Pauli Path Simulators for Utility-Scale Quantum Experiments](https://arxiv.org/abs/2507.10771), arXiv:2507.10771 [quant-ph].

[5] Lukas Broers, et al., [Scalable Simulation of Quantum Many-Body Dynamics with Or-Represented Quantum Algebra](https://arxiv.org/abs/2506.13241), arXiv:2506.13241 [quant-ph].

[6] Bryce Fuller, et al., [Improved Quantum Computation using Operator Backpropagation](https://arxiv.org/abs/2502.01897), arXiv:2502.01897 [quant-ph].
