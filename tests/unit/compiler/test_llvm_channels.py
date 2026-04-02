"""LLVM backend channel runtime lowering coverage."""

import os
import sys


sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from nlpl.parser.lexer import Lexer
from nlpl.parser.parser import Parser
from nlpl.compiler.backends.llvm_ir_generator import LLVMIRGenerator


def _parse(code: str):
    lexer = Lexer(code)
    tokens = lexer.scan_tokens()
    parser = Parser(tokens)
    return parser.parse()


def test_llvm_generates_channel_runtime_calls():
    code = """
    set ch to create channel
    send 1 to ch
    set x to receive from ch
    """

    ast = _parse(code)
    generator = LLVMIRGenerator()
    llvm_ir = generator.generate(ast)

    assert "declare i8* @nlpl_channel_create()" in llvm_ir
    assert "declare void @nlpl_channel_send(i8*, i64)" in llvm_ir
    assert "declare i64 @nlpl_channel_receive(i8*)" in llvm_ir
    assert "call i8* @nlpl_channel_create()" in llvm_ir
    assert "call void @nlpl_channel_send(i8*" in llvm_ir
    assert "call i64 @nlpl_channel_receive(i8* " in llvm_ir


def test_llvm_channel_float_payload_uses_bitcast_transport():
    code = """
    set ch to create channel
    send 1.5 to ch
    set x to receive from ch
    """

    ast = _parse(code)
    generator = LLVMIRGenerator()
    llvm_ir = generator.generate(ast)

    assert "bitcast double" in llvm_ir
    assert "to i64" in llvm_ir
    assert "bitcast i64" in llvm_ir
    assert "to double" in llvm_ir
