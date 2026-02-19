"""
Test string interpolation (f-strings).
"""

from src.nlpl.parser.ast import FStringExpression, Literal, Identifier
from src.nlpl.parser.parser import Parser
from src.nlpl.parser.lexer import Lexer, TokenType

def test_fstring_parsing():
    """Test parsing f-strings."""
    print("Testing F-String Parsing...")
    
    # Test 1: Simple interpolation
    print("\n1. Testing simple interpolation:")
    code = 'f"Hello, {name}!"'
    
    lexer = Lexer(code)
    parser = Parser(lexer.scan_tokens())
    
    # For now, just test that we can create the AST node manually
    parts = [
        (True, "Hello, "),
        (False, Identifier("name")),
        (True, "!")
    ]
    fstring = FStringExpression(parts)
    
    assert len(fstring.parts) == 3
    assert fstring.parts[0] == (True, "Hello, ")
    print("    F-string AST node created")
    
    # Test 2: Expression interpolation
    print("\n2. Testing expression interpolation:")
    parts2 = [
        (True, "Result: "),
        (False, Literal(TokenType.INTEGER_LITERAL, 42)),
    ]
    fstring2 = FStringExpression(parts2)
    assert len(fstring2.parts) == 2
    print("    Expression interpolation works")
    
    print("\n F-string AST tests passed!")
    print("Note: Parser integration pending")

if __name__ == "__main__":
    test_fstring_parsing()
