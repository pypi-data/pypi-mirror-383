# This code is a Qiskit project.
#
# (C) Copyright IBM 2025.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

# Warning: this module is not documented and it does not have an RST file.
# If we ever publicly expose interfaces users can import from this module,
# we should set up its RST file.
"""Primary Pauli propagation functionality."""

from .propagation import (
    RotationGates,
    circuit_to_rotation_gates,
    evolve_through_cliffords,
    propagate_through_circuit,
    propagate_through_operator,
    propagate_through_rotation_gates,
)

__all__ = [
    "RotationGates",
    "circuit_to_rotation_gates",
    "evolve_through_cliffords",
    "propagate_through_circuit",
    "propagate_through_operator",
    "propagate_through_rotation_gates",
]
