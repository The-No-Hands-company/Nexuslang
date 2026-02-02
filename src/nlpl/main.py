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
from .tools import get_profiler, enable_profiling, disable_profiling

def run_program(source_code, debug=False, type_check=True, profiler=None):
    """
    Run an NLPL program from source code.
    
    Args:
        source_code (str): The source code of the NLPL program
        debug (bool): Whether to enable debug mode
        type_check (bool): Whether to enable type checking
        profiler: Optional profiler instance for performance tracking
    
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
    
    # Attach profiler if provided
    if profiler:
        interpreter.profiler = profiler
    
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
    parser.add_argument('file', nargs='?', help='The NLPL file to execute (omit for interactive REPL)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--no-type-check', action='store_true', help='Disable type checking')
    parser.add_argument('--repl', action='store_true', help='Start interactive REPL (default if no file)')
    parser.add_argument('--debugger', action='store_true', help='Enable interactive debugger')
    parser.add_argument('--break', '-b', dest='breakpoints', action='append',
                       help='Set breakpoint at line (can be used multiple times)')
    parser.add_argument('--profile', action='store_true', help='Enable runtime profiling')
    parser.add_argument('--profile-output', help='Save profile results to JSON file')
    parser.add_argument('--profile-flamegraph', help='Export flamegraph format to file')
    
    args = parser.parse_args()
    
    # Initialize profiler if requested
    profiler = None
    if args.profile:
        profiler = enable_profiling()
        profiler.start()
    
    # Start REPL if no file specified or --repl flag
    if args.file is None or (args.repl and not args.file):
        from .repl.repl import REPL
        repl = REPL(debug=args.debug, type_check=not args.no_type_check)
        try:
            repl.run()
        except Exception as e:
            print(f"REPL Error: {e}")
            if args.debug:
                import traceback
                traceback.print_exc()
            sys.exit(1)
        return
    
    # Check if the file exists
    if not os.path.isfile(args.file):
        print(f"Error: File '{args.file}' not found")
        sys.exit(1)
    
    # Read the file
    with open(args.file, 'r') as f:
        source_code = f.read()
    
    # Run with debugger if requested
    if args.debugger or args.breakpoints:
        from .debugger.debugger import Debugger
        from .parser.lexer import Lexer
        from .parser.parser import Parser
        
        # Setup runtime and interpreter
        runtime = Runtime()
        register_stdlib(runtime)
        interpreter = Interpreter(runtime, enable_type_checking=not args.no_type_check)
        
        # Create and attach debugger
        debugger = Debugger(interpreter, interactive=True)
        interpreter.debugger = debugger
        interpreter.current_file = args.file
        
        # Set breakpoints from command line
        if args.breakpoints:
            for bp in args.breakpoints:
                try:
                    line = int(bp)
                    debugger.add_breakpoint(args.file, line)
                except ValueError:
                    print(f"Warning: Invalid breakpoint: {bp}")
        
        print(f"Debugging: {args.file}")
        if args.breakpoints:
            print(f"Breakpoints: {len(debugger.list_breakpoints())}")
        print()
        
        try:
            # Parse
            lexer = Lexer(source_code)
            tokens = lexer.tokenize()
            
            if args.debug:
                print("Tokens:")
                for token in tokens:
                    print(f"  {token}")
            
            parser = Parser(tokens)
            ast = parser.parse()
            
            if args.debug:
                print("\nAST:")
                print_ast(ast)
            
            # Execute with debugger
            result = interpreter.interpret(ast)
            
            if result is not None:
                print(f"\nProgram result: {result}")
            
            print("\n" + "="*60)
            debugger.print_statistics()
        
        except Exception as e:
            print(f"\nError: {e}")
            if args.debug:
                import traceback
                traceback.print_exc()
            sys.exit(1)
        
        return
    
    # Run normally without debugger
    try:
        result = run_program(source_code, args.debug, not args.no_type_check, profiler)
        if result is not None:
            print(f"Program result: {result}")
        
        # Print and export profiling results if enabled
        if profiler:
            profiler.stop()
            print("\n" + "="*70)
            profiler.print_report()
            
            if args.profile_output:
                profiler.export_json(args.profile_output)
                print(f"\nProfile results saved to: {args.profile_output}")
            
            if args.profile_flamegraph:
                profiler.export_flamegraph(args.profile_flamegraph)
                print(f"Flamegraph data saved to: {args.profile_flamegraph}")
    except Exception as e:
        print(f"Error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 