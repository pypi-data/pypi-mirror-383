import math
from itertools import combinations

from geqo.core.basic import BasicGate, InverseBasicGate
from geqo.core.quantum_circuit import Sequence
from geqo.core.quantum_operation import QuantumOperation
from geqo.gates.fundamental_gates import (
    CNOT,
    Hadamard,
    PauliX,
    PauliY,
    PauliZ,
    Phase,
    SwapQubits,
)
from geqo.gates.multi_qubit_gates import Toffoli
from geqo.gates.rotation_gates import Rx, Ry, Rz
from geqo.operations.controls import QuantumControl
from geqo.operations.measurement import Measure
from geqo.utils._base_.helpers import embedSequences, num2bin


class PermuteQubits(QuantumOperation):
    """This class allows to define a unitary operation that corresponds to a permutation
    of qubits. The argument is the target order of the permuted qubits, which are denoted
    by 0, ..., n-1 for n qubits.

    For instance, ```PermuteQubits([2,1,0])``` defines the bit reversal on three qubits.
    """

    def __init__(self, targetOrder):
        """
        The constructor of this class takes a permutation in list representation as input. For
        instance, the targetOrder [2,1,0] corresponds to a reversed order of qubits.

        Parameters
        ----------
        targetOrder : list(int)
                      The new order of qubits after the permutation. The order is
                      represented as a list of indices, starting with 0 as index of
                      the first qubit.

        Returns
        -------
        PermuteQubits : geqo.algorithms.PermuteQubits
            An object of this class that corresponds to the specified permutation of qubits.
        """
        self.targetOrder = targetOrder

    def __repr__(self):
        """
        Returns a representation of the object as character string.
        -------
        string_representation : String
            Representation of the object as character string.
        """
        string_representation = "PermuteQubits(" + str(self.targetOrder) + ")"
        return string_representation

    def __eq__(self, other):
        """
        Comparator with other objects.

        Parameters
        ----------
        other : An object, which should be compared to this object.

        Returns
        -------
        True : If the provided object is of the same type and if it corresponds to the same permutation of qubits.
        False : else
        """
        if not isinstance(other, PermuteQubits):
            return False
        return self.targetOrder == other.targetOrder

    def getInverse(self):
        """
        Return an object of the same class, but it corresponds to the inverse permutation of qubits as this object.

        Returns
        -------
        PermuteQubits : geqo.algorithm.PermuteQubits
            A new object of this class, which corresponds to the inverse permutation of qubits.
        """

        newOrder = []
        for x in range(len(self.targetOrder)):
            newOrder.append(self.targetOrder.index(x))
        return PermuteQubits(newOrder)

    def getEquivalentSequence(self):
        """
        Return an object of the class ```Sequence```, which does not contain any operators, because a
        permutation of qubits is considered to be as a non-decomposable operation.

        Returns
        -------

        sequence : geqo.core.Sequence
            An object of the class ```Sequence```  without operations, but with the appropriate bits and qubits.
        """
        numberQubits = self.getNumberQubits()
        allQubits = list(range(numberQubits))
        sequence = Sequence(allQubits, [], [(self, allQubits, [])])
        return sequence

    def getNumberQubits(self):
        """
        Return the number of qubits that are used by this permuation operation.

        Returns
        -------
        numberQubits : int
            The number of qubits, which are used by this permutation of qubits. This is equal
            to the length of the list representation of the permuation.
        """
        numberQubits = len(self.targetOrder)
        return numberQubits

    def getNumberClassicalBits(self):
        """
        Returns
        -------
        0 : int
            The number of classical bits, which are used by PermuteQubits, is zero.
        """
        return 0

    def isUnitary(self):
        """
        Returns
        -------
        True : Bool
            This is a unitary operation.
        """
        return True

    def hasDecomposition(self):
        """
        Returns
        -------
        False : Bool
            A permutation of qubits is considered to be as a non-decomposable operation.
        """
        return False


