"""TypeChecker coverage tests for parallel for loops."""

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


def test_typechecker_accepts_parallel_for_over_list():
    code = """
    set items to [1, 2, 3]
    parallel for each x in items
        set y to x plus 1
    end
    """

    ast = _parse(code)
    checker = TypeChecker()
    errors = checker.check_program(ast)

    assert errors == []


def test_typechecker_rejects_parallel_for_over_non_list():
    code = """
    set items to 42
    parallel for each x in items
        set y to x
    end
    """

    ast = _parse(code)
    checker = TypeChecker()
    errors = checker.check_program(ast)

    assert any("Parallel for iterable must be a list" in err for err in errors)
