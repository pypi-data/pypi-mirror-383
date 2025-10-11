import pytest

try:
    import cupy as cp

    try:
        cp.cuda.Device(0).compute_capability
        use_cupy = True
    except Exception:
        import numpy as cp

        use_cupy = False
except ImportError:
    import numpy as cp

    use_cupy = False

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
from geqo.core.quantum_operation import QuantumOperation
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
from geqo.initialization.state import SetBits, SetDensityMatrix, SetQubits
from geqo.operations.controls import ClassicalControl, QuantumControl
from geqo.operations.measurement import DropQubits, Measure
from geqo.simulators.cupy.implementation import (
    ensembleSimulatorCuPy,
    getUnitaryCuPy,
    mixedStateSimulatorCuPy,
    statevectorSimulatorCuPy,
    unitarySimulatorCuPy,
)

gates = [
    PauliX(),
    PauliY(),
    PauliZ(),
    SwapQubits(),
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
    QuantumControl([0], Ry("a")),
    PermuteQubits([1, 0]),
    QubitReversal(2),
]

op = []
for g in gates:
    if g.getNumberQubits() == 1:
        op.extend([(g, [0], []), (g.getInverse(), [0], [])])
    else:
        op.extend([(g, [0, 1], []), (g.getInverse(), [0, 1], [])])

identity_seq = Sequence([0, 1], [], op)


