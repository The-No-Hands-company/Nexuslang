"""LLVM backend coverage for parallel-for and contract/assertion lowering."""

import os
import sys


sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from nexuslang.compiler.backends.llvm_ir_generator import LLVMIRGenerator
from nexuslang.parser.ast import (
    Program,
    ParallelForLoop,
    ListExpression,
    Literal,
    PrintStatement,
    Identifier,
    RequireStatement,
    ExpectStatement,
    TryCatchBlock,
    RaiseStatement,
    Block,
)


def test_llvm_parallel_for_is_lowered_to_loop_ir():
    ast = Program([
        ParallelForLoop(
            "item",
            ListExpression([Literal("integer", 1), Literal("integer", 2)]),
            [PrintStatement(Identifier("item"))],
        )
    ])

    generator = LLVMIRGenerator()
    llvm_ir = generator.generate(ast)

    assert "define i32 @main(" in llvm_ir
    assert "for.cond" in llvm_ir or "foreach.cond" in llvm_ir


def test_llvm_contracts_and_expect_emit_runtime_panic_guards():
    ast = Program([
        RequireStatement(Literal("boolean", False), Literal("string", "require failed")),
        ExpectStatement(Literal("integer", 1), "equal", Literal("integer", 2)),
    ])

    generator = LLVMIRGenerator()
    llvm_ir = generator.generate(ast)

    assert "call void @nxl_panic(i8*" in llvm_ir
    assert "contract.fail" in llvm_ir


def test_llvm_try_catch_block_lowers_with_landingpad_and_raise():
    ast = Program([
        TryCatchBlock(
            try_block=Block([
                RaiseStatement(message=Literal("string", "boom")),
            ]),
            catch_block=Block([
                PrintStatement(Identifier("err")),
            ]),
            exception_var="err",
        )
    ])

    generator = LLVMIRGenerator()
    llvm_ir = generator.generate(ast)

    assert "landingpad { i8*, i32 }" in llvm_ir
    assert "call i8* @__cxa_begin_catch(i8*" in llvm_ir
    assert "store i8*" in llvm_ir
    assert "@__nxl_throw" in llvm_ir or "@__cxa_throw" in llvm_ir
