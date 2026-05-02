"""C backend coverage for basic pattern matching lowering."""

import os
import sys


sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from nexuslang.compiler.backends.c_generator import CCodeGenerator
from nexuslang.parser.lexer import Lexer
from nexuslang.parser.parser import Parser


def _parse(code: str):
    lexer = Lexer(code)
    tokens = lexer.scan_tokens()
    parser = Parser(tokens)
    return parser.parse()


def test_c_match_expression_lowers_integer_cases_and_wildcard():
    ast = _parse(
        """
function main returns Integer
    set x to 2
    match x with
        case 1
            print text "one"
        case 2
            print text "two"
        case _
            print text "other"
    end
    return 0
end
"""
    )

    c_code = CCodeGenerator(target="c").generate(ast)

    assert "bool __nxl_match_done_" in c_code
    assert "== 1" in c_code
    assert "== 2" in c_code
    assert "other" in c_code


def test_c_match_expression_lowers_string_literal_case_with_strcmp():
    ast = _parse(
        """
function main returns Integer
    set status to "ready"
    match status with
        case "ready"
            print text "go"
        case _
            print text "stop"
    end
    return 0
end
"""
    )

    c_code = CCodeGenerator(target="c").generate(ast)

    assert "strcmp(" in c_code
    assert "ready" in c_code


def test_c_match_expression_lowers_identifier_binding_and_guard():
    ast = _parse(
        """
function main returns Integer
    set x to 5
    match x with
        case n if n is greater than 3
            print text n
        case _
            print text 0
    end
    return 0
end
"""
    )

    c_code = CCodeGenerator(target="c").generate(ast)

    assert "__match_bind_n_" in c_code
    assert "> 3" in c_code
    assert "printf(\"%d\\n\"," in c_code