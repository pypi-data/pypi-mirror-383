from unittest.mock import Mock, patch

import numpy as np
import pytest

import bloqade.analog.emulate.ir.space
from bloqade.analog.emulate.ir.space import Space
from bloqade.analog.emulate.ir.emulator import Register
from bloqade.analog.emulate.ir.atom_type import TwoLevelAtom, ThreeLevelAtom


def test_two_level_space():
    positions = [(0, 0), (0, 1)]
    register = Register(TwoLevelAtom, positions, 0)
    space = Space.create(register)
    print(space)
    assert space.n_atoms == 2
    assert space.size == 4
    assert np.all(space.configurations == np.array([0, 1, 2, 3]))


def test_two_level_subspace():
    positions = [(0, 0), (0, 1)]
    register = Register(TwoLevelAtom, positions, 1.1)
    space = Space.create(register)
    print(space)
    assert space.n_atoms == 2
    assert space.size == 3
    assert np.all(space.configurations == np.array([0, 1, 2]))


def test_two_level_subspace_2():
    positions = [(0, 0), (0, 1), (1, 0), (1, 1)]
    register = Register(TwoLevelAtom, positions, np.sqrt(2) + 0.1)
    space = Space.create(register)
    print(space)
    assert space.n_atoms == 4
    assert space.size == 5
    assert np.all(space.configurations == np.array([0, 1, 2, 4, 8]))


def test_two_level_subspace_3():
    space_part = Space.create(Register(TwoLevelAtom, [(0, 0), (0, 1)], 1.1))

    space = Space.create(Register(TwoLevelAtom, [(0, 0), (0, 1), (0, 5), (0, 6)], 1.1))

    config = space_part.configurations
    actual_configs = np.kron(config, np.ones_like(config, dtype=np.uint8)) + np.kron(
        np.ones_like(config) * 2**2, config
    )

    actual_configs.sort()

    np.testing.assert_equal(space.configurations, actual_configs)


def test_three_level_space():
    positions = [(0, 0), (0, 1)]
    register = Register(ThreeLevelAtom, positions, 0)
    space = Space.create(register)
    print(space)
    assert space.n_atoms == 2
    assert space.size == 9
    assert np.all(space.configurations == np.array([0, 1, 2, 3, 4, 5, 6, 7, 8]))


def test_three_level_subspace():
    positions = [(0, 0), (0, 1)]
    register = Register(ThreeLevelAtom, positions, 1.1)
    space = Space.create(register)
    print(space)
    assert space.n_atoms == 2
    assert space.size == 8
    assert np.all(space.configurations == np.array([0, 1, 2, 3, 4, 5, 6, 7]))


def test_three_level_subspace_2():
    positions = [(0, 0), (0.5, np.sqrt(3) / 2), (0, 1)]
    register = Register(ThreeLevelAtom, positions, 1.1)
    space = Space.create(register)
    print(space)
    assert space.n_atoms == 3
    assert space.size == 20
    assert np.all(
        space.configurations
        == np.array(
            [0, 1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15, 16, 18, 19, 21, 22]
        )
    )


def test_three_level_subspace_3():
    space = Space.create(Register(TwoLevelAtom, [(0, 0), (0, 4), (0, 5)], 1.1))
    assert np.all(space.configurations == np.array([0, 1, 2, 3, 4, 5]))

    space_part = Space.create(Register(ThreeLevelAtom, [(0, 0), (0, 1)], 1.1))

    space = Space.create(
        Register(ThreeLevelAtom, [(0, 0), (0, 1), (0, 5), (0, 6)], 1.1)
    )

    config = space_part.configurations
    actual_configs = np.kron(config, np.ones_like(config, dtype=np.uint8)) + np.kron(
        np.ones_like(config) * 3**2, config
    )

    actual_configs.sort()

    np.testing.assert_equal(space.configurations, actual_configs)


def test_two_level_integer_to_string():
    assert TwoLevelAtom.integer_to_string(0, 2) == "|gg>"
    assert TwoLevelAtom.integer_to_string(1, 2) == "|rg>"
    assert TwoLevelAtom.integer_to_string(2, 2) == "|gr>"
    assert TwoLevelAtom.integer_to_string(3, 2) == "|rr>"


