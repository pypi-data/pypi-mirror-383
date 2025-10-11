from geqo.utils._base_.helpers import (
    bin2num,
    embedSequences,
    getSingleQubitOperationOnRegister,
    num2bin,
    partial_diag,
    partialTrace,
)

from ..__deps__ import (
    _OPTIONAL_CUPY_SIMULATORS_ENABLED,
    _OPTIONAL_NUMPY_SIMULATORS_ENABLED,
    _OPTIONAL_SYMPY_SIMULATORS_ENABLED,
)

if _OPTIONAL_SYMPY_SIMULATORS_ENABLED:
    from geqo.utils._sympy_.helpers import (
        getSingleQubitOperationOnRegister,
        multiQubitsUnitary,
        newPartialTrace,
        partialTrace,
        permutationMatrixQubitsSymPy,
        projection,
    )

if _OPTIONAL_NUMPY_SIMULATORS_ENABLED:
    from geqo.utils._numpy_.helpers import (
        getSingleQubitOperationOnRegister,
        partialTrace,
        permutationMatrixQubitsNumPy,
    )

if _OPTIONAL_CUPY_SIMULATORS_ENABLED:
    from geqo.utils._cupy_.helpers import (
        cupyWarmup,
        getQFTCuPy,
        getRXCupy,
        getRYCupy,
        multiQubitsUnitaryCupy,
        partial_diag_cupy,
        partialTraceCupy,
        permutationMatrixCupy,
        projection_cupy,
        # unitaryDensityMatrixCupy,
    )

__all__ = [
    "bin2num",
    "num2bin",
    "embedSequences",
    "getSingleQubitOperationOnRegister",
    "partialTrace",
    "permutationMatrixQubitsNumPy",
    "permutationMatrixQubitsSymPy",
    "partial_diag",
    "projection",
    "multiQubitsUnitary",
    "newPartialTrace",
    "cupyWarmup",
    "getRXCupy",
    "getRYCupy",
    "getQFTCuPy",
    "permutationMatrixCupy",
    "partialTraceCupy",
    "partial_diag_cupy",
    "projection_cupy",
    "multiQubitsUnitaryCupy",
    # "unitaryDensityMatrixCupy",
]
