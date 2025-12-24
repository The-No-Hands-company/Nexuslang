"""
Definition Provider
===================

Provides go-to-definition functionality.
"""

from typing import Optional
import re


class DefinitionProvider:
    """
    Provides go-to-definition for NLPL symbols.
    
    Supports:
    - Functions
    - Variables
    - Classes
    - Imports
    """
    
    def __init__(self, server):
        self.server = server
    
    def get_definition(self, text: str, position, uri: str):
        """
        Find definition of symbol at position.
        
        Args:
            text: Document text
            position: Cursor position
            uri: Document URI
            
        Returns:
            Location or None
        """
        from ..lsp.server import Location, Range, Position
        
        # Get symbol at position
        symbol = self._get_symbol_at_position(text, position)
        if not symbol:
            return None
        
        # Find definition
        def_line, def_col = self._find_definition(text, symbol)
        if def_line is None:
            return None
        
        # Create location
        return Location(
            uri=uri,
            range=Range(
                start=Position(def_line, def_col),
                end=Position(def_line, def_col + len(symbol))
            )
        )
    
    def _get_symbol_at_position(self, text: str, position) -> Optional[str]:
        """Extract symbol at cursor position."""
        lines = text.split('\n')
        if position.line >= len(lines):
            return None
        
        line = lines[position.line]
        if position.character >= len(line):
            return None
        
        # Find word boundaries
        start = position.character
        end = position.character
        
        # Expand left
        while start > 0 and (line[start - 1].isalnum() or line[start - 1] == '_'):
            start -= 1
        
        # Expand right
        while end < len(line) and (line[end].isalnum() or line[end] == '_'):
            end += 1
        
        symbol = line[start:end]
        return symbol if symbol else None
    
    def _find_definition(self, text: str, symbol: str) -> tuple[Optional[int], Optional[int]]:
        """
        Find definition line and column.
        
        Returns:
            (line, column) or (None, None)
        """
        lines = text.split('\n')
        
        # Look for function definition
        func_pattern = rf'function\s+{re.escape(symbol)}\b'
        for i, line in enumerate(lines):
            match = re.search(func_pattern, line, re.IGNORECASE)
            if match:
                return (i, match.start() + len('function '))
        
        # Look for class definition
        class_pattern = rf'class\s+{re.escape(symbol)}\b'
        for i, line in enumerate(lines):
            match = re.search(class_pattern, line, re.IGNORECASE)
            if match:
                return (i, match.start() + len('class '))
        
        # Look for variable assignment
        var_pattern = rf'set\s+{re.escape(symbol)}\s+to'
        for i, line in enumerate(lines):
            match = re.search(var_pattern, line, re.IGNORECASE)
            if match:
                return (i, match.start() + len('set '))
        
        return (None, None)


__all__ = ['DefinitionProvider']