def test_two_level_string_to_integer():
    assert TwoLevelAtom.string_to_integer("|gg>") == 0
    assert TwoLevelAtom.string_to_integer("|rg>") == 1
    assert TwoLevelAtom.string_to_integer("|gr>") == 2
    assert TwoLevelAtom.string_to_integer("|rr>") == 3


def test_three_level_integer_to_string():
    assert ThreeLevelAtom.integer_to_string(0, 2) == "|gg>"
    assert ThreeLevelAtom.integer_to_string(1, 2) == "|hg>"
    assert ThreeLevelAtom.integer_to_string(2, 2) == "|rg>"
    assert ThreeLevelAtom.integer_to_string(3, 2) == "|gh>"
    assert ThreeLevelAtom.integer_to_string(4, 2) == "|hh>"
    assert ThreeLevelAtom.integer_to_string(5, 2) == "|rh>"
    assert ThreeLevelAtom.integer_to_string(6, 2) == "|gr>"
    assert ThreeLevelAtom.integer_to_string(7, 2) == "|hr>"
    assert ThreeLevelAtom.integer_to_string(8, 2) == "|rr>"


def test_three_level_string_to_integer():
    assert ThreeLevelAtom.string_to_integer("|gg>") == 0
    assert ThreeLevelAtom.string_to_integer("|hg>") == 1
    assert ThreeLevelAtom.string_to_integer("|rg>") == 2
    assert ThreeLevelAtom.string_to_integer("|gh>") == 3
    assert ThreeLevelAtom.string_to_integer("|hh>") == 4
    assert ThreeLevelAtom.string_to_integer("|rh>") == 5
    assert ThreeLevelAtom.string_to_integer("|gr>") == 6
    assert ThreeLevelAtom.string_to_integer("|hr>") == 7
    assert ThreeLevelAtom.string_to_integer("|rr>") == 8


def test_two_level_transition_indices():
    positions = [(0, 0), (0, 1), (1, 0)]
    register = Register(TwoLevelAtom, positions, 0)
    space = Space.create(register)
    print(space)

    # 0. |ggg> -> |rgg>
    # 1. |rgg> ->
    # 2. |grg> -> |rrg>
    # 3. |rrg> ->
    # 4. |ggr> -> |rgr>
    # 5. |rgr> ->
    # 6. |grr> -> |rrr>
    # 7. |rrr> ->

    row_indices, col_indices = space.transition_state_at(0, 0, 1)

    row_indices_expected = np.argwhere(
        np.array([True, False, True, False, True, False, True, False])
    ).ravel()
    col_indices_expected = np.array([1, 3, 5, 7])

    assert np.all(row_indices == row_indices_expected)
    assert np.all(col_indices == col_indices_expected)

    # 0. |ggg> -> |grg>
    # 1. |rgg> -> |rrg>
    # 2. |grg> ->
    # 3. |rrg> ->
    # 4. |ggr> -> |grr>
    # 5. |rgr> -> |rrr>
    # 6. |grr> ->
    # 7. |rrr> ->

    row_indices, col_indices = space.transition_state_at(1, 0, 1)

    row_indices_expected = np.argwhere(
        np.array([True, True, False, False, True, True, False, False])
    ).ravel()
    col_indices_expected = np.array([2, 3, 6, 7])

    assert np.all(row_indices == row_indices_expected)
    assert np.all(col_indices == col_indices_expected)

    # 0. |ggg> -> |ggr>
    # 1. |rgg> -> |rgr>
    # 2. |grg> -> |grr>
    # 3. |rrg> -> |rrr>
    # 4. |ggr> ->
    # 5. |rgr> ->
    # 6. |grr> ->
    # 7. |rrr> ->

    row_indices, col_indices = space.transition_state_at(2, 0, 1)

    row_indices_expected = np.argwhere(
        np.array([True, True, True, True, False, False, False, False])
    ).ravel()
    col_indices_expected = np.array([4, 5, 6, 7])

    assert np.all(row_indices == row_indices_expected)
    assert np.all(col_indices == col_indices_expected)


