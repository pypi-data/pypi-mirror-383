from abc import abstractmethod

import numpy  # some functions still use numpy to avoid GPU overhead

from geqo.__logger__ import get_logger
from geqo.algorithms import PCCM, QFT, InversePCCM, InverseQFT, PermuteQubits
from geqo.core import BasicGate, InverseBasicGate, Sequence
from geqo.core.quantum_operation import QuantumOperation
from geqo.gates import (
    CNOT,
    Hadamard,
    InversePhase,
    InverseRx,
    InverseRy,
    InverseRz,
    InverseRzz,
    InverseSGate,
    PauliX,
    PauliY,
    PauliZ,
    Phase,
    Rx,
    Ry,
    Rz,
    Rzz,
    SGate,
    SwapQubits,
    Toffoli,
)
from geqo.initialization import SetBits, SetDensityMatrix, SetQubits
from geqo.operations import ClassicalControl, DropQubits, Measure, QuantumControl
from geqo.simulators.base import BaseQASM
from geqo.utils import (
    bin2num,
    getQFTCuPy,
    getRXCupy,
    getRYCupy,
    multiQubitsUnitaryCupy,
    partial_diag_cupy,
    partialTraceCupy,
    permutationMatrixCupy,
    projection_cupy,
)

logger = get_logger(__name__)

try:
    import cupy as cp

    try:
        cp.cuda.Device(0).compute_capability
        use_cupy = True
        logger.info("GPU available. CuPy is used ")
    except Exception:
        import numpy as cp

        use_cupy = False
        logger.info("no GPU available. NumPy is used ")
except ImportError:
    import numpy as cp

    use_cupy = False
    logger.info("CuPy not installed. NumPy is used ")


def getUnitaryCuPy(gate: QuantumOperation, values: dict) -> cp.ndarray:
    if isinstance(gate, BasicGate):
        if gate.name not in values:
            logger.error("Parameter %s in BasicGate is undefined.", gate.name)
            raise Exception(
                "Parameter " + str(gate.name) + " in BasicGate is undefined."
            )
        return values[gate.name]
    elif type(gate) is InverseBasicGate:
        if gate.name not in values:
            logger.error(
                "Parameter %s in InverseBasicGate is undefined.",
                gate.name,
            )
            raise Exception(
                "Parameter " + str(gate.name) + " in InverseBasicGate is undefined."
            )
        return values[gate.name].conj().T
    elif isinstance(gate, PauliX):
        return cp.array([[0.0, 1.0], [1.0, 0.0]], dtype=cp.complex128)
    elif isinstance(gate, PauliY):
        return cp.array([[0.0, -1j], [1j, 0.0]], dtype=cp.complex128)
    elif isinstance(gate, PauliZ):
        return cp.array([[1.0, 0.0], [0.0, -1.0]], dtype=cp.complex128)
    elif isinstance(gate, Phase):
        return cp.array(
            [[1.0, 0.0], [0.0, cp.exp(1j * values[gate.name])]], dtype=cp.complex128
        )
    elif isinstance(gate, InversePhase):
        return cp.array(
            [[1.0, 0.0], [0.0, cp.exp(-1j * values[gate.name])]], dtype=cp.complex128
        )
    elif isinstance(gate, Hadamard):
        w2 = 1 / cp.sqrt(2)
        return cp.array([[w2, w2], [w2, -w2]], dtype=cp.complex128)
    elif isinstance(gate, SGate):
        return cp.array([[1.0, 0.0], [0.0, 1j]], dtype=cp.complex128)
    elif isinstance(gate, InverseSGate):
        return cp.array([[1.0, 0.0], [0.0, -1j]], dtype=cp.complex128)
    elif isinstance(gate, SwapQubits):
        return cp.array(
            [
                [1.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 1.0, 0.0],
                [0.0, 1.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 1.0],
            ],
            dtype=cp.complex128,
        )
    elif isinstance(gate, CNOT):
        return cp.array(
            [
                [1.0, 0.0, 0.0, 0.0],
                [0.0, 1.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 1.0],
                [0.0, 0.0, 1.0, 0.0],
            ],
            dtype=cp.complex128,
        )
    elif isinstance(gate, PermuteQubits):
        qubits = list(range(len(gate.targetOrder)))
        perm = permutationMatrixCupy([gate.targetOrder.index(q) for q in qubits])
        return perm
    elif isinstance(gate, QuantumControl):
        u = getUnitaryCuPy(gate.qop, values)
        size = u.shape[0]
        dim = 2 ** len(gate.onoff) * size
        target_state_num = bin2num(gate.onoff)
        res = cp.eye(dim, dtype=u.dtype)
        start = target_state_num * size
        end = start + size
        res[start:end, start:end] = u
        return res
    elif isinstance(gate, Rx):
        return getRXCupy(values[gate.name])
    elif isinstance(gate, InverseRx):
        return getRXCupy(-values[gate.name])
    elif isinstance(gate, Ry):
        return getRYCupy(values[gate.name])
    elif isinstance(gate, InverseRy):
        return getRYCupy(-values[gate.name])
    elif isinstance(gate, Rz):
        return cp.array(
            [
                [cp.exp(-1j * values[gate.name] / 2), 0.0],
                [0.0, cp.exp(1j * values[gate.name] / 2)],
            ],
            dtype=cp.complex128,
        )
    elif isinstance(gate, InverseRz):
        return cp.array(
            [
                [cp.exp(1j * values[gate.name] / 2), 0.0],
                [0.0, cp.exp(-1j * values[gate.name] / 2)],
            ],
            dtype=cp.complex128,
        )
    elif isinstance(gate, Rzz):
        return cp.array(
            [
                [cp.exp(-1j * values[gate.name] / 2), 0.0, 0.0, 0.0],
                [0.0, cp.exp(1j * values[gate.name] / 2), 0.0, 0.0],
                [0.0, 0.0, cp.exp(1j * values[gate.name] / 2), 0.0],
                [0.0, 0.0, 0.0, cp.exp(-1j * values[gate.name] / 2)],
            ],
            dtype=cp.complex128,
        )
    elif isinstance(gate, InverseRzz):
        return cp.array(
            [
                [cp.exp(1j * values[gate.name] / 2), 0.0, 0.0, 0.0],
                [0.0, cp.exp(-1j * values[gate.name] / 2), 0.0, 0.0],
                [0.0, 0.0, cp.exp(-1j * values[gate.name] / 2), 0.0],
                [0.0, 0.0, 0.0, cp.exp(1j * values[gate.name] / 2)],
            ],
            dtype=cp.complex128,
        )
    elif isinstance(gate, QFT):
        return getQFTCuPy(gate.numberQubits, inverse=False)
    elif isinstance(gate, InverseQFT):
        return getQFTCuPy(gate.qft.numberQubits, inverse=True)
    else:
        logger.error("gate %s not implemented yet", gate)
        raise Exception("gate " + str(gate) + " not implemented yet")


