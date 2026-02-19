"""
Test f-string lexer implementation.
"""

import sys
sys.path.insert(0, '/run/media/zajferx/Data/dev/The-No-hands-Company/projects/Active/NLPL/src')

from nlpl.parser.lexer import Lexer, TokenType

def test_fstring_lexer():
    """Test lexer recognition of f-strings."""
    print("Testing F-String Lexer...")
    
    # Test 1: Simple f-string
    print("\n1. Testing simple f-string:")
    code = 'f"Hello, {name}!"'
    lexer = Lexer(code)
    tokens = lexer.scan_tokens()
    
    # Should have FSTRING_LITERAL token
    fstring_tokens = [t for t in tokens if t.type == TokenType.FSTRING_LITERAL]
    assert len(fstring_tokens) == 1, f"Expected 1 f-string token, got {len(fstring_tokens)}"
    
    parts = fstring_tokens[0].literal
    print(f"   Parts: {parts}")
    assert len(parts) == 3, f"Expected 3 parts, got {len(parts)}"
    assert parts[0] == ('literal', 'Hello, ', None)
    assert parts[1] == ('expr', 'name', None)
    assert parts[2] == ('literal', '!', None)
    print("    Simple f-string lexed correctly")
    
    # Test 2: Expression in f-string
    print("\n2. Testing expression in f-string:")
    code2 = 'f"Result: {x + y}"'
    lexer2 = Lexer(code2)
    tokens2 = lexer2.scan_tokens()
    
    fstring_tokens2 = [t for t in tokens2 if t.type == TokenType.FSTRING_LITERAL]
    parts2 = fstring_tokens2[0].literal
    print(f"   Parts: {parts2}")
    assert parts2[1] == ('expr', 'x + y', None)
    print("    Expression f-string lexed correctly")
    
    # Test 3: Multiple interpolations
    print("\n3. Testing multiple interpolations:")
    code3 = 'f"{a} + {b} = {a + b}"'
    lexer3 = Lexer(code3)
    tokens3 = lexer3.scan_tokens()
    
    fstring_tokens3 = [t for t in tokens3 if t.type == TokenType.FSTRING_LITERAL]
    parts3 = fstring_tokens3[0].literal
    print(f"   Parts: {parts3}")
    assert len(parts3) == 5
    print("    Multiple interpolations work")
    
    print("\n All f-string lexer tests passed!")

if __name__ == "__main__":
    test_fstring_lexer()
