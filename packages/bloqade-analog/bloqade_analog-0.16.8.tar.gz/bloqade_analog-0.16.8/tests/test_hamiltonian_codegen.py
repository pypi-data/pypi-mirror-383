from decimal import Decimal
from functools import reduce
from itertools import combinations

import numpy as np
import pytest

from bloqade.analog.atom_arrangement import Chain

np.random.seed(2304023)
L_VALUES = [1, 2, 3, 4, 5]


def get_manybody_op(i, L, op):
    if op.ndim == 1:
        Ident = np.ones_like(op)
    else:
        Ident = np.eye(op.shape[0])

    if i < 0 or i >= L:
        raise ValueError("i must be in range [0, L-1]")

    if L <= 1:
        return op

    i = L - i - 1

    if i == 0:
        rhs = reduce(np.kron, [Ident] * (L - 1))
        return np.kron(op, rhs)
    elif i == L - 1:
        lhs = reduce(np.kron, [Ident] * i)
        return np.kron(lhs, op)
    else:
        lhs = reduce(np.kron, [Ident] * i)
        rhs = reduce(np.kron, [Ident] * (L - i - 1))
        return np.kron(np.kron(lhs, op), rhs)


def project_to_subspace(operator, configurations):
    from scipy.sparse import csr_matrix

    proj_shape = (configurations.size, operator.shape[0])
    data = np.ones_like(configurations)
    rows = np.arange(configurations.size)
    cols = configurations
    proj = csr_matrix((data, (rows, cols)), shape=proj_shape)

    if operator.ndim == 1:
        return proj @ operator
    else:
        return proj @ operator @ proj.T


####################
# Test uniform ops #
####################
@pytest.mark.parametrize("L", L_VALUES)
def test_2_level_uniform_detuning(L):

    program = Chain(L, lattice_spacing=6.1).rydberg.detuning.uniform.constant(1.0, 1.0)
    (hamiltonian_data,) = program.bloqade.python().hamiltonian()
    hamiltonian = hamiltonian_data.hamiltonian

    detuning_op = np.array([0, -1], dtype=int)

    detuning = sum([get_manybody_op(i, L, detuning_op) for i in range(L)])

    assert np.all(hamiltonian.detuning_ops[0].diagonal == detuning)

    (hamiltonian_data,) = program.bloqade.python().hamiltonian(blockade_radius=6.2)
    hamiltonian = hamiltonian_data.hamiltonian

    detuning_op_proj = project_to_subspace(detuning, hamiltonian.space.configurations)

    assert np.all(hamiltonian.detuning_ops[0].diagonal == detuning_op_proj)


@pytest.mark.parametrize("L", L_VALUES)
def test_2_level_uniform_rabi_real(L):
    program = Chain(L, lattice_spacing=6.1).rydberg.rabi.amplitude.uniform.constant(
        1.0, 1.0
    )

    (hamiltonian_data,) = program.bloqade.python().hamiltonian()
    hamiltonian = hamiltonian_data.hamiltonian
    rabi_op = np.array([[0, 1], [1, 0]], dtype=int)

    rabi = sum([get_manybody_op(i, L, rabi_op) for i in range(L)])

    assert np.all(hamiltonian.rabi_ops[0].op.tocsr().toarray() == rabi)

    (hamiltonian_data,) = program.bloqade.python().hamiltonian(blockade_radius=6.2)
    hamiltonian = hamiltonian_data.hamiltonian

    rabi_op_proj = project_to_subspace(rabi, hamiltonian.space.configurations)

    assert np.all(hamiltonian.rabi_ops[0].op.tocsr().toarray() == rabi_op_proj)


@pytest.mark.parametrize("L", L_VALUES)
def test_2_level_uniform_complex(L):
    program = (
        Chain(L, lattice_spacing=6.1)
        .rydberg.rabi.amplitude.uniform.constant(1.0, 1.0)
        .phase.uniform.constant(0.0, 1.0)
    )

    (hamiltonian_data,) = program.bloqade.python().hamiltonian()
    hamiltonian = hamiltonian_data.hamiltonian
    rabi_op = np.array([[0, 0], [1, 0]], dtype=int)

    rabi = sum([get_manybody_op(i, L, rabi_op) for i in range(L)])

    assert np.all(hamiltonian.rabi_ops[0].op.tocsr().toarray() == rabi)

    (hamiltonian_data,) = program.bloqade.python().hamiltonian(blockade_radius=6.2)
    hamiltonian = hamiltonian_data.hamiltonian

    rabi_op_proj = project_to_subspace(rabi, hamiltonian.space.configurations)

    assert np.all(hamiltonian.rabi_ops[0].op.tocsr().toarray() == rabi_op_proj)