def test_two_level_subspace_transition_indices():
    positions = [(0, 0), (0, 1), (1, 0)]
    register = Register(TwoLevelAtom, positions, 1)
    space = Space.create(register)
    print(space)

    # 0. |ggg> -> |rgg>
    # 1. |rgg> ->
    # 2. |grg> ->
    # 3. |ggr> ->
    # 4. |grr> ->

    row_indices, col_indices = space.transition_state_at(0, 0, 1)

    row_indices_expected = np.array([0])
    col_indices_expected = np.array(
        [
            space.fock_state_to_index("|rgg>"),
        ]
    )

    assert np.all(row_indices == row_indices_expected)
    assert np.all(col_indices == col_indices_expected)

    # 0. |ggg> -> |grg>
    # 1. |rgg> ->
    # 2. |grg> ->
    # 3. |ggr> -> |grr>
    # 4. |grr> ->

    row_indices, col_indices = space.transition_state_at(1, 0, 1)

    row_indices_expected = np.array([0, 3])
    col_indices_expected = np.array(
        [
            space.fock_state_to_index("|grg>"),
            space.fock_state_to_index("|grr>"),
        ]
    )

    assert np.all(row_indices == row_indices_expected)
    assert np.all(col_indices == col_indices_expected)

    # 0. |ggg> -> |ggr>
    # 1. |rgg> ->
    # 2. |grg> -> |grr>
    # 3. |ggr> ->
    # 4. |grr> ->

    row_indices, col_indices = space.transition_state_at(2, 0, 1)

    row_indices_expected = np.array([0, 2])
    col_indices_expected = np.array(
        [
            space.fock_state_to_index("|ggr>"),
            space.fock_state_to_index("|grr>"),
        ]
    )

    assert np.all(row_indices == row_indices_expected)
    assert np.all(col_indices == col_indices_expected)


def test_three_level_transition_indices():
    positions = [(0, 0), (0, 1)]
    register = Register(ThreeLevelAtom, positions, 0)
    space = Space.create(register)
    print(space)

    # 0. |gg> -> |hg>
    # 1. |hg> ->
    # 2. |rg> ->
    # 3. |gh> -> |hh>
    # 4. |hh> ->
    # 5. |rh> ->
    # 6. |gr> -> |hr>
    # 7. |hr> ->
    # 8. |rr> ->

    row_indices, col_indices = space.transition_state_at(0, 0, 1)

    row_indices_expected = np.argwhere(
        np.array([True, False, False, True, False, False, True, False, False])
    ).ravel()
    col_indices_expected = np.array(
        [
            ThreeLevelAtom.string_to_integer("|hg>"),
            ThreeLevelAtom.string_to_integer("|hh>"),
            ThreeLevelAtom.string_to_integer("|hr>"),
        ]
    )

    assert np.all(row_indices == row_indices_expected)
    assert np.all(col_indices == col_indices_expected)

    # 0. |gg> ->
    # 1. |hg> -> |rg>
    # 2. |rg> ->
    # 3. |gh> ->
    # 4. |hh> -> |rh>
    # 5. |rh> ->
    # 6. |gr> ->
    # 7. |hr> -> |rr>
    # 8. |rr> ->

    row_indices, col_indices = space.transition_state_at(0, 1, 2)

    row_indices_expected = np.argwhere(
        np.array([False, True, False, False, True, False, False, True, False])
    ).ravel()
    col_indices_expected = np.array(
        [
            ThreeLevelAtom.string_to_integer("|rg>"),
            ThreeLevelAtom.string_to_integer("|rh>"),
            ThreeLevelAtom.string_to_integer("|rr>"),
        ]
    )

    assert np.all(row_indices == row_indices_expected)
    assert np.all(col_indices == col_indices_expected)