class BaseSimulatorCupy(BaseQASM):
    def __init__(self, numberQubits: int, values: dict):
        self.numberQubits = numberQubits
        super().__init__(values)

    @abstractmethod
    def prepareBackend(self, operations: list[QuantumOperation]):
        pass

    @abstractmethod
    def apply(self, gate: QuantumOperation, targets: list[int], *args, **kwargs):
        pass

    def setValue(self, name: str, value: list | float | cp.ndarray):
        self.values[name] = value

    def sequence_to_qasm3(self, sequence: Sequence) -> str:
        lines = self._qasm_lines_init(sequence)
        qasm_lines = self._qasm_lines_body(sequence, lines)

        return qasm_lines


class ensembleSimulatorCuPy(BaseSimulatorCupy):
    def __init__(self, numberQubits: int, numberBits: int):
        values = {}
        super().__init__(numberQubits, values)
        self.numberBits = numberBits
        rho = cp.zeros(
            (2**numberQubits, 2**numberQubits), dtype=cp.complex128
        )  # rho as cupy array
        rho[0, 0] = 1.0
        self.ensemble = {}
        bits = (0,) * numberBits
        self.ensemble[bits] = (1.0, rho)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.numberQubits}, {self.numberBits})"

    def prepareBackend(self, operations: list[QuantumOperation]):
        for ops in operations:
            if isinstance(ops, PCCM):
                logger.info("prepare execution of PCCM")
                self.values[ops.nameSpacePrefix + "RX(π/2)"] = cp.pi / 2
                self.values[ops.nameSpacePrefix + "RX(-π/2)"] = -cp.pi / 2
                self.values[ops.nameSpacePrefix + "RY(-π/2)"] = -cp.pi / 2
                nameAngle = ops.nameSpacePrefix + ops.name
                if nameAngle not in self.values:
                    logger.info("%s not specified in the backend ", nameAngle)
                else:
                    logger.debug(
                        "found nameAngle %s with value %s ",
                        nameAngle,
                        self.values[nameAngle],
                    )
                    self.values[ops.nameSpacePrefix + "RX(" + str(nameAngle) + ")"] = (
                        self.values[nameAngle]
                    )

            elif isinstance(ops, InversePCCM):
                self.prepareBackend([ops.pccm])
            elif isinstance(ops, QFT):
                logger.info("prepare execution of QFT")
                n = ops.numberQubits
                for j in range(1, n):
                    self.values[ops.nameSpacePrefix + "Ph" + str(j)] = (
                        2 * cp.pi / (2 ** (j + 1))
                    )
            elif isinstance(ops, InverseQFT):
                self.prepareBackend([ops.qft])
            elif isinstance(ops, Toffoli):
                logger.info("prepare execution of Toffoli")
                self.values[ops.nameSpacePrefix + "S.Pi/4"] = cp.pi / 4
                self.values[ops.nameSpacePrefix + "-S.Pi/4"] = -cp.pi / 4
            else:
                logger.error("prepareBackend: operation not supported: %s", ops)
                raise Exception("prepareBackend: operation not supported:", str(ops))

    def apply(
        self,
        gate: QuantumOperation,
        targets: list[int],
        classicalTargets: list[int] | None = None,
    ):
        if classicalTargets is None:
            classicalTargets = []

        if isinstance(gate, ClassicalControl):
            if gate.qop.isUnitary():
                controls = classicalTargets  # control bits
                target_qubits = targets  # quantum targets
                onoffMapping = [controls.index(t) for t in sorted(controls)]
                condition = [gate.onoff[i] for i in onoffMapping]

                newEnsemble = {}
                for s in self.ensemble:
                    bits = [s[i] for i in range(self.numberBits) if i in controls]
                    if bits == condition:  # if the control condition is met
                        if not isinstance(gate.qop, (QFT, InverseQFT)):
                            dec = gate.qop.getEquivalentSequence()
                        else:  # There is QubitReversal inside QFT. Try to avoid second decomposition.
                            dec = Sequence(
                                [*range(gate.qop.getNumberQubits())],
                                [],
                                [(gate.qop, [*range(gate.qop.getNumberQubits())], [])],
                            )
                        qubitMapping = {}
                        qubits = [*range(len(dec.qubits))]
                        for x in range(len(dec.qubits)):
                            qubitMapping[qubits[x]] = target_qubits[x]

                        unitaries = cp.eye(2**self.numberQubits, dtype=cp.complex128)
                        for d in dec.gatesAndTargets:
                            op = d[0]
                            subtargets = [qubitMapping[x] for x in d[1]]
                            u = multiQubitsUnitaryCupy(
                                getUnitaryCuPy(op, self.values),
                                [*range(self.numberQubits)],
                                subtargets,
                            )
                            unitaries = u @ unitaries

                        newEnsemble[s] = (
                            self.ensemble[s][0],
                            unitaries @ self.ensemble[s][1] @ unitaries.conj().T,
                        )

                    else:  # if the control condition is not met
                        newEnsemble[s] = (
                            self.ensemble[s][0],
                            self.ensemble[s][1],
                        )
                self.ensemble = newEnsemble
            else:  # non-unitary target operation
                logger.error("Controlled operations cannot be non-unitary.")
                raise Exception("Controlled operations cannot be non-unitary.")

        # If there is a decomposition into a sequence of other gates, then use it.
        elif gate.hasDecomposition() is True and not isinstance(
            gate, (QFT, InverseQFT)
        ):
            dec = gate.getEquivalentSequence()
            qubitMapping = {}
            for x in range(len(dec.qubits)):
                qubitMapping[dec.qubits[x]] = targets[x]

            bitMapping = {}
            for x in range(len(dec.bits)):
                bitMapping[dec.bits[x]] = classicalTargets[x]

            for d in dec.gatesAndTargets:
                if len(dec.qubits) > 0:
                    qkey_type = type(dec.qubits[0])
                    apply_qtargets = [
                        qubitMapping[x]
                        if type(x) is qkey_type
                        else qubitMapping[dec.qubits[x]]
                        for x in d[1]
                    ]
                else:
                    apply_qtargets = []
                if len(dec.bits) > 0:
                    ckey_type = type(dec.bits[0])
                    apply_ctargets = [
                        bitMapping[x]
                        if type(x) is ckey_type
                        else bitMapping[dec.bits[x]]
                        for x in d[2]
                    ]
                else:
                    apply_ctargets = []
                self.apply(
                    d[0],
                    apply_qtargets,
                    apply_ctargets,
                )

        # If the gate is unitary, then get the matrix and
        # apply it to the right order of qubits.
        elif gate.isUnitary():
            u3 = multiQubitsUnitaryCupy(
                getUnitaryCuPy(gate, self.values), [*range(self.numberQubits)], targets
            )

            newEnsemble = {}
            for s in self.ensemble:
                newEnsemble[s] = (
                    self.ensemble[s][0],
                    u3 @ self.ensemble[s][1] @ u3.conj().T,
                )
            self.ensemble = newEnsemble

        elif isinstance(gate, SetDensityMatrix):
            if gate.name not in self.values:
                logger.error("name of parameter %s not known to simulator", gate.name)
                raise Exception(
                    "name of parameter " + str(gate.name) + " not known to simulator"
                )

            # trace out the target qubits
            newEnsemble = {}
            for ens in self.ensemble:
                rho_part, perm = partialTraceCupy(
                    self.ensemble[ens][1], list(range(self.numberQubits)), targets
                )
                newEnsemble[ens] = (
                    self.ensemble[ens][0],
                    perm.T @ cp.kron(rho_part, self.values[gate.name]) @ perm,
                )
            self.ensemble = newEnsemble
        elif isinstance(gate, Measure):
            non_target = numpy.setdiff1d(
                numpy.arange(self.numberQubits),
                numpy.array(targets),
                assume_unique=True,
            )

            newEnsemble = {}
            for s in self.ensemble:
                currentProb = self.ensemble[s][0]
                currentRho = self.ensemble[s][1]

                outcome = partial_diag_cupy(
                    currentRho, list(range(self.numberQubits)), non_target
                )

                for out in outcome:
                    resultProb = out[1]

                    resultRho = projection_cupy(
                        currentRho, self.numberQubits, targets, out[0]
                    )

                    prob = resultProb * currentProb
                    # rho = resultRho / resultProb

                    # use numpy here to avoid GPU overhead
                    newBits = numpy.array([x for x in s])  # make a copy
                    newBits[numpy.array(classicalTargets)] = out[0]
                    newBits = tuple([int(b) for b in newBits])

                    if newBits in newEnsemble:
                        previousProb = newEnsemble[newBits][0]
                        newEnsemble[newBits] = (
                            prob + previousProb,
                            (
                                previousProb * newEnsemble[newBits][1]
                                + prob * resultRho / resultProb
                            )
                            / (prob + previousProb),
                        )
                    else:
                        newEnsemble[newBits] = (prob, resultRho / resultProb)

            self.ensemble = newEnsemble

        elif type(gate) is SetBits:
            if gate.name not in self.values:
                logger.error("name of parameter %s not known to simulator", gate.name)
                raise Exception(
                    "name of parameter " + str(gate.name) + " not known to simulator"
                )
            bitValues = self.values[gate.name]

            newEnsemble = {}
            for s in self.ensemble:
                prob = self.ensemble[s][0]

                # set the bits as defined in SetBits. We must respect a bitMapping
                s3 = numpy.array([x for x in s])
                s3[numpy.array(classicalTargets)] = numpy.array(bitValues)
                s3 = tuple(s3)

                if s3 not in newEnsemble:
                    newEnsemble[s3] = (prob, self.ensemble[s][1])
                else:
                    previousProb = newEnsemble[s3][0]
                    newEnsemble[s3] = (
                        prob + previousProb,
                        (previousProb * newEnsemble[s3][1] + prob * self.ensemble[s][1])
                        / (prob + previousProb),
                    )
            self.ensemble = newEnsemble

        elif type(gate) is SetQubits:
            if gate.name not in self.values:
                logger.error("name of parameter %s not known to simulator", gate.name)
                raise Exception(
                    "name of parameter " + str(gate.name) + " not known to simulator"
                )

            qubitValues = self.values[gate.name]
            newDensityMatrix = cp.zeros(
                (2 ** len(targets), 2 ** len(targets)), dtype=cp.complex128
            )
            index = bin2num(qubitValues)
            newDensityMatrix[index, index] = 1.0

            # trace out the target qubits
            newEnsemble = {}
            for ens in self.ensemble:
                prob = self.ensemble[ens][0]
                rho_part, perm = partialTraceCupy(
                    self.ensemble[ens][1], list(range(self.numberQubits)), targets
                )
                newEnsemble[ens] = (
                    prob,
                    perm.T @ cp.kron(rho_part, newDensityMatrix) @ perm,
                )
            self.ensemble = newEnsemble

        elif type(gate) is DropQubits:
            # trace out the dropped qubits
            newEnsemble = {}
            for ens in self.ensemble:
                prob = self.ensemble[ens][0]
                rho_reduced, _ = partialTraceCupy(
                    self.ensemble[ens][1], list(range(self.numberQubits)), targets
                )
                newEnsemble[ens] = (prob, rho_reduced)

            self.ensemble = newEnsemble
            self.numberQubits -= len(targets)

        else:
            logger.error(
                "gate not implemented for %s: %s", self.__class__.__name__, gate
            )
            raise Exception(
                f"gate not implemented for {self.__class__.__name__}: {gate}"
            )


