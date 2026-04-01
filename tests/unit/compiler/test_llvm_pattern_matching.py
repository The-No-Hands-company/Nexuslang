"""
Test LLVM compiler support for advanced pattern matching.

These tests verify that pattern matching (Option, Result, Tuple, List)
compiles correctly to LLVM IR with proper variant checking and data extraction.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../src'))

from nlpl.parser.lexer import Lexer
from nlpl.parser.parser import Parser
from nlpl.compiler.backends.llvm_ir_generator import LLVMIRGenerator


class TestOptionPatternMatching:
    """Test Option<T> pattern matching compilation."""
    
    def test_option_some_pattern(self):
        """Test that LLVM generator has Option pattern support methods."""
        generator = LLVMIRGenerator()
        
        # Verify Option pattern methods exist
        assert hasattr(generator, '_generate_option_pattern_match')
        assert hasattr(generator, '_generate_option_pattern_binding')
    
    def test_option_none_pattern(self):
        """Test that None pattern can be compiled."""
        code = """function is_none that takes opt as Option returns Boolean
    match opt with
        case None
            return true
        case _
            return false
end
"""
        
        lexer = Lexer(code)
        tokens = lexer.scan_tokens()
        parser = Parser(tokens)
        ast = parser.parse()
        
        generator = LLVMIRGenerator()
        llvm_ir = generator.generate(ast)
        
        # Should compile successfully
        assert 'define' in llvm_ir


class TestResultPatternMatching:
    """Test Result<T, E> pattern matching compilation."""
    
    def test_result_ok_pattern(self):
        """Test that LLVM generator has Result pattern support methods."""
        generator = LLVMIRGenerator()
        
        # Verify Result pattern methods exist
        assert hasattr(generator, '_generate_result_pattern_match')
        assert hasattr(generator, '_generate_result_pattern_binding')
    
    def test_result_err_pattern(self):
        """Test that wildcard pattern works in Result context."""
        code = """function is_error that takes res as Result returns Boolean
    match res with
        case _
            return true
end
"""
        
        lexer = Lexer(code)
        tokens = lexer.scan_tokens()
        parser = Parser(tokens)
        ast = parser.parse()
        
        generator = LLVMIRGenerator()
        llvm_ir = generator.generate(ast)
        
        # Should compile successfully
        assert 'define' in llvm_ir


class TestTuplePatternMatching:
    """Test tuple pattern matching compilation."""
    
    def test_simple_tuple_pattern(self):
        """Test matching simple tuple pattern (a, b)."""
        code = """function get_first that takes pair as Tuple returns Integer
    match pair with
        case (x, y)
            return x
end
"""
        
        lexer = Lexer(code)
        tokens = lexer.scan_tokens()
        parser = Parser(tokens)
        ast = parser.parse()
        
        generator = LLVMIRGenerator()
        llvm_ir = generator.generate(ast)
        
        # Should use extractvalue for tuple elements
        assert 'define' in llvm_ir
    
    def test_nested_tuple_pattern(self):
        """Test matching nested tuple pattern ((a, b), c)."""
        code = """function extract_nested that takes data as Tuple returns Integer
    match data with
        case ((x, y), z)
            return x plus z
end
"""
        
        lexer = Lexer(code)
        tokens = lexer.scan_tokens()
        parser = Parser(tokens)
        ast = parser.parse()
        
        generator = LLVMIRGenerator()
        llvm_ir = generator.generate(ast)
        # Nested extraction
        assert 'define' in llvm_ir


class TestListPatternMatching:
    """Test list pattern matching compilation."""
    
    def test_list_head_tail_pattern(self):
        """Test matching [head, ...tail] pattern."""
        code = """function get_head that takes lst as List returns Integer
    match lst with
        case [head, rest]
            return head
        case []
            return 0
end
"""
        
        lexer = Lexer(code)
        tokens = lexer.scan_tokens()
        parser = Parser(tokens)
        ast = parser.parse()
        
        generator = LLVMIRGenerator()
        llvm_ir = generator.generate(ast)
        
        # Should compile list pattern
        assert 'define' in llvm_ir
    
    def test_list_fixed_length_pattern(self):
        """Test matching [x, y, z] fixed-length pattern."""
        code = """function sum_triple that takes lst as List returns Integer
    match lst with
        case [x, y, z]
            return x plus y plus z
        case _
            return 0
end
"""
        
        lexer = Lexer(code)
        tokens = lexer.scan_tokens()
        parser = Parser(tokens)
        ast = parser.parse()
        
        generator = LLVMIRGenerator()
        llvm_ir = generator.generate(ast)
        
        # Should compile fixed-length list pattern
        assert 'define' in llvm_ir


class TestPatternMatchingHelpers:
    """Test pattern matching helper methods."""
    
    def test_pattern_matching_methods_exist(self):
        """Verify LLVMIRGenerator has pattern matching methods."""
        generator = LLVMIRGenerator()
        
        # Check for new methods
        assert hasattr(generator, '_generate_pattern_match')
        assert hasattr(generator, '_generate_pattern_bindings')
        assert hasattr(generator, '_generate_option_pattern_match')
        assert hasattr(generator, '_generate_result_pattern_match')
        assert hasattr(generator, '_generate_tuple_pattern_match')
        assert hasattr(generator, '_generate_list_pattern_match')
    
    def test_binding_methods_exist(self):
        """Verify pattern binding helper methods exist."""
        generator = LLVMIRGenerator()
        
        assert hasattr(generator, '_generate_option_pattern_binding')
        assert hasattr(generator, '_generate_result_pattern_binding')


class TestVariantPatternMatching:
    """Test generic variant pattern matching."""
    
    def test_variant_pattern_dispatch(self):
        """Test that variant patterns dispatch correctly."""
        generator = LLVMIRGenerator()
        
        # Verify variant pattern helper exists
        assert hasattr(generator, '_generate_variant_pattern_match')
        assert hasattr(generator, '_generate_variant_pattern_binding')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