def test_three_level_subspace_transition_indices():
    positions = [(0, 0), (0, 1)]
    register = Register(ThreeLevelAtom, positions, 1.1)
    space = Space.create(register)
    print(space)

    # 0. |gg> -> |hg>
    # 1. |hg> ->
    # 2. |rg> ->
    # 3. |gh> -> |hh>
    # 4. |hh> ->
    # 5. |rh> ->
    # 6. |gr> -> |hr>
    # 7. |hr> ->

    row_indices, col_indices = space.transition_state_at(0, 0, 1)

    row_indices_expected = np.array([0, 3, 6])
    col_indices_expected = np.array(
        [
            ThreeLevelAtom.string_to_integer("|hg>"),
            ThreeLevelAtom.string_to_integer("|hh>"),
            ThreeLevelAtom.string_to_integer("|hr>"),
        ]
    )

    assert np.all(row_indices == row_indices_expected)
    assert np.all(col_indices == col_indices_expected)

    # 0. |gg> ->
    # 1. |hg> -> |rg>
    # 2. |rg> ->
    # 3. |gh> ->
    # 4. |hh> -> |rh>
    # 5. |rh> ->
    # 6. |gr> ->
    # 7. |hr> ->

    row_indices, col_indices = space.transition_state_at(0, 1, 2)

    row_indices_expected = np.array([1, 4])
    col_indices_expected = np.array(
        [
            ThreeLevelAtom.string_to_integer("|rg>"),
            ThreeLevelAtom.string_to_integer("|rh>"),
        ]
    )

    assert np.all(row_indices == row_indices_expected)
    assert np.all(col_indices == col_indices_expected)


def test_two_level_swap_indices():
    positions = [(0, 0), (0, 1), (1, 0)]
    register = Register(TwoLevelAtom, positions, 0)
    space = Space.create(register)
    print(space)

    row_indices, col_indices = space.swap_state_at(0, 0, 1)

    row_indices_expected = slice(None, None, None)
    col_indices_expected = np.array([1, 0, 3, 2, 5, 4, 7, 6])

    assert row_indices == row_indices_expected
    assert np.all(col_indices == col_indices_expected)

    row_indices, col_indices = space.swap_state_at(1, 0, 1)

    row_indices_expected = slice(None, None, None)
    col_indices_expected = np.array([2, 3, 0, 1, 6, 7, 4, 5])

    assert row_indices == row_indices_expected
    assert np.all(col_indices == col_indices_expected)

    row_indices, col_indices = space.swap_state_at(2, 0, 1)

    row_indices_expected = slice(None, None, None)
    col_indices_expected = np.array([4, 5, 6, 7, 0, 1, 2, 3])

    assert row_indices == row_indices_expected
    assert np.all(col_indices == col_indices_expected)


def test_two_level_subspace_swap_indices():
    positions = [(0, 0), (0, 1), (1, 0)]
    register = Register(TwoLevelAtom, positions, 1)
    space = Space.create(register)
    print(space)

    # 0. |ggg> -> |rgg>
    # 1. |rgg> -> |ggg>
    # 2. |grg> ->
    # 3. |ggr> ->
    # 4. |grr> ->

    row_indices, col_indices = space.swap_state_at(0, 0, 1)

    row_indices_expected = np.argwhere(
        np.array([True, True, False, False, False])
    ).ravel()
    col_indices_expected = np.array(
        [
            space.fock_state_to_index("|rgg>"),
            space.fock_state_to_index("|ggg>"),
        ]
    )

    assert np.all(row_indices == row_indices_expected)
    assert np.all(col_indices == col_indices_expected)

    # 0. |ggg> -> |grg>
    # 1. |rgg> ->
    # 2. |grg> -> |ggg>
    # 3. |ggr> -> |grr>
    # 4. |grr> -> |ggr>

    row_indices, col_indices = space.swap_state_at(1, 0, 1)

    row_indices_expected = np.argwhere(
        np.array([True, False, True, True, True])
    ).ravel()
    col_indices_expected = np.array(
        [
            space.fock_state_to_index("|grg>"),
            space.fock_state_to_index("|ggg>"),
            space.fock_state_to_index("|grr>"),
            space.fock_state_to_index("|ggr>"),
        ]
    )

    assert np.all(row_indices == row_indices_expected)
    assert np.all(col_indices == col_indices_expected)

    # 0. |ggg> -> |ggr>
    # 1. |rgg> ->
    # 2. |grg> -> |grr>
    # 3. |ggr> -> |ggg>
    # 4. |grr> -> |grg>

    row_indices, col_indices = space.swap_state_at(2, 0, 1)

    row_indices_expected = np.argwhere(
        np.array([True, False, True, True, True])
    ).ravel()
    col_indices_expected = np.array(
        [
            space.fock_state_to_index("|ggr>"),
            space.fock_state_to_index("|grr>"),
            space.fock_state_to_index("|ggg>"),
            space.fock_state_to_index("|grg>"),
        ]
    )

    assert np.all(row_indices == row_indices_expected)
    assert np.all(col_indices == col_indices_expected)


