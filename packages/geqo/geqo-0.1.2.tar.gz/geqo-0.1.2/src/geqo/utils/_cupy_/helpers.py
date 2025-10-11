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


def cupyWarmup():
    """Warm up the GPU. It's a good practice to run this function before simulating a large circuit for the first time,
    as the initial CUDA API call might take some time to process. For more information please refer to:
    https://docs.cupy.dev/en/stable/user_guide/performance.html"""
    a = cp.random.rand(100, 100) @ cp.random.rand(100, 1)
    b = cp.random.rand(100) * cp.random.rand(100)
    cp.dot(a.ravel(), b)
    d = cp.zeros((1024, 1024), dtype=cp.complex128)
    d[cp.arange(512)[:, None], cp.arange(512)[None, :]] = 1.0 + 1.0j
    # cp.cuda.Device(0).synchronize()


def getRXCupy(angle):
    """Return CuPy matrix for Rx gate with given angle."""
    return cp.array(
        [
            [cp.cos(angle / 2), -1j * cp.sin(angle / 2)],
            [-1j * cp.sin(angle / 2), cp.cos(angle / 2)],
        ],
        dtype=cp.complex128,
    )


def getRYCupy(angle):
    """Return CuPy matrix for Ry gate with given angle."""
    return cp.array(
        [
            [cp.cos(angle / 2), -cp.sin(angle / 2)],
            [cp.sin(angle / 2), cp.cos(angle / 2)],
        ],
        dtype=cp.complex128,
    )


def getQFTCuPy(n, inverse):
    """Return CuPy matrix for QFT."""
    sign = -1 if inverse else 1
    N = 2**n
    omega = cp.exp(sign * 2 * cp.pi * 1j / N)
    j = cp.arange(N).reshape((N, 1))
    k = cp.arange(N).reshape((1, N))
    qft = omega ** (j * k)
    qft = qft / cp.sqrt(N)

    return qft.astype(cp.complex128)


def permutationMatrixCupy(perm: list):
    """Return cupy permutation matrix for given qubit permutation."""
    n = len(perm)
    dim = 2**n

    # Create all binary representations at once
    binary_indices = cp.arange(dim)[:, None] >> cp.arange(n)[None, ::-1] & 1
    # >> n shift the binary string by n bits to the right (i.e. 0100 >> 2 = 0001)
    # & 1 returns 0 if the number is even and 1 if odd. (i.e. 3 & 1 = 1)

    # Apply the permutation to each binary representation
    permuted_binary = binary_indices[:, perm]

    # Convert binary arrays to decimal by vectorization
    powers = cp.array([2 ** (n - i - 1) for i in range(n)])
    row_indices = cp.sum(binary_indices * powers, axis=1)
    col_indices = cp.sum(permuted_binary * powers, axis=1)

    result = cp.zeros((dim, dim))
    result[row_indices, col_indices] = 1

    return result


def partialTraceCupy(rho, qubits, dropTargets):
    """Fully vectorized partial trace implementation without any loops."""
    undroppedQubits = [q for q in qubits if q not in dropTargets]

    targetOrder2 = undroppedQubits + dropTargets

    perm = permutationMatrixCupy([targetOrder2.index(q) for q in qubits])

    rho2 = perm @ rho @ perm.T

    # Calculate dimensions
    n_kept = len(undroppedQubits)
    n_traced = len(dropTargets)
    dim_kept = 2**n_kept
    dim_traced = 2**n_traced

    # Reshape the density matrix to separate kept and traced-out subsystems
    # Each of the first two and last two dimensions forms an axis corresponding to the full Hilbert space of the system (2^num_qubits)
    rho_reshaped = rho2.reshape(dim_kept, dim_traced, dim_kept, dim_traced)

    # Perform the partial trace using einsum
    # Sum over the second and fourth dimensions (traced-out subsystems)
    rhoNew = cp.einsum("jiki->jk", rho_reshaped)

    return rhoNew, perm


