import numpy as np
import pytest
from scipy.stats import ks_2samp
from beartype.typing import Dict

from bloqade.analog import var, cast, dumps, loads, start
from bloqade.analog.atom_arrangement import Chain


def test_integration_1():
    batch = (
        start.add_position((0, 0))
        .add_position((0, 5.0))
        .scale("r")
        .rydberg.detuning.uniform.piecewise_linear(
            [0.1, "ramp_time", 0.1], [-100, -100, 100, 100]
        )
        .amplitude.uniform.piecewise_linear([0.1, "ramp_time", 0.1], [0, 10, 10, 0])
        .assign(ramp_time=3.0, r=8)
        .bloqade.python()
        .run(10000, cache_matrices=True, blockade_radius=6.0, interaction_picture=True)
    )

    batch_str = dumps(batch)
    batch2 = loads(batch_str)
    assert isinstance(batch2, type(batch))
    batch2.report().bitstrings()


def test_integration_2():
    ramp_time = var("ramp_time")
    (
        start.add_position((0, 0))
        .add_position((0, 5.0))
        .scale("r")
        .rydberg.detuning.uniform.piecewise_linear(
            [0.1, "ramp_time", 0.1], [-100, -100, 100, 100]
        )
        .amplitude.uniform.piecewise_linear([0.1, ramp_time, 0.1], [0, 10, 10, 0])
        .phase.uniform.piecewise_constant(
            [0.1, ramp_time / 2, ramp_time / 2, 0.1], [0, 0, np.pi, np.pi]
        )
        .assign(ramp_time=3.0, r=6)
        .bloqade.python()
        .run(10000, cache_matrices=False, blockade_radius=6.0, multiprocessing=False)
        .report()
        .bitstrings()
    )


def test_integration_3():
    ramp_time = var("ramp_time")
    (
        start.add_position((0, 0))
        .add_position((0, 5.0))
        .scale("r")
        .rydberg.detuning.uniform.piecewise_linear(
            [0.1, ramp_time, 0.1], [-100, -100, 100, 100]
        )
        .amplitude.uniform.piecewise_linear([0.1, ramp_time, 0.1], [0, 10, 10, 0])
        .phase.uniform.piecewise_constant(
            [0.1, ramp_time / 2, ramp_time / 2, 0.1], [0, 0, np.pi, np.pi]
        )
        .amplitude.scale("rabi_mask")
        .fn(lambda t: 4 * np.sin(3 * t), ramp_time + 0.2)
        .assign(ramp_time=3.0, rabi_mask=[10.0, 0.1], r=6)
        .bloqade.python()
        .run(10000, cache_matrices=True, blockade_radius=6.0)
        .report()
        .bitstrings()
    )


def test_integration_4():
    ramp_time = var("ramp_time")
    (
        start.add_position((0, 0))
        .add_position((0, 5.0))
        .scale("r")
        .rydberg.detuning.uniform.piecewise_linear(
            [0.1, ramp_time, 0.1], [-100, -100, 100, 100]
        )
        .amplitude.uniform.piecewise_linear([0.1, ramp_time, 0.1], [0, 10, 10, 0])
        .amplitude.scale("rabi_mask")
        .fn(lambda t: 4 * np.sin(3 * t), ramp_time + 0.2)
        .amplitude.location(1)
        .linear(0.0, 1.0, ramp_time + 0.2)
        .assign(ramp_time=3.0, rabi_mask=[10.0, 0.1], r=6)
        .bloqade.python()
        .run(10000, cache_matrices=True, blockade_radius=6.0)
        .report()
        .bitstrings()
    )


def test_integration_5():
    ramp_time = var("ramp_time")
    (
        start.add_position((0, 0))
        .add_position((0, 5.0))
        .scale("r")
        .rydberg.detuning.uniform.piecewise_linear(
            [0.1, ramp_time, 0.1], [-100, -100, 100, 100]
        )
        .amplitude.uniform.piecewise_linear([0.1, ramp_time, 0.1], [0, 10, 10, 0])
        .phase.location(1)
        .linear(0.0, 1.0, ramp_time + 0.2)
        .assign(ramp_time=3.0, r=6)
        .bloqade.python()
        .run(10000, cache_matrices=True, blockade_radius=6.0)
        .report()
        .bitstrings()
    )


