"""
Definition Provider
===================

Provides go-to-definition functionality using AST-based symbol resolution.
"""

from typing import Optional, Tuple, Dict, List
import re
import os
from ..parser.lexer import Lexer
from ..parser.parser import Parser
from ..analysis import ASTSymbolExtractor, SymbolTable


class DefinitionProvider:
    """
    Provides go-to-definition for NLPL symbols using AST analysis.
    
    Supports:
    - Functions (cross-file)
    - Classes (cross-file)
    - Variables (local and module-level)
    - Methods (within classes)
    - Import resolution
    - Workspace-wide search
    """
    
    def __init__(self, server):
        self.server = server
        # Stdlib modules for quick lookup
        self.stdlib_modules = {
            'math', 'string', 'io', 'system', 'collections', 'network'
        }
        # Cache symbol tables per document
        self.symbol_tables: Dict[str, SymbolTable] = {}
    
    def _get_or_build_symbol_table(self, text: str, uri: str) -> Optional[SymbolTable]:
        """
        Get cached symbol table or build new one from document text.
        
        Args:
            text: Document text
            uri: Document URI
            
        Returns:
            SymbolTable or None if parse fails
        """
        try:
            # Try to parse and extract symbols
            lexer = Lexer(text)
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            ast = parser.parse()
            
            extractor = ASTSymbolExtractor(uri)
            symbol_table = extractor.extract(ast)
            
            # Cache it
            self.symbol_tables[uri] = symbol_table
            return symbol_table
        except Exception as e:
            # Parse failed - return cached version if available
            return self.symbol_tables.get(uri, None)
    
    def get_definition(self, text: str, position, uri: str):
        """
        Find definition of symbol at position using AST-based resolution.
        
        Args:
            text: Document text
            position: Cursor position
            uri: Document URI
            
        Returns:
            Location or None
        """
        # Build symbol table from AST
        symbol_table = self._get_or_build_symbol_table(text, uri)
        if not symbol_table:
            # Fallback to regex-based search
            return self._fallback_search(text, position, uri)
        
        # Get symbol at position from symbol table
        symbol = symbol_table.get_symbol_at_position(uri, position.line, position.character)
        if symbol:
            # Found symbol - return its definition location
            from lsprotocol.types import Location, Range, Position as LSPPosition
            return Location(
                uri=symbol.location.uri,
                range=Range(
                    start=LSPPosition(line=symbol.location.line, character=symbol.location.column),
                    end=LSPPosition(line=symbol.location.line, character=symbol.location.column + len(symbol.name))
                )
            )
        
        # Try fallback
        return self._fallback_search(text, position, uri)
    
    def _fallback_search(self, text: str, position, uri: str):
        """Fallback to regex-based search if AST analysis fails."""
        # Get symbol at position
        symbol = self._get_symbol_at_position(text, position)
        if not symbol:
            return None
        
        # Check if it's an import
        import_target = self._get_import_target(text, position, symbol)
        if import_target:
            return self._resolve_import(import_target, uri)
        
        # Try current file first
        location = self._find_in_current_file(text, symbol, uri, position)
        if location:
            return location
        
        # Try imported modules
        location = self._find_in_imports(text, symbol, uri)
        if location:
            return location
        
        # Try all open documents
        location = self._find_in_workspace(symbol)
        if location:
            return location
        
        return None
    
    def _get_import_target(self, text: str, position, symbol: str) -> Optional[str]:
        """Check if symbol is part of an import statement."""
        lines = text.split('\n')
        if position.line >= len(lines):
            return None
        
        line = lines[position.line]
        
        # Check for "import module_name"
        import_match = re.search(r'\bimport\s+(\w+)', line, re.IGNORECASE)
        if import_match and import_match.group(1) == symbol:
            return symbol
        
        # Check for "from module_name import symbol"
        from_match = re.search(r'\bfrom\s+(\w+)\s+import\s+(\w+)', line, re.IGNORECASE)
        if from_match:
            module_name, imported_symbol = from_match.groups()
            if module_name == symbol:
                return module_name
            elif imported_symbol == symbol:
                return f"{module_name}.{imported_symbol}"
        
        return None
    
    def _resolve_import(self, import_target: str, current_uri: str):
        """Resolve import to file path."""
        from ..lsp.server import Location, Range, Position
        
        # Split module.symbol if present
        parts = import_target.split('.')
        module_name = parts[0]
        symbol_name = parts[1] if len(parts) > 1 else None
        
        # Skip stdlib modules
        if module_name in self.stdlib_modules:
            return None
        
        # Find module file
        current_dir = os.path.dirname(current_uri.replace('file://', ''))
        module_path = os.path.join(current_dir, f"{module_name}.nlpl")
        
        if os.path.exists(module_path):
            module_uri = f"file://{module_path}"
            
            # If looking for specific symbol in module
            if symbol_name and module_uri in self.server.documents:
                module_text = self.server.documents[module_uri]
                return self._find_in_current_file(module_text, symbol_name, module_uri, None)
            
            # Point to start of module
            return Location(
                uri=module_uri,
                range=Range(
                    start=Position(0, 0),
                    end=Position(0, 0)
                )
            )
        
        return None
    
    def _find_in_current_file(self, text: str, symbol: str, uri: str, current_position):
        """Find definition in current file."""
        from ..lsp.server import Location, Range, Position
        
        line, column = self._find_definition(text, symbol, current_position)
        
        if line is not None and column is not None:
            return Location(
                uri=uri,
                range=Range(
                    start=Position(line, column),
                    end=Position(line, column + len(symbol))
                )
            )
        
        return None
    
    def _find_in_imports(self, text: str, symbol: str, current_uri: str):
        """Find definition in imported modules."""
        lines = text.split('\n')
        imports = []
        
        # Extract import statements
        for line in lines:
            match = re.search(r'\bimport\s+(\w+)', line, re.IGNORECASE)
            if match:
                imports.append(match.group(1))
            
            match = re.search(r'\bfrom\s+(\w+)\s+import\s+(\w+)', line, re.IGNORECASE)
            if match:
                module_name, imported_symbol = match.groups()
                if imported_symbol == symbol:
                    imports.append(module_name)
        
        # Search imported modules
        current_dir = os.path.dirname(current_uri.replace('file://', ''))
        
        for module_name in imports:
            if module_name in self.stdlib_modules:
                continue
            
            module_path = os.path.join(current_dir, f"{module_name}.nlpl")
            if os.path.exists(module_path):
                module_uri = f"file://{module_path}"
                
                # Get module text
                if module_uri in self.server.documents:
                    module_text = self.server.documents[module_uri]
                else:
                    try:
                        with open(module_path, 'r') as f:
                            module_text = f.read()
                    except:
                        continue
                
                # Find symbol in module
                location = self._find_in_current_file(module_text, symbol, module_uri, None)
                if location:
                    return location
        
        return None
    
    def _find_in_workspace(self, symbol: str):
        """Find definition across all open documents."""
        for uri, text in self.server.documents.items():
            location = self._find_in_current_file(text, symbol, uri, None)
            if location:
                return location
        
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
    
    def _find_definition(self, text: str, symbol: str, current_position) -> Tuple[Optional[int], Optional[int]]:
        """
        Find definition line and column.
        
        Returns:
            (line, column) or (None, None)
        """
        lines = text.split('\n')
        
        # Look for function definition
        func_pattern = rf'\bfunction\s+{re.escape(symbol)}\b'
        for i, line in enumerate(lines):
            # Skip current line to avoid self-reference
            if current_position and i == current_position.line:
                continue
            match = re.search(func_pattern, line, re.IGNORECASE)
            if match:
                return (i, match.start() + len('function '))
        
        # Look for class definition
        class_pattern = rf'\bclass\s+{re.escape(symbol)}\b'
        for i, line in enumerate(lines):
            if current_position and i == current_position.line:
                continue
            match = re.search(class_pattern, line, re.IGNORECASE)
            if match:
                return (i, match.start() + len('class '))
        
        # Look for method definition
        method_pattern = rf'\bmethod\s+{re.escape(symbol)}\b'
        for i, line in enumerate(lines):
            if current_position and i == current_position.line:
                continue
            match = re.search(method_pattern, line, re.IGNORECASE)
            if match:
                return (i, match.start() + len('method '))
        
        # Look for variable assignment (closest before current position)
        var_pattern = rf'\bset\s+{re.escape(symbol)}\s+to\b'
        best_match = (None, None)
        search_limit = current_position.line if current_position else len(lines)
        
        for i, line in enumerate(lines):
            # Only look at lines before current position
            if i >= search_limit:
                break
            
            match = re.search(var_pattern, line, re.IGNORECASE)
            if match:
                # Keep updating to find the closest one
                best_match = (i, match.start() + len('set '))
        
        if best_match[0] is not None:
            return best_match
        
        return (None, None)


__all__ = ['DefinitionProvider']
