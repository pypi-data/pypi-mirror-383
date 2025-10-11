from beartype import beartype
from beartype.typing import Set, Dict, FrozenSet
from pydantic.v1.dataclasses import dataclass

import bloqade.analog.ir.control.waveform as waveform
from bloqade.analog.ir.visitor import BloqadeIRVisitor


@dataclass(frozen=True)
class WaveformScanResult:
    bindings: Dict[waveform.Waveform, str]
    imports: Dict[str, FrozenSet[str]]


class WaveformScan(BloqadeIRVisitor):
    def __init__(
        self,
        bindings: Dict[waveform.Waveform, str] = {},
        imports: Dict[str, Set[str]] = {},
    ):
        self.bindings = dict(bindings)
        self.imports = dict(imports)
        self.i = 0

    def add_binding(self, node: waveform.Waveform):
        if node in self.bindings:
            return

        symbol = f"__bloqade_var{self.i}"

        while symbol in self.imports.values():
            self.i += 1
            symbol = f"__bloqade_var{self.i}"

        self.i += 1

        self.bindings[node] = symbol

    def generic_visit(self, node: waveform.Waveform):
        if isinstance(node, waveform.Waveform):
            self.add_binding(node)
        super().generic_visit(node)

    @beartype
    def scan(self, node: waveform.Waveform) -> WaveformScanResult:
        self.visit(node)
        imports = {
            module: frozenset(imports) for module, imports in self.imports.items()
        }
        return WaveformScanResult(self.bindings, imports)
