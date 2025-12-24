"""
Enhanced error reporting for NLPL.
Provides detailed error messages with source context, suggestions, and formatting.
"""

from typing import Optional, List
import difflib


class NLPLError(Exception):
    """Base class for all NLPL errors."""
    def __init__(self, message: str, line: Optional[int] = None, column: Optional[int] = None,
                 source_line: Optional[str] = None, error_type: str = "Error"):
        self.message = message
        self.line = line
        self.column = column
        self.source_line = source_line
        self.error_type = error_type
        super().__init__(self._format_error())
    
    def _format_error(self) -> str:
        """Format the error message with context."""
        parts = [f"{self.error_type}: {self.message}"]
        
        if self.line is not None:
            parts.append(f"\n  at line {self.line}" + (f", column {self.column}" if self.column else ""))
        
        if self.source_line:
            # Add source line with line number
            line_str = str(self.line) if self.line else "?"
            parts.append(f"\n\n  {line_str} | {self.source_line}")
            
            # Add caret pointer if we have a column
            if self.column is not None:
                # Calculate padding (line number + " | " + column offset)
                padding = len(line_str) + 3 + self.column - 1
                parts.append(f"\n  {' ' * padding}^")
        
        return "".join(parts)


class NLPLSyntaxError(NLPLError):
    """Syntax error with suggestions."""
    def __init__(self, message: str, line: Optional[int] = None, column: Optional[int] = None,
                 source_line: Optional[str] = None, suggestion: Optional[str] = None,
                 expected: Optional[str] = None, got: Optional[str] = None):
        self.suggestion = suggestion
        self.expected = expected
        self.got = got
        super().__init__(message, line, column, source_line, "Syntax Error")
    
    def _format_error(self) -> str:
        """Format syntax error with additional context."""
        base = super()._format_error()
        
        if self.expected and self.got:
            base += f"\n\n  Expected: {self.expected}"
            base += f"\n  Got: {self.got}"
        
        if self.suggestion:
            base += f"\n\n  💡 Suggestion: {self.suggestion}"
        
        return base


class NLPLRuntimeError(NLPLError):
    """Runtime error with stack trace."""
    def __init__(self, message: str, line: Optional[int] = None, column: Optional[int] = None,
                 source_line: Optional[str] = None, stack_trace: Optional[List[str]] = None,
                 variable_context: Optional[dict] = None):
        self.stack_trace = stack_trace or []
        self.variable_context = variable_context or {}
        super().__init__(message, line, column, source_line, "Runtime Error")
    
    def _format_error(self) -> str:
        """Format runtime error with stack trace."""
        base = super()._format_error()
        
        if self.stack_trace:
            base += "\n\n  Call stack:"
            for i, frame in enumerate(reversed(self.stack_trace)):
                base += f"\n    {i + 1}. {frame}"
        
        if self.variable_context:
            base += "\n\n  Local variables:"
            for name, value in self.variable_context.items():
                value_str = repr(value)
                if len(value_str) > 50:
                    value_str = value_str[:47] + "..."
                base += f"\n    {name} = {value_str}"
        
        return base


class NLPLNameError(NLPLError):
    """Name error with did-you-mean suggestions."""
    def __init__(self, name: str, line: Optional[int] = None, column: Optional[int] = None,
                 source_line: Optional[str] = None, available_names: Optional[List[str]] = None):
        self.name = name
        self.available_names = available_names or []
        
        # Find similar names
        self.suggestions = get_close_matches(name, self.available_names)
        
        message = f"Name '{name}' is not defined"
        super().__init__(message, line, column, source_line, "Name Error")
    
    def _format_error(self) -> str:
        """Format name error with suggestions."""
        base = super()._format_error()
        
        if self.suggestions:
            if len(self.suggestions) == 1:
                base += f"\n\n  💡 Did you mean: '{self.suggestions[0]}'?"
            else:
                base += f"\n\n  💡 Did you mean one of these?"
                for suggestion in self.suggestions[:3]:  # Show top 3
                    base += f"\n    • {suggestion}"
        
        return base


class NLPLTypeError(NLPLError):
    """Type error with type information."""
    def __init__(self, message: str, line: Optional[int] = None, column: Optional[int] = None,
                 source_line: Optional[str] = None, expected_type: Optional[str] = None,
                 got_type: Optional[str] = None):
        self.expected_type = expected_type
        self.got_type = got_type
        super().__init__(message, line, column, source_line, "Type Error")
    
    def _format_error(self) -> str:
        """Format type error with type info."""
        base = super()._format_error()
        
        if self.expected_type and self.got_type:
            base += f"\n\n  Expected type: {self.expected_type}"
            base += f"\n  Got type: {self.got_type}"
        
        return base


def get_close_matches(word: str, possibilities: List[str], n: int = 3, cutoff: float = 0.6) -> List[str]:
    """
    Get close matches to a word from a list of possibilities.
    Uses difflib for fuzzy string matching.
    """
    if not word or not possibilities:
        return []
    
    # Use difflib to find similar strings
    matches = difflib.get_close_matches(word, possibilities, n=n, cutoff=cutoff)
    return matches


def format_source_context(source: str, line: int, column: int, context_lines: int = 2) -> str:
    """
    Format source code context around an error location.
    
    Args:
        source: Full source code
        line: Line number (1-indexed)
        column: Column number (1-indexed)
        context_lines: Number of lines to show before and after
    
    Returns:
        Formatted source context with line numbers and caret pointer
    """
    lines = source.split('\n')
    
    # Adjust for 0-indexed list
    error_line_idx = line - 1
    
    # Calculate range
    start_idx = max(0, error_line_idx - context_lines)
    end_idx = min(len(lines), error_line_idx + context_lines + 1)
    
    # Build context
    result = []
    max_line_num = end_idx
    num_width = len(str(max_line_num))
    
    for i in range(start_idx, end_idx):
        line_num = i + 1
        prefix = f"  {line_num:{num_width}} | "
        
        if i == error_line_idx:
            # Error line - highlight it
            result.append(f"{prefix}{lines[i]}")
            # Add caret pointer
            padding = len(prefix) + column - 1
            result.append(f"  {' ' * padding}^")
        else:
            # Context line
            result.append(f"{prefix}{lines[i]}")
    
    return '\n'.join(result)


def suggest_correction(error_type: str, context: dict) -> Optional[str]:
    """
    Suggest a correction based on the error type and context.
    
    Args:
        error_type: Type of error (e.g., "missing_end", "undefined_variable")
        context: Additional context information
    
    Returns:
        Suggestion string or None
    """
    suggestions = {
        "missing_end": "Make sure to close all blocks (if, while, for, function, class) with 'end'",
        "unexpected_token": "Check for missing or extra keywords, operators, or punctuation",
        "undefined_variable": "Declare variables with 'set <name> to <value>' before using them",
        "undefined_function": "Define functions with 'function <name>' or import them from a module",
        "type_mismatch": "Check that you're using compatible types in operations",
        "indentation_error": "Use consistent indentation (spaces or tabs, not mixed)",
        "missing_colon": "Some statements may need a colon ':' at the end",
        "invalid_syntax": "Review the language syntax - this construct is not valid",
        "division_by_zero": "Check that the divisor is not zero",
        "index_out_of_range": "Ensure the index is within the list/array bounds",
        "key_not_found": "Check that the dictionary key exists before accessing it",
    }
    
    return suggestions.get(error_type)
