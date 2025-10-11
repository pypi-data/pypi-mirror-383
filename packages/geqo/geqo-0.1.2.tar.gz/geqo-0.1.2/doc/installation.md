# Installation

The geqo package can be installed by cloning the repository and
installing it with a package manager. These steps are explained in the following
sections in more detail.

## Clone the repository
```bash
git clone https://github.com/JoSQUANTUM/geqo
```
## Installation with pip or uv
geqo supports two package managers for installation: pip and uv.

### Installation with pip
The following command installs geqo with all options. The available options are explained in the corresponding section below.

The command has to be executed in the geqo folder obtained by the clone command in the previous step.
```bash
pip install -e .[dev,visualization,sympy,numpy,cupy]
```
### Installation with uv
The file `pyproject.toml` is configured to support uv. To install geqo with the two
installation options `visualization` and `sympy` run
```bash
uv sync --extra visualization --extra sympy
```
The available options are explained in the corresponding section below.

## Installation options
The geqo package supports the following optional installation extras:

 - `dev`: Includes development dependencies, such as testing and linting tools.
 - `visualization`: Includes functions for data visualization. This includes functions to plot quantum circuits in both LaTeX and Matplotlib, as well as create bar plots for measurement outcomes
 - `sympy`: Includes the SymPy library for symbolic mathematics. This enables the use of SymPy-based simulators for symbolic math operations.
 - `numpy`: Includes the NumPy library for numeric mathematics. This enables the use of NumPy-based simulators.
 - `cupy`: Includes the CuPy library for numeric mathematics. This enables the use of GPU-accelerated CuPy simulators or vectorized NumPy-based simulators in the absence of a GPU.

You can choose to install any combination of these extras by including them in the installation command, as shown in the examples above. For example, to install the core functionality and the visualization extras, you would use:

```bash
pip install -e .[dev,visualization]
```
or
```bash
uv add git+https://github.com/JoSQUANTUM/geqo.git --optional dev --optional visualization
```
This allows you to customize the installation to include only the features you need for your specific use case.
