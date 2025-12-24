"""
Shared test utilities for NLPL test suite.
Common helper functions and fixtures.
"""

import sys
import os
import textwrap

# Add src directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from nlpl.parser.lexer import Lexer
from nlpl.parser.parser import Parser
from nlpl.interpreter.interpreter import Interpreter
from nlpl.runtime.runtime import Runtime
from nlpl.stdlib import register_stdlib


class NLPLTestBase:
    """Base class for NLPL tests with common utilities."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        self.runtime = Runtime()
        # Register standard library functions
        register_stdlib(self.runtime)
        self.interpreter = Interpreter(self.runtime)
    
    def parse_and_execute(self, code):
        """
        Helper method to parse and execute NLPL code.
        
        Args:
            code: NLPL source code to execute
            
        Returns:
            Result of interpretation
        """
        # Remove leading whitespace from test code (handles triple-quoted strings with indentation)
        code = textwrap.dedent(code)
        
        # Ensure code ends with newline for proper parsing
        if not code.endswith('\n'):
            code += '\n'
        
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        return self.interpreter.interpret(ast)
    
    def get_variable(self, name):
        """Get a variable value from the interpreter."""
        return self.interpreter.get_variable(name)
    
    def assert_variable(self, name, expected_value):
        """Assert that a variable has the expected value."""
        actual = self.get_variable(name)
        assert actual == expected_value, f"Expected {name}={expected_value}, got {actual}"


def parse_nlpl(code):
    """
    Parse NLPL code and return AST.
    
    Args:
        code: NLPL source code
        
    Returns:
        AST representing the code
    """
    if not code.endswith('\n'):
        code += '\n'
    
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    return parser.parse()


def execute_nlpl(code):
    """
    Execute NLPL code and return runtime and interpreter.
    
    Args:
        code: NLPL source code
        
    Returns:
        Tuple of (runtime, interpreter)
    """
    if not code.endswith('\n'):
        code += '\n'
    
    runtime = Runtime()
    interpreter = Interpreter(runtime)
    
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    interpreter.interpret(ast)
    
    return runtime, interpreter
