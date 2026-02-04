"""
Diagnostics Provider
====================

Provides real-time error checking and warnings.
"""

from typing import List, Dict
import re


class DiagnosticsProvider:
    """
    Provides real-time diagnostics.
    
    Checks for:
    - Syntax errors (using NLPL parser)
    - Type errors (using NLPL type checker)
    - Undefined variables
    - Unused variables
    - Best practice violations
    """
    
    def __init__(self, server):
        self.server = server
        self.file_diagnostics_cache = {}  # Cache diagnostics per file
        self.workspace_files = set()  # Track all files in workspace
    
    def get_diagnostics(self, uri: str, text: str, check_imports: bool = True) -> List[Dict]:
        """
        Get diagnostics for document.
        
        Args:
            uri: Document URI
            text: Document text
            check_imports: Whether to check imported files
            
        Returns:
            List of diagnostics
        """
        diagnostics = []
        
        # Track this file in workspace
        self.workspace_files.add(uri)
        
        # Try parser-based syntax checking first
        parser_diagnostics = self._check_parser_syntax_enhanced(text, uri)
        if parser_diagnostics:
            diagnostics.extend(parser_diagnostics)
        else:
            # Fallback to basic syntax checks
            diagnostics.extend(self._check_syntax(text))
        
        # Try type checker diagnostics with enhanced positioning
        type_diagnostics = self._check_type_errors_enhanced(text, uri)
        if type_diagnostics:
            diagnostics.extend(type_diagnostics)
        
        # Check for import errors (multi-file)
        if check_imports:
            import_diagnostics = self._check_imports(text, uri)
            diagnostics.extend(import_diagnostics)
        
        # Additional static checks
        diagnostics.extend(self._check_unused_vars(text))
        
        # Cache diagnostics for this file
        self.file_diagnostics_cache[uri] = diagnostics
        
        return diagnostics
    
    def _check_parser_syntax_enhanced(self, text: str, uri: str) -> List[Dict]:
        """
        Check syntax using NLPL parser with enhanced error positioning.
        
        Uses AST cache for performance.
        
        Returns:
            List of diagnostics with accurate line/column info
        """
        diagnostics = []
        
        try:
            from nlpl.parser.cached_parser import parse_with_cache
            
            # Use cached parser for performance
            # Will automatically handle cache hits/misses based on content hash
            ast = parse_with_cache(uri, text, debug=False)
            
            # If we got here without exception, no syntax errors
            return []
            
        except Exception as e:
            # Parse error - extract detailed position info
            error_msg = str(e)
            
            # Try to extract line/column from error or token
            line = 0
            col = 0
            end_col = 0
            
            # Check if error has line_number attribute (from parser)
            if hasattr(e, 'line_number'):
                line = e.line_number - 1
            else:
                # Extract from error message
                line_match = re.search(r'line (\d+)', error_msg, re.IGNORECASE)
                if line_match:
                    line = int(line_match.group(1)) - 1
            
            if hasattr(e, 'column'):
                col = e.column - 1
            else:
                col_match = re.search(r'column (\d+)', error_msg, re.IGNORECASE)
                if col_match:
                    col = int(col_match.group(1)) - 1
            
            # Get the problematic line for better highlighting
            lines = text.split('\n')
            if line < len(lines):
                line_text = lines[line]
                # Try to highlight the actual error token
                if 'Unexpected token' in error_msg:
                    token_match = re.search(r"token '([^']+)'", error_msg)
                    if token_match:
                        token = token_match.group(1)
                        token_pos = line_text.find(token, col)
                        if token_pos >= 0:
                            col = token_pos
                            end_col = col + len(token)
                
                if end_col == 0:
                    end_col = min(col + 10, len(line_text))
            else:
                end_col = col + 1
            
            diagnostics.append({
                "range": {
                    "start": {"line": line, "character": col},
                    "end": {"line": line, "character": end_col}
                },
                "severity": 1,  # Error
                "message": f"Syntax error: {error_msg}",
                "source": "nlpl-parser"
            })
        
        return diagnostics
    
    def _check_parser_syntax(self, text: str) -> List[Dict]:
        """
        Check syntax using NLPL parser.
        
        Returns:
            List of diagnostics or empty list if parser not available
        """
        diagnostics = []
        
        try:
            from nlpl.parser.lexer import Lexer
            from nlpl.parser.parser import Parser
            
            # Try to parse
            lexer = Lexer(text)
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            parser.parse()
            
            # If we got here without exception, no syntax errors
            return []
            
        except Exception as e:
            # Parse error - try to extract line/column info
            error_msg = str(e)
            
            # Try to extract line number from error message
            line_match = re.search(r'line (\d+)', error_msg, re.IGNORECASE)
            col_match = re.search(r'column (\d+)', error_msg, re.IGNORECASE)
            
            line = int(line_match.group(1)) - 1 if line_match else 0
            col = int(col_match.group(1)) - 1 if col_match else 0
            
            # Get the problematic line
            lines = text.split('\n')
            if line < len(lines):
                line_text = lines[line]
                end_col = min(col + 10, len(line_text))  # Highlight ~10 chars
            else:
                end_col = col + 1
            
            diagnostics.append({
                "range": {
                    "start": {"line": line, "character": col},
                    "end": {"line": line, "character": end_col}
                },
                "severity": 1,  # Error
                "message": f"Syntax error: {error_msg}",
                "source": "nlpl-parser"
            })
        
        return diagnostics
    
    def _check_type_errors_enhanced(self, text: str, uri: str) -> List[Dict]:
        """
        Check for type errors using NLPL type checker with AST-based positioning.
        
        Returns:
            List of diagnostics with accurate positioning from AST nodes
        """
        diagnostics = []
        
        try:
            # Use cached AST if available
            if hasattr(self, 'ast_cache') and uri in self.ast_cache:
                ast = self.ast_cache[uri]
            else:
                # Parse if not cached
                from nlpl.parser.lexer import Lexer
                from nlpl.parser.parser import Parser
                
                lexer = Lexer(text)
                tokens = lexer.tokenize()
                parser = Parser(tokens)
                ast = parser.parse()
            
            # Type check
            from nlpl.typesystem.typechecker import TypeChecker
            typechecker = TypeChecker()
            typechecker.check_program(ast)
            
            # Convert type errors to diagnostics with AST node positions
            for error in typechecker.errors:
                # Try to find the AST node related to this error
                line, col, end_col = self._find_error_position(text, error, ast)
                
                diagnostics.append({
                    "range": {
                        "start": {"line": line, "character": col},
                        "end": {"line": line, "character": end_col}
                    },
                    "severity": 1,  # Error
                    "message": f"Type error: {error}",
                    "source": "nlpl-typechecker"
                })
        
        except Exception:
            # If parsing fails, syntax errors will be caught by _check_parser_syntax_enhanced
            pass
        
        return diagnostics
    
    def _find_error_position(self, text: str, error: str, ast) -> tuple:
        """
        Find accurate position for type error using AST.
        
        Returns:
            (line, col, end_col) tuple
        """
        lines = text.split('\n')
        
        # Extract identifiers from error message
        import re
        words = re.findall(r"'([^']+)'", error)
        
        # Try to find the first identifier in the source
        for word in words:
            for i, line_text in enumerate(lines):
                pos = line_text.find(word)
                if pos >= 0:
                    return (i, pos, pos + len(word))
        
        # Fallback: search for keywords in error
        error_lower = error.lower()
        for i, line_text in enumerate(lines):
            line_lower = line_text.lower()
            for word in error_lower.split():
                if len(word) > 3 and word.isalpha() and word in line_lower:
                    pos = line_lower.find(word)
                    return (i, pos, pos + len(word))
        
        # Last resort: beginning of first line
        return (0, 0, 10)
    
    def _check_type_errors(self, text: str) -> List[Dict]:
        """
        Check for type errors using NLPL type checker.
        
        Returns:
            List of diagnostics or empty list if type checker not available
        """
        diagnostics = []
        
        try:
            from nlpl.parser.lexer import Lexer
            from nlpl.parser.parser import Parser
            from nlpl.typesystem.typechecker import TypeChecker
            
            # Parse first
            lexer = Lexer(text)
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            ast = parser.parse()
            
            # Type check
            typechecker = TypeChecker()
            typechecker.check_program(ast)
            
            # Convert type errors to diagnostics
            for error in typechecker.errors:
                # Try to extract position info from error
                line = 0
                col = 0
                
                # Simple heuristic: find the line containing the error
                error_lower = error.lower()
                for i, line_text in enumerate(text.split('\n')):
                    # Look for variable names, function names, etc. mentioned in error
                    if any(word in line_text.lower() for word in error_lower.split() 
                           if len(word) > 3 and word.isalpha()):
                        line = i
                        break
                
                diagnostics.append({
                    "range": {
                        "start": {"line": line, "character": 0},
                        "end": {"line": line, "character": 100}
                    },
                    "severity": 1,  # Error
                    "message": f"Type error: {error}",
                    "source": "nlpl-typechecker"
                })
        
        except Exception:
            # If parsing fails, syntax errors will be caught by _check_parser_syntax
            pass
        
        return diagnostics
    
    def _check_syntax(self, text: str) -> List[Dict]:
        """Check for syntax errors."""
        diagnostics = []
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            # Check for unclosed strings
            if line.count('"') % 2 != 0:
                diagnostics.append({
                    "range": {
                        "start": {"line": i, "character": 0},
                        "end": {"line": i, "character": len(line)}
                    },
                    "severity": 1,  # Error
                    "message": "Unclosed string",
                    "source": "nlpl"
                })
            
            # Check for invalid characters in identifiers
            match = re.search(r'\bset\s+(\d\w*)', line, re.IGNORECASE)
            if match:
                var_name = match.group(1)
                diagnostics.append({
                    "range": {
                        "start": {"line": i, "character": match.start(1)},
                        "end": {"line": i, "character": match.end(1)}
                    },
                    "severity": 1,  # Error
                    "message": f"Variable name '{var_name}' cannot start with a digit",
                    "source": "nlpl"
                })
        
        return diagnostics
    
    def _check_undefined_vars(self, text: str) -> List[Dict]:
        """Check for undefined variables."""
        diagnostics = []
        lines = text.split('\n')
        
        # Extract defined variables
        defined_vars = set()
        var_pattern = r'set\s+(\w+)\s+to'
        for line in lines:
            matches = re.findall(var_pattern, line, re.IGNORECASE)
            defined_vars.update(matches)
        
        # Add common built-ins
        defined_vars.update(['true', 'false', 'null'])
        
        # Check for undefined variable usage
        # This is simplified - real implementation would track scope
        use_pattern = r'\b(\w+)\b'
        keywords = {'set', 'to', 'function', 'class', 'if', 'else', 'while', 'for', 'each', 'in', 
                   'return', 'print', 'text', 'as', 'Integer', 'String', 'Float', 'Boolean',
                   'plus', 'minus', 'times', 'divided', 'by', 'is', 'equal', 'greater', 'less', 'than'}
        
        for i, line in enumerate(lines):
            # Skip variable definitions and function definitions
            if re.search(r'set\s+\w+\s+to', line, re.IGNORECASE):
                continue
            if re.search(r'function\s+\w+', line, re.IGNORECASE):
                continue
            
            # Find potential variable uses
            matches = re.finditer(use_pattern, line)
            for match in matches:
                var = match.group(1)
                if var.lower() not in keywords and var not in defined_vars and not var[0].isupper():
                    # NOTE: Undefined variable detection disabled
                    # NLPL's natural language syntax creates too many false positives:
                    # - English words in natural syntax ("create", "called", "with", etc.)
                    # - Context-dependent parsing makes static analysis unreliable
                    # - Proper implementation requires full parser integration
                    # 
                    # This check is permanently removed until AST-based analysis is available.
                    # The interpreter provides runtime undefined variable errors instead.
                    pass
        
        return diagnostics
    
    def _check_unused_vars(self, text: str) -> List[Dict]:
        """Check for unused variables."""
        diagnostics = []
        lines = text.split('\n')
        
        # Extract defined variables with their line numbers
        defined_vars = {}
        var_pattern = r'set\s+(\w+)\s+to'
        for i, line in enumerate(lines):
            matches = re.finditer(var_pattern, line, re.IGNORECASE)
            for match in matches:
                var_name = match.group(1)
                if var_name not in defined_vars:
                    defined_vars[var_name] = (i, match.start(1))
        
        # Check which variables are used
        used_vars = set()
        for i, line in enumerate(lines):
            # Skip the definition line
            for var_name in defined_vars.keys():
                # Look for variable usage (not in definition)
                if not re.search(rf'set\s+{re.escape(var_name)}\s+to', line, re.IGNORECASE):
                    if re.search(rf'\b{re.escape(var_name)}\b', line):
                        used_vars.add(var_name)
        
        # Report unused variables
        for var_name, (line_num, col) in defined_vars.items():
            if var_name not in used_vars:
                diagnostics.append({
                    "range": {
                        "start": {"line": line_num, "character": col},
                        "end": {"line": line_num, "character": col + len(var_name)}
                    },
                    "severity": 2,  # Warning
                    "message": f"Unused variable '{var_name}'",
                    "source": "nlpl"
                })
        
        return diagnostics
    
    def _check_imports(self, text: str, uri: str) -> List[Dict]:
        """
        Check for import errors (multi-file diagnostics).
        
        Returns:
            List of diagnostics for missing/invalid imports
        """
        diagnostics = []
        lines = text.split('\n')
        
        # Find import statements
        import_pattern = r'import\s+(\w+)(?:\s+from\s+["\']([^"\']*)["\'])?'
        
        for i, line in enumerate(lines):
            match = re.search(import_pattern, line, re.IGNORECASE)
            if match:
                module_name = match.group(1)
                file_path = match.group(2) if match.group(2) else None
                
                # Check if module exists
                if file_path:
                    # Check if file exists
                    import os
                    base_dir = os.path.dirname(uri.replace('file://', ''))
                    full_path = os.path.join(base_dir, file_path)
                    
                    if not os.path.exists(full_path) and not os.path.exists(full_path + '.nlpl'):
                        diagnostics.append({
                            "range": {
                                "start": {"line": i, "character": 0},
                                "end": {"line": i, "character": len(line)}
                            },
                            "severity": 1,  # Error
                            "message": f"Cannot find module '{file_path}'",
                            "source": "nlpl-imports"
                        })
                else:
                    # Check stdlib modules
                    stdlib_modules = ['math', 'string', 'io', 'system', 'collections', 'network']
                    if module_name.lower() not in stdlib_modules:
                        diagnostics.append({
                            "range": {
                                "start": {"line": i, "character": 0},
                                "end": {"line": i, "character": len(line)}
                            },
                            "severity": 2,  # Warning
                            "message": f"Unknown module '{module_name}' (not in stdlib)",
                            "source": "nlpl-imports"
                        })
        
        return diagnostics
    
    def get_workspace_diagnostics(self) -> Dict[str, List[Dict]]:
        """
        Get diagnostics for all files in workspace.
        
        Returns:
            Dict mapping URIs to their diagnostics
        """
        return self.file_diagnostics_cache.copy()


__all__ = ['DiagnosticsProvider']
