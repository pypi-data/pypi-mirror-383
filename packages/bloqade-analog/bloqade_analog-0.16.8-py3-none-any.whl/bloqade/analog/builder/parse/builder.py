"""
Module for parsing builder definitions into intermediate representation (IR) using the bloqade library.

This module provides a Parser class for parsing various components of a quantum computing program, including atom arrangements,
pulse sequences, analog circuits, and routines. It also defines utility functions for reading addresses, waveforms, drives,
sequences, registers, and pragmas from a builder stream.
"""

from beartype.typing import TYPE_CHECKING, Set, Dict, List, Tuple, Union, Optional

import bloqade.analog.ir as ir
from bloqade.analog.builder.args import Args
from bloqade.analog.builder.base import Builder
from bloqade.analog.builder.field import Field, Detuning, RabiPhase, RabiAmplitude
from bloqade.analog.builder.assign import Assign, ListAssign, BatchAssign
from bloqade.analog.builder.spatial import Scale, Uniform, Location, SpatialModulation
from bloqade.analog.builder.coupling import Rydberg, Hyperfine, LevelCoupling
from bloqade.analog.builder.waveform import Fn, Slice, Record, Sample, WaveformPrimitive
from bloqade.analog.builder.parallelize import Parallelize
from bloqade.analog.builder.parse.stream import BuilderNode, BuilderStream
from bloqade.analog.builder.sequence_builder import SequenceBuilder

if TYPE_CHECKING:
    from bloqade.analog.ir.routine.base import Routine
    from bloqade.analog.ir.analog_circuit import AnalogCircuit
    from bloqade.analog.ir.routine.params import ParamType