class mixedStateSimulatorCuPy(ensembleSimulatorCuPy):
    def __init__(
        self, numberQubits: int, numberBits: int, return_density: bool = False
    ):
        super().__init__(numberQubits, numberBits)
        rho = cp.zeros((2**numberQubits, 2**numberQubits), dtype=cp.complex128)
        rho[0, 0] = 1.0
        self.densityMatrix = rho
        self.measureHistory = []
        self.return_density = return_density

    def apply(
        self,
        gate: QuantumOperation,
        targets: list[int],
        classicalTargets: list[int] | None = None,
    ):
        if classicalTargets is None:
            classicalTargets = []

        if isinstance(gate, ClassicalControl):
            logger.error(
                "cannot perform ClassicalControl in %s", self.__class__.__name__
            )
            raise Exception(
                f"cannot perform ClassicalControl in {self.__class__.__name__}"
            )

        # If there is a decomposition into a sequence of other gates, then use it.
        elif gate.hasDecomposition() is True and not isinstance(
            gate, (QFT, InverseQFT)
        ):
            dec = gate.getEquivalentSequence()
            qubitMapping = {}
            for x in range(len(dec.qubits)):
                qubitMapping[dec.qubits[x]] = targets[x]

            bitMapping = {}
            for x in range(len(dec.bits)):
                bitMapping[dec.bits[x]] = classicalTargets[x]

            for d in dec.gatesAndTargets:
                if len(dec.qubits) > 0:
                    qkey_type = type(dec.qubits[0])
                    apply_qtargets = [
                        qubitMapping[x]
                        if type(x) is qkey_type
                        else qubitMapping[dec.qubits[x]]
                        for x in d[1]
                    ]
                else:
                    apply_qtargets = []
                if len(dec.bits) > 0:
                    ckey_type = type(dec.bits[0])
                    apply_ctargets = [
                        bitMapping[x]
                        if type(x) is ckey_type
                        else bitMapping[dec.bits[x]]
                        for x in d[2]
                    ]
                else:
                    apply_ctargets = []
                self.apply(
                    d[0],
                    apply_qtargets,
                    apply_ctargets,
                )

        # If the gate is unitary, then get the matrix and
        # apply it to the right order of qubits.
        elif gate.isUnitary():
            u3 = multiQubitsUnitaryCupy(
                getUnitaryCuPy(gate, self.values), [*range(self.numberQubits)], targets
            )

            self.densityMatrix = u3 @ self.densityMatrix @ u3.conj().T

        elif isinstance(gate, SetDensityMatrix):
            if gate.name not in self.values:
                logger.error(
                    "name of parameter %s not known to simulator",
                    gate.name,
                )
                raise Exception(
                    "name of parameter " + str(gate.name) + " not known to simulator"
                )

            # trace out the target qubits
            rho_part, perm = partialTraceCupy(
                self.densityMatrix, list(range(self.numberQubits)), targets
            )
            self.densityMatrix = (
                perm.T @ cp.kron(rho_part, self.values[gate.name]) @ perm
            )

        elif isinstance(gate, Measure):
            non_target = list(set(list(range(self.numberQubits))) - set(targets))

            outcome = partial_diag_cupy(
                self.densityMatrix, list(range(self.numberQubits)), non_target
            )

            measurement = {}
            mixedRho = cp.zeros(
                (2**self.numberQubits, 2**self.numberQubits), dtype=cp.complex128
            )

            for out in outcome:
                resultProb = out[1]

                resultRho = projection_cupy(
                    self.densityMatrix, self.numberQubits, targets, out[0]
                )

                mixedRho += resultRho

                measurement[tuple([int(b) for b in out[0]])] = resultProb

            if self.return_density:
                measurement["mixed_state"] = mixedRho

            self.densityMatrix = mixedRho
            self.measureHistory.append(measurement)

        elif isinstance(gate, SetBits):
            logger.error("SetBits not supported by this simulator")
            raise Exception("SetBits not supported by this simulator")

        elif isinstance(gate, SetQubits):
            if gate.name not in self.values:
                logger.error("name of parameter %s not known to simulator", gate.name)
                raise Exception(
                    "name of parameter " + str(gate.name) + " not known to simulator"
                )

            qubitValues = self.values[gate.name]
            newDensityMatrix = cp.zeros(
                (2 ** len(targets), 2 ** len(targets)), dtype=cp.complex128
            )
            index = bin2num(qubitValues)
            newDensityMatrix[index, index] = 1.0

            # trace out the target qubits and re-combine with newDensityMatrix
            rho_part, perm = partialTraceCupy(
                self.densityMatrix, list(range(self.numberQubits)), targets
            )
            self.densityMatrix = perm.T @ cp.kron(rho_part, newDensityMatrix) @ perm

        elif isinstance(gate, DropQubits):
            # trace out the dropped qubits
            rho_reduced, _ = partialTraceCupy(
                self.densityMatrix, list(range(self.numberQubits)), targets
            )

            self.densityMatrix = rho_reduced
            self.numberQubits -= len(targets)

        else:
            logger.error(
                "gate not implemented for %s: %s", self.__class__.__name__, gate
            )
            raise Exception(
                f"gate not implemented for {self.__class__.__name__}: {gate}"
            )


