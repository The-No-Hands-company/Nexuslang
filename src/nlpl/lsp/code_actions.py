"""
Code Actions Provider
=====================

Provides quick fixes and refactoring actions using AST-based analysis.
"""

from typing import List, Dict, Optional
from ..parser.lexer import Lexer
from ..parser.parser import Parser
from ..analysis import ASTSymbolExtractor, SymbolTable, SymbolKind


class CodeActionsProvider:
    """
    Provides code actions and refactorings using AST-based analysis.
    
    Actions:
    - Fix unclosed strings
    - Remove unused variables
    - Add missing imports
    - Convert types
    - Extract function
    - Add type annotations
    - Organize imports
    - Rename symbol
    """
    
    # Action kinds (LSP standard)
    KIND_QUICKFIX = "quickfix"
    KIND_REFACTOR = "refactor"
    KIND_REFACTOR_EXTRACT = "refactor.extract"
    KIND_SOURCE_ORGANIZE_IMPORTS = "source.organizeImports"
    
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
    
    def get_code_actions(self, uri: str, text: str, range_params: Dict, diagnostics: List[Dict]) -> List[Dict]:
        """
        Get code actions for a range using AST-based analysis.
        
        Args:
            uri: Document URI
            text: Document text
            range_params: Range to check
            diagnostics: Diagnostics in range
            
        Returns:
            List of code actions
        """
        actions = []
        
        # Build symbol table
        symbol_table = self._get_or_build_symbol_table(text, uri)
        
        # Add organize imports action
        actions.append({
            "title": "Organize imports",
            "kind": self.KIND_SOURCE_ORGANIZE_IMPORTS,
            "command": {
                "title": "Organize imports",
                "command": "nlpl.organizeImports",
                "arguments": [uri]
            }
        })
        
        # Check if we have a selection for extract actions
        if self._has_selection(range_params):
            actions.append({
                "title": "Extract function",
                "kind": self.KIND_REFACTOR_EXTRACT,
                "command": {
                    "title": "Extract function",
                    "command": "nlpl.extractFunction",
                    "arguments": [uri, range_params]
                }
            })
        
        # Get symbol at cursor for targeted actions
        if symbol_table:
            start = range_params["start"]
            symbol = symbol_table.get_symbol_at_position(uri, start["line"], start["character"])
            
            if symbol and not symbol.type_annotation:
                actions.append({
                    "title": f"Add type annotation to '{symbol.name}'",
                    "kind": self.KIND_QUICKFIX,
                    "edit": {
                        "changes": {
                            uri: [{
                                "range": {
                                    "start": {
                                        "line": symbol.location.line,
                                        "character": symbol.location.column + len(symbol.name)
                                    },
                                    "end": {
                                        "line": symbol.location.line,
                                        "character": symbol.location.column + len(symbol.name)
                                    }
                                },
                                "newText": " as Any"
                            }]
                        }
                    }
                })
        
        # Actions for specific diagnostics
        for diagnostic in diagnostics:
            message = diagnostic.get('message', '')
            diag_range = diagnostic.get('range', {})

            # Prefer structured fixes from diagnostic payload
            structured_actions = self._actions_from_structured_fixes(uri, text, diagnostic)
            if structured_actions:
                actions.extend(structured_actions)
                continue
            
            # Fix unclosed string
            if 'Unclosed string' in message or 'Unterminated string' in message:
                fix = self._fix_unclosed_string(uri, text, diag_range)
                if fix:
                    fix["diagnostics"] = [diagnostic]
                    actions.append(fix)
            
            # Fix undefined variable
            if 'undefined' in message.lower():
                import re
                match = re.search(r"'(\w+)'", message)
                if match:
                    var_name = match.group(1)
                    declare_action = self._declare_variable_action(uri, diag_range, var_name, diagnostic)
                    if declare_action:
                        actions.append(declare_action)
        
        return actions
    
    def _has_selection(self, range_params: Dict) -> bool:
        """Check if range represents a non-empty selection."""
        start = range_params["start"]
        end = range_params["end"]
        return start["line"] != end["line"] or start["character"] != end["character"]
    
    def _fix_unclosed_string(self, uri: str, text: str, diag_range: Dict) -> Optional[Dict]:
        """Fix unclosed string by adding closing quote."""
        line_num = diag_range.get('start', {}).get('line', 0)
        lines = text.split('\n')
        
        if line_num >= len(lines):
            return None
        
        line = lines[line_num]
        
        # Find the unclosed quote
        if '"' in line and line.count('"') % 2 != 0:
            # Add closing quote at end of line
            return {
                "title": "Add closing quote",
                "kind": "quickfix",
                "diagnostics": [{"range": diag_range}],
                "edit": {
                    "changes": {
                        uri: [{
                            "range": {
                                "start": {"line": line_num, "character": len(line)},
                                "end": {"line": line_num, "character": len(line)}
                            },
                            "newText": '"'
                        }]
                    }
                }
            }
        
        return None

    def _declare_variable_action(self, uri: str, diag_range: Dict, var_name: str, diagnostic: Optional[Dict] = None) -> Optional[Dict]:
        """Create quick fix action to declare a missing variable."""
        start_line = diag_range.get("start", {}).get("line")
        if start_line is None:
            return None

        action = {
            "title": f"Declare '{var_name}'",
            "kind": self.KIND_QUICKFIX,
            "edit": {
                "changes": {
                    uri: [{
                        "range": {
                            "start": {"line": start_line, "character": 0},
                            "end": {"line": start_line, "character": 0}
                        },
                        "newText": f"set {var_name} to Nothing\n"
                    }]
                }
            },
        }
        if diagnostic:
            action["diagnostics"] = [diagnostic]
        return action

    def _actions_from_structured_fixes(self, uri: str, text: str, diagnostic: Dict) -> List[Dict]:
        """Build code actions from structured diagnostic.data.fixes payload."""
        actions: List[Dict] = []
        data = diagnostic.get("data", {})
        if not isinstance(data, dict):
            return actions

        fixes = data.get("fixes", [])
        if not isinstance(fixes, list) or not fixes:
            return actions

        message = diagnostic.get("message", "")
        message_lower = message.lower()
        diag_range = diagnostic.get("range", {})

        for fix_text in fixes:
            if not isinstance(fix_text, str):
                continue
            fix_lower = fix_text.lower()

            if "quote" in fix_lower and ("unclosed string" in message_lower or "unterminated string" in message_lower):
                fix = self._fix_unclosed_string(uri, text, diag_range)
                if fix:
                    fix["diagnostics"] = [diagnostic]
                    actions.append(fix)
                continue

            if "undefined" in message_lower and ("declare" in fix_lower or "define" in fix_lower or "initialize" in fix_lower):
                import re
                match = re.search(r"'(\w+)'", message)
                if match:
                    action = self._declare_variable_action(uri, diag_range, match.group(1), diagnostic)
                    if action:
                        actions.append(action)
                continue

            if "unused variable" in message_lower and ("remove" in fix_lower or "delete" in fix_lower):
                var_name = self._extract_variable_name(message)
                if var_name:
                    action = self._remove_unused_variable(uri, text, var_name, diag_range)
                    if action:
                        action["diagnostics"] = [diagnostic]
                        actions.append(action)
                continue

            if "type" in message_lower and ("annotation" in fix_lower or "add type" in fix_lower):
                action = self._add_type_annotation(uri, text, diag_range, message)
                if action:
                    action["diagnostics"] = [diagnostic]
                    actions.append(action)

        return actions
    
    def _remove_unused_variable(self, uri: str, text: str, var_name: str, diag_range: Dict) -> Optional[Dict]:
        """Remove unused variable declaration."""
        line_num = diag_range.get('start', {}).get('line', 0)
        lines = text.split('\n')
        
        if line_num >= len(lines):
            return None
        
        return {
            "title": f"Remove unused variable '{var_name}'",
            "kind": "quickfix",
            "diagnostics": [{"range": diag_range}],
            "edit": {
                "changes": {
                    uri: [{
                        "range": {
                            "start": {"line": line_num, "character": 0},
                            "end": {"line": line_num + 1, "character": 0}
                        },
                        "newText": ""
                    }]
                }
            }
        }
    
    def _add_type_annotation(self, uri: str, text: str, diag_range: Dict, message: str) -> Optional[Dict]:
        """Add missing type annotation."""
        # Extract expected type from error message
        import re
        type_match = re.search(r"expected '([^']+)'", message, re.IGNORECASE)
        if not type_match:
            return None
        
        expected_type = type_match.group(1)
        line_num = diag_range.get('start', {}).get('line', 0)
        lines = text.split('\n')
        
        if line_num >= len(lines):
            return None
        
        line = lines[line_num]
        
        # Check if it's a variable declaration without type
        var_match = re.search(r'set\s+(\w+)\s+to', line, re.IGNORECASE)
        if var_match:
            var_name = var_match.group(1)
            # Insert type annotation after variable name
            insert_pos = var_match.end(1)
            
            return {
                "title": f"Add type annotation: {expected_type}",
                "kind": "quickfix",
                "diagnostics": [{"range": diag_range}],
                "edit": {
                    "changes": {
                        uri: [{
                            "range": {
                                "start": {"line": line_num, "character": insert_pos},
                                "end": {"line": line_num, "character": insert_pos}
                            },
                            "newText": f" as {expected_type}"
                        }]
                    }
                }
            }
        
        return None
    
    def _get_refactoring_actions(self, uri: str, text: str, range_params: Dict) -> List[Dict]:
        """Get general refactoring actions available in range."""
        actions = []
        
        start_line = range_params.get('start', {}).get('line', 0)
        end_line = range_params.get('end', {}).get('line', 0)
        
        lines = text.split('\n')
        selected_text = '\n'.join(lines[start_line:end_line + 1]) if start_line < len(lines) else ""
        
        # Extract function (if multiple lines selected)
        if end_line > start_line and len(selected_text.strip()) > 0:
            actions.append({
                "title": "Extract to function",
                "kind": "refactor.extract",
                "command": {
                    "title": "Extract to function",
                    "command": "nlpl.extractFunction",
                    "arguments": [uri, range_params]
                }
            })
        
        # Convert to list comprehension (if it's a for loop creating a list)
        if 'for each' in selected_text.lower() and 'create list' in selected_text.lower():
            actions.append({
                "title": "Convert to list comprehension",
                "kind": "refactor.rewrite",
                "command": {
                    "title": "Convert to list comprehension",
                    "command": "nlpl.convertToComprehension",
                    "arguments": [uri, range_params]
                }
            })
        
        return actions
    
    def _extract_variable_name(self, message: str) -> Optional[str]:
        """Extract variable name from diagnostic message."""
        import re
        match = re.search(r"variable '([^']+)'", message)
        return match.group(1) if match else None


__all__ = ['CodeActionsProvider']