@pytest.mark.parametrize("L", L_VALUES)
def test_3_level_uniform_detuning(L):
    program = Chain(L, lattice_spacing=6.1).rydberg.detuning.uniform.constant(1.0, 1.0)

    (hamiltonian_data,) = program.bloqade.python().hamiltonian(use_hyperfine=True)
    hamiltonian = hamiltonian_data.hamiltonian
    detuning_op = np.array([0, 0, -1], dtype=int)

    detuning = sum([get_manybody_op(i, L, detuning_op) for i in range(L)])

    assert np.all(hamiltonian.detuning_ops[0].diagonal == detuning)

    (hamiltonian_data,) = program.bloqade.python().hamiltonian(
        blockade_radius=6.2, use_hyperfine=True
    )
    hamiltonian = hamiltonian_data.hamiltonian

    detuning_op_proj = project_to_subspace(detuning, hamiltonian.space.configurations)

    assert np.all(hamiltonian.detuning_ops[0].diagonal == detuning_op_proj)

    # check hyperfine detuning value

    program = Chain(L, lattice_spacing=6.1).hyperfine.detuning.uniform.constant(
        1.0, 1.0
    )

    (hamiltonian_data,) = program.bloqade.python().hamiltonian(use_hyperfine=True)
    hamiltonian = hamiltonian_data.hamiltonian
    detuning_op = np.array([0, -1, 0], dtype=int)

    detuning = sum([get_manybody_op(i, L, detuning_op) for i in range(L)])

    assert np.all(hamiltonian.detuning_ops[0].diagonal == detuning)

    (hamiltonian_data,) = program.bloqade.python().hamiltonian(blockade_radius=6.2)
    hamiltonian = hamiltonian_data.hamiltonian

    detuning_op_proj = project_to_subspace(detuning, hamiltonian.space.configurations)

    assert np.all(hamiltonian.detuning_ops[0].diagonal == detuning_op_proj)


@pytest.mark.parametrize("L", L_VALUES)
def test_3_level_uniform_rabi_complex(L):
    program = (
        Chain(L, lattice_spacing=6.1)
        .rydberg.rabi.amplitude.uniform.constant(1.0, 1.0)
        .phase.uniform.constant(0.0, 1.0)
    )
    (hamiltonian_data,) = program.bloqade.python().hamiltonian(
        cache_matrices=True, use_hyperfine=True
    )
    hamiltonian = hamiltonian_data.hamiltonian

    rabi_op = np.array([[0, 0, 0], [0, 0, 0], [0, 1, 0]], dtype=int)

    rabi = sum([get_manybody_op(i, L, rabi_op) for i in range(L)])

    print(rabi)
    print(hamiltonian.rabi_ops[0].op.tocsr().toarray())

    assert np.all(hamiltonian.rabi_ops[0].op.tocsr().toarray() == rabi)

    (hamiltonian_data,) = program.bloqade.python().hamiltonian(
        blockade_radius=6.2, use_hyperfine=True
    )
    hamiltonian = hamiltonian_data.hamiltonian

    rabi_op_proj = project_to_subspace(rabi, hamiltonian.space.configurations)

    assert np.all(hamiltonian.rabi_ops[0].op.tocsr().toarray() == rabi_op_proj)

    # check hyperfine rabi value

    program = (
        Chain(L, lattice_spacing=6.1)
        .hyperfine.rabi.amplitude.uniform.constant(1.0, 1.0)
        .phase.uniform.constant(0.0, 1.0)
    )
    (hamiltonian_data,) = program.bloqade.python().hamiltonian(cache_matrices=True)
    hamiltonian = hamiltonian_data.hamiltonian

    rabi_op = np.array([[0, 0, 0], [1, 0, 0], [0, 0, 0]], dtype=int)

    rabi = sum([get_manybody_op(i, L, rabi_op) for i in range(L)])

    print(rabi)
    print(hamiltonian.rabi_ops[0].op.tocsr().toarray())

    assert np.all(hamiltonian.rabi_ops[0].op.tocsr().toarray() == rabi)

    (hamiltonian_data,) = program.bloqade.python().hamiltonian(blockade_radius=6.2)
    hamiltonian = hamiltonian_data.hamiltonian

    rabi_op_proj = project_to_subspace(rabi, hamiltonian.space.configurations)

    assert np.all(hamiltonian.rabi_ops[0].op.tocsr().toarray() == rabi_op_proj)


####################
# Test single atom #
####################


@pytest.mark.parametrize(("i", "L"), [(i, L) for L in L_VALUES for i in range(L)])
def test_2_level_single_atom_detuning(i, L):
    program = (
        Chain(L, lattice_spacing=6.1)
        .rydberg.detuning.location(i, 2.0)
        .constant(1.0, 1.0)
    )

    (hamiltonian_data,) = program.bloqade.python().hamiltonian(cache_matrices=True)
    hamiltonian = hamiltonian_data.hamiltonian

    detuning_op = np.array([0, -1], dtype=int)

    detuning = 2.0 * get_manybody_op(i, L, detuning_op)

    assert np.all(hamiltonian.detuning_ops[0].get_diagonal(0.0) == detuning)

    (hamiltonian_data,) = program.bloqade.python().hamiltonian(blockade_radius=6.2)
    hamiltonian = hamiltonian_data.hamiltonian

    detuning_op_proj = project_to_subspace(detuning, hamiltonian.space.configurations)

    assert np.all(hamiltonian.detuning_ops[0].diagonal == detuning_op_proj)


@pytest.mark.parametrize(("i", "L"), [(i, L) for L in L_VALUES for i in range(L)])
def test_2_level_single_atom_rabi_real(i, L):
    program = (
        Chain(L, lattice_spacing=6.1)
        .rydberg.rabi.amplitude.location(i, 0.5)
        .constant(1.0, 1.0)
    )

    (hamiltonian_data,) = program.bloqade.python().hamiltonian(cache_matrices=True)
    hamiltonian = hamiltonian_data.hamiltonian

    rabi_op = np.array([[0, 1], [1, 0]], dtype=int)

    rabi = get_manybody_op(i, L, rabi_op)

    assert np.all(hamiltonian.rabi_ops[0].op.tocsr().toarray() == rabi)

    (hamiltonian_data,) = program.bloqade.python().hamiltonian(blockade_radius=6.2)
    hamiltonian = hamiltonian_data.hamiltonian

    rabi_op_proj = project_to_subspace(rabi, hamiltonian.space.configurations)

    assert np.all(hamiltonian.rabi_ops[0].op.tocsr().toarray() == rabi_op_proj)


