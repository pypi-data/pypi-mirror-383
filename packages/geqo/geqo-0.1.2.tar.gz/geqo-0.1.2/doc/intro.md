# geqo
geqo is a framework for constructing and describing quantum circuits and executing them on simulators and on quantum hardware devices.

## Quick installation and testing
1. clone the repository: `git clone https://github.com/JoSQUANTUM/geqo`
2. create a virtual environment: `python3 -m venv geqo-test`
3. enable environment: `source geqo-test/bin/activate`
4. install geqo with all options: `pip3 install -e geqo/[sympy,numpy,cupy,visualization,dev]`
5. optional: run unit tests: `python -m pytest geqo/tests/`

geqo is also available on [PyPI](https://pypi.org/project/geqo/). To install from PyPI just create
and activate an environment with steps 2 and 3 and then install geqo with
`pip install geqo[sympy,numpy,cupy,visualization,dev]`.

## Running a simple example
Running a simple example: start Python in the environment and get unitary of a quantum circuit for the EPR pair generation:
```
from geqo.gates import Hadamard, CNOT
from geqo.core import Sequence
seq=Sequence(["q1","q2"],[], [ (Hadamard(),["q1"], []), (CNOT(), ["q1","q2"], []) ])

from geqo.simulators import simulatorUnitarySymPy
sim=simulatorUnitarySymPy(2)
sim.apply(seq,[0,1])
sim.u
```

The expected result is
```
Matrix([
[sqrt(2)/2,         0,  sqrt(2)/2,          0],
[        0, sqrt(2)/2,          0,  sqrt(2)/2],
[        0, sqrt(2)/2,          0, -sqrt(2)/2],
[sqrt(2)/2,         0, -sqrt(2)/2,          0]])
```

## Why a new framework for quantum circuits?
Quantum circuits serve as a general model for quantum computations, employing abstract concepts like bit flips or rotations with
specific angles on qubits.

In practical applications, circuits are executed on a variety of backends, including different numerical or symbolic simulators, as well as various quantum hardware systems. Each of these backends typically has a unique method for representing a given operation
and its parameters.

Consequently, it is desirable to encode quantum circuits using an abstract, representation-independent language. This is precisely the function of geqo. The separation between the circuit description and the concrete backend representation minimizes dependencies on other software packages, keeps geqo lightweight and facilitates easy extension and customization.

## Features
* quantum circuit construction (e.g. basic gates, controlled gates, measurements, classical and quantum control)
* simulators for numerical and symbolic evaluation of circuits, density matrices, state vectors, measurement results
* converter for OpenQASM3
* based on Python with a minimum set of dependencies
* extendible and customizable

## Installation
Instructions for the installation of geqo can be found [here](installation.md).

## Getting started
A great place to start exploring how geqo allows you to build and simulate quantum circuits is our [Introduction](notebooks/Introduction0.ipynb) section.

## API reference
The API has an extensive documentation. Start [here](api-reference.md) to dive into the geqo API.

## Support and contribution
Please contact us under the email address support@jos-quantum.de.
