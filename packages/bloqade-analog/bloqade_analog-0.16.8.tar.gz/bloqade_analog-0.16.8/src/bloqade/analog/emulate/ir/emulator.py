from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, List, Tuple, Callable, Optional
from decimal import Decimal
from functools import cached_property
from dataclasses import field, dataclass

from bloqade.analog.serialize import Serializer
from bloqade.analog.ir.control.waveform import Waveform
from bloqade.analog.emulate.ir.atom_type import AtomType
from bloqade.analog.compiler.codegen.common.json import (
    BloqadeIRSerializer,
    BloqadeIRDeserializer,
)

if TYPE_CHECKING:
    from bloqade.analog.task.base import Geometry


class WaveformRuntime(str, Enum):
    Python = "python"
    Numba = "numba"
    Interpret = "interpret"


@dataclass
@Serializer.register
class JITWaveform:
    assignments: Dict[str, Decimal]
    source: Waveform
    runtime: WaveformRuntime = WaveformRuntime.Interpret

    @cached_property
    def canonicalized_ir(self):
        from bloqade.analog.compiler.rewrite.common import (
            Canonicalizer,
            AssignBloqadeIR,
            AssignToLiteral,
        )
        from bloqade.analog.compiler.analysis.common import (
            ScanVariables,
            AssignmentScan,
        )
        from bloqade.analog.compiler.rewrite.python.waveform import (
            NormalizeWaveformPython,
        )

        assignments = AssignmentScan(self.assignments).scan(self.source)
        ast_assigned = AssignBloqadeIR(assignments).emit(self.source)
        scan = ScanVariables().scan(ast_assigned)

        if not scan.is_assigned:
            missing_vars = scan.scalar_vars.union(scan.vector_vars)
            raise ValueError(
                "Missing assignments for variables:\n"
                + ("\n".join(f"{var}" for var in missing_vars))
                + "\n"
            )

        ast_normalized = NormalizeWaveformPython().visit(ast_assigned)
        ast_literal = AssignToLiteral().visit(ast_normalized)
        ast_canonicalized = Canonicalizer().visit(ast_literal)

        return ast_canonicalized

    def emit(self) -> Callable[[float], float]:
        from bloqade.analog.compiler.codegen.python.waveform import (
            CodegenPythonWaveform,
        )
        from bloqade.analog.compiler.analysis.python.waveform import WaveformScan

        if self.runtime is WaveformRuntime.Interpret:
            return self.canonicalized_ir

        scan_results = WaveformScan().scan(self.canonicalized_ir)
        stub = CodegenPythonWaveform(
            scan_results, jit_compiled=self.runtime is WaveformRuntime.Numba
        ).compile(self.canonicalized_ir)

        return stub


@JITWaveform.set_serializer
def _serialize(obj: JITWaveform) -> Dict[str, Any]:
    return {
        "assignments": obj.assignments,
        "source": BloqadeIRSerializer().default(obj.source),
    }


@JITWaveform.set_deserializer
def _deserializer(d: Dict[str, Any]) -> JITWaveform:
    from json import dumps, loads

    source_str = dumps(d["source"])
    d["source"] = loads(source_str, object_hook=BloqadeIRDeserializer.object_hook)
    return JITWaveform(**d)


class RabiOperatorType(int, Enum):
    RabiAsymmetric = 0
    RabiSymmetric = 1


@dataclass(frozen=True)
@Serializer.register
class RabiOperatorData:
    operator_type: RabiOperatorType
    target_atoms: Dict[int, Decimal]

    def __hash__(self):
        return hash(self.operator_type) ^ hash(frozenset(self.target_atoms.items()))


@RabiOperatorData.set_deserializer
def _deserializer(d: Dict[str, Any]) -> RabiOperatorData:
    d["target_atoms"] = {int(k): v for k, v in d["target_atoms"].items()}
    return RabiOperatorData(**d)


@dataclass
@Serializer.register
class RabiTerm:
    operator_data: RabiOperatorData
    amplitude: JITWaveform
    phase: Optional[JITWaveform] = None


@dataclass(frozen=True)
@Serializer.register
class DetuningOperatorData:
    target_atoms: Dict[int, Decimal]

    def __hash__(self) -> int:
        return hash(frozenset(self.target_atoms.items()))


@DetuningOperatorData.set_deserializer
def _deserializer(d: Dict[str, Any]) -> DetuningOperatorData:
    d["target_atoms"] = {int(k): v for k, v in d["target_atoms"].items()}
    return DetuningOperatorData(**d)


@dataclass
@Serializer.register
class DetuningTerm:
    operator_data: DetuningOperatorData
    amplitude: JITWaveform


