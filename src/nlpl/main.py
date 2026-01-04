"""
Main module for the NLPL interpreter.
This is the entry point for the NLPL interpreter.
"""

import sys
import os
import argparse
import traceback

from .parser.lexer import Lexer
from .parser.parser import Parser
from .interpreter.interpreter import Interpreter
from .runtime.runtime import Runtime
from .stdlib import register_stdlib

def run_program(source_code, debug=False, type_check=True):
    """
    Run an NLPL program from source code.
    
    Args:
        source_code (str): The source code of the NLPL program
        debug (bool): Whether to enable debug mode
        type_check (bool): Whether to enable type checking
    
    Returns:
        The result of the program execution
    """
    # Initialize the runtime
    runtime = Runtime()
    
    # Register standard library functions
    register_stdlib(runtime)
    
    # Initialize components
    lexer = Lexer(source_code)
    tokens = lexer.tokenize()
    
    if debug:
        print("Tokens:")
        for token in tokens:
            print(f"  {token}")
    
    parser = Parser(tokens)
    ast = parser.parse()
    
    if debug:
        print("\nAST:")
        print_ast(ast)
    
    interpreter = Interpreter(runtime, enable_type_checking=type_check)
    
    try:
        result = interpreter.interpret(ast)
        return result
    except TypeError as e:
        print(f"Type Error: {str(e)}")
        return None
    except Exception as e:
        if debug:
            traceback.print_exc()
        else:
            print(f"Runtime Error: {str(e)}")
        return None

def print_ast(node, indent=0):
    """Print the AST in a readable format for debugging."""
    indent_str = "  " * indent
    if hasattr(node, 'statements'):
        print(f"{indent_str}{node}")
        for stmt in node.statements:
            print_ast(stmt, indent + 1)
    elif hasattr(node, 'body') and isinstance(node.body, list):
        print(f"{indent_str}{node}")
        for stmt in node.body:
            print_ast(stmt, indent + 1)
    else:
        print(f"{indent_str}{node}")

def main():
    """Main entry point for the NLPL interpreter."""
    parser = argparse.ArgumentParser(description='Natural Language Programming Language Interpreter')
    parser.add_argument('file', help='The NLPL file to execute')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--no-type-check', action='store_true', help='Disable type checking')
    
    args = parser.parse_args()
    
    # Check if the file exists
    if not os.path.isfile(args.file):
        print(f"Error: File '{args.file}' not found")
        sys.exit(1)
    
    # Read the file
    with open(args.file, 'r') as f:
        source_code = f.read()
    
    # Run the program
    try:
        result = run_program(source_code, args.debug, not args.no_type_check)
        if result is not None:
            print(f"Program result: {result}")
    except Exception as e:
        print(f"Error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 