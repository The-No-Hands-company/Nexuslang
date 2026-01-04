"""
NLPL Code Formatter
===================

Formats NLPL code according to the NLPL style guide.

Formatting Rules:
- 4 spaces for indentation
- Consistent spacing around operators
- Line length under 100 characters
- Blank lines to separate logical sections
- Normalized keyword spacing
"""

import re
from typing import List, Tuple


class NLPLFormatter:
    """
    Formats NLPL code according to style guidelines.
    
    Rules:
    1. Indentation: 4 spaces per level
    2. Spacing: Consistent spacing around operators and keywords
    3. Line length: Keep under 100 characters (soft limit)
    4. Blank lines: Separate functions, classes, and logical sections
    5. Trailing whitespace: Remove all trailing whitespace
    """
    
    def __init__(self):
        self.indent_size = 4
        self.max_line_length = 100
        
        # Keywords that increase indentation
        self.indent_keywords = {
            'function', 'class', 'if', 'else if', 'else',
            'while', 'for', 'try', 'catch', 'finally',
            'struct', 'union', 'enum', 'interface', 'trait',
            'switch', 'case', 'default'
        }
        
        # Keywords that decrease indentation (block endings)
        self.dedent_keywords = {
            'end', 'else', 'else if', 'catch', 'finally',
            'case', 'default'
        }
        
        # Binary operators that should have spacing
        self.binary_operators = [
            'plus', 'minus', 'times', 'divided by', 'modulo',
            'is equal to', 'is not equal to', 'is greater than',
            'is less than', 'is greater than or equal to',
            'is less than or equal to', 'and', 'or',
            'to'  # for assignments: set x to y
        ]
    
    def format(self, code: str) -> str:
        """
        Format NLPL code.
        
        Args:
            code: Raw NLPL code
            
        Returns:
            Formatted NLPL code
        """
        lines = code.split('\n')
        formatted_lines = []
        current_indent = 0
        prev_line_blank = False
        
        for i, line in enumerate(lines):
            # Strip trailing whitespace
            line = line.rstrip()
            
            # Skip empty lines but track them
            if not line.strip():
                # Avoid multiple consecutive blank lines
                if not prev_line_blank:
                    formatted_lines.append('')
                    prev_line_blank = True
                continue
            
            prev_line_blank = False
            
            # Normalize spacing
            line = self._normalize_spacing(line)
            
            # Calculate indentation
            stripped = line.lstrip()
            
            # Check if this line should dedent before formatting
            should_dedent_before = self._should_dedent_before(stripped)
            if should_dedent_before and current_indent > 0:
                current_indent -= 1
            
            # Apply indentation
            indented_line = (' ' * (current_indent * self.indent_size)) + stripped
            
            # Check if this line should indent after formatting
            should_indent_after = self._should_indent_after(stripped)
            if should_indent_after:
                current_indent += 1
            
            # Check if this line should dedent after formatting (e.g., 'end')
            should_dedent_after = self._should_dedent_after(stripped)
            if should_dedent_after and current_indent > 0:
                current_indent -= 1
            
            formatted_lines.append(indented_line)
            
            # Add blank line after function/class definitions
            if self._should_add_blank_after(stripped) and i < len(lines) - 1:
                next_line = lines[i + 1].strip() if i + 1 < len(lines) else ''
                if next_line and not next_line.startswith('#'):
                    formatted_lines.append('')
        
        # Join lines and ensure single newline at end
        result = '\n'.join(formatted_lines)
        
        # Remove trailing blank lines but keep one newline at end
        result = result.rstrip() + '\n'
        
        return result
    
    def _normalize_spacing(self, line: str) -> str:
        """Normalize spacing in a line."""
        # Don't modify comments
        if line.strip().startswith('#'):
            return line.lstrip()
        
        # Don't modify string literals (basic protection)
        # This is a simplified approach - a full implementation would need proper parsing
        if '"' in line or "'" in line:
            # Just strip leading/trailing whitespace for lines with strings
            return line.strip()
        
        # Normalize spacing around operators
        result = line.strip()
        
        # Normalize spacing around 'to' in assignments (but not in words like 'total')
        # Only match 'to' when it's a standalone word
        result = re.sub(r'\b(set\s+\S+)\s+to\s+', r'\1 to ', result)
        
        # Normalize spacing around comparison operators
        result = re.sub(r'\s+is\s+equal\s+to\s+', ' is equal to ', result)
        result = re.sub(r'\s+is\s+not\s+equal\s+to\s+', ' is not equal to ', result)
        result = re.sub(r'\s+is\s+greater\s+than\s+or\s+equal\s+to\s+', ' is greater than or equal to ', result)
        result = re.sub(r'\s+is\s+less\s+than\s+or\s+equal\s+to\s+', ' is less than or equal to ', result)
        result = re.sub(r'\s+is\s+greater\s+than\s+', ' is greater than ', result)
        result = re.sub(r'\s+is\s+less\s+than\s+', ' is less than ', result)
        
        # Normalize spacing around arithmetic operators (only as standalone words)
        result = re.sub(r'\s+\bplus\b\s+', ' plus ', result)
        result = re.sub(r'\s+\bminus\b\s+', ' minus ', result)
        result = re.sub(r'\s+\btimes\b\s+', ' times ', result)
        result = re.sub(r'\s+divided\s+by\s+', ' divided by ', result)
        
        # Normalize spacing around logical operators (only as standalone words)
        result = re.sub(r'\s+\band\b\s+', ' and ', result)
        result = re.sub(r'\s+\bor\b\s+', ' or ', result)
        
        # Clean up multiple spaces
        result = re.sub(r'\s{2,}', ' ', result)
        
        return result
    
    def _should_indent_after(self, line: str) -> bool:
        """Check if indentation should increase after this line."""
        line_lower = line.lower().strip()
        
        # Function definitions (including with modifiers)
        if line_lower.startswith('function '):
            return True
        if line_lower.startswith('public function ') or line_lower.startswith('private function '):
            return True
        if line_lower.startswith('static function '):
            return True
        
        # Class definitions
        if line_lower.startswith('class '):
            return True
        
        # Struct, union, enum definitions
        if line_lower.startswith('struct ') or line_lower.startswith('union ') or line_lower.startswith('enum '):
            return True
        
        # Interface, trait definitions
        if line_lower.startswith('interface ') or line_lower.startswith('trait '):
            return True
        
        # Control flow
        if line_lower.startswith('if '):
            return True
        if line_lower.startswith('else if '):
            return True
        if line_lower.startswith('else'):
            return True
        if line_lower.startswith('while '):
            return True
        if line_lower.startswith('for '):
            return True
        
        # Error handling
        if line_lower.startswith('try'):
            return True
        if line_lower.startswith('catch '):
            return True
        if line_lower.startswith('finally'):
            return True
        
        # Switch statements
        if line_lower.startswith('switch '):
            return True
        if line_lower.startswith('case '):
            return True
        if line_lower.startswith('default'):
            return True
        
        return False
    
    def _should_dedent_before(self, line: str) -> bool:
        """Check if indentation should decrease before this line."""
        line_lower = line.lower().strip()
        
        # End keyword - dedent before formatting
        if line_lower == 'end' or line_lower.startswith('end '):
            return True
        
        # Else, else if
        if line_lower.startswith('else'):
            return True
        
        # Catch, finally
        if line_lower.startswith('catch ') or line_lower.startswith('finally'):
            return True
        
        # Case, default (in switch)
        if line_lower.startswith('case ') or line_lower.startswith('default'):
            return True
        
        return False
    
    def _should_dedent_after(self, line: str) -> bool:
        """Check if indentation should decrease after this line."""
        # No longer needed since 'end' dedents before
        return False
    
    def _should_add_blank_after(self, line: str) -> bool:
        """Check if a blank line should be added after this line."""
        line_lower = line.lower().strip()
        
        # After 'end' of function or class
        if line_lower == 'end' or line_lower.startswith('end '):
            return True
        
        return False
    
    def get_formatting_edits(self, text: str) -> List[dict]:
        """
        Get LSP text edits for formatting.
        
        Args:
            text: Original text
            
        Returns:
            List of LSP TextEdit objects
        """
        formatted = self.format(text)
        
        # If no changes, return empty list
        if formatted == text:
            return []
        
        # Calculate the range for the entire document
        lines = text.split('\n')
        
        # Return a single edit that replaces the entire document
        return [{
            'range': {
                'start': {'line': 0, 'character': 0},
                'end': {'line': len(lines), 'character': 0}
            },
            'newText': formatted
        }]


__all__ = ['NLPLFormatter']
