"""
Test cases for NLPL error handling.
Tests various error conditions and error reporting.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import unittest
from nlpl.interpreter.interpreter import Interpreter
from nlpl.runtime.runtime import Runtime
from nlpl.parser.lexer import Lexer
from nlpl.parser.parser import Parser

class TestErrorHandling(unittest.TestCase):
    """Test cases for NLPL error handling."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.runtime = Runtime()
        self.interpreter = Interpreter(self.runtime)
    
    def test_lexer_errors(self):
        """Test lexer error handling."""
        error_cases = [
            ("@invalid", "unrecognized character '@'"),
            ("123abc", "invalid number format"),
            ('"unclosed string', "unclosed string literal"),
            ("'unclosed string", "unclosed string literal"),
            ("/* unclosed comment", "unclosed comment")
        ]
        
        for source, expected_error in error_cases:
            lexer = Lexer(source)
            with self.assertRaises(Exception) as context:
                while True:
                    token = lexer.get_next_token()
                    if token.type == TokenType.EOF:
                        break
            self.assertTrue(expected_error in str(context.exception))
    
    def test_parser_errors(self):
        """Test parser error handling."""
        error_cases = [
            ("x =", "Unexpected token: EOF"),
            ("function add(", "Unexpected token: EOF"),
            ("if x > 0", "Expected ':'"),
            ("while x > 0", "Expected ':'"),
            ("for i = 0", "Expected 'to'"),
            ("x as Integer =", "Unexpected token: EOF"),
            ("function add(a as Integer) returns Integer:\n    return a + b\nend", "Variable 'b' not declared"),
            ("if x > 0:\n    print(x)\nelse", "Expected ':'"),
            ("while x > 0:\n    print(x)", "Expected 'end'"),
            ("for i as Integer = 0 to 10:\n    print(i)", "Expected 'end'")
        ]
        
        for source, expected_error in error_cases:
            parser = Parser(source)
            with self.assertRaises(Exception) as context:
                parser.parse()
            self.assertTrue(expected_error in str(context.exception))
    
    def test_type_errors(self):
        """Test type error handling."""
        error_cases = [
            ("x as Integer = 'hello'", "Type mismatch: expected Integer, got String"),
            ("x as String = 42", "Type mismatch: expected String, got Integer"),
            ("x as Float = true", "Type mismatch: expected Float, got Boolean"),
            ("function add(a as Integer, b as String) returns Integer:\n    return a + b\nend", "Type mismatch: cannot add Integer and String"),
            ("x as List[Integer] = [1, 'two', 3]", "Type mismatch: expected Integer, got String"),
            ("x as Dictionary[String, Integer] = {'a': 'b'}", "Type mismatch: expected Integer, got String")
        ]
        
        for source, expected_error in error_cases:
            with self.assertRaises(Exception) as context:
                self.interpreter.interpret(source)
            self.assertTrue(expected_error in str(context.exception))
    
    def test_runtime_errors(self):
        """Test runtime error handling."""
        error_cases = [
            ("x = 1 / 0", "Division by zero"),
            ("x as Integer = 1 / 0", "Division by zero"),
            ("x as List[Integer] = []\ny = x[0]", "Index out of range"),
            ("x as Dictionary[String, Integer] = {}\ny = x['key']", "Key 'key' not found"),
            ("x as String = 'hello'\ny = x[10]", "Index out of range"),
            ("function recursive() returns Integer:\n    return recursive()\nend\nx = recursive()", "Maximum recursion depth exceeded")
        ]
        
        for source, expected_error in error_cases:
            with self.assertRaises(Exception) as context:
                self.interpreter.interpret(source)
            self.assertTrue(expected_error in str(context.exception))
    
    def test_scope_errors(self):
        """Test scope error handling."""
        error_cases = [
            ("x = 1", "Variable 'x' not declared"),
            ("function add(a as Integer) returns Integer:\n    return a + b\nend", "Variable 'b' not declared"),
            ("if x > 0:\n    y = 1\nend\nprint(y)", "Variable 'y' not declared"),
            ("while x > 0:\n    y = 1\nend\nprint(y)", "Variable 'y' not declared"),
            ("for i as Integer = 0 to 10:\n    y = 1\nend\nprint(y)", "Variable 'y' not declared")
        ]
        
        for source, expected_error in error_cases:
            with self.assertRaises(Exception) as context:
                self.interpreter.interpret(source)
            self.assertTrue(expected_error in str(context.exception))
    
    def test_module_errors(self):
        """Test module error handling."""
        error_cases = [
            ("import nonexistent_module", "Module 'nonexistent_module' not found"),
            ("from nonexistent_module import function", "Module 'nonexistent_module' not found"),
            ("import math\nmath.nonexistent_function()", "Function 'nonexistent_function' not found in module 'math'"),
            ("from math import nonexistent_function", "Function 'nonexistent_function' not found in module 'math'")
        ]
        
        for source, expected_error in error_cases:
            with self.assertRaises(Exception) as context:
                self.interpreter.interpret(source)
            self.assertTrue(expected_error in str(context.exception))
    
    def test_error_location_reporting(self):
        """Test error location reporting."""
        source = """
        function add(a as Integer, b as Integer) returns Integer:
            return a + c
        end
        
        x = add(1, 2)
        """
        
        try:
            self.interpreter.interpret(source)
            self.fail("Expected error to be raised")
        except Exception as e:
            error_msg = str(e)
            self.assertTrue("line 3" in error_msg)
            self.assertTrue("column" in error_msg)
            self.assertTrue("Variable 'c' not declared" in error_msg)
    
    def test_error_recovery(self):
        """Test error recovery in the interpreter."""
        source = """
        # First statement with error
        x = 1 / 0
        
        # This should not be executed
        y = 42
        """
        
        try:
            self.interpreter.interpret(source)
            self.fail("Expected error to be raised")
        except Exception as e:
            self.assertTrue("Division by zero" in str(e))
            # Verify that y was not assigned
            with self.assertRaises(Exception):
                self.runtime.get_variable("y")

if __name__ == '__main__':
    unittest.main() 