@pytest.mark.parametrize(("i", "L"), [(i, L) for L in L_VALUES for i in range(L)])
def test_2_level_single_atom_complex(i, L):
    program = (
        Chain(L, lattice_spacing=6.1)
        .rydberg.rabi.amplitude.location(i, 0.5)
        .constant(1.0, 1.0)
        .phase.location(i)
        .constant(0.0, 1.0)
    )

    (hamiltonian_data,) = program.bloqade.python().hamiltonian(cache_matrices=True)
    hamiltonian = hamiltonian_data.hamiltonian

    rabi_op = np.array([[0, 0], [1, 0]], dtype=int)
    rabi = get_manybody_op(i, L, rabi_op)

    assert np.all(hamiltonian.rabi_ops[0].op.tocsr().toarray() == rabi)

    (hamiltonian_data,) = program.bloqade.python().hamiltonian(blockade_radius=6.2)
    hamiltonian = hamiltonian_data.hamiltonian

    rabi_op_proj = project_to_subspace(rabi, hamiltonian.space.configurations)

    assert np.all(hamiltonian.rabi_ops[0].op.tocsr().toarray() == rabi_op_proj)


@pytest.mark.parametrize(("i", "L"), [(i, L) for L in L_VALUES for i in range(L)])
def test_3_level_single_atom_detuning(i, L):
    program = (
        Chain(L, lattice_spacing=6.1)
        .rydberg.detuning.location(i, 2.0)
        .constant(1.0, 1.0)
    )

    (hamiltonian_data,) = program.bloqade.python().hamiltonian(
        cache_matrices=True, use_hyperfine=True
    )
    hamiltonian = hamiltonian_data.hamiltonian

    detuning_op = np.array([0, 0, -1], dtype=int)

    detuning = 2.0 * get_manybody_op(i, L, detuning_op)

    assert np.all(hamiltonian.detuning_ops[0].get_diagonal(0.0) == detuning)

    (hamiltonian_data,) = program.bloqade.python().hamiltonian(
        blockade_radius=6.2, use_hyperfine=True
    )
    hamiltonian = hamiltonian_data.hamiltonian

    detuning_op_proj = project_to_subspace(detuning, hamiltonian.space.configurations)

    assert np.all(hamiltonian.detuning_ops[0].diagonal == detuning_op_proj)

    # check hyperfine detuning value

    program = (
        Chain(L, lattice_spacing=6.1)
        .hyperfine.detuning.location(i, 2.0)
        .constant(1.0, 1.0)
    )

    (hamiltonian_data,) = program.bloqade.python().hamiltonian(cache_matrices=True)
    hamiltonian = hamiltonian_data.hamiltonian

    detuning_op = np.array([0, -1, 0], dtype=int)

    detuning = 2.0 * get_manybody_op(i, L, detuning_op)

    assert np.all(hamiltonian.detuning_ops[0].get_diagonal(0.0) == detuning)

    (hamiltonian_data,) = program.bloqade.python().hamiltonian(blockade_radius=6.2)
    hamiltonian = hamiltonian_data.hamiltonian

    detuning_op_proj = project_to_subspace(detuning, hamiltonian.space.configurations)

    assert np.all(hamiltonian.detuning_ops[0].diagonal == detuning_op_proj)


@pytest.mark.parametrize(("i", "L"), [(i, L) for L in L_VALUES for i in range(L)])
def test_3_level_single_atom_rabi_real(i, L):
    program = (
        Chain(L, lattice_spacing=6.1)
        .rydberg.rabi.amplitude.location(i, 0.5)
        .constant(1.0, 1.0)
    )

    (hamiltonian_data,) = program.bloqade.python().hamiltonian(
        use_hyperfine=True, cache_matrices=True
    )
    hamiltonian = hamiltonian_data.hamiltonian

    rabi_op = np.array([[0, 0, 0], [0, 0, 1], [0, 1, 0]], dtype=int)

    rabi = get_manybody_op(i, L, rabi_op)

    assert np.all(hamiltonian.rabi_ops[0].op.tocsr().toarray() == rabi)

    (hamiltonian_data,) = program.bloqade.python().hamiltonian(
        blockade_radius=6.2, use_hyperfine=True
    )
    hamiltonian = hamiltonian_data.hamiltonian

    rabi_op_proj = project_to_subspace(rabi, hamiltonian.space.configurations)

    assert np.all(hamiltonian.rabi_ops[0].op.tocsr().toarray() == rabi_op_proj)

    # check hyperfine rabi value

    program = (
        Chain(L, lattice_spacing=6.1)
        .hyperfine.rabi.amplitude.location(i, 0.5)
        .constant(1.0, 1.0)
    )

    (hamiltonian_data,) = program.bloqade.python().hamiltonian(cache_matrices=True)
    hamiltonian = hamiltonian_data.hamiltonian

    rabi_op = np.array([[0, 1, 0], [1, 0, 0], [0, 0, 0]], dtype=int)

    rabi = get_manybody_op(i, L, rabi_op)

    assert np.all(hamiltonian.rabi_ops[0].op.tocsr().toarray() == rabi)

    (hamiltonian_data,) = program.bloqade.python().hamiltonian(blockade_radius=6.2)
    hamiltonian = hamiltonian_data.hamiltonian

    rabi_op_proj = project_to_subspace(rabi, hamiltonian.space.configurations)

    assert np.all(hamiltonian.rabi_ops[0].op.tocsr().toarray() == rabi_op_proj)