def test_three_level_swap_indices():
    positions = [(0, 0), (0, 1)]
    register = Register(ThreeLevelAtom, positions, 0)
    space = Space.create(register)
    print(space)

    # 0. |gg>
    # 1. |hg>
    # 2. |rg>
    # 3. |gh>
    # 4. |hh>
    # 5. |rh>
    # 6. |gr>
    # 7. |hr>
    # 8. |rr>

    row_indices, col_indices = space.swap_state_at(0, 0, 1)

    row_indices_expected = np.argwhere(
        np.array([True, True, False, True, True, False, True, True, False])
    ).ravel()
    col_indices_expected = np.array(
        [
            ThreeLevelAtom.string_to_integer("|hg>"),
            ThreeLevelAtom.string_to_integer("|gg>"),
            ThreeLevelAtom.string_to_integer("|hh>"),
            ThreeLevelAtom.string_to_integer("|gh>"),
            ThreeLevelAtom.string_to_integer("|hr>"),
            ThreeLevelAtom.string_to_integer("|gr>"),
        ]
    )

    assert np.all(row_indices == row_indices_expected)
    assert np.all(col_indices == col_indices_expected)

    # 0. |gg>
    # 1. |hg>
    # 2. |rg>
    # 3. |gh>
    # 4. |hh>
    # 5. |rh>
    # 6. |gr>
    # 7. |hr>
    # 8. |rr>

    row_indices, col_indices = space.swap_state_at(0, 1, 2)

    row_indices_expected = np.argwhere(
        np.array([False, True, True, False, True, True, False, True, True])
    ).ravel()
    col_indices_expected = np.array(
        [
            ThreeLevelAtom.string_to_integer("|rg>"),
            ThreeLevelAtom.string_to_integer("|hg>"),
            ThreeLevelAtom.string_to_integer("|rh>"),
            ThreeLevelAtom.string_to_integer("|hh>"),
            ThreeLevelAtom.string_to_integer("|rr>"),
            ThreeLevelAtom.string_to_integer("|hr>"),
        ]
    )

    assert np.all(row_indices == row_indices_expected)
    assert np.all(col_indices == col_indices_expected)


def test_three_level_subspace_swap_indices():
    positions = [(0, 0), (0, 1)]
    register = Register(ThreeLevelAtom, positions, 1.1)
    space = Space.create(register)
    print(space)

    # 0. |gg> -> |hg>
    # 1. |hg> -> |gg>
    # 2. |rg> ->
    # 3. |gh> -> |hh>
    # 4. |hh> -> |gh>
    # 5. |rh> ->
    # 6. |gr> -> |hr>
    # 7. |hr> -> |gr>

    row_indices, col_indices = space.swap_state_at(0, 0, 1)

    row_indices_expected = np.argwhere(
        np.array([True, True, False, True, True, False, True, True])
    ).ravel()
    col_indices_expected = np.array(
        [
            ThreeLevelAtom.string_to_integer("|hg>"),
            ThreeLevelAtom.string_to_integer("|gg>"),
            ThreeLevelAtom.string_to_integer("|hh>"),
            ThreeLevelAtom.string_to_integer("|gh>"),
            ThreeLevelAtom.string_to_integer("|hr>"),
            ThreeLevelAtom.string_to_integer("|gr>"),
        ]
    )

    assert np.all(row_indices == row_indices_expected)
    assert np.all(col_indices == col_indices_expected)

    # 0. |gg> ->
    # 1. |hg> -> |rg>
    # 2. |rg> -> |hg>
    # 3. |gh> ->
    # 4. |hh> -> |rh>
    # 5. |rh> -> |hh>
    # 6. |gr> ->
    # 7. |hr> ->

    row_indices, col_indices = space.swap_state_at(0, 1, 2)

    row_indices_expected = np.array([1, 2, 4, 5])
    col_indices_expected = np.array(
        [
            ThreeLevelAtom.string_to_integer("|rg>"),
            ThreeLevelAtom.string_to_integer("|hg>"),
            ThreeLevelAtom.string_to_integer("|rh>"),
            ThreeLevelAtom.string_to_integer("|hh>"),
        ]
    )

    assert np.all(row_indices == row_indices_expected)
    assert np.all(col_indices == col_indices_expected)


