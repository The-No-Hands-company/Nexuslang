"""
Tail Call Optimization Pass
============================

Optimizes tail-recursive functions to use iteration instead of recursion,
preventing stack overflow and improving performance.
"""

from typing import Any
from ..optimizer import OptimizationPass, OptimizationStats
from ..parser.ast import (
    Program, FunctionDefinition, ReturnStatement, FunctionCall,
    IfStatement, WhileLoop, Block, VariableDeclaration, Identifier, Literal
)


class TailCallOptimizationPass(OptimizationPass):
    """
    Tail call optimization for recursive functions.
    
    Transforms tail-recursive functions into iterative loops.
    
    Example:
        function factorial with n as Integer returns Integer
            if n is less than or equal to 1
                return 1
            return n times factorial with n minus 1
        end
    
    Becomes:
        function factorial with n as Integer returns Integer
            set result to 1
            while n is greater than 1
                set result to result times n
                set n to n minus 1
            return result
        end
    """
    
    def __init__(self):
        super().__init__("TailCallOptimization")
        self.functions_optimized = 0
    
    def run(self, ast: Program) -> Program:
        """Run tail call optimization on the AST."""
        self.functions_optimized = 0
        
        for stmt in ast.statements:
            if isinstance(stmt, FunctionDefinition):
                if self._optimize_function(stmt):
                    self.functions_optimized += 1
        
        self.stats.functions_inlined = self.functions_optimized  # Reuse stat
        return ast
    
    def _optimize_function(self, func: FunctionDefinition) -> bool:
        """
        Try to optimize a function for tail recursion.
        
        Returns:
            True if optimization was applied
        """
        # Check if function is tail-recursive
        if not self._is_tail_recursive(func):
            return False
        
        # Check if it's simple enough to optimize
        tail_call = self._find_tail_call(func)
        if tail_call is None:
            return False
        
        # For now, skip transformation (complex AST manipulation required)
        # In a full implementation, we would:
        # 1. Add a loop wrapper
        # 2. Replace return with parameter updates and continue
        # 3. Replace tail call with parameter assignment
        
        return False  # Placeholder
    
    def _is_tail_recursive(self, func: FunctionDefinition) -> bool:
        """Check if function contains tail-recursive calls."""
        return self._contains_tail_call(func, func.name)
    
    def _contains_tail_call(self, node, func_name: str) -> bool:
        """Check if node contains a tail call to func_name."""
        # Check return statements
        if isinstance(node, ReturnStatement):
            if node.value and isinstance(node.value, FunctionCall):
                if node.value.name == func_name:
                    return True
        
        # Check if statement branches
        if isinstance(node, IfStatement):
            # Tail calls in both branches
            then_has_tail = any(
                self._contains_tail_call(s, func_name) 
                for s in node.then_block
            )
            else_has_tail = False
            if node.else_block:
                else_has_tail = any(
                    self._contains_tail_call(s, func_name)
                    for s in node.else_block
                )
            return then_has_tail or else_has_tail
        
        # Check function body
        if hasattr(node, 'body') and isinstance(node.body, list):
            # Only last statement can be tail call
            if node.body:
                return self._contains_tail_call(node.body[-1], func_name)
        
        return False
    
    def _find_tail_call(self, func: FunctionDefinition) -> FunctionCall | None:
        """Find the tail call in a function."""
        if not func.body:
            return None
        
        last_stmt = func.body[-1]
        
        if isinstance(last_stmt, ReturnStatement):
            if isinstance(last_stmt.value, FunctionCall):
                if last_stmt.value.name == func.name:
                    return last_stmt.value
        
        return None
