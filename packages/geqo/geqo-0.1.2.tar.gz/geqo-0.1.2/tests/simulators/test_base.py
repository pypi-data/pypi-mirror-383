import re

import pytest
from sympy import Symbol

from geqo.algorithms.algorithms import (
    PCCM,
    QFT,
    InversePCCM,
    InverseQFT,
    PermuteQubits,
    QubitReversal,
)
from geqo.core.basic import BasicGate, InverseBasicGate
from geqo.core.quantum_circuit import Sequence
from geqo.gates.fundamental_gates import (
    CNOT,
    Hadamard,
    InversePhase,
    InverseSGate,
    PauliX,
    PauliY,
    PauliZ,
    Phase,
    SGate,
    SwapQubits,
)
from geqo.gates.multi_qubit_gates import Toffoli
from geqo.gates.rotation_gates import (
    InverseRx,
    InverseRy,
    InverseRz,
    InverseRzz,
    Rx,
    Ry,
    Rz,
    Rzz,
)
from geqo.initialization.state import SetBits, SetQubits
from geqo.operations.controls import ClassicalControl, QuantumControl
from geqo.operations.measurement import Measure
from geqo.simulators.base import BaseQASM, Simulator, printer, sequencer
from geqo.simulators.numpy.implementation import simulatorStatevectorNumpy
from geqo.simulators.sympy.implementation import ensembleSimulatorSymPy

gates = [
    # BasicGate("b", 1),
    # InverseBasicGate("b", 1),
    PauliX(),
    PauliY(),
    PauliZ(),
    Hadamard(),
    Phase("a"),
    InversePhase("a"),
    CNOT(),
    SGate(),
    InverseSGate(),
    Rx("a"),
    Ry("a"),
    Rz("a"),
    Rzz("a"),
    InverseRx("a"),
    InverseRy("a"),
    InverseRz("a"),
    InverseRzz("a"),
    SwapQubits(),
    QuantumControl([0], Ry("a")),
    PermuteQubits([1, 0]),
    QubitReversal(2),
    QFT(2),
    InverseQFT(2),
    PCCM("a"),
    InversePCCM("a"),
    SetQubits("sq", 1),
    Toffoli(),
]

qctrl_gates = [QuantumControl([1], gates[i]) for i in range(17)]
gates.extend(qctrl_gates)

op = []
for g in gates:
    if g.getNumberQubits() == 1:
        op.append((g, [0], []))
    elif g.getNumberQubits() == 2:
        op.append((g, [0, 1], []))
    else:
        op.append((g, [0, 1, 2], []))


class DummySimulator(Simulator):
    def __init__(self):
        pass

    def __repr__(self):
        return "DummySimulator"

    def apply(self):
        return "applied"


