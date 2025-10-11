from dataclasses import fields

from beartype.typing import Any

import bloqade.analog.ir.scalar as _scalar
import bloqade.analog.ir.control.field as _field
import bloqade.analog.ir.control.pulse as _pulse
import bloqade.analog.ir.analog_circuit as _analog_circuit
import bloqade.analog.ir.control.sequence as _sequence
import bloqade.analog.ir.control.waveform as _waveform
import bloqade.analog.ir.location.location as _location

BloqadeNodeTypes = (
    _scalar.Scalar,
    _scalar.Interval,
    _waveform.Waveform,
    _field.FieldExpr,
    _pulse.PulseExpr,
    _pulse.FieldName,
    _sequence.SequenceExpr,
    _sequence.LevelCoupling,
    _location.AtomArrangement,
    _location.ParallelRegister,
    _location.LocationInfo,
    _analog_circuit.AnalogCircuit,
)


# use dataclasses.fields to get the fields of a dataclass
def iter_fields(node: Any) -> Any:
    for field in fields(node):
        yield field, getattr(node, field.name)


class BloqadeIRVisitor:
    # Following the pattern from from python's node.NodeVisitor

    def visit(self, node: Any) -> Any:
        name = node.__class__.__name__
        module = node.__class__.__module__.split(".")[-1]
        visitor = getattr(self, f"visit_{module}_{name}", self.generic_visit)
        return visitor(node)

    def generic_visit(self, node: Any) -> Any:
        for field, value in iter_fields(node):
            if isinstance(value, BloqadeNodeTypes):
                self.visit(value)
            elif isinstance(value, (list, set, tuple, frozenset)):
                for item in value:
                    if isinstance(item, BloqadeNodeTypes):
                        self.visit(item)
            elif isinstance(value, dict):
                for key, value in value.items():
                    if isinstance(value, BloqadeNodeTypes):
                        self.visit(value)

                    if isinstance(key, BloqadeNodeTypes):
                        self.visit(key)

    def visit_waveform_NullWaveform(self, node: _waveform.NullWaveform):
        raise TypeError(node.error_message)


class BloqadeIRTransformer(BloqadeIRVisitor):
    # Following the pattern from from python's node.NodeTransformer

    def generic_visit(self, node: Any) -> Any:
        constructor_args = {}
        for field, value in iter_fields(node):
            if isinstance(value, BloqadeNodeTypes):
                new_value = self.visit(value)
            elif isinstance(value, (list, set, tuple, frozenset)):
                new_value = value.__class__(
                    (
                        self.visit(item) if isinstance(item, BloqadeNodeTypes) else item
                        for item in value
                    )
                )
            elif isinstance(value, dict):  # sometimes keys are also nodes
                new_value = {}
                for key, value in value.items():
                    if isinstance(value, BloqadeNodeTypes):
                        value = self.visit(value)
                    if isinstance(key, BloqadeNodeTypes):
                        key = self.visit(key)

                    new_value[key] = value
            else:
                new_value = value

            constructor_args[field.name] = new_value
        # IR nodes are immutable, so we have to use the constructor
        return node.__class__(**constructor_args)
