"""
NLPL Compiler Optimization Framework
=====================================

Provides infrastructure for compiler optimizations including:
- Dead code elimination (DCE)
- Constant folding and propagation
- Function inlining
- Peephole optimizations
- Control flow optimizations
"""

from typing import Dict, List, Set, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum


class OptimizationLevel(Enum):
    """Optimization levels similar to GCC/Clang."""
    O0 = 0  # No optimization
    O1 = 1  # Basic optimizations
    O2 = 2  # More optimizations
    O3 = 3  # Aggressive optimizations
    Os = 4  # Optimize for size


@dataclass
class OptimizationStats:
    """Statistics about optimizations performed."""
    dead_functions_removed: int = 0
    dead_variables_removed: int = 0
    unreachable_blocks_removed: int = 0
    constants_folded: int = 0
    functions_inlined: int = 0
    total_passes: int = 0
    
    def __str__(self):
        return f"""Optimization Statistics:
  Dead Functions Removed: {self.dead_functions_removed}
  Dead Variables Removed: {self.dead_variables_removed}
  Unreachable Blocks Removed: {self.unreachable_blocks_removed}
  Constants Folded: {self.constants_folded}
  Functions Inlined: {self.functions_inlined}
  Total Optimization Passes: {self.total_passes}"""


class OptimizationPass:
    """Base class for optimization passes."""
    
    def __init__(self, name: str):
        self.name = name
        self.enabled = True
        self.stats = OptimizationStats()
    
    def run(self, ast: Any) -> Any:
        """Run the optimization pass on the AST."""
        raise NotImplementedError(f"Pass {self.name} must implement run()")
    
    def should_run(self, level: OptimizationLevel) -> bool:
        """Check if this pass should run at the given optimization level."""
        return self.enabled


class OptimizationPipeline:
    """Manages the sequence of optimization passes."""
    
    def __init__(self, level: OptimizationLevel = OptimizationLevel.O0):
        self.level = level
        self.passes: List[OptimizationPass] = []
        self.stats = OptimizationStats()
        self.verbose = False
    
    def add_pass(self, pass_: OptimizationPass):
        """Add an optimization pass to the pipeline."""
        self.passes.append(pass_)
    
    def run(self, ast: Any) -> Any:
        """Run all optimization passes on the AST."""
        current_ast = ast
        
        for pass_ in self.passes:
            if not pass_.should_run(self.level):
                continue
            
            if self.verbose:
                print(f"Running optimization pass: {pass_.name}")
            
            current_ast = pass_.run(current_ast)
            
            # Aggregate statistics
            self.stats.total_passes += 1
            self.stats.dead_functions_removed += pass_.stats.dead_functions_removed
            self.stats.dead_variables_removed += pass_.stats.dead_variables_removed
            self.stats.unreachable_blocks_removed += pass_.stats.unreachable_blocks_removed
            self.stats.constants_folded += pass_.stats.constants_folded
            self.stats.functions_inlined += pass_.stats.functions_inlined
        
        return current_ast
    
    def print_stats(self):
        """Print optimization statistics."""
        print(self.stats)


def create_optimization_pipeline(level: OptimizationLevel, verbose: bool = False) -> OptimizationPipeline:
    """
    Create a standard optimization pipeline for the given level.
    
    O0: No optimizations
    O1: Basic DCE, constant folding
    O2: O1 + inlining, strength reduction, loop unrolling
    O3: O2 + aggressive inlining, CSE, tail call optimization
    Os: Optimize for code size
    """
    from ..optimizer.dead_code_elimination import DeadCodeEliminationPass
    from ..optimizer.constant_folding import ConstantFoldingPass
    from ..optimizer.function_inlining import FunctionInliningPass
    from ..optimizer.strength_reduction import StrengthReductionPass
    from ..optimizer.loop_unrolling import LoopUnrollingPass
    from ..optimizer.common_subexpression_elimination import CommonSubexpressionEliminationPass
    from ..optimizer.tail_call_optimization import TailCallOptimizationPass
    
    pipeline = OptimizationPipeline(level)
    pipeline.verbose = verbose
    
    if level == OptimizationLevel.O0:
        # No optimizations
        return pipeline
    
    # O1 and above: basic optimizations
    if level.value >= OptimizationLevel.O1.value:
        pipeline.add_pass(ConstantFoldingPass())
        pipeline.add_pass(DeadCodeEliminationPass(aggressive=False))
    
    # O2 and above: more optimizations
    if level.value >= OptimizationLevel.O2.value:
        pipeline.add_pass(StrengthReductionPass())
        pipeline.add_pass(LoopUnrollingPass(max_unroll_count=8))
        pipeline.add_pass(FunctionInliningPass(max_size=50))
        pipeline.add_pass(DeadCodeEliminationPass(aggressive=True))
        # Run constant folding again after transformations
        pipeline.add_pass(ConstantFoldingPass())
    
    # O3: aggressive optimizations
    if level == OptimizationLevel.O3:
        pipeline.add_pass(CommonSubexpressionEliminationPass())
        pipeline.add_pass(TailCallOptimizationPass())
        pipeline.add_pass(FunctionInliningPass(max_size=100, aggressive=True))
        # Multiple passes for maximum optimization
        pipeline.add_pass(StrengthReductionPass())
        pipeline.add_pass(DeadCodeEliminationPass(aggressive=True))
        pipeline.add_pass(ConstantFoldingPass())
    
    # Os: optimize for size
    if level == OptimizationLevel.Os:
        pipeline.add_pass(ConstantFoldingPass())
        pipeline.add_pass(DeadCodeEliminationPass(aggressive=True))
        # Small inline threshold for size optimization
        pipeline.add_pass(FunctionInliningPass(max_size=20))
    
    return pipeline


# Export main classes
__all__ = [
    'OptimizationLevel',
    'OptimizationStats',
    'OptimizationPass',
    'OptimizationPipeline',
    'create_optimization_pipeline'
]
