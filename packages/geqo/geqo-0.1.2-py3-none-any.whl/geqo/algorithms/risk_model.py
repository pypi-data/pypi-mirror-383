import math

import numpy as np

from geqo.core.quantum_circuit import Sequence
from geqo.gates import Ry
from geqo.operations.controls import QuantumControl

"""def getRY(phi):
    return  sym.Matrix(
        [
            [sym.cos(phi / 2), -sym.sin(phi / 2)],
            [sym.sin(phi / 2), sym.cos(phi / 2)],
        ]
    )"""


def RiskModel(
    node_probs: dict,
    edge_probs: dict,
):
    """Creates a quantum circuit implementation of the business risk model
    defined by a probabilistic network. The underlying graph of the network
    has to be a directed acyclic graph.

    Input:

        node_probs: dictionary with the nodes as keys and their
            intrinsic probabilities as values

        edge_probs: dictionary with edges as keys and the corresponding
            transition probabilities as values

    Output:

        Quantum circuit implementation of the network and dictionary to
        prepare the SymPy simulator.


    """
    collectedValues = {}

    nodes = list(node_probs.keys())

    gatelist = []

    # Write probabilities for nodes and edges into matrix
    mat = np.zeros((len(nodes), len(nodes)))
    for i in range(len(nodes)):
        mat[i][i] = node_probs[nodes[i]]
    for i in range(len(nodes)):
        for j in range(len(nodes)):
            if (nodes[i], nodes[j]) in edge_probs:
                mat[i][j] = edge_probs[(nodes[i], nodes[j])]

    # Main processing loop.
    indicesProcessed = []
    while len(indicesProcessed) < len(nodes):
        # Find the first unprocessed node that has no unprocessed parents.
        target = None
        for i in range(len(nodes)):
            allParentsAlreadyProcessed = True
            for j in range(len(nodes)):
                if not (i == j) and (mat[j][i] != 0) and j not in indicesProcessed:
                    allParentsAlreadyProcessed = False
            if i not in indicesProcessed and allParentsAlreadyProcessed is True:
                target = i
                break
        indicesProcessed.append(target)

        # In case of a cycle
        if target is None:
            raise BaseException("""Network may not have cycles.""")

        # collecting all parant nodes of the current target
        foundControllers = False
        collectedControllerIndices = []
        for y in range(len(nodes)):
            if mat[y, target] != 0 and not (y == target):
                foundControllers = True
                collectedControllerIndices.append(y)

        if foundControllers is False:
            # This risk item is not triggered by transitions.
            # Just put an uncontrolled gate in for it
            phi = 2 * math.asin(math.sqrt(mat[target, target]))
            # newValue = getRY(phi)
            gatelist.append((Ry(f"Φ{target}"), [str(target)], []))
            collectedValues[f"Φ{target}"] = phi
            # qc.ry(2 * math.asin(math.sqrt(mat[target, target])), qr[target])
        else:
            # This risk item is triggered by one or more other risk items.
            controllist = []
            for i in range(len(collectedControllerIndices)):
                controllist.append(collectedControllerIndices[i])
            controllist.append(target)

            # initializing at inherent probability
            phi = 2 * math.asin(math.sqrt(mat[target, target]))
            gatelist.append((Ry(f"Φ{target}"), [str(target)], []))
            collectedValues[f"Φ{target}"] = phi

            # Iterate over all subsets of control qubits using binary configurations
            for i in range(1, 2 ** len(collectedControllerIndices)):
                cts = format(i, "0" + str(len(collectedControllerIndices)) + "b")

                # calculate the probability that the target node is not triggered
                # given that all nodes in the subset have been triggered and all other
                # control qubits have not
                pTargetOff = 1 - mat[target, target]
                for j in range(len(collectedControllerIndices)):
                    if cts[j] == "1":
                        pTargetOff = pTargetOff * (
                            1 - mat[collectedControllerIndices[j], target]
                        )

                # For this configuration of control qubits, turn the qubit on with
                # the probability 1-pTargetOff, but substract the angle it was
                # initialized in
                theta = 2 * math.asin(math.sqrt(1 - pTargetOff)) - 2 * math.asin(
                    math.sqrt(mat[target, target])
                )
                gatelist.append(
                    (
                        QuantumControl(
                            [int(s) for s in cts],
                            Ry(f"θ{target}"),
                        ),
                        [str(x) for x in controllist],
                        [],
                    )
                )
                collectedValues[f"θ{target}"] = theta

    return Sequence(
        [str(x) for x in list(range(len(nodes)))], [], gatelist, "Risk"
    ), collectedValues
