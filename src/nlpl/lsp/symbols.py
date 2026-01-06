"""
Symbol Provider
===============

Provides symbol search functionality.
"""

from typing import List, Dict
import re


class SymbolProvider:
    """
    Provides workspace symbol search.
    
    Symbol types:
    - Functions
    - Classes
    - Variables
    - Imports
    
    Features:
    - Fuzzy matching
    - Symbol type filtering
    - Workspace-wide indexing
    """
    
    def __init__(self, server):
        self.server = server
    
    def find_symbols(self, query: str, documents: Dict[str, str]) -> List[Dict]:
        """
        Find symbols matching query across workspace.
        
        Args:
            query: Search query (supports fuzzy matching)
            documents: Map of URI -> content
            
        Returns:
            List of symbol information
        """
        symbols = []
        
        for uri, text in documents.items():
            # Find functions
            symbols.extend(self._find_functions(text, uri, query))
            
            # Find classes
            symbols.extend(self._find_classes(text, uri, query))
            
            # Find variables
            symbols.extend(self._find_variables(text, uri, query))
            
            # Find methods
            symbols.extend(self._find_methods(text, uri, query))
        
        # Sort by relevance (fuzzy match score)
        symbols.sort(key=lambda s: self._fuzzy_match_score(query, s["name"]), reverse=True)
        
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