@dataclass
@Serializer.register
class Fields:
    detuning: List[DetuningTerm]
    rabi: List[RabiTerm]


@dataclass(frozen=True)
@Serializer.register
class Register:
    """This class represents the of the atoms in the system."""

    atom_type: AtomType
    sites: List[Tuple[Decimal, Decimal]]
    blockade_radius: Decimal
    geometry: Optional["Geometry"] = None
    full_index_to_index: Dict[int, int] = field(init=False, default_factory=dict)

    def __post_init__(self):
        from bloqade.analog.task.base import Geometry

        if self.geometry is None:
            geometry = Geometry(self.sites, len(self.sites) * [1])
            object.__setattr__(self, "geometry", geometry)

        for i, filling in enumerate(self.geometry.filling):
            if filling:
                self.full_index_to_index[i] = len(self.full_index_to_index)

    def __len__(self):
        return len(self.sites)

    def same(self, other: Any) -> bool:
        if not isinstance(other, Register):
            return False

        return (
            self.atom_type == other.atom_type
            and self.blockade_radius == other.blockade_radius
            and set(self.sites) == set(other.sites)
        )

    # for hashing/comparing I only want to compare based on the effective
    # fock space that gets generated which is determined by the geometry
    # only if the blockade radius is non-zero. I overload the __eq__ and
    # __hash__ methods to achieve this.

    def __eq__(self, other: Any):
        if not isinstance(other, Register):
            return False

        if self.blockade_radius == Decimal("0") and other.blockade_radius == Decimal(
            "0"
        ):
            # if blockade radius is zero, then the positions are irrelevant
            # because the fock states generated by the geometry are the same
            return self.atom_type == other.atom_type and len(self.sites) == len(
                other.sites
            )

        return self.same(other)

    def __hash__(self) -> int:
        if self.blockade_radius == Decimal("0"):
            # if blockade radius is zero, then the positions are irrelevant
            # because the fock states generated by the geometry are the same
            return hash(self.__class__) ^ hash(self.atom_type) ^ hash(len(self.sites))
        else:
            # if blockade radius is non-zero, then the positions are relevant
            # because depending on the location of the atoms and the blockade
            # radius, the fock states generated by the geometry are different
            return (
                hash(self.__class__)
                ^ hash(self.atom_type)
                ^ hash(self.blockade_radius)
                ^ hash(frozenset(self.sites))
            )


@Register.set_deserializer
def _deserializer(d: Dict[str, Any]) -> Register:
    d.pop("full_index_to_index")  # not needed for initialization
    d["sites"] = [tuple(map(Decimal, map(str, site))) for site in d["sites"]]
    return Register(**d)


class LevelCoupling(str, Enum):
    Rydberg = "rydberg"
    Hyperfine = "hyperfine"


@dataclass
@Serializer.register
class EmulatorProgram:
    register: Register
    duration: float
    pulses: Dict[LevelCoupling, Fields]


@EmulatorProgram.set_deserializer
def _deserializer(d: Dict[str, Any]) -> EmulatorProgram:
    d["duration"] = float(d["duration"])
    return EmulatorProgram(**d)


class Visitor:
    def visit_emulator_program(self, node: EmulatorProgram) -> Any:
        raise NotImplementedError

    def visit_compiled_waveform(self, node: JITWaveform) -> Any:
        raise NotImplementedError

    def visit_fields(self, node: Fields) -> Any:
        raise NotImplementedError

    def visit_detuning_operator_data(self, node: DetuningOperatorData) -> Any:
        raise NotImplementedError

    def visit_rabi_operator_data(self, node: RabiOperatorData) -> Any:
        raise NotImplementedError

    def visit_detuning_term(self, node: DetuningTerm) -> Any:
        raise NotImplementedError

    def visit_rabi_term(self, node: RabiTerm) -> Any:
        raise NotImplementedError

    def visit_register(self, node: Register) -> Any:
        raise NotImplementedError

    def visit(self, node) -> Any:
        if isinstance(node, EmulatorProgram):
            return self.visit_emulator_program(node)
        elif isinstance(node, Register):
            return self.visit_register(node)
        elif isinstance(node, Fields):
            return self.visit_fields(node)
        elif isinstance(node, RabiTerm):
            return self.visit_rabi_term(node)
        elif isinstance(node, DetuningTerm):
            return self.visit_detuning_term(node)
        elif isinstance(node, RabiOperatorData):
            return self.visit_rabi_operator_data(node)
        elif isinstance(node, DetuningOperatorData):
            return self.visit_detuning_operator_data(node)
        elif isinstance(node, JITWaveform):
            return self.visit_compiled_waveform(node)
        else:
            raise NotImplementedError(f"Unknown AST node type {type(node)}: {node!r}")