def test_integration_6():
    ramp_time = var("ramp_time")
    (
        start.add_position((0, 0))
        .add_position((0, 5.0))
        .scale("r")
        .rydberg.detuning.uniform.piecewise_linear(
            [0.1, ramp_time, 0.1], [-100, -100, 100, 100]
        )
        .location(1)
        .constant(3.0, ramp_time + 0.2)
        .location(0)
        .linear(2.0, 0, ramp_time + 0.2)
        .amplitude.uniform.piecewise_linear([0.1, ramp_time, 0.1], [0, 10, 10, 0])
        .phase.location(1)
        .linear(0.0, 1.0, ramp_time + 0.2)
        .assign(ramp_time=3.0, r=6)
        .bloqade.python()
        .run(10000, cache_matrices=True, blockade_radius=6.0)
        .report()
        .bitstrings()
    )


def test_serialization():
    ramp_time = var("ramp_time")
    batch = (
        start.add_position((0, 0))
        .add_position((0, 5.0))
        .scale("r")
        .rydberg.detuning.uniform.piecewise_linear(
            [0.1, ramp_time, 0.1], [-100, -100, 100, 100]
        )
        .amplitude.uniform.piecewise_linear([0.1, ramp_time, 0.1], [0, 10, 10, 0])
        .amplitude.scale("rabi_mask")
        .piecewise_linear([0.1, ramp_time, 0.1], [0, 10, 10, 0])
        .amplitude.location(1)
        .linear(0.0, 1.0, ramp_time + 0.2)
        .assign(ramp_time=3.0, rabi_mask=[10.0, 0.1])
        .batch_assign(r=np.linspace(0.1, 4, 5).tolist())
        .bloqade.python()
        ._compile(100)
    )

    obj_str = dumps(batch)
    batch2 = loads(obj_str)
    assert isinstance(batch2, type(batch))


def KS_test(
    lhs_counts: Dict[str, int], rhs_counts: Dict[str, int], alpha: float = 0.05
) -> None:
    lhs_samples = []
    rhs_samples = []

    for bitstring, count in lhs_counts.items():
        lhs_samples += [int(bitstring, 2)] * count

    for bitstring, count in rhs_counts.items():
        rhs_samples += [int(bitstring, 2)] * count

    result = ks_2samp(lhs_samples, rhs_samples, method="exact")

    assert result.pvalue > alpha


def test_bloqade_against_braket():
    np.random.seed(9123892)
    durations = cast([0.1, 0.1, 0.1])

    prog = (
        Chain(3, lattice_spacing=6.1)
        .rydberg.detuning.uniform.piecewise_linear(durations, [-20, -20, "d", "d"])
        .amplitude.uniform.piecewise_linear(durations, [0, 15, 15, 0])
        .phase.uniform.constant(0.3, sum(durations))
        .batch_assign(d=[10, 20])
    )

    nshots = 1000
    a = prog.bloqade.python().run(nshots, cache_matrices=True).report().counts()
    b = prog.braket.local_emulator().run(nshots).report().counts()

    for lhs, rhs in zip(a, b):
        KS_test(lhs, rhs)


def test_bloqade_against_braket_2():
    np.random.seed(192839812)
    durations = cast([0.1, 0.1, 0.1])
    values = [0, 15, 15, 0]

    prog_1 = (
        Chain(3, lattice_spacing=6.1)
        .rydberg.detuning.uniform.piecewise_linear(durations, [-20, -20, "d", "d"])
        .amplitude.uniform.piecewise_linear(durations, values)
        .batch_assign(d=[10, 20])
    )
    prog_2 = (
        Chain(3, lattice_spacing=6.1)
        .rydberg.detuning.uniform.piecewise_linear(durations, [-20, -20, "d", "d"])
        .amplitude.location(0)
        .piecewise_linear(durations, values)
        .amplitude.location(1)
        .piecewise_linear(durations, values)
        .amplitude.location(2)
        .piecewise_linear(durations, values)
        .phase.location(0)
        .constant(0.0, sum(durations))
        .batch_assign(d=[10, 20])
    )

    nshots = 1000
    a = prog_2.bloqade.python().run(nshots, cache_matrices=True).report().counts()
    b = prog_1.braket.local_emulator().run(nshots).report().counts()

    for lhs, rhs in zip(a, b):
        KS_test(lhs, rhs)


