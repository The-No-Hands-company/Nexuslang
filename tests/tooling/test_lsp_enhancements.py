"""
Test LSP Enhancements
=====================

Tests for all LSP provider enhancements:
- References provider (find all references)
- Enhanced definitions provider (cross-file, imports)
- Enhanced hover provider (stdlib docs, parameters)
- Enhanced completions provider (context-aware)
- Enhanced symbols provider (fuzzy matching)
"""

import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from nexuslang.lsp.server import NLPLLanguageServer, Position
from nexuslang.lsp.references import ReferencesProvider
from nexuslang.lsp.definitions import DefinitionProvider
from nexuslang.lsp.hover import HoverProvider
from nexuslang.lsp.completions import CompletionProvider
from nexuslang.lsp.symbols import SymbolProvider


class TestReferencesProvider:
    """Test find-all-references functionality."""
    
    def test_find_function_references(self):
        """Test finding all references to a function."""
        server = NLPLLanguageServer()
        provider = ReferencesProvider(server)
        
        code = """
function calculate that takes x as Integer returns Integer
    return x times 2

set result to calculate with 5
set another to calculate with 10
"""
        
        server.documents["test.nxl"] = code
        
        # Find references to "calculate" at line 1
        position = Position(1, 10)  # on "calculate"
        refs = provider.find_references(code, position, "test.nxl", include_declaration=True)
        
        # Should find: 1 definition + 2 calls = 3 references
        assert len(refs) >= 2, f"Expected at least 2 references, got {len(refs)}"
        
        # Check that we found the calls
        call_lines = [ref["range"]["start"]["line"] for ref in refs]
        assert 4 in call_lines or 5 in call_lines, "Should find function calls"
    
    def test_find_variable_references(self):
        """Test finding all references to a variable."""
        server = NLPLLanguageServer()
        provider = ReferencesProvider(server)
        
        code = """
set counter to 0
set counter to counter plus 1
set doubled to counter times 2
"""
        
        server.documents["test.nxl"] = code
        
        # Find references to "counter" at line 1
        position = Position(1, 5)  # on "counter"
        refs = provider.find_references(code, position, "test.nxl", include_declaration=True)
        
        # Should find: 1 assignment + 2 usages = 3 references
        assert len(refs) >= 2, f"Expected at least 2 references, got {len(refs)}"
    
    def test_find_class_references(self):
        """Test finding all references to a class."""
        server = NLPLLanguageServer()
        provider = ReferencesProvider(server)
        
        code = """
class Person
    property name as String

set p1 to new Person
set p2 as Person to new Person
"""
        
        server.documents["test.nxl"] = code
        
        # Find references to "Person" at line 1
        position = Position(1, 7)  # on "Person"
        refs = provider.find_references(code, position, "test.nxl", include_declaration=True)
        
        # Should find: 1 definition + 2+ instantiations
        assert len(refs) >= 2, f"Expected at least 2 references, got {len(refs)}"


class TestEnhancedDefinitions:
    """Test enhanced go-to-definition functionality."""
    
    def test_find_function_definition(self):
        """Test finding function definition."""
        server = NLPLLanguageServer()
        provider = DefinitionProvider(server)
        
        code = """
function helper that takes x as Integer returns Integer
    return x times 2

set result to helper with 5
"""
        
        server.documents["test.nxl"] = code
        
        # Go to definition of "helper" at line 4
        position = Position(4, 15)  # on "helper"
        location = provider.get_definition(code, position, "test.nxl")
        
        assert location is not None, "Should find function definition"
        assert location.range.start.line == 1, "Should point to function definition line"
    
    def test_find_method_definition(self):
        """Test finding method definition."""
        server = NLPLLanguageServer()
        provider = DefinitionProvider(server)
        
        code = """
class Calculator
    method add that takes x as Integer, y as Integer returns Integer
        return x plus y

set calc to new Calculator
set sum to call add on calc with 1, 2
"""
        
        server.documents["test.nxl"] = code
        
        # Go to definition of "add" at line 6
        position = Position(6, 18)  # on "add"
        location = provider.get_definition(code, position, "test.nxl")
        
        assert location is not None, "Should find method definition"
        assert location.range.start.line == 2, "Should point to method definition line"
    
    def test_find_variable_definition(self):
        """Test finding variable definition (closest before usage)."""
        server = NLPLLanguageServer()
        provider = DefinitionProvider(server)
        
        code = """
set counter to 0
set counter to counter plus 1
set doubled to counter times 2
"""
        
        server.documents["test.nxl"] = code
        
        # Go to definition of "counter" at line 3
        position = Position(3, 16)  # on "counter" in "counter times 2"
        location = provider.get_definition(code, position, "test.nxl")
        
        assert location is not None, "Should find variable definition"
        # Should point to the closest assignment before line 3
        assert location.range.start.line in [1, 2], "Should point to variable assignment"