class unitarySimulatorCuPy(BaseSimulatorCupy):
    """
    Calculate the unitary matrix corresponding to a sequence of
    gates. No non-unitary operations like ClassicalControl, Measurement
    or DropQubits are allowed.
    """

    def __init__(self, numberQubits: int):
        values = {}
        super().__init__(numberQubits, values)
        self.u = cp.eye(2**numberQubits, dtype=cp.complex128)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.numberQubits})"

    def prepareBackend(self, operations: list[QuantumOperation]):
        for ops in operations:
            if isinstance(ops, PCCM):
                logger.info("prepare execution of PCCM")
                self.values[ops.nameSpacePrefix + "RX(π/2)"] = cp.pi / 2
                self.values[ops.nameSpacePrefix + "RX(-π/2)"] = -cp.pi / 2
                self.values[ops.nameSpacePrefix + "RY(-π/2)"] = -cp.pi / 2
                nameAngle = ops.nameSpacePrefix + ops.name
                if nameAngle not in self.values:
                    # print(nameAngle, "not specified in the backend.")
                    logger.info("%s not specified in the backend ", nameAngle)
                else:
                    logger.debug(
                        "found nameAngle %s with value %s ",
                        nameAngle,
                        self.values[nameAngle],
                    )
                    self.values[ops.nameSpacePrefix + "RX(" + str(nameAngle) + ")"] = (
                        self.values[nameAngle]
                    )

            elif isinstance(ops, InversePCCM):
                self.prepareBackend([ops.pccm])
            elif isinstance(ops, QFT):
                logger.info("prepare execution of QFT")
                n = ops.numberQubits
                for j in range(1, n):
                    self.values[ops.nameSpacePrefix + "Ph" + str(j)] = (
                        2 * cp.pi / (2 ** (j + 1))
                    )
            elif isinstance(ops, InverseQFT):
                self.prepareBackend([ops.qft])
            elif isinstance(ops, Toffoli):
                logger.info("prepare execution of Toffoli")
                self.values[ops.nameSpacePrefix + "S.Pi/4"] = cp.pi / 4
                self.values[ops.nameSpacePrefix + "-S.Pi/4"] = -cp.pi / 4
            else:
                logger.error("prepareBackend: operation not supported: %s", ops)
                raise Exception("prepareBackend: operation not supported:", str(ops))

    def apply(self, gate: QuantumOperation, targets: list[int]):
        if isinstance(gate, ClassicalControl):
            logger.error(
                "cannot perform ClassicalControl in %s", self.__class__.__name__
            )
            raise Exception(
                f"cannot perform ClassicalControl in {self.__class__.__name__}"
            )

        # If there is a decomposition into a sequence of other gates, then use it.
        elif gate.hasDecomposition() is True and not isinstance(
            gate, (QFT, InverseQFT)
        ):
            dec = gate.getEquivalentSequence()
            qubitMapping = {}
            for x in range(len(dec.qubits)):
                qubitMapping[dec.qubits[x]] = targets[x]

            for d in dec.gatesAndTargets:
                key_type = type(dec.qubits[0])
                apply_targets = [
                    qubitMapping[x]
                    if type(x) is key_type
                    else qubitMapping[dec.qubits[x]]
                    for x in d[1]
                ]
                self.apply(d[0], apply_targets)

        elif gate.isUnitary():
            u3 = multiQubitsUnitaryCupy(
                getUnitaryCuPy(gate, self.values), [*range(self.numberQubits)], targets
            )

            self.u = u3 @ self.u
        else:
            logger.error(
                "gate not implemented for %s: %s", self.__class__.__name__, gate
            )
            raise Exception(
                f"gate not implemented for {self.__class__.__name__}: {gate}"
            )


