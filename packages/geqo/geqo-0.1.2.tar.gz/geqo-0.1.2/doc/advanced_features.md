# Advanced features of geqo

The following notebooks explain several features, with are specific to geqo and are useful for the construction of complex quantum circuits.

- **Name Space Prefixes**: Some pre-defined gates in geqo are internally composed of several other gates, which might have parameters. To avoid naming conflicts, a name space prefix can be provided to the relevant gate constructors in order to avoid double-using names.
- **Calculation of the Partial Trace**: The partial trace is used to calculate the resulting density matrix of a system if one or more qubits are dropped.
- **Decomposition of gates with many controls**: Many hardware implementations of quantum computers have basic gates, which act on a small number of qubits only. To execute gates with a high number of control qubits, a decomposition is necessary. In this notebook, the decomposition of a highly controlled ```PauliX``` gate into Toffoli gates is studied.
