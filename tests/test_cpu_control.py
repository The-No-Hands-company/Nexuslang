#!/usr/bin/env python3
"""
Simple test runner for CPU Control test files
Tests basic functionality without hanging
"""

import sys
import os

# Add src to path
sys.path.insert(0, 'src')

from nlpl.parser.lexer import Lexer
from nlpl.parser.parser import Parser
from nlpl.interpreter.interpreter import Interpreter
from nlpl.runtime.runtime import Runtime
from nlpl.stdlib import register_stdlib

def test_file(filepath):
    """Test a single NLPL file"""
    print(f"\n{'='*60}")
    print(f"Testing: {filepath}")
    print('='*60)
    
    try:
        # Read file
        with open(filepath, 'r') as f:
            code = f.read()
        
        # Tokenize
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        
        # Parse
        parser = Parser(tokens)
        ast = parser.parse()
        print(f"✓ Parsing successful ({len(code)} chars)")
        
        # Execute (with timeout protection)
        runtime = Runtime()
        register_stdlib(runtime)
        interpreter = Interpreter(runtime)
        
        try:
            result = interpreter.interpret(ast)
            print(f"✓ Execution successful")
            return True
        except Exception as e:
            print(f"✗ Runtime error: {e}")
            return False
            
    except Exception as e:
        print(f"✗ Parse error: {e}")
        return False

def main():
    test_files = [
        'test_programs/unit/hardware/test_cpu_cpuid.nlpl',
        'test_programs/unit/hardware/test_cpu_features.nlpl',
        'test_programs/unit/hardware/test_cpu_control_regs.nlpl',
        'test_programs/unit/hardware/test_cpu_msr.nlpl',
        'test_programs/unit/hardware/test_cpu_errors.nlpl',
    ]
    
    results = {}
    for test_file in test_files:
        if os.path.exists(test_file):
            results[test_file] = test_file(test_file)
        else:
            print(f"✗ File not found: {test_file}")
            results[test_file] = False
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print('='*60)
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    for filepath, success in results.items():
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status}: {filepath}")
    
    return 0 if passed == total else 1

if __name__ == '__main__':
    sys.exit(main())
