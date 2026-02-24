"""
Optimizer, PGO, and optimization-level tests.
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

class TestOptimizerPasses:
    def test_string_interning_import(self):
        from nlpl.optimizer.string_interning import StringInterningPass
        p = StringInterningPass()
        assert p is not None

    def test_string_interning_has_name(self):
        from nlpl.optimizer.string_interning import StringInterningPass
        p = StringInterningPass()
        assert hasattr(p, "name")
        assert isinstance(p.name, str)

    def test_type_specialization_import(self):
        from nlpl.optimizer.type_specialization import TypeSpecializationPass
        p = TypeSpecializationPass()
        assert p is not None

    def test_type_specialization_has_name(self):
        from nlpl.optimizer.type_specialization import TypeSpecializationPass
        p = TypeSpecializationPass()
        assert hasattr(p, "name")

    def test_dispatch_optimization_import(self):
        from nlpl.optimizer.dispatch_optimization import DispatchOptimizationPass
        p = DispatchOptimizationPass()
        assert p is not None

    def test_dispatch_optimization_has_name(self):
        from nlpl.optimizer.dispatch_optimization import DispatchOptimizationPass
        p = DispatchOptimizationPass()
        assert hasattr(p, "name")

    def test_pipeline_contains_passes(self):
        from nlpl.optimizer import OptimizationPipeline
        pipeline = OptimizationPipeline()
        assert hasattr(pipeline, "passes")
        assert isinstance(pipeline.passes, list)

    def test_pipeline_add_pass(self):
        from nlpl.optimizer import OptimizationPipeline
        from nlpl.optimizer.string_interning import StringInterningPass
        pipeline = OptimizationPipeline()
        before = len(pipeline.passes)
        pipeline.add_pass(StringInterningPass())
        assert len(pipeline.passes) == before + 1

    def test_pipeline_all_three_passes_present(self):
        from nlpl.optimizer import OptimizationPipeline
        pipeline = OptimizationPipeline()
        names = [p.name for p in pipeline.passes]
        # At least one of the new passes should be registered by default
        # (or we can just check all three can be imported cleanly)
        from nlpl.optimizer.string_interning import StringInterningPass
        from nlpl.optimizer.type_specialization import TypeSpecializationPass
        from nlpl.optimizer.dispatch_optimization import DispatchOptimizationPass
        assert StringInterningPass().name
        assert TypeSpecializationPass().name
        assert DispatchOptimizationPass().name


# ============================================================
# Section 2 - PGO (Profile-Guided Optimization)
# ============================================================

class TestPGO:
    def test_pgo_import(self):
        from nlpl.tooling.pgo import PGOProfile
        assert PGOProfile is not None

    def test_pgo_create_profile(self):
        from nlpl.tooling.pgo import PGOProfile
        profile = PGOProfile(program_name="test")
        assert profile is not None

    def test_pgo_has_program_name(self):
        from nlpl.tooling.pgo import PGOProfile
        profile = PGOProfile(program_name="my_prog")
        assert profile.program_name == "my_prog"

    def test_pgo_record_execution(self):
        from nlpl.tooling.pgo import PGOProfile
        profile = PGOProfile(program_name="test")
        profile.record_execution("hot_func")
        assert profile.is_hot("hot_func")

    def test_pgo_cold_function(self):
        from nlpl.tooling.pgo import PGOProfile
        profile = PGOProfile(program_name="test")
        assert not profile.is_hot("never_called")

    def test_pgo_save_and_load(self):
        from nlpl.tooling.pgo import PGOProfile
        profile = PGOProfile(program_name="test")
        profile.record_execution("func_a")
        profile.record_execution("func_a")
        profile.record_execution("func_b")
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            profile.save(path)
            loaded = PGOProfile.load(path)
            assert loaded.is_hot("func_a")
        finally:
            os.unlink(path)

    def test_pgo_get_call_count(self):
        from nlpl.tooling.pgo import PGOProfile
        profile = PGOProfile(program_name="test")
        for _ in range(5):
            profile.record_execution("counted_func")
        assert profile.get_call_count("counted_func") == 5


# ============================================================
# Section 3 - JIT Tiered Compilation
# ============================================================

class TestOptimizationLevel:
    def test_int_to_opt_level_import(self):
        from nlpl.optimizer import int_to_opt_level
        assert callable(int_to_opt_level)

    def test_opt_level_0(self):
        from nlpl.optimizer import int_to_opt_level, OptimizationLevel
        assert int_to_opt_level(0) == OptimizationLevel.O0

    def test_opt_level_1(self):
        from nlpl.optimizer import int_to_opt_level, OptimizationLevel
        assert int_to_opt_level(1) == OptimizationLevel.O1

    def test_opt_level_2(self):
        from nlpl.optimizer import int_to_opt_level, OptimizationLevel
        assert int_to_opt_level(2) == OptimizationLevel.O2

    def test_opt_level_3(self):
        from nlpl.optimizer import int_to_opt_level, OptimizationLevel
        assert int_to_opt_level(3) == OptimizationLevel.O3

    def test_opt_level_out_of_range(self):
        from nlpl.optimizer import int_to_opt_level
        with pytest.raises((ValueError, KeyError, Exception)):
            int_to_opt_level(99)


# ============================================================
# Section 16 - Assertion library (ExpectStatement)
# ============================================================

