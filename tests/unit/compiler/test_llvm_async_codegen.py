"""Regression tests for LLVM async/await lowering behavior."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../src'))

from nexuslang.compiler.backends.llvm_ir_generator import LLVMIRGenerator
from nexuslang.parser.lexer import Lexer
from nexuslang.parser.parser import Parser


def _generate_llvm(code: str) -> str:
    lexer = Lexer(code)
    tokens = lexer.scan_tokens()
    parser = Parser(tokens)
    ast = parser.parse()
    return LLVMIRGenerator().generate(ast)


def test_await_non_async_target_is_lowered_synchronously():
    """Awaiting a non-async function should not emit coroutine poll loop."""
    code = """function sync_value returns Integer
    return 42
end

async function wrapper returns Integer
    set value to await sync_value
    return value
end
"""

    llvm_ir = _generate_llvm(code)

    assert "sync_value" in llvm_ir
    assert "await.poll." not in llvm_ir


def test_await_async_target_emits_coroutine_poll_loop():
    """Awaiting a known async function should still emit coroutine polling labels."""
    code = """async function fetch_value returns Integer
    return 7
end

async function wrapper returns Integer
    set value to await fetch_value
    return value
end
"""

    llvm_ir = _generate_llvm(code)

    assert "call i8* @fetch_value()" in llvm_ir
    assert "await.poll." in llvm_ir
