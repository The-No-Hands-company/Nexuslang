"""Backend switch lowering coverage for LLVM and C generators."""

import os
import sys


sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from nexuslang.compiler.backends.c_generator import CCodeGenerator
from nexuslang.compiler.backends.llvm_ir_generator import LLVMIRGenerator
from nexuslang.parser.ast import (
    Program,
    VariableDeclaration,
    Literal,
    Identifier,
    SwitchStatement,
    SwitchCase,
    PrintStatement,
    FallthroughStatement,
)


def _sample_switch_program():
    return Program([
        VariableDeclaration("x", Literal("integer", 1)),
        SwitchStatement(
            expression=Identifier("x"),
            cases=[
                SwitchCase(
                    value=Literal("integer", 1),
                    body=[
                        PrintStatement(Literal("string", "one")),
                        FallthroughStatement(),
                    ],
                ),
                SwitchCase(
                    value=Literal("integer", 2),
                    body=[
                        PrintStatement(Literal("string", "two")),
                    ],
                ),
            ],
            default_case=[PrintStatement(Literal("string", "other"))],
        ),
    ])


def test_c_switch_lowers_cases_default_and_fallthrough():
    ast = _sample_switch_program()

    generator = CCodeGenerator(target="c")
    c_code = generator.generate(ast)

    assert "switch (x) {" in c_code
    assert "case 1:" in c_code
    assert "case 2:" in c_code
    assert "default:" in c_code
    assert "/* fallthrough */" in c_code


def test_llvm_switch_lowers_to_switch_instruction_and_labels():
    ast = _sample_switch_program()

    generator = LLVMIRGenerator()
    llvm_ir = generator.generate(ast)

    assert "switch i64" in llvm_ir
    assert "switch.case." in llvm_ir
    assert "switch.default" in llvm_ir
    assert "switch.end" in llvm_ir
