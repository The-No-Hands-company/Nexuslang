"""
Hover Provider
==============

Provides documentation and type information on hover.
"""

from typing import Optional, Dict
import re


class HoverProvider:
    """
    Provides hover information for symbols.
    
    Shows:
    - Function signatures
    - Variable types
    - Documentation
    - Examples
    """
    
    def __init__(self, server):
        self.server = server
        
        # Documentation for keywords and stdlib
        self.docs = {
            # Keywords
            "function": "Define a function\n\nSyntax:\n```nlpl\nfunction name that takes param as Type returns Type\n    # body\n```",
            "class": "Define a class\n\nSyntax:\n```nlpl\nclass Name\n    property field as Type\n```",
            "set": "Declare or assign a variable\n\nSyntax:\n```nlpl\nset varname to value\n```",
            "if": "Conditional statement\n\nSyntax:\n```nlpl\nif condition\n    # body\n```",
            "for": "For-each loop\n\nSyntax:\n```nlpl\nfor each item in collection\n    # body\n```",
            
            # Standard library
            "sqrt": "**sqrt** - Square root function\n\nFrom: math\n\nSyntax:\n```nlpl\nset result to sqrt with number\n```",
            "print": "**print** - Print to stdout\n\nFrom: io\n\nSyntax:\n```nlpl\nprint text message\n```",
            "split": "**split** - Split string by delimiter\n\nFrom: string\n\nSyntax:\n```nlpl\nset parts to split with text, delimiter\n```",
        }
    
    def get_hover(self, text: str, position) -> Optional[Dict]:
        """
        Get hover information at position.
        
        Args:
            text: Document text
            position: Cursor position
            
        Returns:
            Hover information or None
        """
        # Get symbol at position
        symbol = self._get_symbol_at_position(text, position)
        if not symbol:
            return None
        
        # Check documentation database
        if symbol in self.docs:
            return {
                "contents": {
                    "kind": "markdown",
                    "value": self.docs[symbol]
                }
            }
        
        # Try to infer type/signature from code
        info = self._infer_symbol_info(text, symbol)
        if info:
            return {
                "contents": {
                    "kind": "markdown",
                    "value": info
                }
            }
        
        return None
    
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
    
    def _infer_symbol_info(self, text: str, symbol: str) -> Optional[str]:
        """Infer type/signature information for symbol."""
        lines = text.split('\n')
        
        # Look for function definition
        func_pattern = rf'function\s+{re.escape(symbol)}\s+(.*)'
        for line in lines:
            match = re.search(func_pattern, line, re.IGNORECASE)
            if match:
                signature = match.group(1)
                return f"**{symbol}** - Function\n\n```nlpl\nfunction {symbol} {signature}\n```"
        
        # Look for class definition
        class_pattern = rf'class\s+{re.escape(symbol)}\b'
        for line in lines:
            if re.search(class_pattern, line, re.IGNORECASE):
                return f"**{symbol}** - Class\n\n```nlpl\nclass {symbol}\n```"
        
        # Look for variable with type
        var_pattern = rf'set\s+{re.escape(symbol)}\s+to\s+(.+)'
        for line in lines:
            match = re.search(var_pattern, line, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                return f"**{symbol}** - Variable\n\nValue: `{value}`"
        
        return None


__all__ = ['HoverProvider']
