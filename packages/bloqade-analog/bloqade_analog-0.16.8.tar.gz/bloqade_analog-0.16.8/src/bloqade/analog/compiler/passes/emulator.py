from bloqade.analog.compiler.rewrite.common import (
    AddPadding,
    Canonicalizer,
    FlattenCircuit,
    AssignBloqadeIR,
    AssignToLiteral,
)
from bloqade.analog.compiler.analysis.common import (
    ScanChannels,
    ScanVariables,
    AssignmentScan,
)
from bloqade.analog.compiler.codegen.python.emulator_ir import EmulatorProgramCodeGen


def flatten(circuit):
    level_couplings = ScanChannels().scan(circuit)
    circuit = AddPadding(level_couplings=level_couplings).visit(circuit)
    return FlattenCircuit(level_couplings=level_couplings).visit(circuit)


def assign(assignments, circuit):
    completed_assignments = AssignmentScan(assignments).scan(circuit)
    circuit = AssignBloqadeIR(completed_assignments).emit(circuit)
    assignment_analysis = ScanVariables().scan(circuit)

    if not assignment_analysis.is_assigned:
        missing_vars = assignment_analysis.scalar_vars.union(
            assignment_analysis.vector_vars
        )
        raise ValueError(
            "Missing assignments for variables:\n"
            + ("\n".join(f"{var}" for var in missing_vars))
            + "\n"
        )

    return completed_assignments, Canonicalizer().visit(
        AssignToLiteral().visit(circuit)
    )


def generate_emulator_ir(circuit, blockade_radius, waveform_runtime, use_hyperfine):
    return EmulatorProgramCodeGen(
        blockade_radius=blockade_radius,
        waveform_runtime=waveform_runtime,
        use_hyperfine=use_hyperfine,
    ).emit(circuit)