def partial_diag_cupy(rho, qubits, dropTargets):
    """Compute partial trace over dropTargets and return non-zero diagonal values with bitstring indices."""
    n = len(qubits)
    dropindex = sorted([qubits.index(i) for i in dropTargets])
    keepindex = [i for i in range(n) if i not in dropindex]

    dim = 2**n
    diag = cp.diag(rho)  # diagonal elements

    # Generate all binary representations of indices
    indices = cp.arange(dim)
    bits = (indices[:, None] >> cp.arange(n - 1, -1, -1)) & 1

    # Keep only bits that are not traced out
    kept_bits = bits[:, keepindex]

    # Convert each kept_bits row to an integer key
    powers = 2 ** cp.arange(len(keepindex) - 1, -1, -1)
    keys = (kept_bits * powers).sum(axis=1)

    # Sum up diagonals with the same kept qubits key using bincount
    probs = cp.bincount(keys, weights=cp.real(diag), minlength=2 ** len(keepindex))

    # Get nonzero indices and values
    nonzero_idx = cp.nonzero(probs)[0]
    values = probs[nonzero_idx]

    # Convert indices to binary vectors
    result = []
    for i in range(len(nonzero_idx)):
        if (
            values[i] > 0
        ):  # some very small negative values might occur due to numpy numerical errors
            # bin_vec = cp.array(
            #    [(nonzero_idx[i] >> j) & 1 for j in range(len(keepindex) - 1, -1, -1)]
            # ).get()  # convert bit vector to numpy array (when using cupy)
            bin_vec = cp.array(
                [(nonzero_idx[i] >> j) & 1 for j in range(len(keepindex) - 1, -1, -1)]
            )
            result.append((bin_vec, values[i]))

    return result


def projection_cupy(densityMatrix, num_qubits, targets, basis):
    """Construct the projector of a given basis state and compute the projected density matrix."""
    zero = cp.array([1.0, 0.0])
    one = cp.array([0.0, 1.0])
    identity = cp.array([1.0, 1.0])

    sorted_targets = cp.sort(cp.array(targets))

    # construct the projector
    vectors = []
    for i in range(num_qubits):
        if cp.any(sorted_targets == i):
            idx = cp.searchsorted(sorted_targets, i)  # Find the index in sorted_targets
            component = zero if basis[idx] == 0 else one
            vectors.append(component)
        else:
            vectors.append(identity)

    def tensor_product(vectors):
        """Compute the tensor products for a given list of arrays."""
        Vector = vectors[0]
        for vec in vectors[1:]:
            Vector = cp.kron(Vector, vec)
        return Vector

    proj = tensor_product(vectors)  # projector

    # projector applied to the density matrix
    nonzero = cp.where(proj != 0)[0]
    resultRho = cp.zeros_like(densityMatrix, dtype=cp.complex128)

    # This part uses the vectorized indexing, which facilitates the element assignment subroutine
    rows = nonzero[:, None]  # shape (len(nonzero),1)
    cols = nonzero[None, :]  # shape (1,len(nonzero))
    resultRho[rows, cols] = densityMatrix[rows, cols]

    return resultRho


def multiQubitsUnitaryCupy(u, qubits, targets):
    """
    compute the whole-system unitary `U` given the target qubits and the target unitary `u`.
    """
    targets = [qubits.index(t) for t in targets]
    non_targets = [qubits.index(i) for i in qubits if i not in targets]
    num_qubits = len(qubits)

    # Create non-target combinations and compute their contribution to index
    non_target_bin = (
        cp.arange(2 ** len(non_targets))[:, None] >> cp.arange(len(non_targets))[::-1]
    ) & 1
    powers_non = 2 ** cp.array([num_qubits - 1 - i for i in non_targets])
    non_idx = (non_target_bin * powers_non).sum(axis=1)  # shape (2^(n-t),)

    # Create target combinations (from min to max) and sorted target combination according to the target order
    target_bin = (
        cp.arange(2 ** len(targets))[:, None] >> cp.arange(len(targets))[::-1]
    ) & 1
    perm = [sorted(targets).index(t) for t in targets]
    sorted_bin = target_bin[:, perm]

    # Compute the target contribution of the large U indices
    powers_tar = 2 ** cp.array([num_qubits - 1 - i for i in sorted(targets)])
    U_idx = (target_bin * powers_tar).sum(axis=1)  # shape (2^t,)

    # Compute the small u indices from the sorted target order (target = [q2,q0], nontarget=[q1] then the original indexing should be reversed)
    powers_sort_tar = 2 ** (len(targets) - 1 - cp.arange(len(targets)))
    u_idx = (sorted_bin * powers_sort_tar).sum(axis=1).astype(cp.int64)

    # Compute all full-system U indices (target + non_target contribution)
    idx_rows = non_idx[:, None] + U_idx[None, :]  # shape (2^(n-t), 2^t)
    idx_rows_flat = idx_rows.reshape(-1)

    # Get all values from smaller u according to the sorted target indices
    u_matrix = u[u_idx[:, None], u_idx[None, :]]  # shape (2^t, 2^t)
    tiled_u = cp.tile(
        u_matrix, (2 ** len(non_targets), 1)
    )  # shape (2^(n-t)*2^t, 2^t)  repeat u_matrix 2^(n-t) times along the row and 1 time along the column

    idx_cols = cp.tile(idx_rows, (1, 2 ** len(targets))).reshape(
        -1
    )  # repeat idx_rows 1 time along the row and 2^t times along the column

    # Broadcast rows for assigning
    repeated_rows = cp.repeat(
        idx_rows_flat, 2 ** len(targets)
    )  # repeat every element 4 times i.e. [1,2] => [1,1,1,1,2,2,2,2]

    #  Element assignment
    U = cp.zeros((2**num_qubits, 2**num_qubits), dtype=cp.complex128)
    U[repeated_rows.astype(cp.int64), idx_cols.astype(cp.int64)] = tiled_u.reshape(-1)

    return U


