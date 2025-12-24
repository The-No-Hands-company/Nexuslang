"""
Test cases for the NLPL interpreter.
Tests program execution and runtime behavior.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import unittest
from nlpl.interpreter.interpreter import Interpreter
from nlpl.runtime.runtime import Runtime

class TestInterpreter(unittest.TestCase):
    """Test cases for the NLPL interpreter."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.runtime = Runtime()
        self.interpreter = Interpreter(self.runtime)
    
    def test_variable_declaration_and_assignment(self):
        """Test variable declaration and assignment."""
        source = """
        x as Integer = 42
        y as Float = 3.14
        z as String = "hello"
        """
        result = self.interpreter.interpret(source)
        
        # Check variable values
        self.assertEqual(self.runtime.get_variable("x"), 42)
        self.assertEqual(self.runtime.get_variable("y"), 3.14)
        self.assertEqual(self.runtime.get_variable("z"), "hello")
    
    def test_function_definition_and_call(self):
        """Test function definition and calling."""
        source = """
        function add(a as Integer, b as Integer) returns Integer:
            return a + b
        end
        
        result as Integer = add(5, 3)
        """
        result = self.interpreter.interpret(source)
        
        # Check function result
        self.assertEqual(self.runtime.get_variable("result"), 8)
    
    def test_if_statement(self):
        """Test if statement execution."""
        source = """
        x as Integer = 5
        if x > 0:
            result as String = "Positive"
        else:
            result as String = "Negative"
        end
        """
        result = self.interpreter.interpret(source)
        
        # Check result
        self.assertEqual(self.runtime.get_variable("result"), "Positive")
        
        # Test else branch
        source = """
        x as Integer = -5
        if x > 0:
            result as String = "Positive"
        else:
            result as String = "Negative"
        end
        """
        result = self.interpreter.interpret(source)
        self.assertEqual(self.runtime.get_variable("result"), "Negative")
    
    def test_while_loop(self):
        """Test while loop execution."""
        source = """
        x as Integer = 5
        sum as Integer = 0
        while x > 0:
            sum = sum + x
            x = x - 1
        end
        """
        result = self.interpreter.interpret(source)
        
        # Check final values
        self.assertEqual(self.runtime.get_variable("sum"), 15)  # 5 + 4 + 3 + 2 + 1
        self.assertEqual(self.runtime.get_variable("x"), 0)
    
    def test_for_loop(self):
        """Test for loop execution."""
        source = """
        sum as Integer = 0
        for i as Integer = 1 to 5:
            sum = sum + i
        end
        """
        result = self.interpreter.interpret(source)
        
        # Check final value
        self.assertEqual(self.runtime.get_variable("sum"), 15)  # 1 + 2 + 3 + 4 + 5
    
    def test_arithmetic_operations(self):
        """Test arithmetic operations."""
        source = """
        a as Integer = 10
        b as Integer = 3
        
        sum as Integer = a + b
        diff as Integer = a - b
        product as Integer = a * b
        quotient as Float = a / b
        remainder as Integer = a % b
        """
        result = self.interpreter.interpret(source)
        
        # Check results
        self.assertEqual(self.runtime.get_variable("sum"), 13)
        self.assertEqual(self.runtime.get_variable("diff"), 7)
        self.assertEqual(self.runtime.get_variable("product"), 30)
        self.assertAlmostEqual(self.runtime.get_variable("quotient"), 3.3333333333333335)
        self.assertEqual(self.runtime.get_variable("remainder"), 1)
    
    def test_comparison_operations(self):
        """Test comparison operations."""
        source = """
        x as Integer = 5
        y as Integer = 10
        
        less as Boolean = x < y
        less_equal as Boolean = x <= y
        greater as Boolean = x > y
        greater_equal as Boolean = x >= y
        equal as Boolean = x == y
        not_equal as Boolean = x != y
        """
        result = self.interpreter.interpret(source)
        
        # Check results
        self.assertTrue(self.runtime.get_variable("less"))
        self.assertTrue(self.runtime.get_variable("less_equal"))
        self.assertFalse(self.runtime.get_variable("greater"))
        self.assertFalse(self.runtime.get_variable("greater_equal"))
        self.assertFalse(self.runtime.get_variable("equal"))
        self.assertTrue(self.runtime.get_variable("not_equal"))
    
    def test_logical_operations(self):
        """Test logical operations."""
        source = """
        a as Boolean = true
        b as Boolean = false
        c as Boolean = true
        
        and_result as Boolean = a and b
        or_result as Boolean = a or b
        not_result as Boolean = not b
        complex_result as Boolean = (a and c) or (b and not c)
        """
        result = self.interpreter.interpret(source)
        
        # Check results
        self.assertFalse(self.runtime.get_variable("and_result"))
        self.assertTrue(self.runtime.get_variable("or_result"))
        self.assertTrue(self.runtime.get_variable("not_result"))
        self.assertTrue(self.runtime.get_variable("complex_result"))
    
    def test_string_operations(self):
        """Test string operations."""
        source = """
        str1 as String = "Hello"
        str2 as String = "World"
        
        concat as String = str1 + " " + str2
        length as Integer = len(str1)
        substring as String = substr(str1, 0, 2)
        """
        result = self.interpreter.interpret(source)
        
        # Check results
        self.assertEqual(self.runtime.get_variable("concat"), "Hello World")
        self.assertEqual(self.runtime.get_variable("length"), 5)
        self.assertEqual(self.runtime.get_variable("substring"), "He")
    
    def test_error_handling(self):
        """Test error handling."""
        error_cases = [
            ("x = 1", "Variable 'x' not declared"),
            ("x as Integer = y", "Variable 'y' not declared"),
            ("x as Integer = 1 / 0", "Division by zero"),
            ("function add(a as Integer) returns Integer:\n    return a + b\nend", "Variable 'b' not declared")
        ]
        
        for source, expected_error in error_cases:
            with self.assertRaises(Exception) as context:
                self.interpreter.interpret(source)
            self.assertTrue(expected_error in str(context.exception))
    
    def test_complex_program(self):
        """Test execution of a complex program."""
        source = """
        function factorial(n as Integer) returns Integer:
            if n <= 1:
                return 1
            else:
                return n * factorial(n - 1)
            end
        end
        
        function fibonacci(n as Integer) returns Integer:
            if n <= 1:
                return n
            else:
                return fibonacci(n - 1) + fibonacci(n - 2)
            end
        end
        
        n as Integer = 5
        fact as Integer = factorial(n)
        fib as Integer = fibonacci(n)
        """
        result = self.interpreter.interpret(source)
        
        # Check results
        self.assertEqual(self.runtime.get_variable("fact"), 120)  # 5 * 4 * 3 * 2 * 1
        self.assertEqual(self.runtime.get_variable("fib"), 5)    # 5th Fibonacci number

if __name__ == '__main__':
    unittest.main() 