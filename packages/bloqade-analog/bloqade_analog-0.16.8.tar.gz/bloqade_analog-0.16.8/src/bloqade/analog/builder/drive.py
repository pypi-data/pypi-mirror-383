from bloqade.analog.builder.coupling import Rydberg, Hyperfine


class Drive:
    @property
    def rydberg(self) -> Rydberg:
        """
        Address the Rydberg level coupling in your program.

        - Next possible steps to build your program are specifying the
          [`Rabi`][bloqade.builder.field.Rabi] field or
          [`Detuning`][bloqade.builder.field.Detuning] field.
            - `...rydberg.rabi`: for Rabi field
            - `...rydberg.detuning`: for Detuning field
        - In the absence of a field you the value is set to zero by default.
        """
        return Rydberg(self)

    @property
    def hyperfine(self) -> Hyperfine:
        """
        Address the Hyperfine level coupling in your program.

        - Next possible steps to build your program are specifying the
          [`Rabi`][bloqade.builder.field.Rabi] field or
          [`Detuning`][bloqade.builder.field.Detuning] field.
            - `...hyperfine.rabi`: for Rabi field
            - `...hyperfine.detuning`: for Detuning field
        - In the absence of a field you the value is set to zero by default.

        """
        return Hyperfine(self)