@pytest.mark.parametrize(
    ("i", "L"), [(i, L) for L in [1, 2, 3, 4, 5, 6] for i in range(L)]
)
def test_3_level_single_atom_rabi_complex(i, L):
    program = (
        Chain(L, lattice_spacing=6.1)
        .rydberg.rabi.amplitude.location(i, 0.5)
        .constant(1.0, 1.0)
        .phase.location(i)
        .constant(0.0, 1.0)
    )

    (hamiltonian_data,) = program.bloqade.python().hamiltonian(
        cache_matrices=True, use_hyperfine=True
    )
    hamiltonian = hamiltonian_data.hamiltonian

    rabi_op = np.array([[0, 0, 0], [0, 0, 0], [0, 1, 0]], dtype=int)
    rabi = get_manybody_op(i, L, rabi_op)

    assert np.all(hamiltonian.rabi_ops[0].op.tocsr().toarray() == rabi)

    (hamiltonian_data,) = program.bloqade.python().hamiltonian(
        blockade_radius=6.2, use_hyperfine=True
    )
    hamiltonian = hamiltonian_data.hamiltonian

    rabi_op_proj = project_to_subspace(rabi, hamiltonian.space.configurations)

    assert np.all(hamiltonian.rabi_ops[0].op.tocsr().toarray() == rabi_op_proj)

    # check hyperfine rabi value

    program = (
        Chain(L, lattice_spacing=6.1)
        .hyperfine.rabi.amplitude.location(i, 0.5)
        .constant(1.0, 1.0)
        .phase.location(i)
        .constant(0.0, 1.0)
    )

    (hamiltonian_data,) = program.bloqade.python().hamiltonian(cache_matrices=True)
    hamiltonian = hamiltonian_data.hamiltonian

    rabi_op = np.array([[0, 0, 0], [1, 0, 0], [0, 0, 0]], dtype=int)
    rabi = get_manybody_op(i, L, rabi_op)

    assert np.all(hamiltonian.rabi_ops[0].op.tocsr().toarray() == rabi)

    (hamiltonian_data,) = program.bloqade.python().hamiltonian(blockade_radius=6.2)
    hamiltonian = hamiltonian_data.hamiltonian

    rabi_op_proj = project_to_subspace(rabi, hamiltonian.space.configurations)

    assert np.all(hamiltonian.rabi_ops[0].op.tocsr().toarray() == rabi_op_proj)


####################
# Test full mask   #
####################


@pytest.mark.parametrize("L", L_VALUES)
def test_2_level_mask_detuning(L):
    program = (
        Chain(L, lattice_spacing=6.1)
        .rydberg.detuning.scale("detuning_mask")
        .constant(1.0, 1.0)
    )

    detuning_mask = [Decimal(str(np.random.normal(0.0, 1.0))) for _ in range(L)]
    mask_assignments = dict(detuning_mask=detuning_mask)

    program = program.assign(**mask_assignments)

    (hamiltonian_data,) = program.bloqade.python().hamiltonian(cache_matrices=True)
    hamiltonian = hamiltonian_data.hamiltonian

    detuning_op = np.array([0, -1], dtype=int)

    detuning = sum(
        float(mask) * get_manybody_op(i, L, detuning_op)
        for i, mask in enumerate(detuning_mask)
    )

    assert np.all(hamiltonian.detuning_ops[0].get_diagonal(0.0) == detuning)

    (hamiltonian_data,) = program.bloqade.python().hamiltonian(blockade_radius=6.2)
    hamiltonian = hamiltonian_data.hamiltonian

    detuning_op_proj = project_to_subspace(detuning, hamiltonian.space.configurations)

    assert np.all(hamiltonian.detuning_ops[0].diagonal == detuning_op_proj)


@pytest.mark.parametrize("L", L_VALUES)
def test_2_level_mask_real(L):
    program = (
        Chain(L, lattice_spacing=6.1)
        .rydberg.rabi.amplitude.scale("rabi_mask")
        .constant(1.0, 1.0)
    )

    rabi_mask = [Decimal(str(np.random.normal(0.0, 1.0))) for _ in range(L)]
    mask_assignments = dict(rabi_mask=rabi_mask)

    program = program.assign(**mask_assignments)

    (hamiltonian_data,) = program.bloqade.python().hamiltonian(cache_matrices=True)
    hamiltonian = hamiltonian_data.hamiltonian

    rabi_op = np.array([[0, 1], [1, 0]], dtype=int)

    if L == 1:
        rabi = get_manybody_op(0, L, rabi_op)
    else:
        rabi = sum(
            float(mask) * get_manybody_op(i, L, rabi_op)
            for i, mask in enumerate(rabi_mask)
        )

    assert np.all(hamiltonian.rabi_ops[0].op.tocsr().toarray() == rabi)

    (hamiltonian_data,) = program.bloqade.python().hamiltonian(blockade_radius=6.2)
    hamiltonian = hamiltonian_data.hamiltonian

    rabi_op_proj = project_to_subspace(rabi, hamiltonian.space.configurations)

    assert np.all(hamiltonian.rabi_ops[0].op.tocsr().toarray() == rabi_op_proj)


