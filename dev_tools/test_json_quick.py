#!/usr/bin/env python3
"""Quick test script for JSON module"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from nlpl.parser.lexer import Lexer
from nlpl.parser.parser import Parser
from nlpl.interpreter.interpreter import Interpreter
from nlpl.runtime.runtime import Runtime
from nlpl.stdlib import register_stdlib

# Read test file
with open(sys.argv[1], 'r') as f:
    source_code = f.read()

# Lex and parse
lexer = Lexer(source_code)
tokens = lexer.tokenize()
parser = Parser(tokens)
ast = parser.parse()

# Create runtime and interpreter
runtime = Runtime()
register_stdlib(runtime)
interpreter = Interpreter(runtime)

# Execute
interpreter.interpret(ast)
