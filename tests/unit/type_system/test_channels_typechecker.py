"""TypeChecker coverage tests for channel syntax."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from nlpl.parser.lexer import Lexer
from nlpl.parser.parser import Parser
from nlpl.typesystem.typechecker import TypeChecker


def _parse(code: str):
    lexer = Lexer(code)
    tokens = lexer.scan_tokens()
    parser = Parser(tokens)
    return parser.parse()


def test_typechecker_accepts_channel_send_receive_program():
    code = """
    set ch to create channel
    send 1 to ch
    set x to receive from ch
    """

    ast = _parse(code)
    checker = TypeChecker()
    errors = checker.check_program(ast)
    assert errors == []