class TestEnhancedHover:
    """Test enhanced hover documentation."""
    
    def test_hover_stdlib_function(self):
        """Test hover on stdlib function."""
        server = NLPLLanguageServer()
        provider = HoverProvider(server)
        
        code = """
set result to sqrt with 16
"""
        
        # Hover over "sqrt"
        position = Position(1, 15)  # on "sqrt"
        hover = provider.get_hover(code, position)
        
        assert hover is not None, "Should provide hover info for sqrt"
        assert "sqrt" in hover["contents"]["value"], "Should contain function name"
        assert "math" in hover["contents"]["value"], "Should mention math module"
    
    def test_hover_function_with_parameters(self):
        """Test hover on function shows parameters."""
        server = NLPLLanguageServer()
        provider = HoverProvider(server)
        
        code = """
function calculate that takes x as Integer, y as Float returns Float
    return x plus y

set result to calculate with 5, 3.14
"""
        
        # Hover over "calculate" at line 4 (call site)
        position = Position(4, 15)  # on "calculate"
        hover = provider.get_hover(code, position)
        
        assert hover is not None, "Should provide hover info"
        content = hover["contents"]["value"]
        assert "calculate" in content, "Should contain function name"
        assert "Parameters" in content or "parameter" in content.lower(), "Should list parameters"
    
    def test_hover_variable_with_type(self):
        """Test hover on variable shows type."""
        server = NLPLLanguageServer()
        provider = HoverProvider(server)
        
        code = """
set counter as Integer to 0
"""
        
        # Hover over "counter"
        position = Position(1, 5)  # on "counter"
        hover = provider.get_hover(code, position)
        
        assert hover is not None, "Should provide hover info"
        content = hover["contents"]["value"]
        assert "counter" in content, "Should contain variable name"
        assert "Integer" in content, "Should show type"


class TestEnhancedCompletions:
    """Test enhanced auto-completion."""
    
    def test_context_after_set_to(self):
        """Test completions after 'set X to'."""
        server = NLPLLanguageServer()
        provider = CompletionProvider(server)
        
        code = "set result to "
        position = Position(0, 14)  # after "to "
        
        completions = provider.get_completions(code, position)
        
        # Should suggest values: true, false, null, create, new
        labels = [c["label"] for c in completions]
        assert any("true" in label.lower() for label in labels), "Should suggest true"
        assert any("false" in label.lower() for label in labels), "Should suggest false"
        assert any("create" in label.lower() for label in labels), "Should suggest create"
    
    def test_context_after_as(self):
        """Test type completions after 'as'."""
        server = NLPLLanguageServer()
        provider = CompletionProvider(server)
        
        code = "set value as "
        position = Position(0, 13)  # after "as "
        
        completions = provider.get_completions(code, position)
        
        # Should suggest types
        labels = [c["label"] for c in completions]
        assert "Integer" in labels, "Should suggest Integer"
        assert "Float" in labels, "Should suggest Float"
        assert "String" in labels, "Should suggest String"
    
    def test_context_after_import(self):
        """Test module completions after 'import'."""
        server = NLPLLanguageServer()
        provider = CompletionProvider(server)
        
        code = "import "
        position = Position(0, 7)  # after "import "
        
        completions = provider.get_completions(code, position)
        
        # Should suggest stdlib modules
        labels = [c["label"] for c in completions]
        assert "math" in labels, "Should suggest math module"
        assert "string" in labels, "Should suggest string module"
        assert "io" in labels, "Should suggest io module"
    
    def test_variable_completion_from_scope(self):
        """Test variable completion from current document."""
        server = NLPLLanguageServer()
        provider = CompletionProvider(server)
        
        code = """
set counter to 0
set result to coun
"""
        
        position = Position(2, 19)  # after "coun"
        
        completions = provider.get_completions(code, position)
        
        # Should suggest "counter" variable
        labels = [c["label"] for c in completions]
        assert "counter" in labels, "Should suggest counter variable"
    
    def test_function_completion_from_scope(self):
        """Test function completion from current document."""
        server = NLPLLanguageServer()
        provider = CompletionProvider(server)
        
        code = """
function calculate that takes x as Integer returns Integer
    return x times 2

set result to calc
"""
        
        position = Position(4, 19)  # after "calc"
        
        completions = provider.get_completions(code, position)
        
        # Should suggest "calculate" function
        labels = [c["label"] for c in completions]
        assert "calculate" in labels, "Should suggest calculate function"
    
    def test_class_completion_from_scope(self):
        """Test class completion from current document."""
        server = NLPLLanguageServer()
        provider = CompletionProvider(server)
        
        code = """
class Person
    property name as String

set p to new Per
"""
        
        position = Position(4, 16)  # after "Per"
        
        completions = provider.get_completions(code, position)
        
        # Should suggest "Person" class
        labels = [c["label"] for c in completions]
        assert "Person" in labels, "Should suggest Person class"

    def test_channel_completion_after_create(self):
        """Test channel completion after 'create'."""
        server = NLPLLanguageServer()
        provider = CompletionProvider(server)

        code = "set ch to create "
        position = Position(0, len(code))

        completions = provider.get_completions(code, position)
        labels = [c["label"] for c in completions]
        assert "channel" in labels, "Should suggest channel after create"

    def test_channel_type_completion_after_as(self):
        """Test channel type completion after 'as'."""
        server = NLPLLanguageServer()
        provider = CompletionProvider(server)

        code = "set ch as "
        position = Position(0, len(code))

        completions = provider.get_completions(code, position)
        labels = [c["label"] for c in completions]
        assert "Channel" in labels, "Should suggest Channel type"

    def test_channel_hover_keyword_docs(self):
        """Test hover docs for channel keyword."""
        server = NLPLLanguageServer()
        provider = HoverProvider(server)

        code = "set ch to create channel"
        position = Position(0, code.find("channel") + 1)

        hover = provider.get_hover(code, position)
        assert hover is not None, "Should provide hover info for channel"
        content = hover["contents"]["value"]
        assert "message passing" in content.lower()