class statevectorSimulatorCuPy(BaseSimulatorCupy):
    def __init__(self, numberQubits: int, numberBits: int):
        values = {}
        super().__init__(numberQubits, values)
        self.numberBits = numberBits

        if numberQubits > 32:
            raise NotImplementedError("Too many qubits, limit is 32")

        self.state = cp.zeros(shape=(2**numberQubits, 1), dtype=cp.complex128)
        self.state[0, 0] = 1.0 + 0 * 1j

        self.measurementResult = {}
        self.measurementHappened = False

        self.classicalBits = cp.zeros(numberBits, dtype=cp.int64)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.numberQubits}, {self.numberBits})"

    def prepareBackend(self, operations: list[QuantumOperation]):
        for ops in operations:
            if isinstance(ops, PCCM):
                logger.info("prepare execution of PCCM")
                self.values[ops.nameSpacePrefix + "RX(π/2)"] = cp.pi / 2
                self.values[ops.nameSpacePrefix + "RX(-π/2)"] = -cp.pi / 2
                self.values[ops.nameSpacePrefix + "RY(-π/2)"] = -cp.pi / 2
                nameAngle = ops.nameSpacePrefix + ops.name
                if nameAngle not in self.values:
                    logger.info("%s not specified in the backend ", nameAngle)
                else:
                    logger.debug(
                        "found nameAngle %s with value %s ",
                        nameAngle,
                        self.values[nameAngle],
                    )
                    self.values[ops.nameSpacePrefix + "RX(" + str(nameAngle) + ")"] = (
                        self.values[nameAngle]
                    )

            elif isinstance(ops, InversePCCM):
                self.prepareBackend([ops.pccm])
            elif isinstance(ops, QFT):
                logger.info("prepare execution of QFT")
                n = ops.numberQubits
                for j in range(1, n):
                    self.values[ops.nameSpacePrefix + "Ph" + str(j)] = (
                        2 * cp.pi / (2 ** (j + 1))
                    )
            elif isinstance(ops, InverseQFT):
                self.prepareBackend([ops.qft])
            elif isinstance(ops, Toffoli):
                logger.info("prepare execution of Toffoli")
                self.values[ops.nameSpacePrefix + "S.Pi/4"] = cp.pi / 4
                self.values[ops.nameSpacePrefix + "-S.Pi/4"] = -cp.pi / 4
            else:
                logger.error("prepareBackend: operation not supported: %s", ops)
                raise Exception("prepareBackend: operation not supported:", str(ops))

    def apply(
        self,
        gate: QuantumOperation,
        targets: list[int],
        classicalTargets: list[int] | None = None,
    ):
        if classicalTargets is None:
            classicalTargets = []

        if self.measurementHappened:
            logger.error("no more operation allowed after measurement")
            raise Exception("no more operation allowed after measurement")

        if isinstance(gate, ClassicalControl):
            logger.error(
                "cannot perform ClassicalControl in %s", self.__class__.__name__
            )
            raise Exception(
                f"cannot perform ClassicalControl in {self.__class__.__name__}"
            )

        # If there is a decomposition into a sequence of other gates, then use it.
        elif gate.hasDecomposition() is True and not isinstance(
            gate, (QFT, InverseQFT)
        ):
            dec = gate.getEquivalentSequence()
            qubitMapping = {}
            for x in range(len(dec.qubits)):
                qubitMapping[dec.qubits[x]] = targets[x]

            bitMapping = {}
            for x in range(len(dec.bits)):
                bitMapping[dec.bits[x]] = classicalTargets[x]

            for d in dec.gatesAndTargets:
                if len(dec.qubits) > 0:
                    qkey_type = type(dec.qubits[0])
                    apply_qtargets = [
                        qubitMapping[x]
                        if type(x) is qkey_type
                        else qubitMapping[dec.qubits[x]]
                        for x in d[1]
                    ]
                else:
                    apply_qtargets = []
                if len(dec.bits) > 0:
                    ckey_type = type(dec.bits[0])
                    apply_ctargets = [
                        bitMapping[x]
                        if type(x) is ckey_type
                        else bitMapping[dec.bits[x]]
                        for x in d[2]
                    ]
                else:
                    apply_ctargets = []
                self.apply(
                    d[0],
                    apply_qtargets,
                    apply_ctargets,
                )

        # If the gate is unitary, then get the matrix and
        # apply it to the right order of qubits.
        elif gate.isUnitary():
            non_targets = sorted(set(range(self.numberQubits)) - set(targets))

            target_powers = cp.array([self.numberQubits - 1 - t for t in targets])
            non_target_powers = cp.array(
                [self.numberQubits - 1 - nt for nt in non_targets]
            )

            # Generate all possible binary values for targets and non-targets then convert them to binary strings matrix
            t_bin = (
                cp.arange(2 ** len(targets))[:, None] >> cp.arange(len(targets))[::-1]
            ) & 1
            n_bin = (
                cp.arange(2 ** len(non_targets))[:, None]
                >> cp.arange(len(non_targets))[::-1]
            ) & 1

            # Compute unpermuted binary values
            t_vals = (t_bin * 2**target_powers).sum(axis=1)  # shape (2^t,)
            n_vals = (n_bin * 2**non_target_powers).sum(axis=1)  # shape (2^n,)

            # Compute full indices of all (non-target + target) combinations
            indices = (n_vals[:, None] + t_vals[None, :]).astype(
                cp.int64
            )  # shape (2^n, 2^t)

            # reshape the statevector into an matrix where every row stores all possible full indices of a non-target configuration
            # i.e. target qubit q1 non target q0,q2. If non target = 01, the corresponding row is a vector [bin2num(001),bin2num(011)]
            subspace = self.state[indices].reshape(
                -1, 2 ** len(targets)
            )  # shape (2^n, 2^t)

            # Apply unitary to each row (for each non-target configuration)
            u = getUnitaryCuPy(gate, self.values)  # shape (2^t, 2^t)
            updated = (
                subspace @ u.T
            )  # (2^n, 2^t)  u applied to column vector is u @ v, to row vector is v @ u.T

            self.state[indices.ravel()] = updated.reshape(-1, 1)
            # self.state[indices.ravel()] = (
            #    subspace @ getUnitaryCuPy(gate, self.values).T
            # ).reshape(-1, 1)

        elif isinstance(gate, Measure):
            if len(targets) != gate.numberQubits:
                logger.error(
                    "Number of targets does not match number of measured qubits"
                )
                raise ValueError(
                    "Number of targets does not match number of measured qubits"
                )

            self.measurementHappened = True

            probabilities = dict()

            # Generate all binary representations of indices
            bits = (
                cp.arange(2**self.numberQubits)[:, None]
                >> cp.arange(self.numberQubits - 1, -1, -1)
            ) & 1

            # Keep only the measured bits
            measure_bits = bits[:, targets]

            # Convert each measure_bits row to an integer key
            powers = 2 ** cp.arange(len(targets) - 1, -1, -1)
            keys = (measure_bits * powers).sum(axis=1)

            # Sum up diagonals with the same kept qubits key using bincount
            probs = cp.bincount(
                keys,
                weights=cp.real(self.state.ravel() * self.state.ravel().conj()),
                minlength=2 ** len(targets),
            )

            store_bits = (
                (cp.arange(len(probs))[:, None] >> cp.arange(len(targets) - 1, -1, -1))
                & 1
            ).astype(cp.int64)

            for idx, sb in zip(range(len(probs)), store_bits):
                newClassicalBits = self.classicalBits
                for i in range(len(classicalTargets)):
                    newClassicalBits[classicalTargets[i]] = sb[i]
                newClassicalBits = (
                    tuple(newClassicalBits.get().tolist())
                    if use_cupy
                    else tuple(newClassicalBits.tolist())
                )
                probabilities[newClassicalBits] = probs[idx] if probs[idx] >= 0 else 0

            self.measurementResult = probabilities

        elif isinstance(gate, SetBits):
            bits = self.values.get(gate.name, None)

            if bits is None:
                logger.error('Bit values "%s" not found', gate.name)
                raise ValueError(f'Bit values "{gate.name}" not found')

            if len(classicalTargets) != len(bits):
                logger.error("wrong number of bits in definition for SetBits")
                raise ValueError("wrong number of bits in definition for SetBits")

            for i in range(len(classicalTargets)):
                self.classicalBits[classicalTargets[i]] = bits[i]

        elif isinstance(gate, SetQubits):
            logger.error("cannot set qubits in statevector simulations")
            raise Exception("cannot set qubits in statevector simulations")

        elif isinstance(gate, DropQubits):
            logger.error("cannot drop qubits in statevector simulations")
            raise Exception("cannot drop qubits in statevector simulations")

        elif isinstance(gate, SetDensityMatrix):
            logger.error("cannot set density matrix in statevector simulations")
            raise Exception("cannot set density matrix in statevector simulations")

        else:
            logger.error("gate not supported: %s", str(gate))
            raise Exception(f"gate not supported: {str(gate)}")
