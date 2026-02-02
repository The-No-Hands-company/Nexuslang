"""
Common Subexpression Elimination (CSE) Pass
============================================

Eliminates redundant computation of the same expression.

Example:
    x = a + b
    y = c * (a + b)
    
Becomes:
    temp = a + b
    x = temp
    y = c * temp
"""

from typing import Any, Dict, Set
from ..optimizer import OptimizationPass, OptimizationStats
from ..parser.ast import (
    Program, BinaryOperation, Literal, Identifier,
    VariableDeclaration, FunctionDefinition
)


class CommonSubexpressionEliminationPass(OptimizationPass):
    """
    Common Subexpression Elimination optimization.
    
    Identifies repeated expressions and replaces them with
    references to a temporary variable.
    """
    
    def __init__(self):
        super().__init__("CommonSubexpressionElimination")
        self.expressions_eliminated = 0
        self.expression_map: Dict[str, str] = {}  # expr_hash -> temp_var_name
        self.temp_counter = 0
    
    def run(self, ast: Program) -> Program:
        """Run CSE on the AST."""
        self.expressions_eliminated = 0
        self.expression_map.clear()
        self.temp_counter = 0
        
        # Process each function separately (different scopes)
        for stmt in ast.statements:
            if isinstance(stmt, FunctionDefinition):
                self._process_function(stmt)
        
        self.stats.dead_variables_removed = self.expressions_eliminated  # Reuse stat
        return ast
    
    def _process_function(self, func: FunctionDefinition):
        """Process a single function."""
        # Reset expression map for new scope
        old_map = self.expression_map.copy()
        self.expression_map.clear()
        
        # Analyze and transform statements
        new_body = []
        for stmt in func.body:
            # Collect expressions in this statement
            expressions = self._collect_expressions(stmt)
            
            # Check for common subexpressions
            for expr in expressions:
                expr_hash = self._hash_expression(expr)
                if expr_hash in self.expression_map:
                    # Found common subexpression
                    # Replace with reference to temp var
                    temp_var = self.expression_map[expr_hash]
                    self._replace_expression(stmt, expr, Identifier(temp_var))
                    self.expressions_eliminated += 1
                else:
                    # New expression - create temp var
                    if self._is_complex_expression(expr):
                        temp_var = f"_cse_temp_{self.temp_counter}"
                        self.temp_counter += 1
                        self.expression_map[expr_hash] = temp_var
                        
                        # Insert temp variable assignment
                        temp_decl = VariableDeclaration(
                            name=temp_var,
                            value=expr
                        )
                        new_body.append(temp_decl)
            
            new_body.append(stmt)
        
        func.body = new_body
        self.expression_map = old_map  # Restore previous scope
    
    def _collect_expressions(self, stmt) -> list:
        """Collect all expressions in a statement."""
        expressions = []
        
        if isinstance(stmt, BinaryOperation):
            expressions.append(stmt)
            expressions.extend(self._collect_expressions(stmt.left))
            expressions.extend(self._collect_expressions(stmt.right))
        elif isinstance(stmt, VariableDeclaration):
            if stmt.value:
                expressions.extend(self._collect_expressions(stmt.value))
        elif hasattr(stmt, 'value'):
            if hasattr(stmt.value, '__class__'):
                expressions.extend(self._collect_expressions(stmt.value))
        
        return expressions
    
    def _hash_expression(self, expr) -> str:
        """
        Create a hash/signature for an expression.
        
        Two expressions with the same hash are considered equivalent.
        """
        if isinstance(expr, Literal):
            return f"Lit:{expr.type}:{expr.value}"
        elif isinstance(expr, Identifier):
            return f"Id:{expr.name}"
        elif isinstance(expr, BinaryOperation):
            left_hash = self._hash_expression(expr.left)
            right_hash = self._hash_expression(expr.right)
            return f"BinOp:{expr.operator}:({left_hash},{right_hash})"
        else:
            # Unknown expression type
            return f"Unknown:{id(expr)}"
    
    def _is_complex_expression(self, expr) -> bool:
        """Check if expression is complex enough to benefit from CSE."""
        if isinstance(expr, (Literal, Identifier)):
            return False
        return True
    
    def _replace_expression(self, stmt, old_expr, new_expr):
        """Replace an expression in a statement."""
        # This is a simplified replacement - full implementation
        # would need deep traversal and replacement
        
        if isinstance(stmt, VariableDeclaration):
            if stmt.value is old_expr:
                stmt.value = new_expr
        elif isinstance(stmt, BinaryOperation):
            if stmt.left is old_expr:
                stmt.left = new_expr
            else:
                self._replace_expression(stmt.left, old_expr, new_expr)
            
            if stmt.right is old_expr:
                stmt.right = new_expr
            else:
                self._replace_expression(stmt.right, old_expr, new_expr)