class TestBase:
    def test_abstract_methods(self):
        # Verify all required abstract methods exist
        assert hasattr(Simulator, "__init__")
        assert hasattr(Simulator, "__repr__")
        assert hasattr(Simulator, "apply")

    def test_simulator(self):
        with pytest.raises(
            TypeError, match="Can't instantiate abstract class Simulator"
        ):
            Simulator()

    def test_dummy_simulator_instantiation(self):
        sim = DummySimulator()
        assert repr(sim) == "DummySimulator"
        assert sim.apply() == "applied"

    def test_sequencer(self):
        nbits = 2
        nqubits = 3
        sim = sequencer(nqubits, nbits)

        assert sim.numberBits == nbits
        assert sim.numberQubits == nqubits
        assert sim.seq == []
        assert str(sim) == "sequencer (#steps so far: " + str(len(sim.seq)) + ")"

        sim.apply(Hadamard(), [0])
        sim.apply(Rx("a"), [1])
        sim.apply(SGate(), [2])
        sim.apply(Measure(2), [0, 1], [0, 1])

        assert str(sim) == "sequencer (#steps so far: " + str(len(sim.seq)) + ")"
        assert sim.seq == [
            [Hadamard(), [0], []],
            [Rx("a"), [1], []],
            [SGate(), [2], []],
            [Measure(2), [0, 1], [0, 1]],
        ]

        sequence = Sequence(
            [0, 1, 2],
            [0, 1],
            [
                [Hadamard(), [0], []],
                [Rx("a"), [1], []],
                [SGate(), [2], []],
                [Measure(2), [0, 1], [0, 1]],
            ],
        )
        assert sim.getSequence() == sequence

    def test_printer(self):
        nqubits = 3
        nbits = 2
        sim = printer(nqubits, nbits)
        assert sim.numberQubits == nqubits
        assert sim.numberBits == nbits
        assert sim.steps == 0

        assert str(sim) == "printer (#steps so far: " + str(sim.steps) + ")"

        sim.apply(Hadamard(), [0])
        sim.apply(Rx("a"), [1])
        sim.apply(SGate(), [2])
        sim.apply(Measure(2), [0, 1])

        assert sim.steps == 4

    def test_base_qasm(self):
        values = {"a": 1}
        qasm = BaseQASM(values)

        assert qasm.values == values
        assert (
            str(qasm)
            == "QASM3 converter initialized."
            + f"Parameters queried from values dictionary: {values}"
        )

        seq = Sequence([0, 1, 2], [0, 1, 2], [(Rx("a"), [0], [])])

        qasm.apply(seq)
        qasm.sequence_to_qasm3(seq)

    def test_sequence_to_qasm(self):
        sim = ensembleSimulatorSymPy(3, 3)

        angles = [
            Phase("a"),
            InversePhase("a"),
            Rx("a"),
            Ry("a"),
            Rz("a"),
            Rzz("a"),
            InverseRx("a"),
            InverseRy("a"),
            InverseRz("a"),
            InverseRzz("a"),
        ]

        qctrl_angles = [QuantumControl([1], angles[i]) for i in range(len(angles))]
        angles.extend(qctrl_angles)
        angles.append(SetQubits("sq", 1))

        for angle in angles:
            name = (
                angle.name if not isinstance(angle, QuantumControl) else angle.qop.name
            )
            if isinstance(angle, SetQubits):
                message = f"Cannot fetch SetQubits values {name} from the backend."
            else:
                message = f"Cannot fetch phase angle {name} from the backend."
            with pytest.raises(
                ValueError,
                match=re.escape(message),
            ):
                n = angle.getNumberQubits()
                seq = Sequence([0, 1, 2], [0, 1, 2], [(angle, [*range(n)], [])])
                sim.sequence_to_qasm3(seq)

        with pytest.raises(
            NotImplementedError,
            match=re.escape(f"Unsupported gate/operation: {SetBits('sb', 1)}"),
        ):
            seq = Sequence([0, 1, 2], [0, 1, 2], [(SetBits("sb", 1), [], [0])])
            sim.sequence_to_qasm3(seq)

        # test sympy simulator
        sim.setValue("a", Symbol("a"))
        sim.setValue("sq", [1])
        sim.prepareBackend(
            [QFT(2), InverseQFT(2), PCCM("a"), InversePCCM("a"), Toffoli()]
        )
        op.append(
            (ClassicalControl([1], QuantumControl([1], Rzz("a"))), [2, 0, 1], [1])
        )
        op.append((QuantumControl([0, 1], PauliX()), [0, 1, 2], []))
        op.append((ClassicalControl([1], Hadamard()), [2], [1]))
        op.append((Measure(3), [0, 1, 2], [0, 1, 2]))
        seq = Sequence([0, 1, 2], [0, 1, 2], op)

        code = sim.sequence_to_qasm3(seq)
        expected = "OPENQASM 3.0; \ninclude 'stdgates.inc';\ngate rzz(theta) a, b {\n                cx a, b;\n                rz(theta) b;\n                cx a, b;\n            }\ninput float a;\nqubit[3] q;\nbit[3] c;\nx q[0];\ny q[0];\nz q[0];\nh q[0];\np(a) q[0];\np(-a) q[0];\ncx q[0], q[1];\ns q[0];\nsdg q[0];\nrx(a) q[0];\nry(a) q[0];\nrz(a) q[0];\nrzz(a) q[0], q[1];\nrx(-a) q[0];\nry(-a) q[0];\nrz(-a) q[0];\nrzz(-a) q[0], q[1];\nswap q[0], q[1];\nx q[0];\nctrl(1) @ ry(a) q[0], q[1];\nx q[0];\nswap q[0], q[1];\nswap q[0], q[1];\nh q[0];\nctrl(1) @ p(1.5707963267948966) q[1], q[0];\nh q[1];\nswap q[0], q[1];\nswap q[0], q[1];\nh q[1];\nctrl(1) @ p(-1.5707963267948966) q[1], q[0];\nh q[0];\nrx(1.5707963267948966) q[0];\nrx(1.5707963267948966) q[1];\nctrl(1) @ rx(a) q[0], q[1];\nctrl(1) @ rx(-1.5707963267948966) q[1], q[0];\nrx(-1.5707963267948966) q[0];\nry(-1.5707963267948966) q[1];\nry(--1.5707963267948966) q[1];\nrx(--1.5707963267948966) q[0];\nctrl(1) @ rx(--1.5707963267948966) q[1], q[0];\nctrl(1) @ rx(-a) q[0], q[1];\nrx(-1.5707963267948966) q[1];\nrx(-1.5707963267948966) q[0];\nreset q[0];\nx q[0];\nccx q[0], q[1], q[2];\nctrl(1) @ x q[0], q[1];\nctrl(1) @ y q[0], q[1];\nctrl(1) @ z q[0], q[1];\nctrl(1) @ h q[0], q[1];\nctrl(1) @ p(a) q[0], q[1];\nctrl(1) @ p(-a) q[0], q[1];\nctrl(1) @ cx q[0], q[1], q[2];\nctrl(1) @ s q[0], q[1];\nctrl(1) @ sdg q[0], q[1];\nctrl(1) @ rx(a) q[0], q[1];\nctrl(1) @ ry(a) q[0], q[1];\nctrl(1) @ rz(a) q[0], q[1];\nctrl(1) @ rzz(a) q[0], q[1], q[2];\nctrl(1) @ rx(-a) q[0], q[1];\nctrl(1) @ ry(-a) q[0], q[1];\nctrl(1) @ rz(-a) q[0], q[1];\nctrl(1) @ rzz(-a) q[0], q[1], q[2];\nif (c[1] == true) {\n    ctrl(1) @ rzz(a) q[2], q[0], q[1];\n}\nx q[0];\nctrl(2) @ x q[0], q[1], q[2];\nx q[0];\nif (c[1] == true) {\n    h q[2];\n}\nmeasure q[0] -> c[0];\nmeasure q[1] -> c[1];\nmeasure q[2] -> c[2];"
        assert code == expected

        # test numpy simulator
        sim = simulatorStatevectorNumpy(3, 3)
        sim.setValue("a", 1.23)

        op2 = []
        op2.append(
            (ClassicalControl([1], QuantumControl([1], Rzz("a"))), [2, 0, 1], [1])
        )
        op2.append((ClassicalControl([1], Rzz("a")), [2, 0], [1]))
        op2.append((ClassicalControl([1], QuantumControl([1], SGate())), [2, 0], [1]))
        seq = Sequence([0, 1, 2], [0, 1, 2], op2)

        code = sim.sequence_to_qasm3(seq)
        expected = "OPENQASM 3.0; \ninclude 'stdgates.inc';\ngate rzz(theta) a, b {\n                cx a, b;\n                rz(theta) b;\n                cx a, b;\n            }\nqubit[3] q;\nbit[3] c;\nif (c[1] == true) {\n    ctrl(1) @ rzz(1.23) q[2], q[0], q[1];\n}\nif (c[1] == true) {\n    rzz(1.23) q[2], q[0];\n}\nif (c[1] == true) {\n    ctrl(1) @ s q[2], q[0];\n}"
        assert code == expected

        # test BasicGate
        sim = simulatorStatevectorNumpy(3, 1)
        op3 = [
            (BasicGate("a", 2), ["a", "b"], ["1"]),
            (QuantumControl([1], BasicGate("a", 2)), ["c", "b", "a"], []),
            (ClassicalControl([0], BasicGate("a", 2)), [1, 0], ["1"]),
            (
                ClassicalControl([1], QuantumControl([0], InverseBasicGate("b", 1))),
                [0, 2],
                [0],
            ),
            (PauliX(), ["b"], []),
        ]

        seq = Sequence(["a", "b", "c"], ["1"], op3)

        ua = [[0, 0, 0, 1], [0, 0, 1, 0], [0, 1, 0, 0], [1, 0, 0, 0]]
        s = 0.5**0.5
        ub = [[s, s], [s, -s]]
        sim.setValue("a", ua)
        sim.setValue("b", ub)
        code = sim.sequence_to_qasm3(seq)
        expected = "OPENQASM 3.0; \ninclude 'stdgates.inc';\nqubit[3] q;\nbit[1] c;\ncx q[0], q[1];\nx q[1];\nctrl(1) @ rz(-3.141592653589793) q[1], q[0];\nx q[1];\nx q[1];\nctrl(1) @ ry(3.141592653589793) q[1], q[0];\nx q[1];\nx q[1];\nctrl(1) @ rz(3.141592653589793) q[1], q[0];\nx q[1];\nx q[1];\nctrl(1) @ p(-3.141592653589793) q[1], q[0];\nx q[1];\ncx q[0], q[1];\ncx q[0], q[1];\nctrl(1) @ rz(-3.141592653589793) q[1], q[0];\nctrl(1) @ ry(3.141592653589793) q[1], q[0];\nctrl(1) @ rz(3.141592653589793) q[1], q[0];\nctrl(1) @ p(-3.141592653589793) q[1], q[0];\ncx q[0], q[1];\nctrl(1) @ cx q[2], q[1], q[0];\nx q[0];\nctrl(2) @ rz(-3.141592653589793) q[2], q[0], q[1];\nx q[0];\nx q[0];\nctrl(2) @ ry(3.141592653589793) q[2], q[0], q[1];\nx q[0];\nx q[0];\nctrl(2) @ rz(3.141592653589793) q[2], q[0], q[1];\nx q[0];\nx q[0];\nctrl(2) @ p(-3.141592653589793) q[2], q[0], q[1];\nx q[0];\nctrl(1) @ cx q[2], q[1], q[0];\nctrl(1) @ cx q[2], q[1], q[0];\nctrl(2) @ rz(-3.141592653589793) q[2], q[0], q[1];\nctrl(2) @ ry(3.141592653589793) q[2], q[0], q[1];\nctrl(2) @ rz(3.141592653589793) q[2], q[0], q[1];\nctrl(2) @ p(-3.141592653589793) q[2], q[0], q[1];\nctrl(1) @ cx q[2], q[1], q[0];\nif (c[0] == false) {\n    cx q[1], q[0];\n}\nif (c[0] == false) {\n    x q[0];\nctrl(1) @ rz(-3.141592653589793) q[0], q[1];\nx q[0];\n}\nif (c[0] == false) {\n    x q[0];\nctrl(1) @ ry(3.141592653589793) q[0], q[1];\nx q[0];\n}\nif (c[0] == false) {\n    x q[0];\nctrl(1) @ rz(3.141592653589793) q[0], q[1];\nx q[0];\n}\nif (c[0] == false) {\n    x q[0];\nctrl(1) @ p(-3.141592653589793) q[0], q[1];\nx q[0];\n}\nif (c[0] == false) {\n    cx q[1], q[0];\n}\nif (c[0] == false) {\n    cx q[1], q[0];\n}\nif (c[0] == false) {\n    ctrl(1) @ rz(-3.141592653589793) q[0], q[1];\n}\nif (c[0] == false) {\n    ctrl(1) @ ry(3.141592653589793) q[0], q[1];\n}\nif (c[0] == false) {\n    ctrl(1) @ rz(3.141592653589793) q[0], q[1];\n}\nif (c[0] == false) {\n    ctrl(1) @ p(-3.141592653589793) q[0], q[1];\n}\nif (c[0] == false) {\n    cx q[1], q[0];\n}\nif (c[0] == true) {\n    x q[0];\nctrl(1) @ rz(-3.141592653589793) q[0], q[2];\nx q[0];\n}\nif (c[0] == true) {\n    x q[0];\nctrl(1) @ ry(1.5707963267948966) q[0], q[2];\nx q[0];\n}\nif (c[0] == true) {\n    x q[0];\nctrl(1) @ rz(3.141592653589793) q[0], q[2];\nx q[0];\n}\nif (c[0] == true) {\n    x q[0];\nctrl(1) @ p(-3.141592653589793) q[0], q[2];\nx q[0];\n}\nx q[1];"
        assert code == expected
