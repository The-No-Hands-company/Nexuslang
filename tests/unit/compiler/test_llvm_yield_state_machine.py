"""LLVM backend tests for function-body yield suspension-state lowering."""

import os
import sys


sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from nexuslang.compiler.backends.llvm_ir_generator import LLVMIRGenerator
from nexuslang.parser.ast import Program, FunctionDefinition, YieldExpression, Literal


def test_llvm_function_body_yield_lowers_to_state_machine():
    ast = Program([
        FunctionDefinition(
            name="gen_values",
            parameters=[],
            body=[
                YieldExpression(Literal("integer", 10)),
                YieldExpression(Literal("integer", 20)),
            ],
            return_type="Integer",
        )
    ])

    generator = LLVMIRGenerator()
    llvm_ir = generator.generate(ast)

    assert "@.yield_state.gen_values = internal global i64 0" in llvm_ir
    assert "define i64 @gen_values()" in llvm_ir
    assert "switch i64" in llvm_ir
    assert "yield.state.0" in llvm_ir
    assert "yield.state.1" in llvm_ir
    assert "yield.state.2" in llvm_ir
    assert "store i64 1, i64* @.yield_state.gen_values" in llvm_ir
    assert "store i64 2, i64* @.yield_state.gen_values" in llvm_ir