def test_fock_state_to_index():
    positions = [(0, 0), (0, 1), (1, 0)]
    register = Register(TwoLevelAtom, positions, 0)
    space = Space.create(register)
    print(space)

    assert space.fock_state_to_index("|ggg>") == 0
    assert space.fock_state_to_index("|rgg>") == 1
    assert space.fock_state_to_index("|grg>") == 2
    assert space.fock_state_to_index("|rrg>") == 3
    assert space.fock_state_to_index("|ggr>") == 4
    assert space.fock_state_to_index("|rgr>") == 5
    assert space.fock_state_to_index("|grr>") == 6
    assert space.fock_state_to_index("|rrr>") == 7

    positions = [(0, 0), (0, 1), (1, 0)]
    register = Register(TwoLevelAtom, positions, 1)
    space = Space.create(register)
    print(space)

    # 0. |ggg>
    # 1. |rgg>
    # 2. |grg>
    # 3. |ggr>
    # 4. |grr>

    assert space.fock_state_to_index("|ggg>") == 0
    assert space.fock_state_to_index("|rgg>") == 1
    assert space.fock_state_to_index("|grg>") == 2
    assert space.fock_state_to_index("|ggr>") == 3
    assert space.fock_state_to_index("|grr>") == 4

    with pytest.raises(ValueError):
        space.fock_state_to_index("|rrr>")

    with pytest.raises(ValueError):
        space.fock_state_to_index("|rgr>")


def test_index_to_fock_state():
    positions = [(0, 0), (0, 1), (1, 0)]
    register = Register(TwoLevelAtom, positions, 0)
    space = Space.create(register)
    print(space)

    assert space.index_to_fock_state(0) == "|ggg>"
    assert space.index_to_fock_state(1) == "|rgg>"
    assert space.index_to_fock_state(2) == "|grg>"
    assert space.index_to_fock_state(3) == "|rrg>"
    assert space.index_to_fock_state(4) == "|ggr>"
    assert space.index_to_fock_state(5) == "|rgr>"
    assert space.index_to_fock_state(6) == "|grr>"
    assert space.index_to_fock_state(7) == "|rrr>"

    positions = [(0, 0), (0, 1), (1, 0)]
    register = Register(TwoLevelAtom, positions, 1)
    space = Space.create(register)
    print(space)

    # 0. |ggg>
    # 1. |rgg>
    # 2. |grg>
    # 3. |ggr>
    # 4. |grr>

    assert space.index_to_fock_state(0) == "|ggg>"
    assert space.index_to_fock_state(1) == "|rgg>"
    assert space.index_to_fock_state(2) == "|grg>"
    assert space.index_to_fock_state(3) == "|ggr>"
    assert space.index_to_fock_state(4) == "|grr>"

    with pytest.raises(ValueError):
        space.index_to_fock_state(-1)

    with pytest.raises(ValueError):
        space.index_to_fock_state(6)


def test_zero_state():
    positions = [(0, 0), (0, 1), (1, 0)]
    register = Register(TwoLevelAtom, positions, 0)
    space = Space.create(register)
    print(space)

    assert np.all(space.zero_state().data == np.array([1, 0, 0, 0, 0, 0, 0, 0]))

    positions = [(0, 0), (0, 1), (1, 0)]
    register = Register(TwoLevelAtom, positions, 1)
    space = Space.create(register)
    print(space)

    assert np.all(space.zero_state().data == np.array([1, 0, 0, 0, 0]))


