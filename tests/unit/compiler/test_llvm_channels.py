"""LLVM backend behavior for channel operations."""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from nlpl.parser.lexer import Lexer
from nlpl.parser.parser import Parser
from nlpl.compiler.backends.llvm_ir_generator import LLVMIRGenerator


def _parse(code: str):
    lexer = Lexer(code)
    tokens = lexer.scan_tokens()
    parser = Parser(tokens)
    return parser.parse()


def test_llvm_raises_clear_error_for_channel_operations():
    code = """
    set ch to create channel
    send 1 to ch
    set x to receive from ch
    """

    ast = _parse(code)
    generator = LLVMIRGenerator()

    with pytest.raises(ValueError, match="Channel send/receive is not yet supported"):
        generator.generate(ast)
