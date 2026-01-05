"""
NLPL Language Server Protocol (LSP) Implementation
===================================================

Provides IDE integration for NLPL:
- Auto-completion
- Go-to-definition
- Hover documentation
- Real-time diagnostics
- Rename refactoring
- Code formatting
- Symbol search

Based on LSP specification: https://microsoft.github.io/language-server-protocol/
"""

from nlpl.lsp.server import NLPLLanguageServer
from nlpl.lsp.completions import CompletionProvider
from nlpl.lsp.definitions import DefinitionProvider
from nlpl.lsp.hover import HoverProvider
from nlpl.lsp.diagnostics import DiagnosticsProvider
from nlpl.lsp.symbols import SymbolProvider
from nlpl.lsp.code_actions import CodeActionsProvider
from nlpl.lsp.signature_help import SignatureHelpProvider

__all__ = [
    'NLPLLanguageServer',
    'CompletionProvider',
    'DefinitionProvider',
    'HoverProvider',
    'DiagnosticsProvider',
    'SymbolProvider',
    'CodeActionsProvider',
    'SignatureHelpProvider'
]