@pytest.mark.parametrize("L", L_VALUES)
def test_2_level_mask_complex(L):
    program = (
        Chain(L, lattice_spacing=6.1)
        .rydberg.rabi.amplitude.scale("rabi_mask")
        .constant(1.0, 1.0)
        .phase.uniform.constant(0.0, 1.0)
    )

    rabi_mask = [Decimal(str(np.random.normal(0.0, 1.0))) for _ in range(L)]
    mask_assignments = dict(
        rabi_mask=rabi_mask,
    )

    program = program.assign(**mask_assignments)

    (hamiltonian_data,) = program.bloqade.python().hamiltonian(cache_matrices=True)
    hamiltonian = hamiltonian_data.hamiltonian

    rabi_op = np.array([[0, 0], [1, 0]], dtype=int)

    if L == 1:
        rabi = get_manybody_op(0, L, rabi_op)
    else:
        rabi = sum(
            float(mask) * get_manybody_op(i, L, rabi_op)
            for i, mask in enumerate(rabi_mask)
        )

    assert np.all(hamiltonian.rabi_ops[0].op.tocsr().toarray() == rabi)

    (hamiltonian_data,) = program.bloqade.python().hamiltonian(blockade_radius=6.2)
    hamiltonian = hamiltonian_data.hamiltonian

    rabi_op_proj = project_to_subspace(rabi, hamiltonian.space.configurations)

    assert np.all(hamiltonian.rabi_ops[0].op.tocsr().toarray() == rabi_op_proj)


@pytest.mark.parametrize("L", L_VALUES)
def test_3_level_detuning(L):
    detuning_mask = [Decimal(str(np.random.normal(0.0, 1.0))) for _ in range(L)]
    mask_assignments = dict(detuning_mask=detuning_mask)

    program = (
        Chain(L, lattice_spacing=6.1)
        .rydberg.detuning.scale("detuning_mask")
        .constant(1.0, 1.0)
    )

    program = program.assign(**mask_assignments)

    (hamiltonian_data,) = program.bloqade.python().hamiltonian(
        cache_matrices=True, use_hyperfine=True
    )
    hamiltonian = hamiltonian_data.hamiltonian

    detuning_op = np.array([0, 0, -1], dtype=int)
    detuning = sum(
        float(mask) * get_manybody_op(i, L, detuning_op)
        for i, mask in enumerate(detuning_mask)
    )

    assert np.all(hamiltonian.detuning_ops[0].get_diagonal(0.0) == detuning)

    (hamiltonian_data,) = program.bloqade.python().hamiltonian(
        blockade_radius=6.2, use_hyperfine=True
    )
    hamiltonian = hamiltonian_data.hamiltonian

    detuning_op_proj = project_to_subspace(detuning, hamiltonian.space.configurations)

    assert np.all(hamiltonian.detuning_ops[0].diagonal == detuning_op_proj)

    # check hyperfine detuning value

    program = (
        Chain(L, lattice_spacing=6.1)
        .hyperfine.detuning.scale("detuning_mask")
        .constant(1.0, 1.0)
    )

    program = program.assign(**mask_assignments)

    (hamiltonian_data,) = program.bloqade.python().hamiltonian(cache_matrices=True)
    hamiltonian = hamiltonian_data.hamiltonian

    detuning_op = np.array([0, -1, 0], dtype=int)
    detuning = sum(
        float(mask) * get_manybody_op(i, L, detuning_op)
        for i, mask in enumerate(detuning_mask)
    )

    assert np.all(hamiltonian.detuning_ops[0].get_diagonal(0.0) == detuning)

    (hamiltonian_data,) = program.bloqade.python().hamiltonian(blockade_radius=6.2)
    hamiltonian = hamiltonian_data.hamiltonian

    detuning_op_proj = project_to_subspace(detuning, hamiltonian.space.configurations)

    assert np.all(hamiltonian.detuning_ops[0].diagonal == detuning_op_proj)


@pytest.mark.parametrize("L", L_VALUES)
def test_3_level_mask_rabi_real(L):
    rabi_mask = [Decimal(str(np.random.normal(0.0, 1.0))) for _ in range(L)]
    mask_assignments = dict(rabi_mask=rabi_mask)

    program = (
        Chain(L, lattice_spacing=6.1)
        .rydberg.rabi.amplitude.scale("rabi_mask")
        .constant(1.0, 1.0)
    )

    program = program.assign(**mask_assignments)

    (hamiltonian_data,) = program.bloqade.python().hamiltonian(
        cache_matrices=True, use_hyperfine=True
    )
    hamiltonian = hamiltonian_data.hamiltonian

    rabi_op = np.array([[0, 0, 0], [0, 0, 1], [0, 1, 0]], dtype=int)

    if L == 1:
        rabi = get_manybody_op(0, L, rabi_op)
    else:
        rabi = sum(
            float(mask) * get_manybody_op(i, L, rabi_op)
            for i, mask in enumerate(rabi_mask)
        )

    assert np.all(hamiltonian.rabi_ops[0].op.tocsr().toarray() == rabi)

    (hamiltonian_data,) = program.bloqade.python().hamiltonian(
        blockade_radius=6.2, use_hyperfine=True
    )
    hamiltonian = hamiltonian_data.hamiltonian

    rabi_op_proj = project_to_subspace(rabi, hamiltonian.space.configurations)

    assert np.all(hamiltonian.rabi_ops[0].op.tocsr().toarray() == rabi_op_proj)

    # check hyperfine rabi value

    program = (
        Chain(L, lattice_spacing=6.1)
        .hyperfine.rabi.amplitude.scale("rabi_mask")
        .constant(1.0, 1.0)
    )

    program = program.assign(**mask_assignments)

    (hamiltonian_data,) = program.bloqade.python().hamiltonian(cache_matrices=True)
    hamiltonian = hamiltonian_data.hamiltonian

    rabi_op = np.array([[0, 1, 0], [1, 0, 0], [0, 0, 0]], dtype=int)

    if L == 1:
        rabi = get_manybody_op(0, L, rabi_op)
    else:
        rabi = sum(
            float(mask) * get_manybody_op(i, L, rabi_op)
            for i, mask in enumerate(rabi_mask)
        )

    assert np.all(hamiltonian.rabi_ops[0].op.tocsr().toarray() == rabi)

    (hamiltonian_data,) = program.bloqade.python().hamiltonian(blockade_radius=6.2)
    hamiltonian = hamiltonian_data.hamiltonian

    rabi_op_proj = project_to_subspace(rabi, hamiltonian.space.configurations)

    assert np.all(hamiltonian.rabi_ops[0].op.tocsr().toarray() == rabi_op_proj)


