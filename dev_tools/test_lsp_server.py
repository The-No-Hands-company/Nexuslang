#!/usr/bin/env python3
"""
Comprehensive LSP Server Test
Tests server initialization, completions, hover, and all features
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from nlpl.lsp.server import NLPLLanguageServer, Position
from nlpl.lsp.completions import CompletionProvider
from nlpl.lsp.hover import HoverProvider
from nlpl.lsp.definitions import DefinitionProvider

def test_server_initialization():
    """Test server can initialize"""
    print("=" * 60)
    print("Test 1: Server Initialization")
    print("=" * 60)
    
    try:
        server = NLPLLanguageServer()
        print("✓ Server instance created successfully")
        
        # Test initialization
        init_params = {
            "capabilities": {
                "textDocument": {
                    "completion": {"dynamicRegistration": True},
                    "hover": {"dynamicRegistration": True},
                    "definition": {"dynamicRegistration": True}
                }
            }
        }
        
        response = server._handle_initialize(1, init_params)
        print(f"✓ Initialize response received")
        print(f"  Capabilities: {list(response['result']['capabilities'].keys())[:5]}...")
        
        return server
    except Exception as e:
        print(f"✗ Server initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_completions(server):
    """Test completion provider"""
    print("\n" + "=" * 60)
    print("Test 2: Completion Provider")
    print("=" * 60)
    
    test_cases = [
        {
            "name": "Keyword completion",
            "text": "fun",
            "position": Position(line=0, character=3),
            "expected_keywords": ["function"]
        },
        {
            "name": "Type completion after 'as'",
            "text": "set x as Int",
            "position": Position(line=0, character=12),
            "expected_keywords": ["Integer", "IntRange"]
        },
        {
            "name": "Stdlib completion",
            "text": "import math\nset result to sq",
            "position": Position(line=1, character=18),
            "expected_keywords": ["sqrt", "square_root"]
        },
        {
            "name": "Context after 'set x to'",
            "text": "set value to ",
            "position": Position(line=0, character=13),
            "expected_keywords": ["true", "false", "new"]
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest 2.{i}: {test['name']}")
        print(f"  Text: {repr(test['text'])}")
        print(f"  Position: line {test['position'].line}, char {test['position'].character}")
        
        try:
            completions = server.completion_provider.get_completions(
                test['text'], 
                test['position']
            )
            
            if completions:
                labels = [c['label'] for c in completions[:10]]
                print(f"  ✓ Got {len(completions)} completions")
                print(f"  Top suggestions: {labels}")
                
                # Check if expected keywords are present
                found = [kw for kw in test['expected_keywords'] if kw in labels]
                if found:
                    print(f"  ✓ Expected keywords found: {found}")
                else:
                    print(f"  ⚠ Expected keywords not in top 10: {test['expected_keywords']}")
            else:
                print(f"  ⚠ No completions returned")
                
        except Exception as e:
            print(f"  ✗ Error: {e}")
            import traceback
            traceback.print_exc()


def test_hover(server):
    """Test hover provider"""
    print("\n" + "=" * 60)
    print("Test 3: Hover Provider")
    print("=" * 60)
    
    test_cases = [
        {
            "name": "Hover over keyword 'function'",
            "text": "function calculate with x as Integer",
            "position": Position(line=0, character=2)
        },
        {
            "name": "Hover over stdlib function 'sqrt'",
            "text": "import math\nset result to sqrt with 16.0",
            "position": Position(line=1, character=16)
        },
        {
            "name": "Hover over user function",
            "text": "function add with a as Integer, b as Integer returns Integer\n  return a plus b\nend\nset x to add with 1, 2",
            "position": Position(line=3, character=10)
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest 3.{i}: {test['name']}")
        print(f"  Text: {repr(test['text'][:50])}...")
        print(f"  Position: line {test['position'].line}, char {test['position'].character}")
        
        try:
            hover_info = server.hover_provider.get_hover(test['text'], test['position'])
            
            if hover_info:
                content = hover_info.get('contents', {})
                if isinstance(content, dict):
                    value = content.get('value', '')
                elif isinstance(content, str):
                    value = content
                else:
                    value = str(content)
                    
                print(f"  ✓ Hover info returned")
                print(f"  Content preview: {value[:100]}")
            else:
                print(f"  ⚠ No hover info returned")
                
        except Exception as e:
            print(f"  ✗ Error: {e}")


def test_goto_definition(server):
    """Test go-to-definition"""
    print("\n" + "=" * 60)
    print("Test 4: Go-to-Definition")
    print("=" * 60)
    
    test_code = """function calculate with x as Integer returns Integer
  return x times 2
end

