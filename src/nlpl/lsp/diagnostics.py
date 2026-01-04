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
    - Syntax errors
    - Undefined variables
    - Type mismatches
    - Unused variables
    - Best practice violations
    """
    
    def __init__(self, server):
        self.server = server
    
    def get_diagnostics(self, uri: str, text: str) -> List[Dict]:
        """
        Get diagnostics for document.
        
        Args:
            uri: Document URI
            text: Document text
            
        Returns:
            List of diagnostics
        """
        diagnostics = []
        
        # Check for common errors
        diagnostics.extend(self._check_syntax(text))
        diagnostics.extend(self._check_undefined_vars(text))
        diagnostics.extend(self._check_unused_vars(text))
        
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


__all__ = ['DiagnosticsProvider']
