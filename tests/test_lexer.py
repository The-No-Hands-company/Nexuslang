"""
Test cases for the NLPL lexer.
Tests token recognition, error handling, and edge cases.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import unittest
from nlpl.parser.lexer import Lexer, TokenType

class TestLexer(unittest.TestCase):
    """Test cases for the NLPL lexer."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.lexer = None
    
    def test_keywords(self):
        """Test recognition of all keywords."""
        keywords = {
            "if": TokenType.IF,
            "else": TokenType.ELSE,
            "while": TokenType.WHILE,
            "for": TokenType.FOR,
            "function": TokenType.FUNCTION,
            "return": TokenType.RETURN,
            "class": TokenType.CLASS,
            "import": TokenType.IMPORT,
            "from": TokenType.FROM,
            "as": TokenType.AS,
            "returns": TokenType.RETURNS,
            "Integer": TokenType.INTEGER_TYPE,
            "Float": TokenType.FLOAT_TYPE,
            "String": TokenType.STRING_TYPE,
            "Boolean": TokenType.BOOLEAN_TYPE,
            "Null": TokenType.NULL_TYPE,
            "List": TokenType.LIST_TYPE,
            "Dictionary": TokenType.DICTIONARY_TYPE
        }
        
        for keyword, expected_type in keywords.items():
            self.lexer = Lexer(keyword)
            token = self.lexer.get_next_token()
            self.assertEqual(token.type, expected_type)
            self.assertEqual(token.value, keyword)
            self.assertEqual(token.line, 1)
            self.assertEqual(token.column, 1)
    
    def test_operators(self):
        """Test recognition of all operators."""
        operators = {
            "+": TokenType.PLUS,
            "-": TokenType.MINUS,
            "*": TokenType.MULTIPLY,
            "/": TokenType.DIVIDE,
            "=": TokenType.EQUALS,
            "==": TokenType.EQUALS_EQUALS,
            "!=": TokenType.NOT_EQUALS,
            "<": TokenType.LESS_THAN,
            "<=": TokenType.LESS_THAN_EQUALS,
            ">": TokenType.GREATER_THAN,
            ">=": TokenType.GREATER_THAN_EQUALS,
            "and": TokenType.AND,
            "or": TokenType.OR,
            "not": TokenType.NOT
        }
        
        for operator, expected_type in operators.items():
            self.lexer = Lexer(operator)
            token = self.lexer.get_next_token()
            self.assertEqual(token.type, expected_type)
            self.assertEqual(token.value, operator)
    
    def test_identifiers(self):
        """Test recognition of valid identifiers."""
        identifiers = [
            "variable",
            "myVariable",
            "my_variable",
            "variable123",
            "_variable",
            "v123"
        ]
        
        for identifier in identifiers:
            self.lexer = Lexer(identifier)
            token = self.lexer.get_next_token()
            self.assertEqual(token.type, TokenType.IDENTIFIER)
            self.assertEqual(token.value, identifier)
    
    def test_numbers(self):
        """Test recognition of integer and float literals."""
        numbers = [
            ("123", TokenType.INTEGER, 123),
            ("123.456", TokenType.FLOAT, 123.456),
            ("0", TokenType.INTEGER, 0),
            ("0.0", TokenType.FLOAT, 0.0),
            ("-123", TokenType.INTEGER, -123),
            ("-123.456", TokenType.FLOAT, -123.456)
        ]
        
        for number_str, expected_type, expected_value in numbers:
            self.lexer = Lexer(number_str)
            token = self.lexer.get_next_token()
            self.assertEqual(token.type, expected_type)
            self.assertEqual(token.value, expected_value)
    
    def test_strings(self):
        """Test recognition of string literals."""
        strings = [
            ('"hello"', "hello"),
            ("'world'", "world"),
            ('"hello\nworld"', "hello\nworld"),
            ('"hello\tworld"', "hello\tworld"),
            ('"hello\\"world"', 'hello"world')
        ]
        
        for string_str, expected_value in strings:
            self.lexer = Lexer(string_str)
            token = self.lexer.get_next_token()
            self.assertEqual(token.type, TokenType.STRING)
            self.assertEqual(token.value, expected_value)
    
    def test_whitespace(self):
        """Test handling of whitespace."""
        self.lexer = Lexer("  \t\n  ")
        token = self.lexer.get_next_token()
        self.assertEqual(token.type, TokenType.EOF)
    
    def test_comments(self):
        """Test handling of comments."""
        self.lexer = Lexer("# This is a comment\nvariable")
        token = self.lexer.get_next_token()
        self.assertEqual(token.type, TokenType.IDENTIFIER)
        self.assertEqual(token.value, "variable")
    
    def test_error_handling(self):
        """Test error handling for invalid characters."""
        invalid_chars = ["@", "$", "&", "~"]
        
        for char in invalid_chars:
            self.lexer = Lexer(char)
            with self.assertRaises(Exception) as context:
                self.lexer.get_next_token()
            self.assertTrue("unrecognized character" in str(context.exception))
    
    def test_line_and_column_tracking(self):
        """Test line and column tracking."""
        source = "variable\n  another_variable\n    third_variable"
        self.lexer = Lexer(source)
        
        # First line
        token = self.lexer.get_next_token()
        self.assertEqual(token.line, 1)
        self.assertEqual(token.column, 1)
        
        # Second line
        token = self.lexer.get_next_token()
        self.assertEqual(token.line, 2)
        self.assertEqual(token.column, 3)
        
        # Third line
        token = self.lexer.get_next_token()
        self.assertEqual(token.line, 3)
        self.assertEqual(token.column, 5)
    
    def test_complex_program(self):
        """Test lexing a complex program."""
        source = """
        function calculate_sum(a as Integer, b as Integer) returns Integer:
            return a + b
        end
        
        if x > 0:
            print("Positive")
        else:
            print("Negative")
        end
        """
        
        self.lexer = Lexer(source)
        tokens = []
        
        while True:
            token = self.lexer.get_next_token()
            if token.type == TokenType.EOF:
                break
            tokens.append(token)
        
        # Verify token sequence
        expected_types = [
            TokenType.FUNCTION,
            TokenType.IDENTIFIER,
            TokenType.LPAREN,
            TokenType.IDENTIFIER,
            TokenType.AS,
            TokenType.INTEGER_TYPE,
            TokenType.COMMA,
            TokenType.IDENTIFIER,
            TokenType.AS,
            TokenType.INTEGER_TYPE,
            TokenType.RPAREN,
            TokenType.RETURNS,
            TokenType.INTEGER_TYPE,
            TokenType.COLON,
            TokenType.RETURN,
            TokenType.IDENTIFIER,
            TokenType.PLUS,
            TokenType.IDENTIFIER,
            TokenType.END,
            TokenType.IF,
            TokenType.IDENTIFIER,
            TokenType.GREATER_THAN,
            TokenType.INTEGER,
            TokenType.COLON,
            TokenType.IDENTIFIER,
            TokenType.LPAREN,
            TokenType.STRING,
            TokenType.RPAREN,
            TokenType.ELSE,
            TokenType.COLON,
            TokenType.IDENTIFIER,
            TokenType.LPAREN,
            TokenType.STRING,
            TokenType.RPAREN,
            TokenType.END
        ]
        
        self.assertEqual(len(tokens), len(expected_types))
        for token, expected_type in zip(tokens, expected_types):
            self.assertEqual(token.type, expected_type)

if __name__ == '__main__':
    unittest.main() 