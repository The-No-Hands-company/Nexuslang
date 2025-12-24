"""
Test f-string parser implementation.
"""

import sys
sys.path.insert(0, '/run/media/zajferx/Data/dev/The-No-hands-Company/projects/Active/NLPL/src')

from nlpl.parser.lexer import Lexer
from nlpl.parser.parser import Parser
from nlpl.parser.ast import FStringExpression, Identifier

def test_fstring_parser():
    """Test parser conversion of f-strings to AST."""
    print("Testing F-String Parser...")
    
    # Test 1: Simple f-string
    print("\n1. Testing simple f-string parsing:")
    code = 'f"Hello, {name}!"'
    lexer = Lexer(code)
    tokens = lexer.scan_tokens()
    parser = Parser(tokens)
    
    # Parse as expression
    ast = parser.expression()
    
    assert isinstance(ast, FStringExpression), f"Expected FStringExpression, got {type(ast)}"
    assert len(ast.parts) == 3
    assert ast.parts[0] == (True, 'Hello, ')
    assert ast.parts[0][0] == True  # is_literal
    assert isinstance(ast.parts[1][1], Identifier)  # expression
    assert ast.parts[1][1].name == 'name'
    assert ast.parts[2] == (True, '!')
    print("   ✓ Simple f-string parsed correctly")
    
    # Test 2: Expression in f-string
    print("\n2. Testing expression parsing:")
    code2 = 'f"Result: {x + y}"'
    lexer2 = Lexer(code2)
    tokens2 = lexer2.scan_tokens()
    parser2 = Parser(tokens2)
    ast2 = parser2.expression()
    
    assert isinstance(ast2, FStringExpression)
    assert len(ast2.parts) == 2
    print(f"   Parts: {ast2.parts}")
    print("   ✓ Expression f-string parsed")
    
    print("\n✅ All f-string parser tests passed!")

if __name__ == "__main__":
    test_fstring_parser()
