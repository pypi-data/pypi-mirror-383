# Copyright (c) 2021-2025, NVIDIA CORPORATION & AFFILIATES
#
# SPDX-License-Identifier: BSD-3-Clause


import importlib
import numpy as np

import cirq
from cirq import protocols, unitary, Circuit, MeasurementGate

from .helpers import _get_backend_asarray_func, get_dtype_name

def remove_measurements(circuit):
    """
    Return a circuit with final measurement operations removed
    """
    circuit = circuit.copy()
    if circuit.has_measurements():
        if not circuit.are_all_measurements_terminal():
            raise ValueError('mid-circuit measurement not supported in tensor network simulation')
        else:
            predicate = lambda operation: isinstance(operation.gate, MeasurementGate)
            measurement_gates = list(circuit.findall_operations(predicate))
            circuit.batch_remove(measurement_gates)
    return circuit

def get_inverse_circuit(circuit):
    """
    Return a circuit with all gate operations inversed
    """
    return protocols.inverse(circuit)

def unfold_circuit(circuit, backend, dtype, check_diagonal=True, **kwargs):
    """
    Unfold the circuit to obtain the qubits and all gate tensors.

    Args:
        circuit: A :class:`cirq.Circuit` object. All parameters in the circuit must be resolved.
        dtype: Data type for the tensor operands.
        backend: The package the tensor operands belong to.

    Returns:
        All qubits and gate operations from the input circuit
    """
    qubits = sorted(circuit.all_qubits())
    package = importlib.import_module(backend)
    asarray = _get_backend_asarray_func(package)
    gates = []
    gates_are_diagonal = []
    for moment in circuit.moments:
        for operation in moment:
            gate_qubits = operation.qubits
            operand = unitary(operation.gate)
            if check_diagonal:
                gates_are_diagonal.append(cirq.is_diagonal(operand, atol=1e-14))
            else:
                gates_are_diagonal.append(False)
            tensor = operand.reshape((2,) * 2 * len(gate_qubits))
            if get_dtype_name(dtype).startswith("float"):
                if not np.isreal(tensor).all():
                    imag_max = abs(tensor.imag).max()
                    raise RuntimeError(f"gate operand found to have imaginary part {imag_max=} while real dtype {dtype} is specified")
                tensor = tensor.real
            tensor = asarray(tensor, dtype=dtype)
            gates.append((tensor, operation.qubits))
    return qubits, gates, gates_are_diagonal

def get_lightcone_circuit(circuit, coned_qubits):
    """
    Use unitary reversed lightcone cancellation technique to reduce the effective circuit size based on the qubits to be coned. 

    Args:
        circuit: A :class:`cirq.Circuit` object. 
        coned_qubits: An iterable of qubits to be coned.

    Returns:
        A :class:`cirq.Circuit` object that potentially contains less number of gates
    """
    coned_qubits = set(coned_qubits)
    all_operations = list(circuit.all_operations())
    n_qubits = len(circuit.all_qubits())
    ix = len(all_operations)
    tail_operations = []
    while len(coned_qubits) != n_qubits and ix>0:
        ix -= 1
        operation = all_operations[ix]
        qubit_set = set(operation.qubits)
        if qubit_set & coned_qubits:
            tail_operations.append(operation)
            coned_qubits |= qubit_set
    newqc = Circuit(all_operations[:ix]+tail_operations[::-1])
    return newqc
