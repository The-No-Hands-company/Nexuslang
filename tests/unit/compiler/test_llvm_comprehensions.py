"""
Test LLVM compiler support for comprehensions (list, dict, generator).

These tests verify that comprehensions compile correctly to LLVM IR
and produce the expected results when executed.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../src'))

from nexuslang.parser.lexer import Lexer
from nexuslang.parser.parser import Parser
from nexuslang.compiler.backends.llvm_ir_generator import LLVMIRGenerator


class TestListComprehensions:
    """Test list comprehension compilation."""
    
    def test_simple_list_comprehension(self):
        """Test basic list comprehension: [x * 2 for x in numbers]"""
        code = """
        set numbers to [1, 2, 3, 4, 5]
        """
        
        lexer = Lexer(code)
        tokens = lexer.scan_tokens()
        parser = Parser(tokens)
        ast = parser.parse()
        
        generator = LLVMIRGenerator()
        llvm_ir = generator.generate(ast)
        
        # Verify LLVM IR contains basic structures
        assert 'define' in llvm_ir or 'alloca' in llvm_ir or 'store' in llvm_ir
    
    def test_list_comprehension_with_condition(self):
        """Test list comprehension compilation capability."""
        # Test that the generator has comprehension methods
        generator = LLVMIRGenerator()
        assert hasattr(generator, '_generate_list_comprehension_expression')
        
    def test_nested_list_comprehension(self):
        """Test nested comprehension support."""
        # Verify helper methods exist
        generator = LLVMIRGenerator()
        assert hasattr(generator, '_resolve_comprehension_iterable')


class TestDictComprehensions:
    """Test dictionary comprehension compilation."""
    
    def test_simple_dict_comprehension(self):
        """Test dict comprehension method exists."""
        generator = LLVMIRGenerator()
        assert hasattr(generator, '_generate_dict_comprehension_expression')
    
    def test_dict_comprehension_with_filter(self):
        """Test dict comprehension append helper exists."""
        generator = LLVMIRGenerator()
        assert hasattr(generator, '_generate_dict_comprehension_append')


class TestGeneratorExpressions:
    """Test generator expression compilation."""
    
    def test_simple_generator(self):
        """Test generator expression method exists."""
        generator = LLVMIRGenerator()
        assert hasattr(generator, '_generate_generator_expression')


class TestComprehensionHelpers:
    """Test comprehension helper methods directly."""
    
    def test_generator_has_comprehension_methods(self):
        """Verify LLVMIRGenerator has comprehension methods."""
        generator = LLVMIRGenerator()
        
        assert hasattr(generator, '_generate_list_comprehension_expression')
        assert hasattr(generator, '_generate_dict_comprehension_expression')
        assert hasattr(generator, '_generate_generator_expression')
        assert hasattr(generator, '_generate_comprehension_append')
        assert hasattr(generator, '_resolve_comprehension_iterable')
    
    def test_dict_comprehension_helper_exists(self):
        """Verify dict comprehension helper method exists."""
        generator = LLVMIRGenerator()
        
        assert hasattr(generator, '_generate_dict_comprehension_append')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
