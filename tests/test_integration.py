"""
Integration test cases for the NLPL compiler pipeline.
Tests the entire process from source code to execution.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import unittest
import os
import tempfile
from nlpl.interpreter.interpreter import Interpreter
from nlpl.runtime.runtime import Runtime
from nlpl.stdlib import register_stdlib

class TestIntegration(unittest.TestCase):
    """Integration test cases for the NLPL compiler pipeline."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.runtime = Runtime()
        register_stdlib(self.runtime)
        self.interpreter = Interpreter(self.runtime)
        
        # Create temporary directory for file operations
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
    
    def tearDown(self):
        """Clean up after each test method."""
        os.chdir(self.original_cwd)
        # Clean up temporary files
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)
    
    def test_hello_world(self):
        """Test a simple Hello World program."""
        source = """
        print("Hello, World!")
        """
        result = self.interpreter.interpret(source)
        # Note: We can't easily capture stdout in tests
        # The actual output would be "Hello, World!"
    
    def test_calculator(self):
        """Test a simple calculator program."""
        source = """
        function add(a as Integer, b as Integer) returns Integer:
            return a + b
        end
        
        function subtract(a as Integer, b as Integer) returns Integer:
            return a - b
        end
        
        function multiply(a as Integer, b as Integer) returns Integer:
            return a * b
        end
        
        function divide(a as Integer, b as Integer) returns Float:
            return a / b
        end
        
        # Test the calculator
        x as Integer = 10
        y as Integer = 3
        
        sum as Integer = add(x, y)
        diff as Integer = subtract(x, y)
        product as Integer = multiply(x, y)
        quotient as Float = divide(x, y)
        """
        result = self.interpreter.interpret(source)
        
        # Check results
        self.assertEqual(self.runtime.get_variable("sum"), 13)
        self.assertEqual(self.runtime.get_variable("diff"), 7)
        self.assertEqual(self.runtime.get_variable("product"), 30)
        self.assertAlmostEqual(self.runtime.get_variable("quotient"), 3.3333333333333335)
    
    def test_file_operations(self):
        """Test file operations with error handling."""
        source = """
        # Test file operations
        content as String = "Hello, World!"
        file_path as String = "test.txt"
        
        # Write to file
        io.write(file_path, content)
        
        # Read from file
        read_content as String = io.read(file_path)
        
        # Append to file
        io.append(file_path, "\nAppended content")
        appended_content as String = io.read(file_path)
        
        # Delete file
        io.delete(file_path)
        
        # Try to read deleted file (should raise error)
        try:
            io.read(file_path)
        except:
            error_handled as Boolean = true
        end
        """
        result = self.interpreter.interpret(source)
        
        # Check results
        self.assertEqual(self.runtime.get_variable("read_content"), "Hello, World!")
        self.assertEqual(self.runtime.get_variable("appended_content"), "Hello, World!\nAppended content")
        self.assertTrue(self.runtime.get_variable("error_handled"))
    
    def test_math_operations(self):
        """Test mathematical operations using the math module."""
        source = """
        # Test mathematical constants
        pi as Float = math.PI
        e as Float = math.E
        
        # Test basic arithmetic functions
        abs_val as Integer = math.abs(-42)
        sqrt_val as Float = math.square_root(16)
        pow_val as Integer = math.power(2, 3)
        
        # Test trigonometric functions
        sin_val as Float = math.sine(math.PI / 2)
        cos_val as Float = math.cosine(0)
        tan_val as Float = math.tangent(math.PI / 4)
        
        # Test statistical functions
        numbers as List[Integer] = [1, 2, 3, 4, 5]
        mean_val as Float = math.mean(numbers)
        median_val as Float = math.median(numbers)
        std_dev as Float = math.standard_deviation(numbers)
        """
        result = self.interpreter.interpret(source)
        
        # Check results
        self.assertAlmostEqual(self.runtime.get_variable("pi"), 3.141592653589793)
        self.assertAlmostEqual(self.runtime.get_variable("e"), 2.718281828459045)
        self.assertEqual(self.runtime.get_variable("abs_val"), 42)
        self.assertEqual(self.runtime.get_variable("sqrt_val"), 4.0)
        self.assertEqual(self.runtime.get_variable("pow_val"), 8)
        self.assertAlmostEqual(self.runtime.get_variable("sin_val"), 1.0)
        self.assertEqual(self.runtime.get_variable("cos_val"), 1.0)
        self.assertAlmostEqual(self.runtime.get_variable("tan_val"), 1.0)
        self.assertEqual(self.runtime.get_variable("mean_val"), 3.0)
        self.assertEqual(self.runtime.get_variable("median_val"), 3.0)
        self.assertAlmostEqual(self.runtime.get_variable("std_dev"), 1.4142135623730951)
    
    def test_string_operations(self):
        """Test string operations using the string module."""
        source = """
        # Test string manipulation
        str1 as String = "hello"
        str2 as String = "world"
        
        # Test case conversion
        upper as String = string.uppercase(str1)
        lower as String = string.lowercase("HELLO")
        title as String = string.title("hello world")
        
        # Test string operations
        length as Integer = string.length(str1)
        concat as String = string.concatenate(str1, " ", str2)
        substr as String = string.substring(str1, 0, 2)
        
        # Test string searching
        contains as Boolean = string.contains("hello world", "world")
        index as Integer = string.index_of("hello world", "world")
        starts_with as Boolean = string.starts_with("hello world", "hello")
        ends_with as Boolean = string.ends_with("hello world", "world")
        
        # Test string replacement
        replaced as String = string.replace("hello world", "world", "there")
        
        # Test string splitting and joining
        words as List[String] = string.split("hello world", " ")
        joined as String = string.join(words, "-")
        """
        result = self.interpreter.interpret(source)
        
        # Check results
        self.assertEqual(self.runtime.get_variable("upper"), "HELLO")
        self.assertEqual(self.runtime.get_variable("lower"), "hello")
        self.assertEqual(self.runtime.get_variable("title"), "Hello World")
        self.assertEqual(self.runtime.get_variable("length"), 5)
        self.assertEqual(self.runtime.get_variable("concat"), "hello world")
        self.assertEqual(self.runtime.get_variable("substr"), "he")
        self.assertTrue(self.runtime.get_variable("contains"))
        self.assertEqual(self.runtime.get_variable("index"), 6)
        self.assertTrue(self.runtime.get_variable("starts_with"))
        self.assertTrue(self.runtime.get_variable("ends_with"))
        self.assertEqual(self.runtime.get_variable("replaced"), "hello there")
        self.assertEqual(self.runtime.get_variable("words"), ["hello", "world"])
        self.assertEqual(self.runtime.get_variable("joined"), "hello-world")
    
    def test_complex_program(self):
        """Test a complex program that uses multiple features."""
        source = """
        # Define a class for a bank account
        class BankAccount:
            balance as Float
            
            function init(initial_balance as Float) returns BankAccount:
                self.balance = initial_balance
                return self
            end
            
            function deposit(amount as Float) returns Float:
                self.balance = self.balance + amount
                return self.balance
            end
            
            function withdraw(amount as Float) returns Float:
                if amount > self.balance:
                    raise "Insufficient funds"
                end
                self.balance = self.balance - amount
                return self.balance
            end
        end
        
        # Create a list of accounts
        accounts as List[BankAccount] = []
        
        # Create some accounts
        account1 as BankAccount = BankAccount.init(1000.0)
        account2 as BankAccount = BankAccount.init(2000.0)
        
        # Add accounts to list
        collections.append(accounts, account1)
        collections.append(accounts, account2)
        
        # Perform some transactions
        new_balance1 as Float = account1.deposit(500.0)
        new_balance2 as Float = account2.withdraw(1000.0)
        
        # Calculate total balance
        total_balance as Float = 0.0
        for account as BankAccount in accounts:
            total_balance = total_balance + account.balance
        end
        
        # Save account data to file
        data as String = string.concatenate(
            "Account 1 balance: ", string.to_string(new_balance1), "\n",
            "Account 2 balance: ", string.to_string(new_balance2), "\n",
            "Total balance: ", string.to_string(total_balance)
        )
        io.write("accounts.txt", data)
        
        # Read back the data
        saved_data as String = io.read("accounts.txt")
        """
        result = self.interpreter.interpret(source)
        
        # Check results
        self.assertEqual(self.runtime.get_variable("new_balance1"), 1500.0)
        self.assertEqual(self.runtime.get_variable("new_balance2"), 1000.0)
        self.assertEqual(self.runtime.get_variable("total_balance"), 2500.0)
        self.assertTrue("Account 1 balance: 1500.0" in self.runtime.get_variable("saved_data"))
        self.assertTrue("Account 2 balance: 1000.0" in self.runtime.get_variable("saved_data"))
        self.assertTrue("Total balance: 2500.0" in self.runtime.get_variable("saved_data"))

if __name__ == '__main__':
    unittest.main() 