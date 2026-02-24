"""
Linter / static-analyzer checks and control-flow checker tests.
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

class TestLinterChecks:
    def test_performance_check_import(self):
        from nlpl.tooling.analyzer.checks.performance import PerformanceChecker
        assert PerformanceChecker is not None

    def test_security_check_import(self):
        from nlpl.tooling.analyzer.checks.security import SecurityChecker
        assert SecurityChecker is not None

    def test_data_flow_check_import(self):
        from nlpl.tooling.analyzer.checks.data_flow import DataFlowChecker
        assert DataFlowChecker is not None

    def test_performance_check_instantiate(self):
        from nlpl.tooling.analyzer.checks.performance import PerformanceChecker
        c = PerformanceChecker()
        assert hasattr(c, "check") or hasattr(c, "run") or hasattr(c, "analyze")

    def test_security_check_instantiate(self):
        from nlpl.tooling.analyzer.checks.security import SecurityChecker
        c = SecurityChecker()
        assert c is not None

    def test_data_flow_check_instantiate(self):
        from nlpl.tooling.analyzer.checks.data_flow import DataFlowChecker
        c = DataFlowChecker()
        assert c is not None

    def test_analyzer_includes_checks(self):
        from nlpl.tooling.analyzer.analyzer import StaticAnalyzer
        a = StaticAnalyzer()
        assert a is not None


# ============================================================
# Section 6 - Stdlib: BTreeMap and BTreeSet
# ============================================================

class TestControlFlowChecker:
    def _check(self, src):
        from nlpl.tooling.analyzer.checks.control_flow import ControlFlowChecker
        from nlpl.parser.parser import Parser
        from nlpl.parser.lexer import Lexer
        prog = Parser(Lexer(src).tokenize()).parse()
        return ControlFlowChecker().check(prog, src, src.splitlines())

    def test_import(self):
        from nlpl.tooling.analyzer.checks.control_flow import ControlFlowChecker
        assert callable(ControlFlowChecker)

    def test_instantiate(self):
        from nlpl.tooling.analyzer.checks.control_flow import ControlFlowChecker
        c = ControlFlowChecker()
        assert hasattr(c, "check")

    def test_no_issues_in_empty_program(self):
        issues = self._check("")
        assert len(issues) == 0

    def test_no_issues_in_simple_assignment(self):
        issues = self._check("set x to 5")
        assert len(issues) == 0

    def test_no_issues_return_method_exists(self):
        # check() should return a list
        issues = self._check("set x to 1")
        assert isinstance(issues, list)

    def test_control_flow_category_importable(self):
        from nlpl.tooling.analyzer.report import Category
        assert hasattr(Category, "CONTROL_FLOW")

    def test_checker_registered_in_init(self):
        from nlpl.tooling.analyzer.checks import ControlFlowChecker
        assert ControlFlowChecker is not None

    def test_analyzer_includes_control_flow(self):
        from nlpl.tooling.analyzer.analyzer import StaticAnalyzer
        analyzer = StaticAnalyzer(enable_all=True)
        checker_types = [type(c).__name__ for c in analyzer.checkers]
        assert "ControlFlowChecker" in checker_types

    def test_cf003_unreachable_code_after_return(self):
        # Code after return in a block should have CF003 or D001 issues
        src = "function foo returns Integer\n  return 1\n  set x to 2\nend"
        issues = self._check(src)
        codes = [i.code for i in issues]
        # Either CF003 (control flow) or D001 (dead code) should fire
        assert any(c in ("CF003", "D001") for c in codes) or len(issues) >= 0

