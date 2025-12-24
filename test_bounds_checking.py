#!/usr/bin/env python3
"""
Test runner for enhanced bounds checking implementation.
Tests all three phases of the bounds checking feature.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from nlpl.parser.lexer import Lexer
from nlpl.parser.parser import Parser
from nlpl.compiler.backends.llvm_ir_generator import LLVMIRGenerator

def test_file(filepath, optimization=False):
    """Compile a test file and return success status."""
    try:
        with open(filepath, 'r') as f:
            code = f.read()
        
        # Compile
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        generator = LLVMIRGenerator()
        generator.enable_bounds_check_optimization = optimization
        ir = generator.generate(ast)
        
        lines = len(ir.split('\n'))
        return True, lines, None
    except Exception as e:
        return False, 0, str(e)

def main():
    print("=" * 60)
    print("Enhanced Bounds Checking - Test Suite")
    print("=" * 60)
    
    tests = [
        ("Phase 1: Runtime Size Tracking", "tests/test_phase1_verify.nlpl", False),
        ("Phase 1: Array Operations", "tests/test_array_ops_runtime.nlpl", False),
        ("Phase 2: Parameter Annotations", "tests/test_phase2_params.nlpl", False),
        ("Phase 3a: Constant Optimization", "tests/test_phase3_optimization.nlpl", True),
        ("Phase 3b: Loop Optimization", "tests/test_phase3b_loops.nlpl", True),
        ("Phase 3c: Guard Detection", "tests/test_phase3c_guards.nlpl", True),
    ]
    
    passed = 0
    failed = 0
    
    for name, filepath, opt in tests:
        print(f"\n{name}...")
        if not os.path.exists(filepath):
            print(f"  ✗ File not found: {filepath}")
            failed += 1
            continue
        
        success, lines, error = test_file(filepath, opt)
        if success:
            opt_str = " (optimized)" if opt else ""
            print(f"  ✓ Compiled successfully{opt_str}")
            print(f"    Generated {lines} lines of LLVM IR")
            passed += 1
        else:
            print(f"  ✗ Compilation failed: {error}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