@patch("bloqade.analog.emulate.ir.space.np.random.choice")
def test_sample_state(patch_choice):
    positions = [(0, 0), (0, 1), (1, 0)]
    register = Register(TwoLevelAtom, positions, 1)
    space = Space.create(register)
    print(space)

    bloqade.analog.emulate.ir.space.np.random.choice.return_value = np.array(
        [0, 1, 2, 3, 4]
    )
    state_vector = np.array([0.1, 0.2, 0.3, 0.4, 0.5])

    expected_bitstrings = np.array(
        [
            [0, 0, 0],
            [1, 0, 0],
            [0, 1, 0],
            [1, 1, 0],
            [0, 0, 1],
        ]
    )
    bitstrings = space.sample_state_vector(state_vector, 5)
    print(bitstrings)
    assert np.all(bitstrings == expected_bitstrings)

    positions = [(0, 0), (0, 1)]
    register = Register(ThreeLevelAtom, positions, 1)
    space = Space.create(register)
    print(space)

    bloqade.analog.emulate.ir.space.np.random.choice.return_value = np.array(
        [0, 1, 2, 3, 4, 5, 6, 7, 8]
    )

    # 0. |gg> -> |gg>
    # 1. |hg> -> |gg>
    # 2. |rg> -> |rg>
    # 3. |gh> -> |gg>
    # 4. |hh> -> |gg>
    # 5. |rh> -> |rg>
    # 6. |gr> -> |gr>
    # 7. |hr> -> |gr>
    # 8. |rr> -> |rr>

    state_vector = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.1, 0.2, 0.3])

    expected_bitstrings = np.array(
        [
            [0, 0],
            [0, 0],
            [1, 0],
            [0, 0],
            [0, 0],
            [1, 0],
            [0, 1],
            [0, 1],
            [1, 1],
        ]
    )

    bitstrings = space.sample_state_vector(state_vector, 9)
    print(bitstrings)

    assert np.all(bitstrings == expected_bitstrings)


def test_str():
    positions = [(0, 0), (0, 1)]
    register = Register(ThreeLevelAtom, positions, 1)
    space = Space.create(register)

    assert (
        str(space) == "0. |gg>\n"
        "1. |hg>\n"
        "2. |rg>\n"
        "3. |gh>\n"
        "4. |hh>\n"
        "5. |rh>\n"
        "6. |gr>\n"
        "7. |hr>\n"
    )

    positions = [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0), (2, 1), (3, 0), (3, 1)]
    register = Register(ThreeLevelAtom, positions, 1)
    space = Space.create(register)

    assert (
        str(space) == "   0. |gggggggg>\n"
        "   1. |hggggggg>\n"
        "   2. |rggggggg>\n"
        "   3. |ghgggggg>\n"
        "   4. |hhgggggg>\n"
        "   5. |rhgggggg>\n"
        "   6. |grgggggg>\n"
        "   7. |hrgggggg>\n"
        "   8. |gghggggg>\n"
        "   9. |hghggggg>\n"
        "  10. |rghggggg>\n"
        "  11. |ghhggggg>\n"
        "  12. |hhhggggg>\n"
        "  13. |rhhggggg>\n"
        "  14. |grhggggg>\n"
        "        ...\n"
        "2833. |rhhhrhhr>\n"
        "2834. |grhhrhhr>\n"
        "2835. |hrhhrhhr>\n"
        "2836. |gggrrhhr>\n"
        "2837. |hggrrhhr>\n"
        "2838. |rggrrhhr>\n"
        "2839. |ghgrrhhr>\n"
        "2840. |hhgrrhhr>\n"
        "2841. |rhgrrhhr>\n"
        "2842. |gghrrhhr>\n"
        "2843. |hghrrhhr>\n"
        "2844. |rghrrhhr>\n"
        "2845. |ghhrrhhr>\n"
        "2846. |hhhrrhhr>\n"
        "2847. |rhhrrhhr>\n"
    )


@patch("bloqade.analog.emulate.ir.space.np.iinfo")
def test_dtype(patch_iinfo):
    patch_iinfo.return_value = Mock(max=10)

    positions = [(0, 0), (0, 1)]
    register = Register(TwoLevelAtom, positions, 0)
    space = Space.create(register)

    assert space.index_type == np.int32
    assert space.state_type.char == space.configurations.dtype.char

    positions = [(0, 0), (0, 1), (1, 0), (1, 1)]
    register = Register(TwoLevelAtom, positions, 0)
    space = Space.create(register)

    assert space.index_type == np.int64
