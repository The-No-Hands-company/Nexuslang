"""
Contract programming: require, ensure, guarantee, NLPLContractError.
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

class TestContractProgramming:
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

    def test_require_passes_when_true(self):
        self._interp("set x to 5\nrequire x is greater than 0")

    def test_require_raises_when_false(self):
        from nlpl.errors import NLPLContractError
        with pytest.raises(NLPLContractError):
            self._interp("set x to 0\nrequire x is greater than 5")

    def test_ensure_passes_when_true(self):
        self._interp("set result to 10\nensure result is greater than 0")

    def test_ensure_raises_when_false(self):
        from nlpl.errors import NLPLContractError
        with pytest.raises(NLPLContractError):
            self._interp("set result to 0\nensure result is greater than 5")

    def test_guarantee_passes_when_true(self):
        self._interp("set n to 3\nguarantee n equals 3")

    def test_guarantee_raises_when_false(self):
        from nlpl.errors import NLPLContractError
        with pytest.raises(NLPLContractError):
            self._interp("set n to 1\nguarantee n equals 2")

    def test_contract_error_is_importable(self):
        from nlpl.errors import NLPLContractError
        assert issubclass(NLPLContractError, Exception)

    def test_require_with_literal_true(self):
        self._interp("require 1 equals 1")

    def test_require_with_literal_false(self):
        from nlpl.errors import NLPLContractError
        with pytest.raises(NLPLContractError):
            self._interp("require 1 equals 2")

    def test_guarantee_contract_kind(self):
        from nlpl.errors import NLPLContractError
        try:
            self._interp("guarantee 1 equals 2")
        except NLPLContractError as e:
            assert e.contract_kind == "guarantee"
        else:
            pytest.fail("Expected NLPLContractError")

    def test_require_contract_kind(self):
        from nlpl.errors import NLPLContractError
        try:
            self._interp("require 1 equals 2")
        except NLPLContractError as e:
            assert e.contract_kind == "require"
        else:
            pytest.fail("Expected NLPLContractError")


# ============================================================
# Section 18 - ControlFlowChecker
# ============================================================

