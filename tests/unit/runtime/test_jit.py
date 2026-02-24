"""
JIT compilation and type-feedback tests.
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

class TestJIT:
    def test_tiered_compiler_import(self):
        from nlpl.jit.tiered_compiler import TieredCompiler
        assert TieredCompiler is not None

    def test_tiered_compiler_create(self):
        from nlpl.jit.tiered_compiler import TieredCompiler
        tc = TieredCompiler()
        assert tc is not None

    def test_tiered_compiler_tier_of_unknown(self):
        from nlpl.jit.tiered_compiler import TieredCompiler, ExecutionTier
        tc = TieredCompiler()
        tier = tc.tier_of("unknown_function")
        assert tier == ExecutionTier.INTERPRETER

    def test_tiered_compiler_inject_tier(self):
        from nlpl.jit.tiered_compiler import TieredCompiler, ExecutionTier, FunctionTierState
        tc = TieredCompiler()
        tc._function_states["hot_fn"] = FunctionTierState(
            name="hot_fn", tier=ExecutionTier.OPTIMIZING_JIT
        )
        assert tc.tier_of("hot_fn") == ExecutionTier.OPTIMIZING_JIT

    def test_function_tier_state_import(self):
        from nlpl.jit.tiered_compiler import FunctionTierState, ExecutionTier
        state = FunctionTierState(name="fn", tier=ExecutionTier.INTERPRETER)
        assert state.name == "fn"

    def test_execution_tier_values(self):
        from nlpl.jit.tiered_compiler import ExecutionTier
        assert hasattr(ExecutionTier, "INTERPRETER")
        assert hasattr(ExecutionTier, "OPTIMIZING_JIT")


# ============================================================
# Section 4 - Type Feedback
# ============================================================

class TestTypeFeedback:
    def test_function_feedback_import(self):
        from nlpl.jit.type_feedback import FunctionFeedback
        assert FunctionFeedback is not None

    def test_function_feedback_record_call(self):
        from nlpl.jit.type_feedback import FunctionFeedback
        fb = FunctionFeedback("add")
        fb.record_call(["Integer", "Integer"])

    def test_function_feedback_monomorphic(self):
        from nlpl.jit.type_feedback import FunctionFeedback, Polymorphism
        fb = FunctionFeedback("add")
        fb.record_call(["Integer", "Integer"])
        fb.record_call(["Integer", "Integer"])
        assert fb.polymorphism == Polymorphism.MONOMORPHIC

    def test_function_feedback_polymorphic(self):
        from nlpl.jit.type_feedback import FunctionFeedback, Polymorphism
        fb = FunctionFeedback("add")
        fb.record_call(["Integer", "Integer"])
        fb.record_call(["Float", "Float"])
        assert fb.polymorphism in (Polymorphism.POLYMORPHIC, Polymorphism.MEGAMORPHIC)

    def test_type_feedback_collector_import(self):
        from nlpl.jit.type_feedback import TypeFeedbackCollector
        tfc = TypeFeedbackCollector()
        assert tfc is not None

    def test_type_feedback_collector_get_record(self):
        from nlpl.jit.type_feedback import TypeFeedbackCollector
        tfc = TypeFeedbackCollector()
        # get_record returns None for unknown functions - that is the correct behaviour
        rec = tfc.get_record("my_func")
        assert rec is None  # not yet recorded

    def test_type_feedback_collector_get_hints(self):
        from nlpl.jit.type_feedback import TypeFeedbackCollector
        tfc = TypeFeedbackCollector()
        hints = tfc.get_hints("my_func")
        assert isinstance(hints, (list, dict, type(None)))


# ============================================================
# Section 5 - Enhanced Linter Checks
# ============================================================

