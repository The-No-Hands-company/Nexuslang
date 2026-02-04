"""
Symbol Provider
===============

Provides symbol search functionality using AST-based analysis.
"""

from typing import List, Dict, Optional
import re
from ..parser.lexer import Lexer
from ..parser.parser import Parser
from ..analysis import ASTSymbolExtractor, SymbolTable, SymbolKind


class SymbolProvider:
    """
    Provides workspace symbol search using AST-based symbol resolution.
    
    Symbol types:
    - Functions
    - Classes
    - Variables
    - Imports
    - Methods
    - Structs
    - Enums
    
    Features:
    - Fuzzy matching
    - Symbol type filtering
    - Workspace-wide indexing
    - AST-based accuracy
    """
    
    def __init__(self, server):
        self.server = server
        # Cache symbol tables per document
        self.symbol_tables: Dict[str, SymbolTable] = {}
    
    def _get_or_build_symbol_table(self, text: str, uri: str) -> Optional[SymbolTable]:
        """Build symbol table from document text."""
        try:
            lexer = Lexer(text)
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            ast = parser.parse()
            
            extractor = ASTSymbolExtractor(uri)
            symbol_table = extractor.extract(ast)
            
            self.symbol_tables[uri] = symbol_table
            return symbol_table
        except Exception:
            return self.symbol_tables.get(uri, None)
    
    def _symbol_kind_to_lsp(self, kind: SymbolKind) -> int:
        """Convert SymbolKind to LSP symbol kind integer."""
        # LSP SymbolKind values
        mapping = {
            SymbolKind.FILE: 1,
            SymbolKind.MODULE: 2,
            SymbolKind.NAMESPACE: 3,
            SymbolKind.PACKAGE: 4,
            SymbolKind.CLASS: 5,
            SymbolKind.METHOD: 6,
            SymbolKind.PROPERTY: 7,
            SymbolKind.FIELD: 8,
            SymbolKind.CONSTRUCTOR: 9,
            SymbolKind.ENUM: 10,
            SymbolKind.INTERFACE: 11,
            SymbolKind.FUNCTION: 12,
            SymbolKind.VARIABLE: 13,
            SymbolKind.CONSTANT: 14,
            SymbolKind.STRUCT: 23,
            SymbolKind.ENUM_MEMBER: 22,
        }
        return mapping.get(kind, 13)  # Default to Variable
    
    def find_symbols(self, query: str, documents: Dict[str, str]) -> List[Dict]:
        """
        Find symbols matching query across workspace using AST-based resolution.
        
        Args:
            query: Search query (supports fuzzy matching)
            documents: Map of URI -> content
            
        Returns:
            List of symbol information
        """
        symbols = []
        
        for uri, text in documents.items():
            # Build symbol table
            symbol_table = self._get_or_build_symbol_table(text, uri)
            if not symbol_table:
                # Fallback to regex
                symbols.extend(self._fallback_find_symbols(text, uri, query))
                continue
            
            # Find matching symbols using fuzzy match
            matching_symbols = symbol_table.find_symbols_by_name(query, fuzzy=True)
            
            for symbol in matching_symbols:
                symbols.append({
                    "name": symbol.name,
                    "kind": self._symbol_kind_to_lsp(symbol.kind),
                    "location": {
                        "uri": symbol.location.uri,
                        "range": {
                            "start": {"line": symbol.location.line, "character": symbol.location.column},
                            "end": {"line": symbol.location.line, "character": symbol.location.column + len(symbol.name)}
                        }
                    },
                    "containerName": symbol.parent.name if symbol.parent else None
                })
        
        # Sort by relevance (fuzzy match score)
        symbols.sort(key=lambda s: self._fuzzy_match_score(query, s["name"]), reverse=True)
        
        return symbols
    
    def _fallback_find_symbols(self, text: str, uri: str, query: str) -> List[Dict]:
        """Fallback to regex-based symbol finding."""
        symbols = []
        
        # Find functions
        symbols.extend(self._find_functions(text, uri, query))
        
        # Find classes
        symbols.extend(self._find_classes(text, uri, query))
        
        # Find variables
        symbols.extend(self._find_variables(text, uri, query))
        
        # Find methods
        symbols.extend(self._find_methods(text, uri, query))
        
        return symbols
    
    def _find_functions(self, text: str, uri: str, query: str) -> List[Dict]:
        """Find function symbols."""
        symbols = []
        lines = text.split('\n')
        
        pattern = r'function\s+(\w+)'
        for i, line in enumerate(lines):
            matches = re.finditer(pattern, line, re.IGNORECASE)
            for match in matches:
                func_name = match.group(1)
                # Use fuzzy matching
                if self._fuzzy_match(query, func_name):
                    symbols.append({
                        "name": func_name,
                        "kind": 12,  # Function
                        "location": {
                            "uri": uri,
                            "range": {
                                "start": {"line": i, "character": match.start(1)},
                                "end": {"line": i, "character": match.end(1)}
                            }
                        }
                    })
        
        return symbols
    
    def _find_classes(self, text: str, uri: str, query: str) -> List[Dict]:
        """Find class symbols."""
        symbols = []
        lines = text.split('\n')
        
        pattern = r'class\s+(\w+)'
        for i, line in enumerate(lines):
            matches = re.finditer(pattern, line, re.IGNORECASE)
            for match in matches:
                class_name = match.group(1)
                if self._fuzzy_match(query, class_name):
                    symbols.append({
                        "name": class_name,
                        "kind": 5,  # Class
                        "location": {
                            "uri": uri,
                            "range": {
                                "start": {"line": i, "character": match.start(1)},
                                "end": {"line": i, "character": match.end(1)}
                            }
                        }
                    })
        
        return symbols
    
    def _find_variables(self, text: str, uri: str, query: str) -> List[Dict]:
        """Find variable symbols."""
        symbols = []
        lines = text.split('\n')
        
        pattern = r'set\s+(\w+)\s+to'
        for i, line in enumerate(lines):
            matches = re.finditer(pattern, line, re.IGNORECASE)
            for match in matches:
                var_name = match.group(1)
                if self._fuzzy_match(query, var_name):
                    symbols.append({
                        "name": var_name,
                        "kind": 13,  # Variable
                        "location": {
                            "uri": uri,
                            "range": {
                                "start": {"line": i, "character": match.start(1)},
                                "end": {"line": i, "character": match.end(1)}
                            }
                        }
                    })
        
        return symbols
    
    def _find_methods(self, text: str, uri: str, query: str) -> List[Dict]:
        """Find method symbols."""
        symbols = []
        lines = text.split('\n')
        
        pattern = r'method\s+(\w+)'
        for i, line in enumerate(lines):
            matches = re.finditer(pattern, line, re.IGNORECASE)
            for match in matches:
                method_name = match.group(1)
                if self._fuzzy_match(query, method_name):
                    symbols.append({
                        "name": method_name,
                        "kind": 6,  # Method
                        "location": {
                            "uri": uri,
                            "range": {
                                "start": {"line": i, "character": match.start(1)},
                                "end": {"line": i, "character": match.end(1)}
                            }
                        }
                    })
        
        return symbols
    
    def _fuzzy_match(self, query: str, target: str) -> bool:
        """Check if query fuzzy matches target."""
        if not query:
            return True
        
        query = query.lower()
        target = target.lower()
        
        # Exact substring match
        if query in target:
            return True
        
        # Fuzzy match: all query chars appear in order in target
        query_idx = 0
        for char in target:
            if query_idx < len(query) and char == query[query_idx]:
                query_idx += 1
        
        return query_idx == len(query)
    
    def _fuzzy_match_score(self, query: str, target: str) -> float:
        """Calculate fuzzy match score (0-1, higher is better)."""
        if not query:
            return 0.5
        
        query = query.lower()
        target = target.lower()
        
        # Exact match gets highest score
        if query == target:
            return 1.0
        
        # Exact substring match
        if query in target:
            return 0.9
        
        # Starts with query
        if target.startswith(query):
            return 0.8
        
        # Fuzzy match score based on character positions
        query_idx = 0
        total_distance = 0
        last_pos = -1
        
        for i, char in enumerate(target):
            if query_idx < len(query) and char == query[query_idx]:
                if last_pos >= 0:
                    total_distance += (i - last_pos - 1)
                last_pos = i
                query_idx += 1
        
        if query_idx != len(query):
            return 0.0  # Not all chars matched
        
        # Score based on how compact the match is
        compactness = 1.0 - (total_distance / len(target))
        return 0.5 + (compactness * 0.3)


__all__ = ['SymbolProvider']
