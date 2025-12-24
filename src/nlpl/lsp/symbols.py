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
    """
    
    def __init__(self, server):
        self.server = server
    
    def find_symbols(self, query: str, documents: Dict[str, str]) -> List[Dict]:
        """
        Find symbols matching query across workspace.
        
        Args:
            query: Search query
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
                if query.lower() in func_name.lower():
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
                if query.lower() in class_name.lower():
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
                if query.lower() in var_name.lower():
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


__all__ = ['SymbolProvider']
