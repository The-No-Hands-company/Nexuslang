"""
NLPL - Natural Language Programming Language

A truly universal programming language that combines natural English-like syntax
with low-level capabilities.
"""

import sys

__version__ = "0.1.0"
__author__ = "The No Hands Company"

# Python 3.14 has import system bugs - use compatibility layer
if False: # sys.version_info >= (3, 14): # Forced disabled for debugging
    from .py314_compat import load_module_direct
    from pathlib import Path
    
    # Load modules directly to avoid import hang
    _nlpl_dir = Path(__file__).parent
    _lexer_module = load_module_direct(
        str(_nlpl_dir / 'parser' / 'lexer.py'),
        'nlpl.parser.lexer'
    )
    Lexer = _lexer_module.Lexer
    Token = _lexer_module.Token
    TokenType = _lexer_module.TokenType
    
    _parser_module = load_module_direct(
        str(_nlpl_dir / 'parser' / 'parser.py'),
        'nlpl.parser.parser'
    )
    Parser = _parser_module.Parser
    
    _interp_module = load_module_direct(
        str(_nlpl_dir / 'interpreter' / 'interpreter.py'),
        'nlpl.interpreter.interpreter'
    )
    Interpreter = _interp_module.Interpreter
    
    _runtime_module = load_module_direct(
        str(_nlpl_dir / 'runtime' / 'runtime.py'),
        'nlpl.runtime.runtime'
    )
    Runtime = _runtime_module.Runtime
else:
    # Normal import for Python < 3.14
    from .parser.lexer import Lexer, Token, TokenType
    from .parser.parser import Parser
    from .interpreter.interpreter import Interpreter
    from .runtime.runtime import Runtime

__all__ = [
    "Lexer",
    "Token", 
    "TokenType",
    "Parser",
    "Interpreter",
    "Runtime",
]