class QubitReversal(QuantumOperation):
    """This operation is reversing the order of qubits. It corresponds to a permutation of the
    states of the computational basis.

    See ```https://en.wikipedia.org/wiki/Bit-reversal_permutation``` for the related bit-reversal permutation.
    """

    def __init__(self, numberQubits):
        """
        The constructor of this class takes the number of qubits as input.

        Parameters
        ----------
        numberQubits : int
                      The number of qubits for this qubit reversal operation.

        Returns
        -------
        QubitReversal : geqo.algorithms.QubitReversal
            An object of this class that corresponds to the specified qubit reversal operation.
        """
        self.numberQubits = numberQubits

    def __repr__(self):
        """
        Returns a representation of the object as character string.
        -------
        string_representation : String
            Representation of the object as character string.
        """
        string_representation = "QubitReversal(" + str(self.numberQubits) + ")"
        return string_representation

    def __eq__(self, other):
        """
        Comparator with other objects.

        Parameters
        ----------
        other : An object, which should be compared to this object.

        Returns
        -------
        True : If the provided object is of the same type and if it has the same number of qubits.
        False : else
        """
        if not isinstance(other, QubitReversal):
            return False
        return self.numberQubits == other.numberQubits

    def getInverse(self):
        """
        Return this object because the reversal of qubits is inverse to itself.

        Returns
        -------
        QubitReversal : geqo.algorithm.QubitReversal
            Return the same object because it is self-inverse.
        """
        return self

    def getEquivalentSequence(self):
        """
        Return an object of the class ```Sequence```, which contains a sequence of qubit swaps. The sequence of swaps
        correspond to the qubit reversal.

        Returns
        -------

        sequence : geqo.core.Sequence
            An object of the class ```Sequence```  with swap operations and the appropriate bits and qubits.
        """
        numberQubits = self.getNumberQubits()
        allQubits = list(range(numberQubits))
        seq = []
        for i in range(numberQubits // 2):
            seq.append((SwapQubits(), [i, numberQubits - i - 1], []))
        return Sequence(allQubits, [], seq)

    def getNumberQubits(self):
        """
        Return the number of qubits that are used by this qubit reversal operation.

        Returns
        -------
        numberQubits : int
            The number of qubits, which are used by this qubit reversal.
        """
        numberQubits = self.numberQubits
        return numberQubits

    def getNumberClassicalBits(self):
        """
        Returns
        -------
        0 : int
            The number of classical bits, which are used by this qubit reversal operation, is zero.
        """
        return 0

    def isUnitary(self):
        """
        Returns
        -------
        True : Bool
            This is a unitary operation.
        """
        return True

    def hasDecomposition(self):
        """
        Returns
        -------
        True : Bool
            The qubit reversal can be decomposed into a sequence of qubit swaps.
        """
        return True


class QFT(QuantumOperation):
    """This operation corresponds to the quantum Fourier transform on a specified number of qubits.

    For the definition, see ```https://en.wikipedia.org/wiki/Quantum_Fourier_transform```.

    The inverse can be obtained with ```getInverse()``` and it returns an object of type ```InverseQFT```.


    The QFT can be decomposed into a sequence of controlled phase operations and Hadamard gates, see
    ```https://en.wikipedia.org/wiki/Toffoli_gate#Related_logic_gates``` for details.

    This decomposition can be obtained with the function ```getEquivalentSequence```. It returns
    a sequence of Hadamard gates and gates of the class Phase with the names ```Ph1```, ```Ph2``, ...
    where ```Phk``` corresponds to a phase gate with phase $e^{2pi i/2^k}.

    For instance, the QFT on two qubits
    corresponds to the sequence ```Sequence([], [0, 1], [(Hadamard(), [0]), (QuantumControl([1], Phase("Ph1")), [1, 0]), (Hadamard(), [1]), (QubitReversal(2), [0, 1])])``` where ```Ph1```
    denotes

    To avoid conflicts with the names of other gates, a name space prefix can be provided to the
    contructor of QFT. For instance, the object ```QFT(2, "test.")``` leads to the sequence
    ```Sequence([], [0, 1], [(Hadamard(), [0]), (QuantumControl([1], Phase("test.Ph1")), [1, 0]), (Hadamard(), [1]), (QubitReversal(2), [0, 1])])```.

    For convenience, a backend might be prepared for applying a QFT with the function ```prepareBackend```
    of the corresponding backend class.
    """

    def __init__(self, numberQubits, nameSpacePrefix=""):
        """
        The constructor of this class takes a the number of qubits and an optional name space prefix as
        parameters.

        Parameters
        ----------
        numberQubits : int
                      The number of qubits, which the QFT acts on.
        nameSpacePrefix : string
                    The provided character string is prependet to all internally defined operations.

        Returns
        -------
        QFT : geqo.algorithms.QFT
            An object of this class that corresponds to the QFT.
        """
        self.numberQubits = numberQubits
        self.nameSpacePrefix = nameSpacePrefix

    def __repr__(self):
        """
        Returns a representation of the object as character string.
        -------
        string_representation : String
            Representation of the object as character string.
        """
        string_representation = (
            "QFT(" + str(self.numberQubits) + ', "' + self.nameSpacePrefix + '")'
        )
        return string_representation

    def __eq__(self, other):
        """
        Comparator with other objects.

        Parameters
        ----------
        other : An object, which should be compared to this object.

        Returns
        -------
        True : If the provided object is of the same type and if it has the same number of qubits and the same name space prefix.
        False : else
        """
        if not isinstance(other, QFT):
            return False
        return (
            self.numberQubits == other.numberQubits
            and self.nameSpacePrefix == other.nameSpacePrefix
        )

    def getInverse(self):
        """
        Return an object of the class ```InverseQFT``` with the same number of qubits and the same name space prefix.

        Returns
        -------
        InverseQFT : geqo.algorithm.InverseQFT
            A new object of this class, which corresponds to the inverse QFT.
        """
        return InverseQFT(self.numberQubits, self.nameSpacePrefix)

    def getEquivalentSequence(self):
        """
        Return an object of the class ```Sequence```, which contains a sequence of Hadamard and controlled phase gates. The sequence of gates
        correspond to the QFT.

        Returns
        -------

        sequence : geqo.core.Sequence
            An object of the class ```Sequence```  with Hadamard and controlled phase operations and the appropriate bits and qubits.
        """
        h = Hadamard()
        n = self.numberQubits
        seq = []
        for i in range(n):
            seq.append((h, [i], []))
            for j in range(1, n - i):
                seq.append(
                    (
                        QuantumControl(
                            [1], Phase(self.nameSpacePrefix + "Ph" + str(j))
                        ),
                        [i + j, i],
                        [],
                    )
                )
        seq.append((QubitReversal(n), list(range(n)), []))
        return Sequence(list(range(n)), [], seq)

    def getNumberQubits(self):
        """
        Return the number of qubits that are used by this QFT operation.

        Returns
        -------
        numberQubits : int
            The number of qubits, which are used by this QFT operation.
        """
        numberQubits = self.numberQubits
        return numberQubits

    def getNumberClassicalBits(self):
        """
        Returns
        -------
        0 : int
            The number of classical bits, which are used by the QFT, is zero.
        """
        return 0

    def hasDecomposition(self):
        """
        Returns
        -------
        True : Bool
            The QFT can be decomposed into a sequence of Hadamard gates and controlled phase gates and a qubit reversal.
        """
        return True

    def isUnitary(self):
        """
        Returns
        -------
        True : Bool
            This is a unitary operation.
        """
        return True


class InverseQFT(QuantumOperation):
    """This operation corresponds to the inverse of the quantum Fourier transform on a specified
    number of qubits.

    The inverse can be obtained with ```getInverse()``` and it returns an object of type ```QFT```.

    For more information, please refer to the documentation of the class ```QFT```.
    """

    def __init__(self, numberQubits, nameSpacePrefix=""):
        """
        The constructor of this class takes a the number of qubits and an optional name space prefix as
        parameters.

        Parameters
        ----------
        numberQubits : int
                      The number of qubits, which the InverseQFT acts on.
        nameSpacePrefix : string
                    The provided character string is prependet to all internally defined operations.

        Returns
        -------
        InverseQFT : geqo.algorithms.InverseQFT
            An object of this class that corresponds to the InverseQFT.
        """
        self.qft = QFT(numberQubits, nameSpacePrefix)
        self.nameSpacePrefix = nameSpacePrefix

    def __repr__(self):
        """
        Returns a representation of the object as character string.
        -------
        string_representation : String
            Representation of the object as character string.
        """
        string_representation = (
            "InverseQFT("
            + str(self.qft.numberQubits)
            + ', "'
            + self.nameSpacePrefix
            + '")'
        )
        return string_representation

    def __eq__(self, other):
        """
        Comparator with other objects.

        Parameters
        ----------
        other : An object, which should be compared to this object.

        Returns
        -------
        True : If the provided object is of the same type and if it has the same number of qubits and the same name space prefix.
        False : else
        """
        if not isinstance(other, InverseQFT):
            return False
        return self.qft == other.qft and self.nameSpacePrefix == other.nameSpacePrefix

    def getInverse(self):
        """
        Return an object of the class ```QFT``` with the same number of qubits and the same name space prefix.

        Returns
        -------
        QFT : geqo.algorithm.QFT
            A new object of this class, which corresponds to the QFT.
        """
        return self.qft

    def getEquivalentSequence(self):
        """
        Return an object of the class ```Sequence```, which contains a sequence of Hadamard and controlled phase gates. The sequence of gates
        correspond to the InverseQFT.

        Returns
        -------

        sequence : geqo.core.Sequence
            An object of the class ```Sequence```  with Hadamard and controlled phase operations and the appropriate bits and qubits.
        """
        return self.qft.getEquivalentSequence().getInverse()

    def getNumberQubits(self):
        """
        Return the number of qubits that are used by this InverseQFT operation.

        Returns
        -------
        numberQubits : int
            The number of qubits, which are used by this InverseQFT operation.
        """
        return self.qft.numberQubits

    def getNumberClassicalBits(self):
        """
        Returns
        -------
        0 : int
            The number of classical bits, which are used by InverseQFT, is zero.
        """
        return 0

    def hasDecomposition(self):
        """
        Returns
        -------
        True : Bool
            The InverseQFT can be decomposed into a sequence of Hadamard gates and controlled phase gates and a qubit reversal.
        """
        return True

    def isUnitary(self):
        """
        Returns
        -------
        True : Bool
            This is a unitary operation.
        """
        return True


class PCCM(QuantumOperation):
    """The circuit for a phase-covariant cloning machine with one free parameter, which is
    the angle of a controlled rotation in its circuit representation.

    The inverse can be obtained with ```getInverse()``` and it returns an object of type ```InversePCCM```.

    The circuit diagram can be found in figure 3 of
    T. Decker, M. Gallezot, S. F. Kerstan, A. Paesano, A. Ginter, W. Wormsbecher,
    "QKD as a Quantum Machine Learning task", arXiv:2410.01904
    """

    def __init__(self, name, nameSpacePrefix=""):
        """
        The constructor of this class takes a name and an optional name space prefix as
        parameters.

        Parameters
        ----------
        name : string
                    The name for the rotation angle inside the PCCM.
        nameSpacePrefix : string
                    The provided character string is prependet to all internally defined operations.

        Returns
        -------
        PCCM : geqo.algorithms.PCCM
            An object of this class that corresponds to the PCCM.
        """
        self.name = name
        self.nameSpacePrefix = nameSpacePrefix

    def __repr__(self):
        """
        Returns a representation of the object as character string.
        -------
        string_representation : String
            Representation of the object as character string.
        """
        string_representation = (
            'PCCM("' + str(self.name) + '", "' + self.nameSpacePrefix + '")'
        )
        return string_representation

    def __eq__(self, other):
        """
        Comparator with other objects.

        Parameters
        ----------
        other : An object, which should be compared to this object.

        Returns
        -------
        True : If the provided object is of the same type and if it has the same name and name space prefix.
        False : else
        """
        if not isinstance(other, PCCM):
            return False
        return self.name == other.name and self.nameSpacePrefix == other.nameSpacePrefix

    def getInverse(self):
        """
        Return an object of the class ```InversePCCM``` with the same name for the rotation angle and the same name space prefix.

        Returns
        -------
        InversePCCM : geqo.algorithm.InversePCCM
            A new object of this class, which corresponds to the inverse of the PCCM.
        """
        return InversePCCM(self.name, self.nameSpacePrefix)

    def getEquivalentSequence(self):
        """
        Return an object of the class ```Sequence```, which contains a sequence of qubit swaps. The sequence of controlled and uncontrolled
        rotations correspond to the PCCM.

        Returns
        -------

        sequence : geqo.core.Sequence
            An object of the class ```Sequence```  with controlled and uncontrolled rotation operations that correspond to the PCCM.
        """
        gate1 = Rx(self.nameSpacePrefix + "RX(π/2)")
        gate2 = Rx(self.nameSpacePrefix + "RX(π/2)")
        gate3 = QuantumControl(
            [1], Rx(self.nameSpacePrefix + "RX(" + str(self.name) + ")")
        )
        gate4 = QuantumControl([1], Rx(self.nameSpacePrefix + "RX(-π/2)"))
        gate5 = Rx(self.nameSpacePrefix + "RX(-π/2)")
        gate6 = Ry(self.nameSpacePrefix + "RY(-π/2)")
        seq = [
            (gate1, [0], []),
            (gate2, [1], []),
            (gate3, [0, 1], []),
            (gate4, [1, 0], []),
            (gate5, [0], []),
            (gate6, [1], []),
        ]
        s = Sequence([0, 1], [], seq)
        return s

    def getNumberQubits(self):
        """
        Return the number of qubits that are used by this PCCM operation.

        Returns
        -------
        2 : int
            The number of qubits, which are used by the PCCM.
        """
        return 2

    def getNumberClassicalBits(self):
        """
        Returns
        -------
        0 : int
            The number of classical bits, which are used by the PCCM, is zero.
        """
        return 0

    def hasDecomposition(self):
        """
        Returns
        -------
        True : Bool
            The PCCM can be decomposed into a sequence of rotation gates.
        """
        return True

    def isUnitary(self):
        """
        Returns
        -------
        True : Bool
            This is a unitary operation.
        """
        return True


class InversePCCM(QuantumOperation):
    """This operation corresponds to the inverse of the phase-covariant cloning machine with
    a specified angle.

    The inverse can be obtained with ```getInverse()``` and it returns an object of type ```PCCM```.

    For more information, please refer to the documentation of the class ```PCCM```.
    """

    def __init__(self, name, nameSpacePrefix=""):
        """
        The constructor of this class takes a name and an optional name space prefix as
        parameters.

        Parameters
        ----------
        name : string
                    The name for the rotation angle inside the InversePCCM.
        nameSpacePrefix : string
                    The provided character string is prependet to all internally defined operations.

        Returns
        -------
        InversePCCM : geqo.algorithms.InversePCCM
            An object of this class that corresponds to the InversePCCM.
        """
        self.pccm = PCCM(name, nameSpacePrefix)
        self.nameSpacePrefix = nameSpacePrefix

    def __repr__(self):
        """
        Returns a representation of the object as character string.
        -------
        string_representation : String
            Representation of the object as character string.
        """
        string_representation = (
            'InversePCCM("' + str(self.pccm.name) + '", "' + self.nameSpacePrefix + '")'
        )
        return string_representation

    def __eq__(self, other):
        """
        Comparator with other objects.

        Parameters
        ----------
        other : An object, which should be compared to this object.

        Returns
        -------
        True : If the provided object is of the same type and if it has the same name and name space prefix.
        False : else
        """
        if not isinstance(other, InversePCCM):
            return False
        return self.pccm == other.pccm and self.nameSpacePrefix == other.nameSpacePrefix

    def getInverse(self):
        """
        Return an object of the class ```PCCM``` with the same name for the rotation angle and the same name space prefix.

        Returns
        -------
        PCCM : geqo.algorithm.PCCM
            A new object of this class, which corresponds to the PCCM.
        """
        return self.pccm

    def getEquivalentSequence(self):
        """
        Return an object of the class ```Sequence```, which contains a sequence of qubit swaps. The sequence of controlled and uncontrolled
        rotations correspond to the InversePCCM.

        Returns
        -------

        sequence : geqo.core.Sequence
            An object of the class ```Sequence```  with controlled and uncontrolled rotation operations that correspond to the InversePCCM.
        """
        return self.pccm.getEquivalentSequence().getInverse()

    def getNumberQubits(self):
        """
        Return the number of qubits that are used by this InversePCCM operation.

        Returns
        -------
        2 : int
            The number of qubits, which are used by the InversePCCM.
        """
        return 2

    def getNumberClassicalBits(self):
        """
        Returns
        -------
        0 : int
            The number of classical bits, which are used by the InversePCCM, is zero.
        """
        return 0

    def hasDecomposition(self):
        """
        Returns
        -------
        True : Bool
            The InversePCCM can be decomposed into a sequence of rotation gates.
        """
        return True

    def isUnitary(self):
        """
        Returns
        -------
        True : Bool
            This is a unitary operation.
        """
        return True


def controlledXGate(numberControls, namePrefix=""):
    """Implement an ```PauliX``` gate, which is controlled by multiple qubits. It is implemented with
    Toffoli gates and one ancilla qubit. This method creates an exponential number of Toffoli gates in
    the number of control qubits. This function needs one ancilla qubit, which is assumed to be
    the last one in the order.

    Parameters
    ----------
        numberControls : int
            The number of control qubits for this gate.
        namePrefix : string
            This character string is prepended to all internally used definitions.

    Returns
    -------
        toffoli : geqo.gates.multi_qubit_gates.Toffoli
            An object of the class ```Toffoli``` that is used in the decomposition. Its internal name space prefix is set to the given prefix.
        controlledXGateInternal : geqo.core.quantum_circuit.Sequence
            A sequence with gates that correspond to the controlled ```PauliX``` gate.
    """
    controls = list(range(numberControls))
    ancilla = [numberControls + 1]
    target = [numberControls]
    toffoli = Toffoli(namePrefix)
    return toffoli, controlledXGateInternal(controls, ancilla, target, toffoli)


def controlledXGateInternal(controls, ancilla, target, toffoli):
    """
    Internal function for the function ```controlledXGate```.

    Parameters
    ----------
    other : An object, which should be compared to this object.

    Returns
    -------
    a : int
    """
    seq = []

    if len(controls) >= 3:
        buffer = controlledXGateInternal(
            controls[:-1], [controls[-1]], ancilla, toffoli
        )
        for b in buffer.gatesAndTargets:
            seq.append(b)
    else:
        seq.append(
            (
                QuantumControl([1] * (len(controls) - 1), PauliX()),
                controls[:-1] + ancilla,
                [],
            )
        )

    seq.append((toffoli, [controls[-1]] + ancilla + target, []))

    if len(controls) >= 3:
        buffer = controlledXGateInternal(
            controls[:-1], [controls[-1]], ancilla, toffoli
        )
        for b in buffer.gatesAndTargets:
            seq.append(b)
    else:
        seq.append(
            (
                QuantumControl([1] * (len(controls) - 1), PauliX()),
                controls[:-1] + ancilla,
                [],
            )
        )

    seq.append((toffoli, [controls[-1]] + ancilla + target, []))

    return Sequence(controls + target + ancilla, [], seq)


class Pattern:
    """This class helps create a database of patterns, which are used as replacements for parts of a circuit to reduce circuit depth.
    The lambda function is necessary for assisiting the `setValue` method in generating replacements."""

    def __init__(self, name, inputSequence, outputSequence, lambdas):
        """
        The constructor of this class takes a name as parameter, an input and an output sequence and a list of lambda functions.

        Parameters
        ----------
        name : String
            The name of the pattern.
        inputSequence : geqo.core.Sequence
            This sequence represents the pattern that we want to find in a circuit.
        outputSequence : geqo.core.Sequence
            This sequence contains the gates that are used to replace the matched input sequence.
        lambdas
            A list of lambda functions that allow to map the parameters of the input pattern to the parameters of an output pattern.

        Returns
        -------
        geqo.algorithms.Pattern
            An object of this class that corresponds to a pattern for replacing gates with other gates along with a list of lambda functions that map parameters of the input sequence to parameters of the output sequence.
        """
        self.name = name
        self.inputSequence = inputSequence
        self.outputSequence = outputSequence
        self.lambdas = lambdas

    def __repr__(self):
        """
        Returns a representation of the object as character string.
        -------
        string_representation : String
            Representation of the object as character string.
        """
        return (
            "Pattern #bits/#quits="
            + str(len(self.inputSequence.bits))
            + "/"
            + str(len(self.inputSequence.qubits))
            + " and #lamdbas="
            + str(len(self.lambdas))
        )

    def unificator(
        self,
        pattern: QuantumOperation,
        target: QuantumOperation,
        alreadyDefined: dict,
        alreadyDefinedQubits: dict,
        alreadyDefinedBits: dict,
    ):
        """
        This function unifies/matches the parameters associated with the same quantum operation.

        Parameters
        ----------
        pattern : A quantum operation in the pattern database.

        target: A quantum operation in the target circuit.

        alreadyDefined: A dictionary that stores the mapping between pattern paramters and target parameters.

        alreadyDefinedQubits: A dictionary that stores the mapping between pattern qubits and target qubits.

        alreadyDefinedBits: A dictionary that stores the mapping between pattern bits and target bits.

        Returns
        -------
        True/False : whether the unification of the pattern and target quantum operations is possible.

        alreadyDefined: updated mapping of pattern and target parameters.

        alreadyDefinedQubits: updated mapping of pattern and target qubits.

        alreadyDefinedBits: updated mapping of pattern and target bits.
        """
        # This cannot match at all.
        if type(pattern) is not type(target):
            return False, {}, {}, {}

        if type(pattern) in [BasicGate, InverseBasicGate]:
            print("check basic gate")
            if pattern.numberQubits != target.numberQubits:
                return False, {}, {}, {}
            if pattern.name in alreadyDefined:
                if alreadyDefined[pattern.name] == target.name:
                    # Variable already defined and it is a match.
                    return (
                        True,
                        alreadyDefined,
                        alreadyDefinedQubits,
                        alreadyDefinedBits,
                    )
                else:
                    # We have a defined variable, but a mismatch
                    return False, {}, {}, {}
                # not already defined, so define it.
            else:
                alreadyDefined[pattern.name] = target.name
                print("add pattern.name/target.name=", pattern.name, target.name)
                return True, alreadyDefined, alreadyDefinedQubits, alreadyDefinedBits

        elif type(pattern) in [
            CNOT,
            SwapQubits,
            PauliX,
            PauliY,
            PauliZ,
            Hadamard,
            Toffoli,
        ]:
            # Same type is guaranteed above. No parameters to match.
            return True, alreadyDefined, alreadyDefinedQubits, alreadyDefinedBits

        elif type(pattern) is Sequence:
            print("check sequence")
            # Also the bits, qubits and further parameters must match.
            # We assume that the bits and qubits are in both cases 0 and 1. This must be guaranteed in the
            # pattern extractor method (remapping of names to indices).

            if len(pattern.bits) != len(target.bits):
                return False, {}, {}, {}
            if len(pattern.qubits) != len(target.qubits):
                return False, {}, {}, {}
            if len(pattern.gatesAndTargets) != len(target.gatesAndTargets):
                return False, {}, {}, {}

            for ix in range(len(pattern.gatesAndTargets)):
                print("run ix=", ix)
                # Two or three tuples must be the same.
                if len(pattern.gatesAndTargets[ix]) != len(target.gatesAndTargets[ix]):
                    return False, {}, {}, {}

                # check the single targets first
                patternQubits = pattern.gatesAndTargets[ix][1]
                targetQubits = target.gatesAndTargets[ix][1]
                for ip in range(len(patternQubits)):
                    p = patternQubits[ip]
                    t = targetQubits[ip]
                    if p not in alreadyDefinedQubits:
                        print("set qubits", p, "to value", t)
                        alreadyDefinedQubits[p] = t
                    elif alreadyDefinedQubits[p] != t:
                        print(
                            "mismatch already/target qubits:",
                            alreadyDefinedQubits[p],
                            t,
                        )
                        return False, {}, {}, {}  # not matching in targets
                    # else: everything is ok, continue

                if len(pattern.gatesAndTargets[ix]) == 3:
                    if pattern.gatesAndTargets[ix][2] != target.gatesAndTargets[ix][2]:
                        return False, {}, {}, {}

                patternGate = pattern.gatesAndTargets[ix][0]
                targetGate = target.gatesAndTargets[ix][0]
                res1, res2, resQ, resC = self.unificator(
                    patternGate,
                    targetGate,
                    alreadyDefined,
                    alreadyDefinedQubits,
                    alreadyDefinedBits,
                )
                print("res1/res2=", res1, res2)
                if res1 is False:
                    return False, {}, {}, {}
                else:
                    alreadyDefined = res2
                    alreadyDefinedQubits = resQ
                    alreadyDefinedBits = resC
        else:
            raise Exception("gate not supported:", pattern)
        return True, alreadyDefined, alreadyDefinedQubits, alreadyDefinedBits

    def replace_recursion(
        self,
        pattern: QuantumOperation,
        substitutions: dict,
        substitutionsQ: dict,
        substitutionsC: dict,
    ):
        """
        This function replaces the pattern quantum operation with the quantum operation stored in `substitutions`.

        Parameters
        ----------
        pattern : A quantum operation in the pattern database.

        substitutions: A dictionary that stores the matching/unified parameter pairs.

        substitutionsQ: A dictionary that stores the matching/unified qubit pairs.

        substitutionsC: A dictionary that stores the matching/unified bit pairs.

        Returns
        -------
        QuantumOperation: The output quantum operation with the replaced parameters.
        """
        print("replace_recursion called for", pattern)
        if type(pattern) is BasicGate:
            # only substitute if it is not a new one
            print("replace basic gate")
            if pattern.name in substitutions:
                return BasicGate(substitutions[pattern.name], pattern.numberQubits)
            else:
                return BasicGate(pattern.name, pattern.numberQubits)
        elif type(pattern) is InverseBasicGate:
            # only substitute if it is not a new one
            print("replace inverse basic gate")
            if pattern.name in substitutions:
                return InverseBasicGate(
                    substitutions[pattern.name], pattern.numberQubits
                )
            else:
                return InverseBasicGate(pattern.name, pattern.numberQubits)
        elif type(pattern) is Sequence:
            newGatesAndTargets = []
            for i in range(len(pattern.gatesAndTargets)):
                currentGateAndTargets = pattern.gatesAndTargets[i]
                newGate = self.replace_recursion(
                    currentGateAndTargets[0],
                    substitutions,
                    substitutionsQ,
                    substitutionsC,
                )
                newGatesAndTargets.append(
                    (
                        newGate,
                        [substitutionsQ[x] for x in currentGateAndTargets[1]],
                        [substitutionsC[x] for x in currentGateAndTargets[2]],
                    )
                )
                """if len(currentGateAndTargets) == 2:
                    newGatesAndTargets.append(
                        (newGate, [substitutionsQ[x] for x in currentGateAndTargets[1]])
                    )
                else:
                    newGatesAndTargets.append(
                        (
                            newGate,
                            [substitutionsQ[x] for x in currentGateAndTargets[1]],
                            [substitutionsC[x] for x in currentGateAndTargets[2]],
                        )
                    )"""
            return Sequence(
                [substitutionsQ[x] for x in pattern.qubits],
                [substitutionsC[x] for x in pattern.bits],
                newGatesAndTargets,
            )
        elif type(pattern) in [
            CNOT,
            SwapQubits,
            PauliX,
            PauliY,
            PauliZ,
            Hadamard,
            Toffoli,
        ]:
            return pattern
        else:
            raise Exception("gate not supported:", pattern)

    def replacer(self, target: Sequence):
        """
        This function transforms the output sequence of the `Pattern` instance by substituting its parameters
        based on the mapping from the input sequence to the target sequence.

        Parameters
        ----------
        target: The sequence the forms the matching parameter (and qubit) pair with the input sequence of the `Pattern` instance.

        Returns
        -------
        replacerPatternSubst: Updated output sequence with the replaced parameters.

        res2: The mapping between the input sequence and the target sequence used for parameter substitution.
        """
        res1, res2, resQ, resC = self.unificator(self.inputSequence, target, {}, {}, {})
        print("res1/res2/resQ/resC=", res1, res2, resQ, resC)
        if res1 is False:
            return False

        # Replace everything in the replacement pattern with the found variables.
        replacerPattern = self.outputSequence

        replacerPatternSubst = self.replace_recursion(replacerPattern, res2, resQ, resC)
        return replacerPatternSubst, res2


def findLongestRunSequence(
    seq: Sequence, start: int, qubits: list[int], verbose: bool = False
):
    """
    This function scans through the given sequnce and picks out gates whose qubits are:
    1. among the specified target qubits and
    2. not among the qubits involved with the previous operations that contain a non-specified qubit.
    Ex.1 Given the Sequence([],["0","1","2"],[ (Hadamard(),["0"]), (Hadamard(), ["1"]), (CNOT(),["1","2"]), (Hadamard(),["0"])])
    and the specified target qubits ["0","1"], the function picks out [(Hadamard(), ['0']), (Hadamard(), ['1']), (Hadamard(), ['0'])]
    Ex.2 Given the Sequence([],[0,1,2,3],[ (Hadamard(),[0]), (CNOT(),[1,2]), (CNOT(),[2,3]), (CNOT(),[0,2]), (Hadamard(),[0]), (Hadamard(),[1])])
    and the specified target qubits [0,1,2], the function picks out [(Hadamard(), [0]), (CNOT(), [1, 2]), (Hadamard(), [1])], since
    (CNOT(),[2,3]) contains the non-specified qubit 3, and (CNOT(),[0,2]), (Hadamard(),[0]) both contain a qubit (2 and 0) that is involved with
    the previous operation that have a non-specified qubit 3.

    Parameters
    ----------
    seq: The sequence to be scanned.

    start: The starting index of the scan.

    qubits: The specified target qubits.

    verbose: Whether to display scan messages.

    Returns
    -------
    Sequence: The sequence containig the selected gates.

    gatheredIndices: The indices of the selected gates in the scanned sequence.

    """
    currentIndex = start
    gatheredIndices = []
    burnedQubits = []

    while currentIndex < len(seq.gatesAndTargets):
        if verbose:
            print(
                "start loop at index", currentIndex, "with burned qubits:", burnedQubits
            )
        currentGateAndTargets = seq.gatesAndTargets[currentIndex]

        currentGate = currentGateAndTargets[0]
        currentBits = []
        currentQubits = []
        if len(currentGateAndTargets) == 3:
            currentQubits = currentGateAndTargets[1]
            currentBits = currentGateAndTargets[2]
        else:
            raise Exception("not 3 elements as gate and target definition in Sequence")
        """if len(currentGateAndTargets) == 2:
            currentQubits = currentGateAndTargets[1]
        elif len(currentGateAndTargets) == 3:
            currentQubits = currentGateAndTargets[1]
            currentBits = currentGateAndTargets[2]
        else:
            raise Exception(
                "not 2 or 3 elements as gate and target definition in Sequence"
            )"""

        if verbose:
            print(
                "now consider gate",
                currentGate,
                "at position",
                currentIndex,
                "with bits/qubits",
                currentBits,
                currentQubits,
            )

        # Does this gate touch the relevant bits?
        if len(set(currentQubits).intersection(qubits)) == 0:
            # This gate has nothing to do with our scanned qubits. Just skip it.
            if verbose:
                print("no relevant target qubit here")
        else:
            # Check if we touch burned qubits.
            touchedBurnedQubits = set(burnedQubits).intersection(currentQubits)
            if verbose:
                print("we touch these burned qubits:", touchedBurnedQubits)

            # Do we have no burned qubits?
            burnQubits = []
            for x in currentQubits:
                if x not in qubits:
                    burnQubits.append(x)
            if verbose:
                print("we burn these qubits:", burnQubits)

            if len(touchedBurnedQubits) == 0 and len(burnQubits) == 0:
                if verbose:
                    print("we can add this index to result:", currentIndex)
                gatheredIndices.append(currentIndex)
            else:
                # we have burned qubits or we touched burned qubits. We must add
                # all qubits of this gate to burnedQubits
                if verbose:
                    print(
                        "we touched a burned qubit or we have burned qubits, now burn current qubits:",
                        currentQubits,
                    )
                for q in currentQubits:
                    if q not in burnedQubits:
                        burnedQubits.append(q)

            # We must add the burned qubits anyways, even if we have already burned qubits.
            # for b in burnQubits:
            #    burnedQubits.append(b)
        if verbose:
            print("finished with burnedQubits", burnedQubits, "and index", currentIndex)
        currentIndex += 1

    # Construct the new sequence. All indices must be reduced to 0,1,2...
    newGatesAndTargets = []
    for g in gatheredIndices:
        currentGateAndTarget = seq.gatesAndTargets[g]
        newGatesAndTargets.append(
            (
                currentGateAndTarget[0],
                currentGateAndTarget[1],
                currentGateAndTarget[2],
            )
        )
        """if len(currentGateAndTarget) == 2:
            newGatesAndTargets.append(
                (currentGateAndTarget[0], currentGateAndTarget[1])
            )
        elif len(currentGateAndTarget) == 3:
            newGatesAndTargets.append(
                (
                    currentGateAndTarget[0],
                    currentGateAndTarget[1],
                    currentGateAndTarget[2],
                )
            )"""

    return Sequence(qubits, seq.bits, newGatesAndTargets), gatheredIndices


def getAllLongestRuns(sequence: Sequence, numberQubits: int, verbose: bool = False):
    """
    This function scans through the whole sequence in search of potential patterns.
    The search covers all possible `numberQubits`-combinations of target qubits and
    progressively accumulates the longest valid subsequences from the beginning of the sequence.

    Parameters
    ----------
    sequence: The sequence to be scanned.

    numberQuibits: The number of qubits in a combination.

    verbose: Whether to display scan messages.

    Returns
    -------
    candidates: All valid qubit combinations and gate indices that could potentially become patterns.

    gatheredIndices: The indices of the selected gates in the scanned sequence.

    """
    # We only need combinations. The permutations are not necessary because they
    # can be treated with unification.
    candidates = []

    for x in combinations(sequence.qubits, r=numberQubits):
        if verbose:
            print("scan qubits", x)
        currentStartPosition = 0
        while currentStartPosition < len(sequence.gatesAndTargets):
            subseq, indexes = findLongestRunSequence(sequence, currentStartPosition, x)
            if verbose:
                print("longest run:", indexes)
            if len(indexes) > 0:
                # We did find at least one gate in the longest run
                candidates.append((x, indexes))
                currentStartPosition = max(indexes) + 1
            else:
                # there is not a single useful gate on the scanned qubits; we might have to
                # skip until we find something again. The single-Stepping here is not efficient at
                # all, but we have to find the first suitable gate.
                currentStartPosition = currentStartPosition + 1
    return candidates


def getAllRuns(
    sequence: Sequence, numberQubits: int, numberGates: int, verbose: bool = False
):
    """
    This function resembles the `getAllLongestRuns` function, except that it imposes a length constraint `numberGates` on the accumulated subsequences.

    Parameters
    ----------
    sequence: The sequence to be scanned.

    numberQuibits: The number of qubits in a combination.

    numberGates: The number of gates in a subsequence.

    verbose: Whether to display scan messages.

    Returns
    -------
    newCandidates: The updated list of candidates that contain exactly `numberGates` gates in the subsequences.

    """
    candidates = getAllLongestRuns(sequence, numberQubits, verbose)

    newCandidates = []
    for cand in candidates:
        candQubits = cand[0]
        candGates = cand[1]
        if len(candGates) >= numberGates:
            if verbose:
                print(
                    "processing candidate",
                    cand,
                    "len(candGates)/numberGates",
                    len(candGates),
                    numberGates,
                )
                for i in range(0, len(candGates) - numberGates + 1):
                    c = []
                    for j in range(numberGates):
                        c.append(candGates[i + j])
                    print("new candidate:", (candQubits, c))
                    newCandidates.append((candQubits, c))
    return newCandidates


def unitaryDecomposer(u, decompose_givens: bool = False):
    """
    This function decomposes an arbitrary unitary matrix `u` into an equivalent sequence with Toffoli, controlled-rotation, and controlled-phase gates

    Parameters
    ----------
    u: The unitary matrix to be decomposed.

    decompose_givens: Whether to decompose the Givens rotation into Ry Rz gates.

    Returns
    -------
    seq: The decomposed Sequence instance.

    params: A dictionary storing the parameter values of the sequence.
    """
    try:
        import numpy as np
    except ImportError:
        raise ImportError(
            "NumPy package is required for the `unitaryDecomposer` function."
        )

    u = np.array(u).astype(np.complex128)
    u = np.conj(u.T)
    n = int(np.log2(len(u)))

    params = {}

    op = []
    for i in range(2**n):
        for j in range(i + 1, 2**n):
            # submatrix_ij = [[a,r0],[b,r1]]
            a = u[i, i]
            b = u[j, i]
            r0 = u[
                i, j
            ]  # r0 r1 are info for phase correction on the diagonal after applying G
            r1 = u[j, j]
            if (
                np.abs(b) < 1e-9
            ):  # no need to eliminate if the b is already 0  (avoid numerical error so we set 1e-9)
                continue
            norm = np.sqrt(np.abs(a) ** 2 + np.abs(b) ** 2)
            c = a / norm
            s = b / norm

            if (
                decompose_givens
            ):  # express Givens operator with U(θ,φ,λ) = Rz(φ)Ry(θ)Rz(λ)
                abs_c_val = min(
                    1.0, np.abs(c)
                )  # prevent c from exceeding 1 (due to numerical errors)
                theta = 2 * np.arccos(abs_c_val)
                phi = np.angle(c) + np.angle(s) + np.pi
                lam = np.angle(c) - np.angle(s) - np.pi
                if np.abs(theta) > 1e-3:
                    params[f"θ{i}{j}"] = theta
                if np.abs(phi) > 1e-3:
                    params[f"φ{i}{j}"] = phi
                if np.abs(lam) > 1e-3:
                    params[f"λ{i}{j}"] = lam
            else:
                G = np.array([[np.conj(c), np.conj(s)], [-s, c]])
                params[f"G{i}{j}"] = G

            correction_phase_after_G = -np.angle(-s * r0 + c * r1)
            if abs(float(correction_phase_after_G)) > 1e-3:
                params[f"g{i * 2**n + j}"] = correction_phase_after_G

            ibin = num2bin(i, n)
            jbin = num2bin(j, n)
            cnot_pair = []
            first_diff = None
            for k in range(n):
                if ibin[k] != jbin[k] and first_diff is None:
                    first_diff = k
                elif ibin[k] != jbin[k]:
                    cnot_pair.append([first_diff, k])

            for pair in cnot_pair:
                op.append((CNOT(), pair, []))

            if ibin[first_diff] == 0:
                ctrl_bits = ibin
            else:
                ctrl_bits = jbin
            del ctrl_bits[first_diff]

            targets = [*range(n)]
            targets.pop(first_diff)
            # apply U
            if n == 1:
                if np.abs(lam) > 1e-3:
                    op.append(
                        (
                            Rz(f"λ{i}{j}"),
                            targets + [first_diff],
                            [],
                        )
                    )
                if np.abs(theta) > 1e-3:
                    op.append(
                        (
                            Ry(f"θ{i}{j}"),
                            targets + [first_diff],
                            [],
                        )
                    )
                if np.abs(phi) > 1e-3:
                    op.append(
                        (
                            Rz(f"φ{i}{j}"),
                            targets + [first_diff],
                            [],
                        )
                    )
                if np.abs(correction_phase_after_G) > 1e-3:
                    op.append(
                        (
                            Phase(f"g{i * 2**n + j}"),
                            targets + [first_diff],
                            [],
                        )
                    )
            else:  # n >1
                if decompose_givens:
                    if np.abs(lam) > 1e-3:
                        op.append(
                            (
                                QuantumControl(ctrl_bits, Rz(f"λ{i}{j}")),
                                targets + [first_diff],
                                [],
                            )
                        )
                    if np.abs(theta) > 1e-3:
                        op.append(
                            (
                                QuantumControl(ctrl_bits, Ry(f"θ{i}{j}")),
                                targets + [first_diff],
                                [],
                            )
                        )
                    if np.abs(phi) > 1e-3:
                        op.append(
                            (
                                QuantumControl(ctrl_bits, Rz(f"φ{i}{j}")),
                                targets + [first_diff],
                                [],
                            )
                        )
                else:
                    op.append(
                        (
                            QuantumControl(ctrl_bits, BasicGate(f"G{i}{j}", 1)),
                            targets + [first_diff],
                            [],
                        )
                    )

                # phase correction after G
                if np.abs(correction_phase_after_G) > 1e-3:
                    op.append(
                        (
                            QuantumControl(ctrl_bits, Phase(f"g{i * 2**n + j}")),
                            targets + [first_diff],
                            [],
                        )
                    )

            for pair in reversed(cnot_pair):
                op.append((CNOT(), pair, []))

            # update u value (apply G and correction Phase after G)
            A = np.identity(2**n, dtype=complex)  # embed G
            A[i, i] = np.conj(c)
            A[i, j] = np.conj(s)
            A[j, i] = -s
            A[j, j] = c

            B = np.identity(2**n, dtype=complex)  # embed Phase correction
            B[j, j] = np.exp(1j * correction_phase_after_G)

            u = A @ u
            u = B @ u

    seq = Sequence([*range(n)], [], op)
    if len(seq.gatesAndTargets) == 0:
        print("The input matrix is identity. Now decomposition is required.")

    return seq, params


def stateInitialize(state):
    """
    This function initializes the circuit to a given statevector by applying a set of unitary operations to the [1,0,0,...] state

    Parameters
    ----------
    state: The target statevector.

    Returns
    -------
    seq: The sequence of unitary operations that prepares the target statevector.

    params: A dictionary storing the parameter values of the sequence.
    """
    try:
        import numpy as np
    except ImportError:
        raise ImportError("NumPy is required for the `stateInitialize` function.")

    state = np.array(state)
    n = len(state.flatten())
    if not np.log2(n).is_integer():
        raise ValueError("the number of entries in the state must be a power of 2.")

    state = state.reshape(n, 1)
    # Use Householder reflection to construct an unitary whose first column corresponds to the given statevector
    e = np.zeros((n, 1), dtype=np.complex128)
    e[0] = 1.0
    w = state - e
    u = np.identity(n) - 2 * (w @ np.conj(w).T) / (np.conj(w).T @ w)[0]

    seq, params = unitaryDecomposer(u, decompose_givens=True)

    return seq, params


def decompose_mcx(onoff: list[int], targets: list[int], num_qubits: int):
    """
    This function decomposes a multi-controlled X (MCX) gate into a sequence of Toffoli gates. The method is based on Barenco et al. (1995) Lemma 7.2

    Parameters
    ----------
    onoff: The list of control conditions.

    targets: Indices of the target qubits for the MCX gate.

    num_quits: Total number of qubits in the circuit where the gate is embedded.

    Returns
    -------
    seq: The decomposed Sequence instance.
    """
    m = len(onoff)

    if m > math.floor(num_qubits / 2):
        raise ValueError(
            f"maximum number of control qubits is {math.floor(num_qubits / 2)}."
        )
    if m < 3:
        raise ValueError("minimum number of control qubits is 3.")

    last_ctrl = m - 1

    ctrls = targets[:-1]
    idle = [i for i in range(num_qubits) if i not in targets]

    mapping = [0] * num_qubits
    mapping[:m] = ctrls
    mapping[m : num_qubits - 1] = idle
    mapping[num_qubits - 1] = targets[-1]

    op = [(PauliX(), [t], []) for idx, t in enumerate(targets[:-1]) if onoff[idx] == 0]

    op.append(
        (Toffoli(), [mapping[last_ctrl], mapping[2 * last_ctrl - 1], mapping[-1]], [])
    )
    for i in reversed(range(last_ctrl - 2)):
        op.append(
            (
                Toffoli(),
                [
                    mapping[2 + i],
                    mapping[last_ctrl + 1 + i],
                    mapping[last_ctrl + 2 + i],
                ],
                [],
            )
        )
    op.append((Toffoli(), [mapping[0], mapping[1], mapping[last_ctrl + 1]], []))

    for i in range(last_ctrl - 2):
        op.append(
            (
                Toffoli(),
                [
                    mapping[2 + i],
                    mapping[last_ctrl + 1 + i],
                    mapping[last_ctrl + 2 + i],
                ],
                [],
            )
        )
    op.append(
        (Toffoli(), [mapping[last_ctrl], mapping[2 * last_ctrl - 1], mapping[-1]], [])
    )

    for i in reversed(range(last_ctrl - 2)):
        op.append(
            (
                Toffoli(),
                [
                    mapping[2 + i],
                    mapping[last_ctrl + 1 + i],
                    mapping[last_ctrl + 2 + i],
                ],
                [],
            )
        )
    op.append((Toffoli(), [mapping[0], mapping[1], mapping[last_ctrl + 1]], []))
    for i in range(last_ctrl - 2):
        op.append(
            (
                Toffoli(),
                [
                    mapping[2 + i],
                    mapping[last_ctrl + 1 + i],
                    mapping[last_ctrl + 2 + i],
                ],
                [],
            )
        )

    op.extend(
        [(PauliX(), [t], []) for idx, t in enumerate(targets[:-1]) if onoff[idx] == 0]
    )

    seq = Sequence([*range(num_qubits)], [], op)

    return seq


def Shor(N: int, a: int, decompose: bool = False):
    """
    This function generates the quantum circuit for the Shor's algorithm.

    Parameters
    ----------
    N: The target integer to be factorized.

    a: The chosen base integer coprime to N.

    decompose: Whether to decompose larger gates (i.e. MCX, controlled-swap, and QFT) in the sequence.

    Returns
    -------
    shor_seq: The Shor's Sequence instance.
    """
    if math.gcd(a, N) != 1:
        raise ValueError(f"Please choose an 'a' comprime to {N}")

    n = math.floor(math.log2(N)) + 1
    powers = [f"p{i}" for i in range(n)]
    xreg = [f"x{i}" for i in range(n)]
    ancilla = [f"an{i}" for i in range(n)]
    measures = [f"c{i}" for i in range(n)]

    # Initialization
    op = [(PauliX(), [xreg[-1]], [])]
    op.extend([(Hadamard(), [powers[i]], []) for i in range(n)])

    # modular exponentiation
    for p in range(n):
        # CMULT(a) mod N
        A = a ** (2 ** (n - 1 - p))
        add_values = [(A * 2**j) % N for j in range(n - 1, -1, -1)]
        for i in range(n):  # iterate over xreg
            add_bits = num2bin(add_values[i], n)
            for idx, b in enumerate(
                add_bits
            ):  # iterate over binary representation of add_bits
                if b == 1:  # perform addition if the bit value is 1
                    for j in range(idx + 1):  # target qubit index
                        op.append(
                            (
                                QuantumControl([1] * (1 + 1 + idx - j), PauliX()),
                                [powers[p]]
                                + [xreg[i]]
                                + ancilla[j + 1 : idx + 1]
                                + [ancilla[j]],
                                [],
                            )
                        )
        # swap
        op.extend(
            [
                (
                    QuantumControl([1], SwapQubits()),
                    [powers[p], xreg[k], ancilla[k]],
                    [],
                )
                for k in range(n)
            ]
        )

        # inverse CMULT(a^-1) mod N
        inv_A = pow(A, -1, N)  # modular multiplicative inverse of a
        minus_values = [(inv_A * 2**j) % N for j in range(n - 1, -1, -1)]

        for i in reversed(range(n)):
            minus_bits = num2bin(minus_values[i], n)
            for idx in reversed(range(n)):
                b = minus_bits[idx]
                if b == 1:  # perform subtraction if the bit value is 1
                    for j in reversed(range(idx + 1)):  # target qubit index
                        op.append(
                            (
                                QuantumControl([1] * (1 + 1 + idx - j), PauliX()),
                                [powers[p]]
                                + [xreg[i]]
                                + ancilla[j + 1 : idx + 1]
                                + [ancilla[j]],
                                [],
                            )
                        )

    # inverse QFT
    op.append((InverseQFT(n), powers, []))

    op.append((Measure(n), powers, measures))
    shor_seq = Sequence(powers + xreg + ancilla, measures, op)

    # decompose  MCX, controlled-swap, and QFT gates in Shor
    if decompose:
        op = []
        count = 0
        for gnt in shor_seq.gatesAndTargets:
            gate = gnt[0]
            targets = gnt[1]
            if isinstance(gate, QuantumControl):
                if isinstance(gate.qop, SwapQubits):  # control swap gates
                    op.append((Toffoli(), targets, []))
                    op.append((Toffoli(), [targets[0], targets[2], targets[1]], []))
                    op.append((Toffoli(), targets, []))
                elif len(gate.onoff) == 2:  # Toffoli gates
                    op.append((Toffoli(), targets, []))
                else:  # more than 2 controls
                    if type(targets[0]) is str:  # turn targets into integer indices
                        int_targets = [shor_seq.qubits.index(t) for t in targets]
                    else:
                        int_targets = targets
                    seq = decompose_mcx(gate.onoff, int_targets, len(shor_seq.qubits))
                    seq.name = f"s{count}"
                    count += 1
                    op.append((seq, shor_seq.qubits, []))
            elif isinstance(gate, InverseQFT):
                qft_seq = gate.getEquivalentSequence()
                op.append((qft_seq, targets, []))
            else:
                op.append(gnt)

        shor_seq = Sequence(shor_seq.qubits, shor_seq.bits, op)
        shor_seq = embedSequences(shor_seq)

    return shor_seq