class Parser:
    """A class for parsing quantum computing program components into intermediate representation (IR)."""

    stream: Optional["BuilderStream"] = None
    vector_node_names: Set[str] = set()
    sequence: ir.Sequence = ir.Sequence.create()
    register: Union[ir.AtomArrangement, ir.ParallelRegister, None] = None
    batch_params: List[Dict[str, "ParamType"]] = [{}]
    static_params: Dict[str, "ParamType"] = {}
    order: Tuple[str, ...] = ()

    def reset(self, builder: Builder):
        """Reset the parser's state."""
        self.stream = BuilderStream.create(builder)
        self.vector_node_names = set()
        self.sequence = ir.Sequence.create()
        self.register = None
        self.batch_params = [{}]
        self.static_params = {}
        self.order = ()

    def read_address(self, stream) -> Tuple[LevelCoupling, Field, BuilderNode]:
        """
        Read an address from the builder stream.

        Args:
            stream: The builder stream.

        Returns:
            Tuple[LevelCoupling, Field, BuilderNode]: A tuple containing the level coupling, field, and spatial modulation.
        """
        spatial = stream.read_next([Location, Uniform, Scale])
        curr = spatial

        if curr is None:
            return (None, None, None)

        while curr.next is not None:
            if not isinstance(curr.node, SpatialModulation):
                break
            curr = curr.next

        if type(spatial.node.__parent__) in [Detuning, RabiAmplitude, RabiPhase]:
            field = spatial.node.__parent__  # field is updated
            if type(field) in [RabiAmplitude, RabiPhase]:
                coupling = field.__parent__.__parent__  # skip Rabi
            else:
                coupling = field.__parent__

            # coupling not updated
            if type(coupling) not in [Rydberg, Hyperfine]:
                coupling = None
            return (coupling, field, spatial)
        else:  # only spatial is updated
            return (None, None, spatial)

    def read_waveform(self, head: BuilderNode) -> Tuple[ir.Waveform, BuilderNode]:
        """
        Read a waveform from the builder stream.

        Args:
            head (BuilderNode): The head of the builder stream.

        Returns:
            Tuple[ir.Waveform, BuilderNode]: A tuple containing the waveform and the next builder node.
        """
        curr = head
        waveform = None
        while curr is not None:
            node = curr.node

            if isinstance(node, Slice):
                waveform = waveform[node._start : node._stop]
            elif isinstance(node, Record):
                waveform = waveform.record(node._name)
            elif isinstance(node, Sample):
                interpolation = node._interpolation
                if interpolation is None:
                    if self.field_name == ir.rabi.phase:
                        interpolation = ir.Interpolation.Constant
                    else:
                        interpolation = ir.Interpolation.Linear
                fn_waveform = node.__parent__.__bloqade_ir__()
                sample_waveform = ir.Sample(fn_waveform, interpolation, node._dt)
                if waveform is None:
                    waveform = sample_waveform
                else:
                    waveform = waveform.append(sample_waveform)
            elif (
                isinstance(node, Fn)
                and curr.next is not None
                and isinstance(curr.next.node, Sample)
            ):
                pass
            elif isinstance(node, WaveformPrimitive):
                if waveform is None:
                    waveform = node.__bloqade_ir__()
                else:
                    waveform = waveform.append(node.__bloqade_ir__())
            else:
                break

            curr = curr.next

        return waveform, curr

    def read_drive(self, head) -> ir.Field:
        """
        Read a drive from the builder stream.

        Args:
            head: The head of the builder stream.

        Returns:
            ir.Field: The drive field.
        """
        if head is None:
            return ir.Field({})

        sm = head.node.__bloqade_ir__()
        wf, _ = self.read_waveform(head.next)

        return ir.Field({sm: wf})

    def read_sequence(self) -> ir.Sequence:
        """
        Read a sequence from the builder stream.

        Returns:
            ir.Sequence: The parsed sequence.
        """
        if isinstance(self.stream.curr.node, SequenceBuilder):
            # case with sequence builder object.
            self.sequence = self.stream.read().node._sequence
            return self.sequence

        stream = self.stream.copy()
        while stream.curr is not None:
            coupling_builder, field_builder, spatial_head = self.read_address(stream)

            if coupling_builder is not None:
                # update to new pulse coupling
                self.coupling_name = coupling_builder.__bloqade_ir__()

            if field_builder is not None:
                # update to new field coupling
                self.field_name = field_builder.__bloqade_ir__()

            if spatial_head is None:
                break

            pulse = self.sequence.pulses.get(self.coupling_name, ir.Pulse({}))
            field = pulse.fields.get(self.field_name, ir.Field({}))

            drive = self.read_drive(spatial_head)
            field = field.add(drive)

            pulse = ir.Pulse.create(pulse.fields | {self.field_name: field})
            self.sequence = ir.Sequence.create(
                self.sequence.pulses | {self.coupling_name: pulse}
            )

        return self.sequence

    def read_register(self) -> ir.AtomArrangement:
        """
        Read an atom arrangement register from the builder stream.

        Returns:
            ir.AtomArrangement: The parsed atom arrangement.
        """
        # register is always head of the stream
        register_node = self.stream.read()
        self.register = register_node.node

        return self.register

    def read_pragmas(self) -> None:
        """Read pragmas from the builder stream."""
        pragma_types = (
            Assign,
            BatchAssign,
            ListAssign,
            Args,
            Parallelize,
        )

        stream = self.stream.copy()
        curr = stream.read_next(pragma_types)

        while curr is not None:
            node = curr.node

            if isinstance(node, Assign):
                self.static_params = dict(node._static_params)
            elif isinstance(node, BatchAssign) or isinstance(node, ListAssign):
                self.batch_params = node._batch_params
            elif isinstance(node, Args):
                order = node._order

                seen = set()
                dup = []
                for x in order:
                    if x not in seen:
                        seen.add(x)
                    else:
                        dup.append(x)

                if dup:
                    raise ValueError(f"Cannot have duplicate names {dup}.")

                self.order = order

            elif isinstance(node, Parallelize):
                self.register = ir.ParallelRegister(
                    self.register, node._cluster_spacing
                )
            else:
                break

            curr = curr.next

    def parse_register(
        self, builder: Builder
    ) -> Union[ir.AtomArrangement, ir.ParallelRegister]:
        """
        Parse an atom arrangement register from the builder.

        Args:
            builder (Builder): The builder instance.

        Returns:
            Union[ir.AtomArrangement, ir.ParallelRegister]: The parsed atom arrangement or parallel register.
        """
        self.reset(builder)
        self.read_register()
        self.read_pragmas()
        return self.register

    def parse_sequence(self, builder: Builder) -> ir.Sequence:
        """
        Parse a sequence from the builder.

        Args:
            builder (Builder): The builder instance.

        Returns:
            ir.Sequence: The parsed sequence.
        """
        self.reset(builder)
        self.read_sequence()
        return self.sequence

    def parse_circuit(self, builder: Builder) -> "AnalogCircuit":
        """
        Parse an analog circuit from the builder.

        Args:
            builder (Builder): The builder instance.

        Returns:
            AnalogCircuit: The parsed analog circuit.
        """
        from bloqade.analog.ir.analog_circuit import AnalogCircuit

        self.reset(builder)
        self.read_register()
        self.read_sequence()

        circuit = AnalogCircuit(self.register, self.sequence)

        return circuit

    def parse(self, builder: Builder) -> "Routine":
        """
        Parse a routine from the builder.

        Args:
            builder (Builder): The builder instance.

        Returns:
            Routine: The parsed routine.
        """
        from bloqade.analog.ir.routine.base import Routine
        from bloqade.analog.ir.analog_circuit import AnalogCircuit
        from bloqade.analog.ir.routine.params import Params, ScalarArg, VectorArg
        from bloqade.analog.compiler.analysis.common.scan_variables import ScanVariables

        self.reset(builder)
        self.read_register()
        self.read_sequence()
        self.read_pragmas()

        circuit = AnalogCircuit(self.register, self.sequence)

        var_res = ScanVariables().scan(circuit)
        # mark vector and scalar arguments
        args_list = [
            (VectorArg(name) if name in var_res.vector_vars else ScalarArg(name))
            for name in self.order
        ]

        params = Params(
            n_sites=self.register.n_sites,
            static_params=self.static_params,
            batch_params=self.batch_params,
            args_list=args_list,
        )

        return Routine(builder, circuit, params)
