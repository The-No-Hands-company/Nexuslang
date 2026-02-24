"""
Assertion library tests: lexer, AST, parser, and interpreter integration.
Split from test_session_features.py.
"""

import sys
import os
import tempfile
import pytest
from pathlib import Path

_SRC = str(Path(__file__).resolve().parent.parent.parent.parent / "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

class TestAssertionLibraryLexer:
    def _lex(self, src):
        from nlpl.parser.lexer import Lexer
        return Lexer(src).tokenize()

    def test_require_keyword_token(self):
        from nlpl.parser.lexer import TokenType
        toks = self._lex("require x")
        assert TokenType.REQUIRE in [t.type for t in toks]

    def test_ensure_keyword_token(self):
        from nlpl.parser.lexer import TokenType
        toks = self._lex("ensure x")
        assert TokenType.ENSURE in [t.type for t in toks]

    def test_guarantee_keyword_token(self):
        from nlpl.parser.lexer import TokenType
        toks = self._lex("guarantee x")
        assert TokenType.GUARANTEE in [t.type for t in toks]

    def test_expect_token_with_equal(self):
        from nlpl.parser.lexer import TokenType
        toks = self._lex("expect x to equal 5")
        types = [t.type for t in toks]
        assert TokenType.EXPECT in types
        assert TokenType.TO in types

    def test_expect_token_with_not(self):
        from nlpl.parser.lexer import TokenType
        toks = self._lex("expect x to not equal 5")
        types = [t.type for t in toks]
        assert TokenType.NOT in types

class TestAssertionLibraryAST:
    def test_expect_statement_import(self):
        from nlpl.parser.ast import ExpectStatement
        node = ExpectStatement(actual_expr=None, matcher="equal")
        assert node.node_type == "expect_statement"

    def test_expect_statement_matcher(self):
        from nlpl.parser.ast import ExpectStatement
        node = ExpectStatement(actual_expr=None, matcher="greater_than")
        assert node.matcher == "greater_than"

    def test_expect_statement_negated_default_false(self):
        from nlpl.parser.ast import ExpectStatement
        node = ExpectStatement(actual_expr=None, matcher="equal")
        assert node.negated is False

    def test_expect_statement_negated_true(self):
        from nlpl.parser.ast import ExpectStatement
        node = ExpectStatement(actual_expr=None, matcher="equal", negated=True)
        assert node.negated is True

    def test_require_statement_import(self):
        from nlpl.parser.ast import RequireStatement
        node = RequireStatement(condition=None)
        assert node.node_type == "require_statement"

    def test_ensure_statement_import(self):
        from nlpl.parser.ast import EnsureStatement
        node = EnsureStatement(condition=None)
        assert node.node_type == "ensure_statement"

    def test_guarantee_statement_import(self):
        from nlpl.parser.ast import GuaranteeStatement
        node = GuaranteeStatement(condition=None)
        assert node.node_type == "guarantee_statement"

class TestAssertionLibraryParser:
    def _parse(self, src):
        from nlpl.parser.parser import Parser
        from nlpl.parser.lexer import Lexer
        return Parser(Lexer(src).tokenize()).parse()

    def test_parse_expect_equal(self):
        from nlpl.parser.ast import ExpectStatement
        prog = self._parse("set x to 5\nexpect x to equal 5")
        assert any(isinstance(s, ExpectStatement) for s in prog.statements)

    def test_parse_expect_equal_matcher(self):
        from nlpl.parser.ast import ExpectStatement
        prog = self._parse("set x to 5\nexpect x to equal 5")
        node = next(s for s in prog.statements if isinstance(s, ExpectStatement))
        assert node.matcher == "equal"

    def test_parse_expect_not_equal(self):
        from nlpl.parser.ast import ExpectStatement
        prog = self._parse("set x to 5\nexpect x to not equal 3")
        node = next(s for s in prog.statements if isinstance(s, ExpectStatement))
        assert node.negated is True

    def test_parse_expect_greater_than(self):
        from nlpl.parser.ast import ExpectStatement
        prog = self._parse("set x to 5\nexpect x to be greater than 3")
        node = next(s for s in prog.statements if isinstance(s, ExpectStatement))
        assert node.matcher == "greater_than"

    def test_parse_expect_less_than(self):
        from nlpl.parser.ast import ExpectStatement
        prog = self._parse("set x to 5\nexpect x to be less than 10")
        node = next(s for s in prog.statements if isinstance(s, ExpectStatement))
        assert node.matcher == "less_than"

    def test_parse_expect_greater_than_or_equal_to(self):
        from nlpl.parser.ast import ExpectStatement
        prog = self._parse("set x to 5\nexpect x to be greater than or equal to 5")
        node = next(s for s in prog.statements if isinstance(s, ExpectStatement))
        assert node.matcher == "greater_than_or_equal_to"

    def test_parse_expect_less_than_or_equal_to(self):
        from nlpl.parser.ast import ExpectStatement
        prog = self._parse("set x to 5\nexpect x to be less than or equal to 5")
        node = next(s for s in prog.statements if isinstance(s, ExpectStatement))
        assert node.matcher == "less_than_or_equal_to"

    def test_parse_expect_contain(self):
        from nlpl.parser.ast import ExpectStatement
        prog = self._parse('set s to "hello"\nexpect s to contain "ell"')
        node = next(s for s in prog.statements if isinstance(s, ExpectStatement))
        assert node.matcher == "contain"

    def test_parse_expect_be_true(self):
        from nlpl.parser.ast import ExpectStatement
        prog = self._parse("set flag to true\nexpect flag to be true")
        node = next(s for s in prog.statements if isinstance(s, ExpectStatement))
        assert node.matcher == "be_true"

    def test_parse_expect_be_false(self):
        from nlpl.parser.ast import ExpectStatement
        prog = self._parse("set flag to false\nexpect flag to be false")
        node = next(s for s in prog.statements if isinstance(s, ExpectStatement))
        assert node.matcher == "be_false"

    def test_parse_expect_be_null(self):
        from nlpl.parser.ast import ExpectStatement
        prog = self._parse("set v to null\nexpect v to be null")
        node = next(s for s in prog.statements if isinstance(s, ExpectStatement))
        assert node.matcher == "be_null"

    def test_parse_require(self):
        from nlpl.parser.ast import RequireStatement
        prog = self._parse("require 1 equals 1")
        assert any(isinstance(s, RequireStatement) for s in prog.statements)

    def test_parse_ensure(self):
        from nlpl.parser.ast import EnsureStatement
        prog = self._parse("ensure 1 equals 1")
        assert any(isinstance(s, EnsureStatement) for s in prog.statements)

    def test_parse_guarantee(self):
        from nlpl.parser.ast import GuaranteeStatement
        prog = self._parse("guarantee 1 equals 1")
        assert any(isinstance(s, GuaranteeStatement) for s in prog.statements)

class TestAssertionLibraryInterpreter:
    def _interp(self, src):
        from nlpl.interpreter.interpreter import Interpreter
        from nlpl.runtime.runtime import Runtime
        from nlpl.stdlib import register_stdlib
        from nlpl.parser.parser import Parser
        from nlpl.parser.lexer import Lexer
        rt = Runtime()
        register_stdlib(rt)
        prog = Parser(Lexer(src).tokenize()).parse()
        i = Interpreter(runtime=rt)
        i.interpret(prog)
        return i

    def test_expect_equal_passes(self):
        self._interp("set x to 5\nexpect x to equal 5")

    def test_expect_equal_fails(self):
        with pytest.raises(AssertionError):
            self._interp("set x to 1\nexpect x to equal 2")

    def test_expect_not_equal_passes(self):
        self._interp("set x to 1\nexpect x to not equal 2")

    def test_expect_not_equal_fails(self):
        with pytest.raises(AssertionError):
            self._interp("set x to 5\nexpect x to not equal 5")

    def test_expect_greater_than_passes(self):
        self._interp("set x to 5\nexpect x to be greater than 3")

    def test_expect_greater_than_fails(self):
        with pytest.raises(AssertionError):
            self._interp("set x to 2\nexpect x to be greater than 5")

    def test_expect_less_than_passes(self):
        self._interp("set x to 3\nexpect x to be less than 10")

    def test_expect_less_than_fails(self):
        with pytest.raises(AssertionError):
            self._interp("set x to 10\nexpect x to be less than 3")

    def test_expect_contain_passes(self):
        self._interp('set s to "hello world"\nexpect s to contain "world"')

    def test_expect_contain_fails(self):
        with pytest.raises(AssertionError):
            self._interp('set s to "hello"\nexpect s to contain "xyz"')

    def test_expect_be_true_passes(self):
        self._interp("set x to 1\nexpect x to be true")

    def test_expect_be_false_passes(self):
        self._interp("set x to 0\nexpect x to be false")

    def test_expect_be_null_passes(self):
        self._interp("set v to null\nexpect v to be null")

    def test_expect_not_be_null_passes(self):
        self._interp("set v to 42\nexpect v to not be null")

    def test_expect_failure_in_test_block_does_not_propagate(self):
        # Inside a test block, expect failures are recorded, not propagated
        self._interp('test "will fail" do\n  expect 1 to equal 2\nend')


# ============================================================
# Section 17 - Contract programming (require / ensure / guarantee)
# ============================================================

