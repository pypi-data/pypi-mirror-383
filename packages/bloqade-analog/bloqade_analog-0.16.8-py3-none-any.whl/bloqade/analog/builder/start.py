from beartype import beartype

from bloqade.analog.builder.base import Builder
from bloqade.analog.builder.drive import Drive
from bloqade.analog.ir.control.sequence import SequenceExpr
from bloqade.analog.builder.sequence_builder import SequenceBuilder


class ProgramStart(Drive, Builder):
    """
    ProgramStart is the base class for a starting/entry node for building a program.
    """

    @beartype
    def apply(self, sequence: SequenceExpr) -> SequenceBuilder:
        """
        Apply a pre-built sequence to a program.

        This allows you to build a program independent of any geometry
        and then `apply` the program to said geometry. Or, if you have a
        program you would like to try on multiple geometries you can
        trivially do so with this.

        Example Usage:
        ```
        >>> from numpy import pi
        >>> seq = start.rydberg.rabi.amplitude.constant(2.0 * pi, 4.5)
        # choose a geometry of interest to apply the program on
        >>> from bloqade.analog.atom_arrangement import Chain, Kagome
        >>> complete_program = Chain(10).apply(seq)
        # you can .apply to as many geometries as you like
        >>> another_complete_program = Kagome(3).apply(seq)
        ```

        - From here you can now do:
            - `...assign(assignments).bloqade`: select the bloqade
                local emulator backend
            - `...assign(assignments).braket`: select braket
                local emulator or QuEra hardware
            - `...assign(assignments).device(specifier_string)`: select
                backend by specifying a string
        - Assign multiple values to a single variable for a parameter sweep:
            - `...assign(assignments).batch_assign(assignments)`:
        - Parallelize the program register, duplicating the geometry and waveform
            sequence to take advantage of all available
          space/qubits on the QPU:
            - `...assign(assignments).parallelize(cluster_spacing)`
        - Defer value assignment of certain variables to runtime:
            - `...assign(assignments).args([previously_defined_vars])`

        """
        return SequenceBuilder(sequence, self)
