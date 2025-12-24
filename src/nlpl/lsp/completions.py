"""
Completion Provider
===================

Provides auto-completion suggestions for NLPL code.
"""

from typing import List, Dict, Optional
import re


class CompletionProvider:
    """
    Provides intelligent auto-completion.
    
    Completion types:
    - Keywords (function, class, set, to, etc.)
    - Variables in scope
    - Functions in scope
    - Standard library functions
    - Snippets (function templates, etc.)
    """
    
    def __init__(self, server):
        self.server = server
        
        # NLPL keywords
        self.keywords = [
            # Declarations
            "function", "class", "struct", "union", "enum",
            "set", "to", "as", "of",
            
            # Control flow
            "if", "else", "while", "for", "each", "in",
            "return", "break", "continue",
            "match", "case", "with",
            
            # Types
            "Integer", "Float", "String", "Boolean",
            "List", "Dictionary", "Optional", "Result",
            "Pointer", "Array",
            
            # Operations
            "plus", "minus", "times", "divided by", "modulo",
            "is", "equal", "greater", "less", "than",
            "and", "or", "not",
            
            # Special
            "import", "export", "from",
            "new", "delete", "sizeof", "typeof",
            "true", "false", "null",
            
            # Error handling
            "Ok", "Error", "panic", "assert",
        ]
        
        # Standard library modules
        self.stdlib_modules = {
            "math": ["sqrt", "sin", "cos", "tan", "floor", "ceil", "abs", "max", "min"],
            "string": ["split", "join", "trim", "replace", "substring", "length"],
            "io": ["read_file", "write_file", "print", "input", "read_line"],
            "system": ["exit", "get_env", "set_env", "execute"],
            "collections": ["sort", "reverse", "filter", "map", "reduce"],
            "network": ["http_get", "http_post", "connect", "listen"],
        }
        
        # Snippets
        self.snippets = {
            "function": {
                "label": "function",
                "insertText": "function ${1:name} that takes ${2:param} as ${3:Type} returns ${4:Type}\n    ${5:# body}\n    return ${6:value}",
                "kind": 15,  # Snippet
                "documentation": "Function definition template"
            },
            "class": {
                "label": "class",
                "insertText": "class ${1:Name}\n    property ${2:field} as ${3:Type}\n    \n    function ${4:method}\n        ${5:# body}",
                "kind": 15,
                "documentation": "Class definition template"
            },
            "if": {
                "label": "if",
                "insertText": "if ${1:condition}\n    ${2:# body}",
                "kind": 15,
                "documentation": "If statement template"
            },
            "for": {
                "label": "for",
                "insertText": "for each ${1:item} in ${2:collection}\n    ${3:# body}",
                "kind": 15,
                "documentation": "For loop template"
            },
        }
    
    def get_completions(self, text: str, position) -> List[Dict]:
        """
        Get completion items at position.
        
        Args:
            text: Document text
            position: Cursor position
            
        Returns:
            List of completion items
        """
        completions = []
        
        # Get line content
        lines = text.split('\n')
        if position.line >= len(lines):
            return completions
        
        line = lines[position.line]
        prefix = line[:position.character]
        
        # Get word being typed
        word_match = re.search(r'(\w+)$', prefix)
        current_word = word_match.group(1) if word_match else ''
        
        # Add keyword completions
        for keyword in self.keywords:
            if keyword.startswith(current_word.lower()):
                completions.append({
                    "label": keyword,
                    "kind": 14,  # Keyword
                    "detail": "NLPL keyword",
                    "insertText": keyword
                })
        
        # Add snippet completions
        for name, snippet in self.snippets.items():
            if name.startswith(current_word.lower()):
                completions.append(snippet)
        
        # Add standard library completions
        for module, functions in self.stdlib_modules.items():
            for func in functions:
                if func.startswith(current_word.lower()):
                    completions.append({
                        "label": func,
                        "kind": 3,  # Function
                        "detail": f"from {module}",
                        "documentation": f"Standard library function from {module} module",
                        "insertText": func
                    })
        
        # Add variable completions from current document
        variables = self._extract_variables(text)
        for var in variables:
            if var.startswith(current_word.lower()):
                completions.append({
                    "label": var,
                    "kind": 6,  # Variable
                    "detail": "Variable",
                    "insertText": var
                })
        
        # Add function completions from current document
        functions = self._extract_functions(text)
        for func in functions:
            if func.startswith(current_word.lower()):
                completions.append({
                    "label": func,
                    "kind": 3,  # Function
                    "detail": "Function",
                    "insertText": func
                })
        
        return completions
    
    def _extract_variables(self, text: str) -> List[str]:
        """Extract variable names from text."""
        variables = set()
        
        # Match: set varname to ...
        pattern = r'set\s+(\w+)\s+to'
        matches = re.findall(pattern, text, re.IGNORECASE)
        variables.update(matches)
        
        return list(variables)
    
    def _extract_functions(self, text: str) -> List[str]:
        """Extract function names from text."""
        functions = set()
        
        # Match: function fname ...
        pattern = r'function\s+(\w+)'
        matches = re.findall(pattern, text, re.IGNORECASE)
        functions.update(matches)
        
        return list(functions)


__all__ = ['CompletionProvider']
