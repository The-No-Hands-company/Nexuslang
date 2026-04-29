"""Regression tests for typechecker edge cases."""

from nexuslang.parser.lexer import Lexer
from nexuslang.parser.parser import Parser
from nexuslang.typesystem.typechecker import TypeChecker


def _typecheck(source: str) -> list[str]:
    tokens = Lexer(source).tokenize()
    program = Parser(tokens, source).parse()
    checker = TypeChecker()
    checker.check_program(program)
    return checker.errors


def test_unary_minus_keyword_is_supported():
    """Natural-language unary minus should be accepted by typechecker."""
    errors = _typecheck("set y to 2\nset x to minus y\n")
    assert "Unsupported unary operator: minus" not in errors


def test_floor_divide_phrase_is_supported():
    """Natural-language floor division should be type-checked as a valid operator."""
    errors = _typecheck("set x to 9 integer divided by 2\n")
    assert "Unsupported binary operator: integer divided by" not in errors


def test_concatenate_operator_is_supported_for_strings():
    """String concatenation keyword should be accepted by typechecker."""
    errors = _typecheck('set x to "a" concatenate "b"\n')
    assert "Unsupported binary operator: concatenate" not in errors


def test_memory_allocation_statement_is_typechecked():
    """Memory allocation should no longer be rejected as unsupported."""
    errors = _typecheck("allocate a new Integer in memory and name it buffer\n")
    assert errors == []


def test_memory_allocation_type_mismatch_reports_error():
    """Allocated type should validate the optional initial value type."""
    errors = _typecheck('allocate a new Integer in memory with value "oops" and name it buffer\n')
    assert any("Cannot initialize allocated 'buffer'" in e for e in errors)


def test_memory_deallocation_existing_variable_is_allowed():
    """Freeing an existing identifier should not produce typechecker errors."""
    errors = _typecheck("set buffer to 1\nfree memory at buffer\n")
    assert errors == []


def test_memory_deallocation_undefined_identifier_reports_error():
    """Freeing unknown memory should produce an actionable diagnostic."""
    errors = _typecheck("free memory at missing_buffer\n")
    assert any("Cannot free undefined memory identifier 'missing_buffer'" in e for e in errors)


def test_arithmetic_type_error_includes_line_context():
    """Type mismatch diagnostics should include source line information."""
    errors = _typecheck("set t to true\nset x to t plus 1\n")
    assert any("Line 2:" in e and "Left operand of 'plus'" in e for e in errors)


def test_logical_type_error_includes_line_context():
    """Logical type mismatch diagnostics should include source line information."""
    errors = _typecheck("set x to 1 and 2\n")
    assert any("Line 1:" in e and "Left operand of 'and'" in e for e in errors)
