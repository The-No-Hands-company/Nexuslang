"""
NLPL Diagnostics and Error Reporting
=====================================

Beautiful, helpful error messages inspired by Rust, Elm, and modern compilers.

Features:
- Colorized output
- Multi-line context
- Caret pointers
- Inline suggestions
- Error codes
- "Did you mean?" fuzzy matching
"""

from nlpl.diagnostics.error_formatter import (
    ErrorFormatter,
    Diagnostic,
    DiagnosticLevel,
    DiagnosticCode
)
from nlpl.diagnostics.source_context import SourceContext
from nlpl.diagnostics.suggestions import SuggestionEngine

__all__ = [
    'ErrorFormatter',
    'Diagnostic',
    'DiagnosticLevel',
    'DiagnosticCode',
    'SourceContext',
    'SuggestionEngine'
]
