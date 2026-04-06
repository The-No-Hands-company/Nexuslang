"""
References Provider
===================

Finds all references to a symbol across the workspace using AST-based analysis.
"""

from typing import List, Dict, Optional, Tuple
import re
from ..parser.lexer import Lexer
from ..parser.parser import Parser
from ..analysis import ASTSymbolExtractor, SymbolTable


class ReferencesProvider:
    """
    Provides find-all-references functionality using AST-based symbol resolution.
    
    Finds all usages of:
    - Functions (definitions and calls)
    - Classes (definitions and instantiations)
    - Variables (assignments and references)
    - Methods (definitions and calls)
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
    
    def find_references(
        self,
        text: str,
        position: 'Position',
        uri: str,
        include_declaration: bool = True
    ) -> List[Dict]:
        """
        Find all references to symbol at position using AST-based resolution.

        Searches open documents first, then all indexed workspace files not
        already open, so cross-file references are always returned.

        Args:
            text: Document text
            position: Cursor position
            uri: Document URI
            include_declaration: Whether to include the declaration/definition

        Returns:
            List of locations where symbol is referenced
        """
        # Try AST-based symbol table for the current file
        symbol_table = self._get_or_build_symbol_table(text, uri)
        if symbol_table:
            symbol = symbol_table.get_symbol_at_position(uri, position.line, position.character)
        else:
            symbol = None

        if symbol:
            # AST path: use symbol table references (within this file)
            references: List[Dict] = []
            if include_declaration and symbol.location:
                references.append({
                    "uri": symbol.location.uri,
                    "range": {
                        "start": {"line": symbol.location.line, "character": symbol.location.column},
                        "end": {"line": symbol.location.line, "character": symbol.location.column + len(symbol.name)}
                    }
                })
            for ref in symbol.references:
                references.append({
                    "uri": ref.uri,
                    "range": {
                        "start": {"line": ref.line, "character": ref.column},
                        "end": {"line": ref.line, "character": ref.column + len(symbol.name)}
                    }
                })
        else:
            # Fallback: regex search across all open documents
            references = self._fallback_find_references(text, position, uri, include_declaration)

        # Extend with cross-file results from workspace files not currently open
        self._add_workspace_references(references, text, position)
        return references

    def _add_workspace_references(
        self,
        references: List[Dict],
        text: str,
        position: 'Position'
    ) -> None:
        """Append references found in workspace files not already in server.documents."""
        if not (hasattr(self.server, 'workspace_index') and self.server.workspace_index):
            return
        symbol = self._get_symbol_at_position(text, position)
        if not symbol:
            return
        symbol_type = self._get_symbol_type(text, position, symbol)
        for file_uri in self.server.workspace_index.indexed_files:
            if file_uri in self.server.documents:
                continue  # Already covered by open-document search
            file_path = self.server.workspace_index._uri_to_path(file_uri)
            try:
                with open(file_path, 'r', encoding='utf-8') as fh:
                    file_text = fh.read()
                doc_refs = self._find_in_document(file_text, symbol, symbol_type, file_uri)
                references.extend(doc_refs)
            except Exception:
                pass
    
    def _fallback_find_references(
        self, 
        text: str, 
        position: 'Position', 
        uri: str,
        include_declaration: bool = True
    ) -> List[Dict]:
        """Fallback to regex-based reference search."""
        # Get symbol at position
        symbol = self._get_symbol_at_position(text, position)
        if not symbol:
            return []
        
        # Determine symbol type
        symbol_type = self._get_symbol_type(text, position, symbol)
        
        # Find all references across all documents
        references = []
        
        for doc_uri, doc_text in self.server.documents.items():
            doc_refs = self._find_in_document(
                doc_text, 
                symbol, 
                symbol_type,
                doc_uri
            )
            references.extend(doc_refs)
        
        # Filter out declaration if requested
        if not include_declaration:
            references = [
                ref for ref in references 
                if not self._is_declaration(ref, text, position, uri)
            ]
        
        return references
    
    def _get_symbol_at_position(self, text: str, position: 'Position') -> Optional[str]:
        """Extract symbol name at cursor position."""
        lines = text.split('\n')
        if position.line >= len(lines):
            return None
        
        line = lines[position.line]
        
        # Extract word at position
        if position.character >= len(line):
            return None
        
        # Find word boundaries
        start = position.character
        end = position.character
        
        # Move back to start of word
        while start > 0 and (line[start - 1].isalnum() or line[start - 1] == '_'):
            start -= 1
        
        # Move forward to end of word
        while end < len(line) and (line[end].isalnum() or line[end] == '_'):
            end += 1
        
        symbol = line[start:end]
        return symbol if symbol else None
    
    def _get_symbol_type(
        self, 
        text: str, 
        position: 'Position', 
        symbol: str
    ) -> str:
        """
        Determine symbol type (function, class, variable, method).
        
        Returns:
            'function' | 'class' | 'variable' | 'method'
        """
        lines = text.split('\n')
        if position.line >= len(lines):
            return 'variable'
        
        line = lines[position.line]
        
        # Check for function definition
        if re.search(rf'\bfunction\s+{re.escape(symbol)}\b', line, re.IGNORECASE):
            return 'function'
        
        # Check for class definition
        if re.search(rf'\bclass\s+{re.escape(symbol)}\b', line, re.IGNORECASE):
            return 'class'
        
        # Check for method definition (inside a class)
        for i in range(position.line - 1, max(0, position.line - 50), -1):
            if re.search(r'\bclass\s+\w+', lines[i], re.IGNORECASE):
                # Inside class, likely a method
                if re.search(rf'\bmethod\s+{re.escape(symbol)}\b', line, re.IGNORECASE):
                    return 'method'
                break
        
        # Check for variable assignment
        if re.search(rf'\bset\s+{re.escape(symbol)}\s+to\b', line, re.IGNORECASE):
            return 'variable'
        
        # Default to variable (could be reference)
        return 'variable'
    
    def _find_in_document(
        self, 
        text: str, 
        symbol: str, 
        symbol_type: str,
        uri: str
    ) -> List[Dict]:
        """Find all references to symbol in a document."""
        references = []
        lines = text.split('\n')
        
        if symbol_type == 'function':
            references.extend(self._find_function_refs(lines, symbol, uri))
        elif symbol_type == 'class':
            references.extend(self._find_class_refs(lines, symbol, uri))
        elif symbol_type == 'method':
            references.extend(self._find_method_refs(lines, symbol, uri))
        elif symbol_type == 'variable':
            references.extend(self._find_variable_refs(lines, symbol, uri))
        
        return references
    
    def _find_function_refs(self, lines: List[str], symbol: str, uri: str) -> List[Dict]:
        """Find function definition and all calls."""
        refs = []
        
        # Pattern for function definition
        def_pattern = rf'\bfunction\s+{re.escape(symbol)}\b'
        
        # Pattern for function calls - NexusLang uses "function_name with args" syntax
        call_pattern = rf'\b{re.escape(symbol)}\s+with\b'
        # Also check for direct calls with parentheses (if used)
        call_pattern2 = rf'\b{re.escape(symbol)}\s*\('
        
        for i, line in enumerate(lines):
            # Check for definition
            match = re.search(def_pattern, line, re.IGNORECASE)
            if match:
                refs.append({
                    "uri": uri,
                    "range": {
                        "start": {"line": i, "character": match.start()},
                        "end": {"line": i, "character": match.end()}
                    }
                })
            
            # Check for calls (with "with" keyword)
            for match in re.finditer(call_pattern, line, re.IGNORECASE):
                refs.append({
                    "uri": uri,
                    "range": {
                        "start": {"line": i, "character": match.start()},
                        "end": {"line": i, "character": match.start() + len(symbol)}
                    }
                })
            
            # Check for calls (with parentheses)
            for match in re.finditer(call_pattern2, line, re.IGNORECASE):
                refs.append({
                    "uri": uri,
                    "range": {
                        "start": {"line": i, "character": match.start()},
                        "end": {"line": i, "character": match.start() + len(symbol)}
                    }
                })
        
        return refs
    
    def _find_class_refs(self, lines: List[str], symbol: str, uri: str) -> List[Dict]:
        """Find class definition and all instantiations."""
        refs = []
        
        # Pattern for class definition
        def_pattern = rf'\bclass\s+{re.escape(symbol)}\b'
        
        # Pattern for class instantiation (create new Person, new Person)
        inst_pattern = rf'\b(?:new\s+)?{re.escape(symbol)}\s*\('
        
        # Pattern for type annotations
        type_pattern = rf'\bas\s+{re.escape(symbol)}\b'
        
        for i, line in enumerate(lines):
            # Check for definition
            match = re.search(def_pattern, line, re.IGNORECASE)
            if match:
                refs.append({
                    "uri": uri,
                    "range": {
                        "start": {"line": i, "character": match.start()},
                        "end": {"line": i, "character": match.end()}
                    }
                })
            
            # Check for instantiations
            for match in re.finditer(inst_pattern, line, re.IGNORECASE):
                # Find start of class name (skip 'new' if present)
                start_pos = match.start()
                if line[start_pos:].lower().startswith('new'):
                    start_pos += 4  # len('new ')
                
                refs.append({
                    "uri": uri,
                    "range": {
                        "start": {"line": i, "character": start_pos},
                        "end": {"line": i, "character": start_pos + len(symbol)}
                    }
                })
            
            # Check for type annotations
            for match in re.finditer(type_pattern, line, re.IGNORECASE):
                # Extract just the class name part
                as_match = re.search(r'as\s+', line[match.start():], re.IGNORECASE)
                if as_match:
                    start_pos = match.start() + as_match.end()
                    refs.append({
                        "uri": uri,
                        "range": {
                            "start": {"line": i, "character": start_pos},
                            "end": {"line": i, "character": start_pos + len(symbol)}
                        }
                    })
        
        return refs
    
    def _find_method_refs(self, lines: List[str], symbol: str, uri: str) -> List[Dict]:
        """Find method definition and all calls."""
        refs = []
        
        # Pattern for method definition
        def_pattern = rf'\bmethod\s+{re.escape(symbol)}\b'
        
        # Pattern for method calls (object.method or call method on object)
        call_pattern = rf'\.{re.escape(symbol)}\s*\('
        call_pattern2 = rf'\bcall\s+{re.escape(symbol)}\s+on\b'
        
        for i, line in enumerate(lines):
            # Check for definition
            match = re.search(def_pattern, line, re.IGNORECASE)
            if match:
                refs.append({
                    "uri": uri,
                    "range": {
                        "start": {"line": i, "character": match.start()},
                        "end": {"line": i, "character": match.end()}
                    }
                })
            
            # Check for calls (object.method)
            for match in re.finditer(call_pattern, line):
                refs.append({
                    "uri": uri,
                    "range": {
                        "start": {"line": i, "character": match.start() + 1},  # Skip '.'
                        "end": {"line": i, "character": match.start() + 1 + len(symbol)}
                    }
                })
            
            # Check for calls (call method on object)
            for match in re.finditer(call_pattern2, line, re.IGNORECASE):
                call_match = re.search(r'call\s+', line[match.start():], re.IGNORECASE)
                if call_match:
                    start_pos = match.start() + call_match.end()
                    refs.append({
                        "uri": uri,
                        "range": {
                            "start": {"line": i, "character": start_pos},
                            "end": {"line": i, "character": start_pos + len(symbol)}
                        }
                    })
        
        return refs
    
    def _find_variable_refs(self, lines: List[str], symbol: str, uri: str) -> List[Dict]:
        """Find variable assignments and all references."""
        refs = []
        
        # Pattern for variable assignment
        assign_pattern = rf'\bset\s+{re.escape(symbol)}\s+to\b'
        
        # Pattern for variable reference (just the symbol as a word)
        ref_pattern = rf'\b{re.escape(symbol)}\b'
        
        for i, line in enumerate(lines):
            # Check for assignment
            match = re.search(assign_pattern, line, re.IGNORECASE)
            if match:
                # Find the exact position of the symbol name
                set_match = re.search(r'set\s+', line[match.start():], re.IGNORECASE)
                if set_match:
                    start_pos = match.start() + set_match.end()
                    refs.append({
                        "uri": uri,
                        "range": {
                            "start": {"line": i, "character": start_pos},
                            "end": {"line": i, "character": start_pos + len(symbol)}
                        }
                    })
            
            # Check for all references
            for match in re.finditer(ref_pattern, line):
                # Skip positions already captured (e.g. the assignment itself)
                already_covered = any(
                    e["range"]["start"]["line"] == i
                    and e["range"]["start"]["character"] == match.start()
                    for e in refs
                )
                if already_covered:
                    continue

                # Avoid matching inside keywords
                if self._is_inside_keyword(line, match.start()):
                    continue

                refs.append({
                    "uri": uri,
                    "range": {
                        "start": {"line": i, "character": match.start()},
                        "end": {"line": i, "character": match.end()}
                    }
                })
        
        return refs
    
    def _is_inside_keyword(self, line: str, position: int) -> bool:
        """Check if position is inside a keyword."""
        keywords = [
            'function', 'class', 'method', 'if', 'else', 'for', 'while',
            'return', 'break', 'continue', 'import', 'from', 'as', 'set',
            'to', 'new', 'call', 'on', 'with', 'returns', 'that', 'takes'
        ]
        
        # Get word boundaries around position
        start = position
        while start > 0 and (line[start - 1].isalnum() or line[start - 1] == '_'):
            start -= 1
        
        end = position
        while end < len(line) and (line[end].isalnum() or line[end] == '_'):
            end += 1
        
        word = line[start:end].lower()
        return word in keywords
    
    def _is_declaration(
        self, 
        ref: Dict, 
        original_text: str, 
        original_position: 'Position',
        original_uri: str
    ) -> bool:
        """Check if a reference is the original declaration."""
        # Same location as original cursor position
        if ref["uri"] != original_uri:
            return False
        
        ref_line = ref["range"]["start"]["line"]
        ref_char = ref["range"]["start"]["character"]
        
        return (ref_line == original_position.line and 
                ref_char == original_position.character)


__all__ = ['ReferencesProvider']
