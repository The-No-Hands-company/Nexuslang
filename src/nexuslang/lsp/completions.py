"""
Completion Provider
===================

Provides auto-completion suggestions for NexusLang code.
"""

from typing import List, Dict, Optional, Type
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
        
        # NexusLang keywords
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
            "create", "channel", "send", "receive", "close",
            "macro", "expand", "comptime", "eval", "const",
            
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
    
    def get_keyword_completions(self) -> List[Dict]:
        """Return completion items for all known NexusLang keywords."""
        return [
            {
                "label": kw,
                "kind": 14,  # Keyword
                "detail": "keyword",
                "insertText": kw
            }
            for kw in self.keywords
        ]

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
        
        # Context-aware completions -----------------------------------------------

        # After "set X to" - suggest values/functions
        if re.search(r'\bset\s+\w+\s+to\s*$', prefix, re.IGNORECASE):
            completions.extend(self._get_value_completions(text, current_word))
        
        # After "function X with" or "function X that takes" - parameter patterns
        elif re.search(r'\bfunction\s+\w+\s+(?:with|that\s+takes)\s*$', prefix, re.IGNORECASE):
            completions.append({
                "label": "param as Type",
                "kind": 15,
                "insertText": "${1:param_name} as ${2:Type}",
                "documentation": "Parameter declaration"
            })
        
        # After "returns" - suggest types
        elif re.search(r'\breturns\s*$', prefix, re.IGNORECASE):
            completions.extend(self._get_type_completions(current_word))
        
        # After "as" - suggest types  
        elif re.search(r'\bas\s*$', prefix, re.IGNORECASE):
            completions.extend(self._get_type_completions(current_word))
        
        # After "from" - suggest modules
        elif re.search(r'\bfrom\s*$', prefix, re.IGNORECASE):
            for module in self.stdlib_modules.keys():
                if module.lower().startswith(current_word.lower()):
                    completions.append({
                        "label": module,
                        "kind": 9,  # Module
                        "detail": "Module",
                        "insertText": module
                    })
        
        # After "import" - suggest modules
        elif re.search(r'\bimport\s*$', prefix, re.IGNORECASE):
            for module in self.stdlib_modules.keys():
                if module.lower().startswith(current_word.lower()):
                    completions.append({
                        "label": module,
                        "kind": 9,
                        "detail": "Module",
                        "insertText": module
                    })

        # After "expand" - suggest known macro names from document
        elif re.search(r'\bexpand\s*$', prefix, re.IGNORECASE):
            for macro_name in self._extract_macro_names(text):
                if macro_name.lower().startswith(current_word.lower()):
                    completions.append({
                        "label": macro_name,
                        "kind": 3,  # Function-like symbol
                        "detail": "Macro",
                        "insertText": macro_name,
                        "documentation": "Expand macro"
                    })

        # After "comptime" - suggest comptime forms
        elif re.search(r'\bcomptime\s*$', prefix, re.IGNORECASE):
            completions.extend([
                {
                    "label": "eval",
                    "kind": 14,
                    "insertText": "eval ${1:expression}",
                    "documentation": "Evaluate expression at compile time"
                },
                {
                    "label": "const",
                    "kind": 14,
                    "insertText": "const ${1:NAME} is ${2:expression}",
                    "documentation": "Define immutable compile-time constant"
                },
                {
                    "label": "assert",
                    "kind": 14,
                    "insertText": "assert ${1:condition}",
                    "documentation": "Assert compile-time condition"
                },
            ])
        
        # After "create" - suggest collection types
        elif re.search(r'\bcreate\s*$', prefix, re.IGNORECASE):
            for coll_type in ["channel", "list", "dictionary", "set", "tuple", "queue", "stack"]:
                completions.append({
                    "label": f"{coll_type}",
                    "kind": 14,
                    "insertText": f"{coll_type}",
                    "documentation": f"Create a {coll_type}"
                })

        # After "send" - suggest send statement snippet
        elif re.search(r'\bsend\s*$', prefix, re.IGNORECASE):
            completions.append({
                "label": "send value to channel",
                "kind": 15,
                "insertText": "${1:value} to ${2:channel}",
                "documentation": "Send a value to a channel"
            })

        # After "send <value> to" - suggest channel variables
        elif re.search(r'\bsend\s+.+\s+to\s*$', prefix, re.IGNORECASE):
            for channel_name in self._extract_channel_variables(text):
                completions.append({
                    "label": channel_name,
                    "kind": 6,
                    "detail": "Channel variable",
                    "insertText": channel_name,
                    "documentation": "Channel"
                })

        # After "receive from" - suggest channel variables
        elif re.search(r'\breceive\s+from\s*$', prefix, re.IGNORECASE):
            for channel_name in self._extract_channel_variables(text):
                completions.append({
                    "label": channel_name,
                    "kind": 6,
                    "detail": "Channel variable",
                    "insertText": channel_name,
                    "documentation": "Channel"
                })

        # After "<funcname> with " — suggest named parameters from function definition
        elif re.search(r'\b(\w+)\s+with\s+$', prefix, re.IGNORECASE):
            func_match = re.search(r'\b(\w+)\s+with\s+$', prefix, re.IGNORECASE)
            if func_match:
                func_name = func_match.group(1)
                named_params = self._get_named_param_completions(text, func_name)
                if named_params:
                    completions.extend(named_params)
                else:
                    # Fall through to general completions below
                    completions.extend(self._get_general_completions(text, current_word))

        # After "<funcname> with param: val and " — suggest more named parameters
        elif re.search(r'\b(\w+)\s+with\s+.+\s+and\s+$', prefix, re.IGNORECASE):
            func_match = re.search(r'\b(\w+)\s+with\s+', prefix, re.IGNORECASE)
            if func_match:
                func_name = func_match.group(1)
                named_params = self._get_named_param_completions(text, func_name)
                if named_params:
                    completions.extend(named_params)
                else:
                    completions.extend(self._get_general_completions(text, current_word))

        # General completions
        else:
            completions.extend(self._get_general_completions(text, current_word))
        
        return completions

    def _get_general_completions(self, text: str, current_word: str) -> List[Dict]:
        """Return general (keyword + user symbol) completions filtered by current_word."""
        completions = []

        # Add keyword completions
        for keyword in self.keywords:
            if keyword.lower().startswith(current_word.lower()):
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
            if var.lower().startswith(current_word.lower()):
                completions.append({
                    "label": var,
                    "kind": 6,  # Variable
                    "detail": "Variable",
                    "insertText": var
                })

        # Add function completions from current document
        functions = self._extract_functions(text)
        for func in functions:
            if func.lower().startswith(current_word.lower()):
                completions.append({
                    "label": func,
                    "kind": 3,  # Function
                    "detail": "Function",
                    "insertText": func
                })

        # Add class completions from current document
        classes = self._extract_classes(text)
        for cls in classes:
            if cls.lower().startswith(current_word.lower()):
                completions.append({
                    "label": cls,
                    "kind": 7,  # Class
                    "detail": "Class",
                    "insertText": cls
                })

        return completions

    def _get_named_param_completions(self, text: str, func_name: str) -> List[Dict]:
        """Suggest named parameters for a specific function call."""
        completions = []
        # Try to find the function definition and extract its parameters
        # Support both "function X with param as Type" and "function X that takes param as Type"
        func_pattern = rf'\bfunction\s+{re.escape(func_name)}\s+(?:with|that\s+takes)\s+(.+?)(?:\s+returns|\s*$)'
        match = re.search(func_pattern, text, re.IGNORECASE | re.MULTILINE)
        if not match:
            return completions
        param_str = match.group(1)
        # Extract "paramname as Type" pairs
        param_matches = re.finditer(r'(\w+)\s+as\s+\w+', param_str, re.IGNORECASE)
        for m in param_matches:
            param_name = m.group(1)
            # Skip non-param tokens like "and"
            if param_name.lower() in ('and', 'with', 'returns', 'default', 'to'):
                continue
            completions.append({
                "label": f"{param_name}:",
                "kind": 14,  # Keyword (represents a named arg label)
                "detail": "named parameter",
                "insertText": f"{param_name}: ${{1:value}}"
            })
        return completions
    
    def _get_type_completions(self, current_word: str) -> List[Dict]:
        """Get type name completions."""
        types = [
            "Integer", "Float", "String", "Boolean",
            "List", "Dictionary", "Set", "Tuple",
            "Optional", "Result", "Pointer", "Array",
            "Queue", "Stack", "Channel"
        ]
        
        completions = []
        for type_name in types:
            if type_name.lower().startswith(current_word.lower()):
                completions.append({
                    "label": type_name,
                    "kind": 7,  # Class (type)
                    "detail": "Type",
                    "insertText": type_name
                })
        
        return completions
    
    def _get_value_completions(self, text: str, current_word: str) -> List[Dict]:
        """Get value/expression completions."""
        completions = []
        
        # Add constants
        for const in ["true", "false", "null"]:
            if const.startswith(current_word.lower()):
                completions.append({
                    "label": const,
                    "kind": 21,  # Constant
                    "detail": "Constant",
                    "insertText": const
                })
        
        # Add "create" for collection initialization
        if "create".startswith(current_word.lower()):
            completions.append({
                "label": "create",
                "kind": 14,
                "detail": "Create collection",
                "insertText": "create ${1:list}"
            })
        
        # Add "new" for object instantiation
        if "new".startswith(current_word.lower()):
            completions.append({
                "label": "new",
                "kind": 14,
                "detail": "Create object",
                "insertText": "new ${1:ClassName}"
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
    
    def _extract_classes(self, text: str) -> List[str]:
        """Extract class names from text."""
        classes = set()
        
        # Match: class ClassName ...
        pattern = r'class\s+(\w+)'
        matches = re.findall(pattern, text, re.IGNORECASE)
        classes.update(matches)
        
        return list(classes)

    def _extract_channel_variables(self, text: str) -> List[str]:
        """Extract channel variable names from text."""
        channels = set()

        # Match: set ch to create channel
        create_pattern = r'set\s+(\w+)\s+to\s+create\s+channel\b'
        channels.update(re.findall(create_pattern, text, re.IGNORECASE))

        # Match: set ch as Channel<Integer> to ... or set ch as Channel to ...
        typed_pattern = r'set\s+(\w+)\s+as\s+Channel(?:\s*<[^>]+>)?\s+to\b'
        channels.update(re.findall(typed_pattern, text, re.IGNORECASE))

        return list(channels)

    def _extract_macro_names(self, text: str) -> List[str]:
        """Extract macro names from local document for expand completions."""
        names = set()
        pattern = re.compile(r'^\s*macro\s+(\w+)\b', re.IGNORECASE)
        for line in text.split('\n'):
            m = pattern.match(line)
            if m:
                names.add(m.group(1))
        return sorted(names)

__all__ = ['CompletionProvider']
