# geqo
geqo is a framework for constructing and describing quantum circuits and executing them on simulators and on quantum hardware devices.

The documentation can be found [here](https://geqo.jos-quantum.de/intro.html).

## Quick installation and testing
1. clone the repository: `git clone https://github.com/JoSQUANTUM/geqo`
2. create a virtual environment: `python -m venv geqo-env`
3. enable environment: `source geqo-env/bin/activate`
4. install geqo with all options: `pip install geqo/[sympy,numpy,cupy,visualization,dev]`
5. optional: run unit tests: `python -m pytest geqo/tests/`

geqo is also available on [PyPI](https://pypi.org/project/geqo/). To install from PyPI just create
and activate an environment with steps 2 and 3 and then install geqo with
`pip install geqo[sympy,numpy,cupy,visualization,dev]`.

## Running a simple example
- the example task is to get unitary of a quantum circuit for the EPR pair generation
- start Python in the environment from the steps above
- run the following commands:

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

