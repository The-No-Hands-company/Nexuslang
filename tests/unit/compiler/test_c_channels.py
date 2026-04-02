"""C backend channel lowering coverage."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from nlpl.parser.lexer import Lexer
from nlpl.parser.parser import Parser
from nlpl.compiler.backends.c_generator import CCodeGenerator


def _parse(code: str):
    lexer = Lexer(code)
    tokens = lexer.scan_tokens()
    parser = Parser(tokens)
    return parser.parse()


def test_c_codegen_includes_channel_runtime_and_calls():
    code = """
    set ch to create channel
    send 1 to ch
    set x to receive from ch
    """

    ast = _parse(code)
    generator = CCodeGenerator(target="c")
    c_code = generator.generate(ast)

    assert "nlpl_channel_create" in c_code
    assert "nlpl_channel_send" in c_code
    assert "nlpl_channel_receive" in c_code
    assert "typedef struct NLPLChannel" in c_code


def test_c_codegen_uses_intptr_t_channel_payload_transport():
    code = """
    set ch to create channel
    send 42 to ch
    set x to receive from ch
    """

    ast = _parse(code)
    generator = CCodeGenerator(target="c")
    c_code = generator.generate(ast)

    assert "(intptr_t)(42)" in c_code
    assert "intptr_t nlpl_channel_receive(void* channel)" in c_code
    assert "while (!ch->head)" in c_code