'''def unitaryDensityMatrixCupy(u, rho, num_qubits, targets):
    """Apply unitary transformation to part of the density matrix associated with the target qubits without permutation or full matrix multiplication."""
    non_targets = list(set(range(num_qubits)) - set(targets))
    non_targets = sorted(non_targets)

    # Create non-target combinations and compute their contribution to index
    non_target_bin = (
        cp.arange(2 ** len(non_targets))[:, None] >> cp.arange(len(non_targets))[::-1]
    ) & 1
    powers_non = 2 ** cp.array([num_qubits - 1 - i for i in non_targets])
    non_idx = (non_target_bin * powers_non).sum(axis=1)  # shape (2^(n-t),)

    # Create target combinations (from min to max) and sorted target combination according to the target order
    target_bin = (
        cp.arange(2 ** len(targets))[:, None] >> cp.arange(len(targets))[::-1]
    ) & 1
    perm1 = [sorted(targets).index(t) for t in targets]
    sorted_bin_before_u = target_bin[
        :, perm1
    ]  # sort the density matrix before application of unitary
    perm2 = [targets.index(t) for t in sorted(targets)]
    sorted_bin_after_u = target_bin[
        :, perm2
    ]  # sort the density matrix after application of unitary

    # Compute the target contribution of the large U indices
    powers_tar = 2 ** cp.array([num_qubits - 1 - i for i in sorted(targets)])
    U_idx = (target_bin * powers_tar).sum(axis=1)  # shape (2^t,)

    # Compute the small u indices from the sorted target order (target = [q2,q0], nontarget=[q1] then the original indexing should be reversed)
    powers_sort_tar = 2 ** (len(targets) - 1 - cp.arange(len(targets)))
    before_u_idx = (
        (sorted_bin_before_u * powers_sort_tar).sum(axis=1).astype(cp.int64)
    )  # permuting index before applying u. shape (2^t)
    after_u_idx = (
        (sorted_bin_after_u * powers_sort_tar).sum(axis=1).astype(cp.int64)
    )  # permuting index after applying u. shape (2^t)

    # Compute all full-system U indices (target + non_target contribution)
    idx_full_mat = non_idx[:, None] + U_idx[None, :]  # shape (2^(n-t), 2^t)
    idx_full = idx_full_mat.reshape(-1).astype(cp.int64)  # shape (2^n ,)

    # 1. extract rhos with different non-targets combinations
    rho_tensor = rho[
        idx_full[:, None], idx_full[None, :]
    ]  # a tensor of extracted rhos with different non_targ combinations [[(0,0),(0,1)],[(1,0),(1,1)]]
    # shape (2^n, 2^n)

    # 2. shuffle the extracted rhos to match the target order
    tiled_before_u_idx = (
        cp.array(
            [before_u_idx + 2 ** len(targets) * i for i in range(2 ** len(non_targets))]
        )
        .astype(cp.int64)
        .reshape(-1)
    )  # shape (2^n)
    rho_tensor = rho_tensor[tiled_before_u_idx[:, None], tiled_before_u_idx[None, :]]

    # 3. apply unitary transformation to all the extracted rhos
    transformed_rho = cp.empty_like(rho_tensor)
    for i in range(2 ** len(non_targets)):
        for j in range(2 ** len(non_targets)):
            transformed_rho[
                2 ** len(targets) * i : 2 ** len(targets) * (i + 1),
                2 ** len(targets) * j : 2 ** len(targets) * (j + 1),
            ] = (
                u
                @ rho_tensor[
                    2 ** len(targets) * i : 2 ** len(targets) * (i + 1),
                    2 ** len(targets) * j : 2 ** len(targets) * (j + 1),
                ]
                @ u.conj().T
            )

    # 4. shuffle the transformed rhos back to the sorted order
    tiled_after_u_idx = (
        cp.array(
            [after_u_idx + 2 ** len(targets) * i for i in range(2 ** len(non_targets))]
        )
        .astype(cp.int64)
        .reshape(-1)
    )  # shape (2^n)
    transformed_rho = transformed_rho[
        tiled_after_u_idx[:, None], tiled_after_u_idx[None, :]
    ]  # shape (2^n ,2^n)

    # 5. Assignment matrix element of new rho
    new_rho = cp.empty_like(transformed_rho)
    new_rho[idx_full[:, None], idx_full[None, :]] = transformed_rho

    return new_rho'''
