"""
NLPL Language Server Protocol (LSP) Implementation
===================================================

Provides IDE integration for NexusLang:
- Auto-completion
- Go-to-definition
- Hover documentation
- Real-time diagnostics
- Rename refactoring
- Code formatting
- Symbol search

Based on LSP specification: https://microsoft.github.io/language-server-protocol/
"""

from nexuslang.lsp.server import NLPLLanguageServer
from nexuslang.lsp.completions import CompletionProvider
from nexuslang.lsp.definitions import DefinitionProvider
from nexuslang.lsp.hover import HoverProvider
from nexuslang.lsp.diagnostics import DiagnosticsProvider
from nexuslang.lsp.symbols import SymbolProvider
from nexuslang.lsp.code_actions import CodeActionsProvider
from nexuslang.lsp.signature_help import SignatureHelpProvider

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