@pytest.mark.parametrize("L", L_VALUES)
def test_3_level_mask_complex(L):
    rabi_mask = [Decimal(str(np.random.normal(0.0, 1.0))) for _ in range(L)]
    mask_assignments = dict(
        rabi_mask=rabi_mask,
    )

    program = (
        Chain(L, lattice_spacing=6.1)
        .rydberg.rabi.amplitude.scale("rabi_mask")
        .constant(1.0, 1.0)
        .phase.uniform.constant(0.0, 1.0)
    )

    program = program.assign(**mask_assignments)

    (hamiltonian_data,) = program.bloqade.python().hamiltonian(
        cache_matrices=True, use_hyperfine=True
    )
    hamiltonian = hamiltonian_data.hamiltonian

    rabi_op = np.array([[0, 0, 0], [0, 0, 0], [0, 1, 0]], dtype=int)

    if L == 1:
        rabi = get_manybody_op(0, L, rabi_op)
    else:
        rabi = sum(
            float(mask) * get_manybody_op(i, L, rabi_op)
            for i, mask in enumerate(rabi_mask)
        )

    assert np.all(hamiltonian.rabi_ops[0].op.tocsr().toarray() == rabi)

    (hamiltonian_data,) = program.bloqade.python().hamiltonian(
        blockade_radius=6.2, use_hyperfine=True
    )
    hamiltonian = hamiltonian_data.hamiltonian

    rabi_op_proj = project_to_subspace(rabi, hamiltonian.space.configurations)

    assert np.all(hamiltonian.rabi_ops[0].op.tocsr().toarray() == rabi_op_proj)

    # check hyperfine rabi value

    program = (
        Chain(L, lattice_spacing=6.1)
        .hyperfine.rabi.amplitude.scale("rabi_mask")
        .constant(1.0, 1.0)
        .phase.uniform.constant(0.0, 1.0)
    )

    program = program.assign(**mask_assignments)

    (hamiltonian_data,) = program.bloqade.python().hamiltonian(cache_matrices=True)
    hamiltonian = hamiltonian_data.hamiltonian

    rabi_op = np.array([[0, 0, 0], [1, 0, 0], [0, 0, 0]], dtype=int)

    if L == 1:
        rabi = get_manybody_op(0, L, rabi_op)
    else:
        rabi = sum(
            float(mask) * get_manybody_op(i, L, rabi_op)
            for i, mask in enumerate(rabi_mask)
        )

    assert np.all(hamiltonian.rabi_ops[0].op.tocsr().toarray() == rabi)

    (hamiltonian_data,) = program.bloqade.python().hamiltonian(blockade_radius=6.2)
    hamiltonian = hamiltonian_data.hamiltonian

    rabi_op_proj = project_to_subspace(rabi, hamiltonian.space.configurations)

    assert np.all(hamiltonian.rabi_ops[0].op.tocsr().toarray() == rabi_op_proj)


####################
# Test multi atom  #
####################


@pytest.mark.parametrize(
    ("sites", "L"),
    [
        (sites, L)
        for L in L_VALUES
        for n_sites in range(2, L + 1)
        for sites in combinations(range(L), n_sites)
    ],
)
def test_2_level_multi_atom_detuning(sites, L):
    program = Chain(L, lattice_spacing=6.1).rydberg.detuning
    detuning_coeffs = [Decimal(str(np.random.normal(0.0, 1.0))) for _ in sites]

    program = program.location(list(sites), detuning_coeffs)

    program = program.constant(1.0, 1.0)

    (hamiltonian_data,) = program.bloqade.python().hamiltonian(cache_matrices=True)
    hamiltonian = hamiltonian_data.hamiltonian

    detuning_op = np.array([0, -1], dtype=int)

    detuning = sum(
        float(mask) * get_manybody_op(i, L, detuning_op)
        for i, mask in zip(sites, detuning_coeffs)
    )

    assert np.all(hamiltonian.detuning_ops[0].get_diagonal(0.0) == detuning)

    (hamiltonian_data,) = program.bloqade.python().hamiltonian(blockade_radius=6.2)
    hamiltonian = hamiltonian_data.hamiltonian

    detuning_op_proj = project_to_subspace(detuning, hamiltonian.space.configurations)

    assert np.all(hamiltonian.detuning_ops[0].diagonal == detuning_op_proj)