def test_bloqade_filling():

    geometry = (
        start.add_position((0, 0), filling=True)
        .add_position((6.1, 0), filling=False)
        .add_position((0, 6.1), filling=False)
        .add_position((6.1, 6.1), filling=True)
    )

    durations = cast([0.1, 0.1, 0.1])
    values_1 = [0, 15, 15, 0]
    values_2 = [0, 2, 15, 0]

    shots = 1000

    result_1 = (
        geometry.rydberg.detuning.uniform.piecewise_linear(
            durations, [-20, -20, "d", "d"]
        )
        .amplitude.location(0)
        .piecewise_linear(durations, values_1)
        .amplitude.location(3)
        .piecewise_linear(durations, values_2)
        .amplitude.location(
            1
        )  # note this drive is ignored because the site is not filled
        .piecewise_linear(durations, values_2)
        .assign(d=10)
        .bloqade.python()
        .run(shots)
    )
    # removing vacant sites implies 0 -> 0 and 2 -> 1 based
    # on the order of how the sites are added
    result_2 = (
        geometry.remove_vacant_sites()
        .rydberg.detuning.uniform.piecewise_linear(durations, [-20, -20, "d", "d"])
        .amplitude.location(0)
        .piecewise_linear(durations, values_1)
        .amplitude.location(1)
        .piecewise_linear(durations, values_2)
        .assign(d=10)
        .bloqade.python()
        .run(shots)
    )

    (a,) = result_1.report().counts()
    (b,) = result_2.report().counts()

    # post-processing to match the keys in
    # both dictionaries. This involves removing the
    # the second and the third bits from the keys in a
    a_post_processed = type(a)()

    for key, value in a.items():
        new_key = "".join((key[0], key[3]))
        a_post_processed[new_key] = value

    KS_test(a_post_processed, b)


@pytest.mark.parametrize(
    "phi, omega, delta",
    [
        (0.0, 1.0, 0.0),
        (np.pi / 2, 1.0, 0.0),
        (np.pi, 1.0, 0.0),
        (3 * np.pi / 2, 1.0, 0.0),
        (0.0, 2.0, 0.0),
        (np.pi / 2, 2.0, 0.0),
        (np.pi, 2.0, 0.0),
        (3 * np.pi / 2, 2.0, 0.0),
        (0.0, 1.0, 1.0),
        (np.pi / 2, 1.0, 1.0),
        (np.pi, 1.0, 1.0),
        (-3 * np.pi / 2, 1.0, 1.0),
        (0.0, 2.0, 1.0),
        (-np.pi / 2, 2.0, 1.0),
        (-np.pi, 2.0, 1.0),
        (-3 * np.pi / 2, 2.0, 1.0),
        (-0.321, 1.0, 0.5),
        (0.543, 1.0, 0.5),
        (2.321, 1.0, 1.1232),
        (-2.543, 4.12390, 2.4354),
    ],
)
def test_hamiltonian(phi, omega, delta):

    def hamiltonian(phi: float, omega: float, delta: float) -> np.ndarray:
        # index 0 is g
        # index 1 is r
        G = 0j
        # Detuning
        G += np.diag([0, -1]) * delta

        G[0, 1] = np.exp(1j * phi) * omega / 2
        G[1, 0] = np.exp(-1j * phi) * omega / 2
        return G

    T = 2 * np.pi
    (program,) = (
        (
            start.add_position([(0, 0)])
            .rydberg.rabi.amplitude.uniform.constant(omega, T)
            .phase.uniform.constant(phi, T)
            .detuning.uniform.constant(delta, T)
        )
        .bloqade.python()
        .hamiltonian()
    )

    mat = program.hamiltonian.tocsr(0.0).toarray()

    assert np.allclose(mat, hamiltonian(phi, omega, delta))