class TestEnhancedSymbols:
    """Test enhanced symbol search."""
    
    def test_fuzzy_match_exact(self):
        """Test exact match."""
        provider = SymbolProvider(None)
        
        assert provider._fuzzy_match("calc", "calculate")
        assert provider._fuzzy_match("Calculate", "calculate")
    
    def test_fuzzy_match_subsequence(self):
        """Test fuzzy subsequence matching."""
        provider = SymbolProvider(None)
        
        # "cae" matches "calculate" (c-a-lcul-a-t-e)
        assert provider._fuzzy_match("cae", "calculate")
        
        # "hf" matches "helper_function" (h-elper_-f-unction)
        assert provider._fuzzy_match("hf", "helper_function")
    
    def test_fuzzy_match_score(self):
        """Test fuzzy match scoring."""
        provider = SymbolProvider(None)
        
        # Exact match should score highest
        exact_score = provider._fuzzy_match_score("calc", "calc")
        assert exact_score == 1.0
        
        # Substring should score high
        substring_score = provider._fuzzy_match_score("calc", "calculate")
        assert substring_score > 0.8
        
        # Prefix should score high
        prefix_score = provider._fuzzy_match_score("cal", "calculate")
        assert prefix_score > 0.7
    
    def test_find_symbols_with_fuzzy(self):
        """Test symbol search with fuzzy matching."""
        server = NLPLLanguageServer()
        provider = SymbolProvider(server)
        
        code = """
function calculate_average that takes nums as List returns Float
    return 0.0

function helper_function that takes x as Integer returns Integer
    return x

class DataProcessor
    property data as List
"""
        
        server.documents["test.nxl"] = code
        
        # Search with "ca" should find "calculate_average"
        symbols = provider.find_symbols("ca", server.documents)
        names = [s["name"] for s in symbols]
        assert "calculate_average" in names, "Should find calculate_average"
        
        # Search with "hf" should find "helper_function"
        symbols = provider.find_symbols("hf", server.documents)
        names = [s["name"] for s in symbols]
        assert "helper_function" in names, "Should find helper_function via fuzzy match"
    
    def test_find_symbols_sorted_by_relevance(self):
        """Test that symbols are sorted by relevance."""
        server = NLPLLanguageServer()
        provider = SymbolProvider(server)
        
        code = """
function calculate that takes x as Integer returns Integer
    return x

function calculate_average that takes nums as List returns Float
    return 0.0

function calibrate that takes val as Float returns Float
    return val
"""
        
        server.documents["test.nxl"] = code
        
        # Search for "cal" - should find all three
        symbols = provider.find_symbols("cal", server.documents)
        
        assert len(symbols) >= 3, f"Should find at least 3 symbols, found {len(symbols)}"
        
        # First result should be "calculate" (starts with "cal")
        # or one of the exact prefix matches
        first_name = symbols[0]["name"]
        assert first_name in ["calculate", "calculate_average", "calibrate"], \
            f"First result should start with 'cal', got {first_name}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