@pytest.mark.parametrize(
    ("sites", "L"),
    [
        (sites, L)
        for L in L_VALUES
        for n_sites in range(2, L + 1)
        for sites in combinations(range(L), n_sites)
    ],
)
def test_2_level_multi_atom_rabi_real(sites, L):
    program = Chain(L, lattice_spacing=6.1).rydberg.rabi.amplitude
    rabi_coeffs = [Decimal(str(np.random.normal(0.0, 1.0))) for _ in sites]

    program = program.location(list(sites), rabi_coeffs)

    program = program.constant(1.0, 1.0)

    (hamiltonian_data,) = program.bloqade.python().hamiltonian(cache_matrices=True)
    hamiltonian = hamiltonian_data.hamiltonian

    rabi_op = np.array([[0, 1], [1, 0]], dtype=int)

    rabi = sum(
        float(mask) * get_manybody_op(i, L, rabi_op)
        for i, mask in zip(sites, rabi_coeffs)
    )

    assert np.all(hamiltonian.rabi_ops[0].op.tocsr().toarray() == rabi)

    (hamiltonian_data,) = program.bloqade.python().hamiltonian(blockade_radius=6.2)
    hamiltonian = hamiltonian_data.hamiltonian

    rabi_op_proj = project_to_subspace(rabi, hamiltonian.space.configurations)

    assert np.all(hamiltonian.rabi_ops[0].op.tocsr().toarray() == rabi_op_proj)


@pytest.mark.parametrize(
    ("sites", "L"),
    [
        (sites, L)
        for L in L_VALUES
        for n_sites in range(2, L + 1)
        for sites in combinations(range(L), n_sites)
    ],
)
def test_2_level_multi_atom_rabi_complex(sites, L):
    rabi_coeffs = [Decimal(str(np.random.normal(0.0, 1.0))) for _ in sites]

    program = (
        Chain(L, lattice_spacing=6.1)
        .rydberg.rabi.amplitude.location(list(sites), rabi_coeffs)
        .constant(1.0, 1.0)
        .phase.uniform.constant(0.0, 1.0)
    )

    (hamiltonian_data,) = program.bloqade.python().hamiltonian(cache_matrices=True)
    hamiltonian = hamiltonian_data.hamiltonian

    rabi_op = np.array([[0, 0], [1, 0]], dtype=int)

    rabi = sum(
        float(mask) * get_manybody_op(i, L, rabi_op)
        for i, mask in zip(sites, rabi_coeffs)
    )

    assert np.all(hamiltonian.rabi_ops[0].op.tocsr().toarray() == rabi)

    (hamiltonian_data,) = program.bloqade.python().hamiltonian(blockade_radius=6.2)
    hamiltonian = hamiltonian_data.hamiltonian

    rabi_op_proj = project_to_subspace(rabi, hamiltonian.space.configurations)

    assert np.all(hamiltonian.rabi_ops[0].op.tocsr().toarray() == rabi_op_proj)


@pytest.mark.parametrize(
    ("sites", "L"),
    [
        (sites, L)
        for L in L_VALUES
        for n_sites in range(2, L + 1)
        for sites in combinations(range(L), n_sites)
    ],
)
def test_3_level_multi_atom_detuning(sites, L):
    detuning_coeffs = [Decimal(str(np.random.normal(0.0, 1.0))) for site in sites]

    program = (
        Chain(L, lattice_spacing=6.1)
        .rydberg.detuning.location(list(sites), detuning_coeffs)
        .constant(1.0, 1.0)
    )

    (hamiltonian_data,) = program.bloqade.python().hamiltonian(
        use_hyperfine=True, cache_matrices=True
    )
    hamiltonian = hamiltonian_data.hamiltonian

    detuning_op = np.array([0, 0, -1], dtype=int)

    detuning = sum(
        float(mask) * get_manybody_op(i, L, detuning_op)
        for i, mask in zip(sites, detuning_coeffs)
    )

    assert np.all(hamiltonian.detuning_ops[0].get_diagonal(0.0) == detuning)

    (hamiltonian_data,) = program.bloqade.python().hamiltonian(
        blockade_radius=6.2, use_hyperfine=True
    )
    hamiltonian = hamiltonian_data.hamiltonian

    detuning_op_proj = project_to_subspace(detuning, hamiltonian.space.configurations)

    assert np.all(hamiltonian.detuning_ops[0].diagonal == detuning_op_proj)

    # check hyperfine detuning value

    program = (
        Chain(L, lattice_spacing=6.1)
        .hyperfine.detuning.location(list(sites), detuning_coeffs)
        .constant(1.0, 1.0)
    )

    (hamiltonian_data,) = program.bloqade.python().hamiltonian(cache_matrices=True)
    hamiltonian = hamiltonian_data.hamiltonian

    detuning_op = np.array([0, -1, 0], dtype=int)

    detuning = sum(
        float(mask) * get_manybody_op(i, L, detuning_op)
        for i, mask in zip(sites, detuning_coeffs)
    )

    assert np.all(hamiltonian.detuning_ops[0].get_diagonal(0.0) == detuning)

    (hamiltonian_data,) = program.bloqade.python().hamiltonian(blockade_radius=6.2)
    hamiltonian = hamiltonian_data.hamiltonian

    detuning_op_proj = project_to_subspace(detuning, hamiltonian.space.configurations)

    assert np.all(hamiltonian.detuning_ops[0].diagonal == detuning_op_proj)