class TestCuPySimulators:
    def test_get_unitary(self):
        sim = ensembleSimulatorCuPy(2, 0)
        op1 = BasicGate("a", 1)
        op2 = InverseBasicGate("a", 1)
        matrix = cp.array([[1, 0], [0, 1]])

        with pytest.raises(Exception) as exc_info:
            getUnitaryCuPy(op1, sim.values)
        exc = exc_info.value
        assert (
            exc.args[0] == "Parameter " + str(op1.name) + " in BasicGate is undefined."
        )

        with pytest.raises(Exception) as exc_info:
            getUnitaryCuPy(op2, sim.values)
        exc = exc_info.value
        assert (
            exc.args[0]
            == "Parameter " + str(op2.name) + " in InverseBasicGate is undefined."
        )

        sim.setValue("a", matrix)
        u1 = getUnitaryCuPy(op1, sim.values)
        u2 = getUnitaryCuPy(op2, sim.values)

        assert cp.allclose(u1, matrix)
        assert cp.allclose(u2, matrix)

        op1 = Rzz("b")
        op2 = InverseRzz("b")
        sim.setValue("b", 1.23)
        u1 = getUnitaryCuPy(op1, sim.values)
        u2 = getUnitaryCuPy(op2, sim.values)
        assert cp.allclose(u1 @ u2, cp.eye(4, dtype=cp.complex128))

    def test_ensemble_simulator(self):
        nqubits = 3
        ncbits = 2
        sim = ensembleSimulatorCuPy(nqubits, ncbits)
        rho = cp.zeros((2**nqubits, 2**nqubits), dtype=cp.complex128)
        rho[0, 0] = 1

        assert sim.numberBits == ncbits
        assert sim.numberQubits == nqubits

        expected = {(0,) * ncbits: (1, rho)}
        assert sim.ensemble.keys() == expected.keys()
        for key in expected:
            val1, arr1 = sim.ensemble[key]
            val2, arr2 = expected[key]
            assert val1 == val2
            cp.testing.assert_allclose(arr1, arr2)

        assert sim.values == {}
        assert (
            str(sim)
            == "ensembleSimulatorCuPy(" + str(nqubits) + ", " + str(ncbits) + ")"
        )

        sim.setValue("a", 1.23)
        sim.setValue("b", 4.56)
        sim.prepareBackend(
            [QFT(2), InverseQFT(2), PCCM("a"), InversePCCM("b"), Toffoli()]
        )
        assert sim.values == {
            "a": 1.23,
            "b": 4.56,
            "Ph1": cp.pi / 2,
            "RX(π/2)": cp.pi / 2,
            "RX(-π/2)": -cp.pi / 2,
            "RY(-π/2)": -cp.pi / 2,
            "RX(a)": 1.23,
            "RX(b)": 4.56,
            "S.Pi/4": cp.pi / 4,
            "-S.Pi/4": -cp.pi / 4,
        }

        with pytest.raises(Exception) as exc_info:
            sim.prepareBackend([Hadamard()])
        exc = exc_info.value
        assert exc.args[0] == "prepareBackend: operation not supported:"
        assert str(Hadamard()) in exc.args[1]

    def test_ensemble_simulator_classical_control(self):
        nqubits = 2
        ncbits = 2
        sim = ensembleSimulatorCuPy(nqubits, ncbits)
        sim.prepareBackend([QFT(2)])
        seq = Sequence(
            [0, 1],
            [0, 1],
            [
                (Hadamard(), [0], []),
                (Measure(2), [0, 1], [0, 1]),
                (ClassicalControl([1, 0], QFT(2)), [0, 1], [0, 1]),
            ],
        )
        sim.apply(seq, [0, 1], [0, 1])

        expected = {
            (0, 0): (
                0.5,
                cp.array(
                    [
                        [1, 0, 0, 0],
                        [0, 0, 0, 0],
                        [0, 0, 0, 0],
                        [0, 0, 0, 0],
                    ],
                    dtype=cp.complex128,
                ),
            ),
            (1, 0): (
                0.5,
                cp.array(
                    [
                        [
                            1 / 4,
                            -1 / 4,
                            1 / 4,
                            -1 / 4,
                        ],
                        [
                            -1 / 4,
                            1 / 4,
                            -1 / 4,
                            1 / 4,
                        ],
                        [
                            1 / 4,
                            -1 / 4,
                            1 / 4,
                            -1 / 4,
                        ],
                        [
                            -1 / 4,
                            1 / 4,
                            -1 / 4,
                            1 / 4,
                        ],
                    ],
                    dtype=cp.complex128,
                ),
            ),
        }

        assert sim.ensemble.keys() == expected.keys()
        for key in expected:
            val1, arr1 = sim.ensemble[key]
            val2, arr2 = expected[key]
            assert cp.allclose(val1, val2)
            cp.testing.assert_allclose(arr1, arr2)

        with pytest.raises(Exception) as exc_info:
            sim.apply(ClassicalControl([0, 0], Measure(2)), [0, 1], [0, 1])
        exc = exc_info.value
        assert exc.args[0] == "Controlled operations cannot be non-unitary."

        with pytest.raises(Exception) as exc_info:
            sim.apply(
                ClassicalControl([0, 0], Sequence([0], [0], [(Measure(1), [0], [0])])),
                [0, 1],
                [0, 1],
            )
        exc = exc_info.value
        assert exc.args[0] == "Controlled operations cannot be non-unitary."

    def test_ensemble_simulator_unitary(self):
        sim = ensembleSimulatorCuPy(2, 2)
        sim.setValue("a", 0.1)
        sim.apply(identity_seq, [0, 1], [0, 1])
        rho = sim.ensemble[(0, 0)][1]
        # rho = rho.applyfunc(sym.re)
        # rho = np.array(rho.evalf(), dtype=np.float64)
        expect = cp.zeros((4, 4), dtype=cp.complex128)
        expect[0, 0] = 1
        cp.testing.assert_allclose(expect, rho, rtol=1e-7, atol=1e-9)

    def test_ensemble_simulator_non_unitary(self):
        # test setdensitymatix
        sim = ensembleSimulatorCuPy(2, 2)
        op = SetDensityMatrix("d1", 2)
        with pytest.raises(Exception) as exc_info:
            sim.apply(op, [0, 1], [0, 1])
        exc = exc_info.value
        assert (
            exc.args[0]
            == "name of parameter " + str(op.name) + " not known to simulator"
        )

        rho = cp.array(
            [[0.5, 0.5, 0, 0], [0.5, 0.5, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
            dtype=cp.complex128,
        )
        sim.setValue("d1", rho)
        sim.apply(op, [0, 1], [0, 1])
        # assert sim.ensemble[(0, 0)][1] == rho
        cp.testing.assert_allclose(sim.ensemble[(0, 0)][1], rho)

        # test measuring partial qubits
        sim.apply(Measure(1), [0], [0])
        assert float(sim.ensemble[(0, 0)][0]) == 1.0

        # test multiple rounds of measurement
        sim.apply(Measure(2), [0, 1], [0, 1])
        sim.apply(Hadamard(), [1])
        sim.apply(Measure(2), [0, 1], [0, 1])

        # test setbits
        sim.apply(Hadamard(), [0])
        sim.apply(Measure(2), [0, 1], [0, 1])
        op = SetBits("sb", 1)
        with pytest.raises(Exception) as exc_info:
            sim.apply(op, [], [0])
        exc = exc_info.value
        assert (
            exc.args[0]
            == "name of parameter " + str(op.name) + " not known to simulator"
        )

        sim.setValue("sb", [1])
        sim.apply(op, [], [0])
        for key in list(sim.ensemble.keys()):
            assert key[0] == 1

        # test setqubits
        op = SetQubits("sq", 2)
        with pytest.raises(Exception) as exc_info:
            sim.apply(op, [0, 1], [0, 1])
        exc = exc_info.value
        assert (
            exc.args[0]
            == "name of parameter " + str(op.name) + " not known to simulator"
        )

        sim.setValue("sq", [1, 0])
        sim.apply(op, [0, 1])
        rho = cp.zeros((4, 4), dtype=cp.complex128)
        rho[2, 2] = 1
        for key, item in sim.ensemble.items():
            # s = np.array(item[1].evalf(), dtype=np.float64)
            s = item[1]
            cp.testing.assert_allclose(s, rho, rtol=1e-7, atol=1e-9)

        # test dropqubits
        sim.apply(DropQubits(1), [0])
        assert sim.numberQubits == 1
        assert sim.ensemble[(1, 1)][1].shape == (2, 2)

        # test unknown operation
        class MockOperation(QuantumOperation):
            def __init__(self):
                super().__init__()

            def __repr__(self):
                return "MockOp"

            def __eq__(self, other):
                if not isinstance(other, MockOperation):
                    return False
                else:
                    return True

            def getInverse(self):
                return self

            def getEquivalentSequence(self):
                return None

            def isUnitary(self):
                return False

            def hasDecomposition(self):
                return False

            def getNumberQubits(self):
                return 1

            def getNumberClassicalBits(self):
                return 0

        op = MockOperation()
        with pytest.raises(Exception) as exc_info:
            sim.apply(op, [0, 1], [0, 1])
        exc = exc_info.value
        assert exc.args[0] == f"gate not implemented for ensembleSimulatorCuPy: {op}"
        # assert exc.args[1] == op

    def test_mixedstate_simulator(self):
        nqubits = 3
        ncbits = 2
        sim = mixedStateSimulatorCuPy(nqubits, ncbits, return_density=True)
        rho = cp.zeros((2**nqubits, 2**nqubits), dtype=cp.complex128)
        rho[0, 0] = 1

        assert sim.numberBits == ncbits
        assert sim.numberQubits == nqubits
        # assert sim.densityMatrix == rho
        cp.testing.assert_allclose(sim.densityMatrix, rho)
        assert sim.return_density
        assert sim.values == {}
        assert (
            str(sim)
            == "mixedStateSimulatorCuPy(" + str(nqubits) + ", " + str(ncbits) + ")"
        )

        sim.setValue("a", 1.23)
        sim.setValue("b", 4.56)
        sim.prepareBackend(
            [QFT(2), InverseQFT(2), PCCM("a"), InversePCCM("b"), Toffoli()]
        )
        assert sim.values == {
            "a": 1.23,
            "b": 4.56,
            "Ph1": cp.pi / 2,
            "RX(π/2)": cp.pi / 2,
            "RX(-π/2)": -cp.pi / 2,
            "RY(-π/2)": -cp.pi / 2,
            "RX(a)": 1.23,
            "RX(b)": 4.56,
            "S.Pi/4": cp.pi / 4,
            "-S.Pi/4": -cp.pi / 4,
        }

        with pytest.raises(Exception) as exc_info:
            sim.prepareBackend([Hadamard()])
        exc = exc_info.value
        assert exc.args[0] == "prepareBackend: operation not supported:"
        assert str(Hadamard()) in exc.args[1]

    def test_mixedstate_simulator_unitary(self):
        sim = mixedStateSimulatorCuPy(2, 2)
        sim.setValue("a", 0.1)
        sim.apply(identity_seq, [0, 1], [0, 1])
        rho = sim.densityMatrix
        # rho = rho.applyfunc(sym.re)
        # rho = np.array(rho.evalf(), dtype=np.float64)
        expect = cp.zeros((4, 4), dtype=cp.complex128)
        expect[0, 0] = 1
        cp.testing.assert_allclose(expect, rho, rtol=1e-7, atol=1e-9)

    def test_mixedstate_simulator_non_unitary(self):
        # test setdensitymatix
        sim = mixedStateSimulatorCuPy(2, 2, return_density=True)
        op = SetDensityMatrix("d1", 2)
        with pytest.raises(Exception) as exc_info:
            sim.apply(op, [0, 1], [0, 1])
        exc = exc_info.value
        assert (
            exc.args[0]
            == "name of parameter " + str(op.name) + " not known to simulator"
        )

        rho = cp.array(
            [[0.5, 0.5, 0, 0], [0.5, 0.5, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
            dtype=cp.complex128,
        )
        sim.setValue("d1", rho)
        sim.apply(op, [0, 1], [0, 1])
        # assert sim.densityMatrix == rho
        cp.testing.assert_allclose(sim.densityMatrix, rho)

        # test measuring partial qubits
        sim.apply(Measure(1), [0], [0])
        assert float(sim.measureHistory[0][(0,)]) == 1.0

        # test multiple rounds of measurement
        sim.apply(Measure(2), [0, 1], [0, 1])
        sim.apply(Hadamard(), [1])
        sim.apply(Measure(2), [0, 1], [0, 1])

        rho = cp.zeros((4, 4), dtype=cp.complex128)
        rho[0, 0] = 0.5
        rho[1, 1] = 0.5
        # s = np.array(sim.densityMatrix.evalf(), dtype=np.float64)
        s = sim.densityMatrix
        cp.testing.assert_allclose(s, rho, rtol=1e-7, atol=1e-9)
        # s2 = np.array(sim.measureHistory[-1]["mixed_state"].evalf(), dtype=np.float64)
        s2 = sim.measureHistory[-1]["mixed_state"]
        cp.testing.assert_allclose(s2, rho, rtol=1e-7, atol=1e-9)

        # test setbits
        sim.apply(Hadamard(), [0])
        sim.apply(Measure(2), [0, 1], [0, 1])
        op = SetBits("sb", 1)
        with pytest.raises(Exception) as exc_info:
            sim.apply(op, [], [0])
        exc = exc_info.value
        assert exc.args[0] == "SetBits not supported by this simulator"

        # test setqubits
        op = SetQubits("sq", 2)
        with pytest.raises(Exception) as exc_info:
            sim.apply(op, [0, 1], [0, 1])
        exc = exc_info.value
        assert (
            exc.args[0]
            == "name of parameter " + str(op.name) + " not known to simulator"
        )

        sim.setValue("sq", [1, 0])
        sim.apply(op, [0, 1])
        rho = cp.zeros((4, 4), dtype=cp.complex128)
        rho[2, 2] = 1
        # s = np.array(sim.densityMatrix.evalf(), dtype=np.float64)
        s = sim.densityMatrix
        cp.testing.assert_allclose(s, rho, rtol=1e-7, atol=1e-9)

        # test dropqubits
        sim.apply(DropQubits(1), [0])
        assert sim.numberQubits == 1
        assert sim.densityMatrix.shape == (2, 2)

        # test unknown operation
        class MockOperation(QuantumOperation):
            def __init__(self):
                super().__init__()

            def __repr__(self):
                return "MockOp"

            def __eq__(self, other):
                if not isinstance(other, MockOperation):
                    return False
                else:
                    return True

            def getInverse(self):
                return self

            def getEquivalentSequence(self):
                return None

            def isUnitary(self):
                return False

            def hasDecomposition(self):
                return False

            def getNumberQubits(self):
                return 1

            def getNumberClassicalBits(self):
                return 0

        op = MockOperation()
        with pytest.raises(Exception) as exc_info:
            sim.apply(op, [0, 1], [0, 1])
        exc = exc_info.value
        assert exc.args[0] == f"gate not implemented for mixedStateSimulatorCuPy: {op}"
        # assert exc.args[1] == op

    def test_new_unitary_simulator(self):
        nqubits = 2
        sim = unitarySimulatorCuPy(nqubits)
        u = cp.eye(2**nqubits, dtype=cp.complex128)

        assert sim.numberQubits == nqubits
        # assert sim.u == u
        cp.testing.assert_allclose(sim.u, u)
        assert sim.values == {}
        assert str(sim) == "unitarySimulatorCuPy(" + str(nqubits) + ")"

        sim.setValue("a", 1.23)
        sim.setValue("b", 4.56)
        sim.prepareBackend(
            [QFT(2), InverseQFT(2), PCCM("a"), InversePCCM("b"), Toffoli()]
        )
        assert sim.values == {
            "a": 1.23,
            "b": 4.56,
            "Ph1": cp.pi / 2,
            "RX(π/2)": cp.pi / 2,
            "RX(-π/2)": -cp.pi / 2,
            "RY(-π/2)": -cp.pi / 2,
            "RX(a)": 1.23,
            "RX(b)": 4.56,
            "S.Pi/4": cp.pi / 4,
            "-S.Pi/4": -cp.pi / 4,
        }

        with pytest.raises(Exception) as exc_info:
            sim.prepareBackend([Hadamard()])
        exc = exc_info.value
        assert exc.args[0] == "prepareBackend: operation not supported:"
        assert str(Hadamard()) in exc.args[1]

        sim.setValue("a", 0.1)
        sim.apply(identity_seq, [0, 1])
        expect = cp.eye(4, dtype=cp.complex128)
        # s = np.array(sim.u, dtype=np.float64)
        s = sim.u
        cp.testing.assert_allclose(expect, s, rtol=1e-7, atol=1e-9)

        class MockOperation(QuantumOperation):
            def __init__(self):
                super().__init__()

            def __repr__(self):
                return "MockOp"

            def __eq__(self, other):
                if not isinstance(other, MockOperation):
                    return False
                else:
                    return True

            def getInverse(self):
                return self

            def getEquivalentSequence(self):
                return None

            def isUnitary(self):
                return False

            def hasDecomposition(self):
                return False

            def getNumberQubits(self):
                return 1

            def getNumberClassicalBits(self):
                return 0

        op = MockOperation()
        with pytest.raises(Exception) as exc_info:
            sim.apply(op, [0, 1])
        exc = exc_info.value
        assert exc.args[0] == f"gate not implemented for unitarySimulatorCuPy: {op}"
        # assert exc.args[1] == op

    def test_statevector_simulator(self):
        nqubits = 3
        ncbits = 2
        sim = statevectorSimulatorCuPy(nqubits, ncbits)
        state = cp.zeros(shape=(2**nqubits, 1), dtype=cp.complex128)
        state[0, 0] = 1.0 + 0 * 1j

        assert sim.numberBits == ncbits
        assert sim.numberQubits == nqubits
        assert cp.array_equal(sim.state, state)
        assert sim.measurementResult == {}
        assert not sim.measurementHappened
        assert sim.values == {}
        for i in range(ncbits):
            assert sim.classicalBits[i] == 0
        assert (
            str(sim)
            == "statevectorSimulatorCuPy(" + str(nqubits) + ", " + str(ncbits) + ")"
        )

        with pytest.raises(
            NotImplementedError,
            match="Too many qubits, limit is 32",
        ):
            sim_fail = statevectorSimulatorCuPy(33, 33)
            sim_fail.numberBits = 0

        sim.setValue("a", 1.23)
        # b = 2.34
        sim.prepareBackend(
            [QFT(2), InverseQFT(2), PCCM("a"), InversePCCM("b"), Toffoli()]
        )
        assert sim.values == {
            "a": 1.23,
            "Ph1": cp.pi / 2,
            "RX(π/2)": cp.pi / 2,
            "RX(-π/2)": -cp.pi / 2,
            "RY(-π/2)": -cp.pi / 2,
            "RX(a)": 1.23,
            # "RX(b)": b,
            "S.Pi/4": cp.pi / 4,
            "-S.Pi/4": -cp.pi / 4,
        }

        with pytest.raises(Exception) as exc_info:
            sim.prepareBackend([Hadamard()])
        exc = exc_info.value
        assert exc.args[0] == "prepareBackend: operation not supported:"
        assert str(Hadamard()) in exc.args[1]

    def test_statevector_simulator_unitary(self):
        sim = statevectorSimulatorCuPy(2, 0)
        sim.setValue("a", 0.1)
        matrix = cp.array([[1, 0], [0, 1]], dtype=cp.complex128)
        sim.setValue("b", matrix)
        sim.apply(identity_seq, [0, 1])
        state = sim.state
        expect = cp.array([1.0, 0.0, 0.0, 0.0], dtype=cp.complex128).reshape(4, 1)
        assert cp.allclose(expect, state)

    def test_statevector_simulator_non_unitary(self):
        # test Measure
        sim = statevectorSimulatorCuPy(2, 2)
        with pytest.raises(
            ValueError,
            match="Number of targets does not match number of measured qubits",
        ):
            sim.apply(Measure(3), [0, 1], [0, 1])
        # with pytest.raises(Exception) as exc_info:
        #    sim.apply(Measure(2), [0, 1], [0, 1])
        # exc = exc_info.value
        # assert exc.args[0] == "quantum control of measurement not supported"

        sim.apply(Hadamard(), [0])
        sim.apply(Measure(2), [0, 1], [0, 1])

        assert sim.measurementHappened
        assert cp.allclose(sim.measurementResult[(0, 0)], 0.5)
        assert cp.allclose(sim.measurementResult[(1, 0)], 0.5)

        # test SetBits
        setbit = SetBits("sb", 1)
        with pytest.raises(Exception) as exc_info:
            sim.apply(setbit, [], [0])
        exc = exc_info.value
        assert exc.args[0] == "no more operation allowed after measurement"

        sim = sim = statevectorSimulatorCuPy(2, 2)
        with pytest.raises(
            ValueError,
            match=f'Bit values "{setbit.name}" not found',
        ):
            sim.apply(setbit, [], [0])

        sim.setValue("sb", [1])
        with pytest.raises(
            ValueError,
            match="wrong number of bits in definition for SetBits",
        ):
            sim.apply(setbit, [], [0, 1])

        sim.apply(setbit, [], [0])
        assert sim.classicalBits[0] == 1
        assert sim.classicalBits[1] == 0

        # test SetQubits
        setqubits = SetQubits("sq", 1)
        with pytest.raises(Exception) as exc_info:
            sim.apply(setqubits, [0])
        exc = exc_info.value
        assert exc.args[0] == "cannot set qubits in statevector simulations"

        # test DropQubits
        dropqubits = DropQubits(1)
        with pytest.raises(Exception) as exc_info:
            sim.apply(dropqubits, [0])
        exc = exc_info.value
        assert exc.args[0] == "cannot drop qubits in statevector simulations"

        # test SetDensityMatrix
        setden = SetDensityMatrix("sd", 1)
        with pytest.raises(Exception) as exc_info:
            sim.apply(setden, [0])
        exc = exc_info.value
        assert exc.args[0] == "cannot set density matrix in statevector simulations"

        # test ClassicalControl
        setden = ClassicalControl([1], Hadamard())
        with pytest.raises(Exception) as exc_info:
            sim.apply(setden, [1], [0])
        exc = exc_info.value
        assert (
            exc.args[0] == "cannot perform ClassicalControl in statevectorSimulatorCuPy"
        )

        # test unknown operation
        class MockOperation(QuantumOperation):
            def __init__(self):
                super().__init__()

            def __repr__(self):
                return "MockOp"

            def __eq__(self, other):
                if not isinstance(other, MockOperation):
                    return False
                else:
                    return True

            def getInverse(self):
                return self

            def getEquivalentSequence(self):
                return None

            def isUnitary(self):
                return False

            def hasDecomposition(self):
                return False

            def getNumberQubits(self):
                return 1

            def getNumberClassicalBits(self):
                return 0

        op = MockOperation()
        with pytest.raises(Exception) as exc_info:
            sim.apply(op, [0, 1], [0, 1])
        exc = exc_info.value
        assert exc.args[0] == f"gate not supported: {str(op)}"
        # assert exc.args[1] == str(op)