set result to calculate with 5
"""
    
    # Test jumping to 'calculate' function definition
    print("\nTest 4.1: Jump to function definition")
    print(f"  Text: {repr(test_code[:50])}...")
    print(f"  Cursor on 'calculate' at line 4")
    
    try:
        uri = "file:///test.nlpl"
        server.documents[uri] = test_code
        
        location = server.definition_provider.get_definition(
            test_code,
            Position(line=4, character=16),  # Position of 'calculate' in call
            uri
        )
        
        if location:
            print(f"  ✓ Definition found")
            # location is a Location object, convert to dict
            loc_dict = location.to_dict() if hasattr(location, 'to_dict') else location
            if isinstance(loc_dict, dict):
                print(f"  Location: Line {loc_dict['range']['start']['line']}, "
                      f"Char {loc_dict['range']['start']['character']}")
            else:
                print(f"  Location object: {type(location)}")
        else:
            print(f"  ⚠ Definition not found")
            
    except Exception as e:
        print(f"  ✗ Error: {e}")


def test_diagnostics_detailed(server):
    """Test diagnostics with various error types"""
    print("\n" + "=" * 60)
    print("Test 5: Detailed Diagnostics")
    print("=" * 60)
    
    test_cases = [
        {
            "name": "Syntax error",
            "code": 'set x to "unclosed string',
            "expected": "Unterminated string"
        },
        {
            "name": "Unused variable",
            "code": "set unused to 42",
            "expected": "Unused variable"
        },
        {
            "name": "Type error",
            "code": """function add with a as Integer, b as Integer returns String
  return a plus b
end""",
            "expected": "Type error"
        },
        {
            "name": "Valid code (no errors)",
            "code": """set x to 10
print text x to_string""",
            "expected": None
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest 5.{i}: {test['name']}")
        print(f"  Code: {repr(test['code'][:50])}...")
        
        try:
            uri = f"file:///test{i}.nlpl"
            diagnostics = server.diagnostics_provider.get_diagnostics(uri, test['code'])
            
            if test['expected'] is None:
                if not diagnostics:
                    print(f"  ✓ No diagnostics (as expected)")
                else:
                    print(f"  ⚠ Unexpected diagnostics: {len(diagnostics)}")
                    for d in diagnostics:
                        print(f"    - {d['message']}")
            else:
                if diagnostics:
                    found = any(test['expected'].lower() in d['message'].lower() 
                              for d in diagnostics)
                    if found:
                        print(f"  ✓ Expected error found: '{test['expected']}'")
                        print(f"    Total diagnostics: {len(diagnostics)}")
                    else:
                        print(f"  ⚠ Expected '{test['expected']}' not found")
                        print(f"    Got: {[d['message'][:50] for d in diagnostics]}")
                else:
                    print(f"  ⚠ No diagnostics returned (expected: {test['expected']})")
                    
        except Exception as e:
            print(f"  ✗ Error: {e}")


def test_code_actions(server):
    """Test code actions/quick fixes"""
    print("\n" + "=" * 60)
    print("Test 6: Code Actions (Quick Fixes)")
    print("=" * 60)
    
    test_code = """set unused_var to 42
set message to "unclosed string
"""
    
    print(f"Code: {repr(test_code)}")
    
    try:
        uri = "file:///test_actions.nlpl"
        diagnostics = server.diagnostics_provider.get_diagnostics(uri, test_code)
        
        print(f"✓ Diagnostics found: {len(diagnostics)}")
        for d in diagnostics:
            print(f"  - {d['message']}")
        
        actions = server.code_actions_provider.get_code_actions(
            uri,
            test_code,
            {"start": {"line": 0, "character": 0}, "end": {"line": 2, "character": 0}},
            diagnostics
        )
        
        if actions:
            print(f"✓ Code actions available: {len(actions)}")
            for action in actions:
                print(f"  - {action['title']} (kind: {action.get('kind', 'unknown')})")
        else:
            print(f"⚠ No code actions returned")
            
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()


def test_signature_help(server):
    """Test signature help"""
    print("\n" + "=" * 60)
    print("Test 7: Signature Help")
    print("=" * 60)
    
    test_code = """function calculate with x as Integer, y as Integer returns Integer
  return x plus y
end

set result to calculate with 10, """
    
    print(f"Code: {repr(test_code[:60])}...")
    print(f"Cursor position: Inside function call")
    
    try:
        sig_help = server.signature_help_provider.get_signature_help(
            test_code,
            Position(line=4, character=33)  # After the comma
        )
        
        if sig_help:
            print(f"✓ Signature help returned")
            signatures = sig_help.get('signatures', [])
            if signatures:
                sig = signatures[0]
                print(f"  Signature: {sig.get('label', 'N/A')}")
                print(f"  Active parameter: {sig_help.get('activeParameter', 0)}")
                params = sig.get('parameters', [])
                if params:
                    print(f"  Parameters: {[p.get('label', 'N/A') for p in params]}")
        else:
            print(f"⚠ No signature help returned")
            
    except Exception as e:
        print(f"✗ Error: {e}")


def run_all_tests():
    """Run all LSP tests"""
    print("\n" + "=" * 70)
    print(" NLPL LSP Server - Comprehensive Test Suite")
    print("=" * 70 + "\n")
    
    # Initialize server
    server = test_server_initialization()
    if not server:
        print("\n✗ Server initialization failed, aborting tests")
        return False
    
    # Run all tests
    test_completions(server)
    test_hover(server)
    test_goto_definition(server)
    test_diagnostics_detailed(server)
    test_code_actions(server)
    test_signature_help(server)
    
    print("\n" + "=" * 70)
    print(" Test Suite Complete")
    print("=" * 70 + "\n")
    
    return True


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