@pytest.mark.parametrize(
    ("sites", "L"),
    [
        (sites, L)
        for L in L_VALUES
        for n_sites in range(2, L + 1)
        for sites in combinations(range(L), n_sites)
    ],
)
def test_3_level_multi_atom_real(sites, L):
    rabi_coeffs = [Decimal(str(np.random.normal(0.0, 1.0))) for site in sites]

    program = (
        Chain(L, lattice_spacing=6.1)
        .rydberg.rabi.amplitude.location(list(sites), rabi_coeffs)
        .constant(1.0, 1.0)
    )

    (hamiltonian_data,) = program.bloqade.python().hamiltonian(
        cache_matrices=True, use_hyperfine=True
    )
    hamiltonian = hamiltonian_data.hamiltonian

    rabi_op = np.array([[0, 0, 0], [0, 0, 1], [0, 1, 0]], dtype=int)

    rabi = sum(
        float(mask) * get_manybody_op(i, L, rabi_op)
        for i, mask in zip(sites, rabi_coeffs)
    )

    assert np.all(hamiltonian.rabi_ops[0].op.tocsr().toarray() == rabi)

    (hamiltonian_data,) = program.bloqade.python().hamiltonian(
        blockade_radius=6.2, use_hyperfine=True
    )
    hamiltonian = hamiltonian_data.hamiltonian

    rabi_op_proj = project_to_subspace(rabi, hamiltonian.space.configurations)

    assert np.all(hamiltonian.rabi_ops[0].op.tocsr().toarray() == rabi_op_proj)

    # check hyperfine rabi value

    program = (
        Chain(L, lattice_spacing=6.1)
        .hyperfine.rabi.amplitude.location(list(sites), rabi_coeffs)
        .constant(1.0, 1.0)
    )

    (hamiltonian_data,) = program.bloqade.python().hamiltonian(cache_matrices=True)
    hamiltonian = hamiltonian_data.hamiltonian

    rabi_op = np.array([[0, 1, 0], [1, 0, 0], [0, 0, 0]], dtype=int)

    rabi = sum(
        float(mask) * get_manybody_op(i, L, rabi_op)
        for i, mask in zip(sites, rabi_coeffs)
    )

    assert np.all(hamiltonian.rabi_ops[0].op.tocsr().toarray() == rabi)

    (hamiltonian_data,) = program.bloqade.python().hamiltonian(blockade_radius=6.2)
    hamiltonian = hamiltonian_data.hamiltonian

    rabi_op_proj = project_to_subspace(rabi, hamiltonian.space.configurations)

    assert np.all(hamiltonian.rabi_ops[0].op.tocsr().toarray() == rabi_op_proj)


@pytest.mark.parametrize(
    ("sites", "L"),
    [
        (sites, L)
        for L in L_VALUES
        for n_sites in range(2, L + 1)
        for sites in combinations(range(L), n_sites)
    ],
)
def test_3_level_multi_atom_complex(sites, L):
    rabi_coeffs = [Decimal(str(np.random.normal(0.0, 1.0))) for site in sites]

    program = (
        Chain(L, lattice_spacing=6.1)
        .rydberg.rabi.amplitude.location(list(sites), rabi_coeffs)
        .constant(1.0, 1.0)
        .phase.uniform.constant(0.0, 1.0)
    )

    (hamiltonian_data,) = program.bloqade.python().hamiltonian(
        use_hyperfine=True, cache_matrices=True
    )
    hamiltonian = hamiltonian_data.hamiltonian

    rabi_op = np.array([[0, 0, 0], [0, 0, 0], [0, 1, 0]], dtype=int)

    rabi = sum(
        float(mask) * get_manybody_op(i, L, rabi_op)
        for i, mask in zip(sites, rabi_coeffs)
    )

    assert np.all(hamiltonian.rabi_ops[0].op.tocsr().toarray() == rabi)

    (hamiltonian_data,) = program.bloqade.python().hamiltonian(
        blockade_radius=6.2, use_hyperfine=True
    )
    hamiltonian = hamiltonian_data.hamiltonian

    rabi_op_proj = project_to_subspace(rabi, hamiltonian.space.configurations)

    assert np.all(hamiltonian.rabi_ops[0].op.tocsr().toarray() == rabi_op_proj)

    # check hyperfine rabi value

    program = (
        Chain(L, lattice_spacing=6.1)
        .hyperfine.rabi.amplitude.location(list(sites), rabi_coeffs)
        .constant(1.0, 1.0)
        .phase.uniform.constant(0.0, 1.0)
    )

    (hamiltonian_data,) = program.bloqade.python().hamiltonian(cache_matrices=True)
    hamiltonian = hamiltonian_data.hamiltonian

    rabi_op = np.array([[0, 0, 0], [1, 0, 0], [0, 0, 0]], dtype=int)

    rabi = sum(
        float(mask) * get_manybody_op(i, L, rabi_op)
        for i, mask in zip(sites, rabi_coeffs)
    )

    assert np.all(hamiltonian.rabi_ops[0].op.tocsr().toarray() == rabi)

    (hamiltonian_data,) = program.bloqade.python().hamiltonian(blockade_radius=6.2)
    hamiltonian = hamiltonian_data.hamiltonian

    rabi_op_proj = project_to_subspace(rabi, hamiltonian.space.configurations)

    assert np.all(hamiltonian.rabi_ops[0].op.tocsr().toarray() == rabi_op_proj)
