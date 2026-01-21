#!/usr/bin/env python3
"""
NLPL LLVM Compiler
==================

Compile NLPL source code to native executables using LLVM backend.

Usage:
    python nlplc_llvm.py input.nlpl -o output         # Compile to executable
    python nlplc_llvm.py input.nlpl --ir               # Show LLVM IR only
    python nlplc_llvm.py input.nlpl --obj output.o     # Compile to object file
    
Examples:
    python nlplc_llvm.py test.nlpl -o test
    ./test  # Run the compiled executable
"""

import sys
import os
import argparse
import importlib.util

# Add src to path - need parent directory since this is in dev_tools
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(project_root, 'src'))

# Python 3.14 Workaround: Direct module loading to avoid import system bugs
def load_module_py314(filepath, module_name):
    """Load a module directly using importlib to bypass Python 3.14 import bugs."""
    spec = importlib.util.spec_from_file_location(module_name, filepath)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {module_name} from {filepath}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

# Detect Python 3.14 and use workaround
if sys.version_info >= (3, 14):
    print("Note: Python 3.14 detected - using compatibility mode", file=sys.stderr)
    src_dir = os.path.join(project_root, 'src')
    
    # Load modules directly
    lexer_mod = load_module_py314(
        os.path.join(src_dir, 'nlpl', 'parser', 'lexer.py'),
        'nlpl.parser.lexer'
    )
    Lexer = lexer_mod.Lexer
    
    # Load AST module (needed by parser)
    ast_mod = load_module_py314(
        os.path.join(src_dir, 'nlpl', 'parser', 'ast.py'),
        'nlpl.parser.ast'
    )
    
    parser_mod = load_module_py314(
        os.path.join(src_dir, 'nlpl', 'parser', 'parser.py'),
        'nlpl.parser.parser'
    )
    Parser = parser_mod.Parser
    
    # Load compiler backend
    llvm_gen_mod = load_module_py314(
        os.path.join(src_dir, 'nlpl', 'compiler', 'backends', 'llvm_ir_generator.py'),
        'nlpl.compiler.backends.llvm_ir_generator'
    )
    LLVMIRGenerator = llvm_gen_mod.LLVMIRGenerator
    LLVM_AVAILABLE = llvm_gen_mod.LLVM_AVAILABLE
    
    # Load optimizer
    opt_mod = load_module_py314(
        os.path.join(src_dir, 'nlpl', 'optimizer', '__init__.py'),
        'nlpl.optimizer'
    )
    OptimizationLevel = opt_mod.OptimizationLevel
    create_optimization_pipeline = opt_mod.create_optimization_pipeline
else:
    # Normal imports for Python < 3.14
    from nlpl.parser.lexer import Lexer
    from nlpl.parser.parser import Parser
    from nlpl.compiler.backends.llvm_ir_generator import LLVMIRGenerator, LLVM_AVAILABLE
    from nlpl.optimizer import OptimizationLevel, create_optimization_pipeline


def main():
    parser = argparse.ArgumentParser(description='NLPL LLVM Compiler')
    parser.add_argument('input', help='Input NLPL source file')
    parser.add_argument('-o', '--output', help='Output executable file')
    parser.add_argument('--ir', action='store_true', help='Show LLVM IR only')
    parser.add_argument('--obj', help='Output object file (.o)')
    parser.add_argument('--optimize', '-O', type=int, default=0, choices=[0, 1, 2, 3],
                       help='Optimization level (0-3)')
    parser.add_argument('--module', action='store_true', 
                       help='Compile as module (generate .ll file only)')
    parser.add_argument('-g', '--debug', action='store_true',
                       help='Include debug information (DWARF)')
    parser.add_argument('--header', help='Generate C header file for exported functions')
    
    args = parser.parse_args()
    
    # Check if llvmlite is available
    if not LLVM_AVAILABLE:
        print("ERROR: LLVM backend not available")
        print("This should not happen - pure Python implementation")
        sys.exit(1)
    
    # Read source file
    try:
        with open(args.input, 'r') as f:
            source_code = f.read()
    except FileNotFoundError:
        print(f"ERROR: File not found: {args.input}")
        sys.exit(1)
    
    print(f"Compiling {args.input}...")
    
    # Lexer
    lexer = Lexer(source_code)
    tokens = lexer.tokenize()
    
    # Parser
    parser_obj = Parser(tokens)
    ast = parser_obj.parse()
    
    # Pattern matching analysis (warnings for non-exhaustive or unreachable cases)
    from nlpl.compiler.pattern_analysis import analyze_pattern_match
    from nlpl.parser.ast import MatchExpression
    
    visited = set()
    
    def analyze_patterns(node, depth=0):
        """Recursively analyze pattern matching in AST."""
        # Prevent infinite recursion
        if depth > 100:
            return
        
        # Avoid revisiting nodes
        node_id = id(node)
        if node_id in visited:
            return
        visited.add(node_id)
        
        if isinstance(node, MatchExpression):
            warnings = analyze_pattern_match(node)
            for warning in warnings:
                print(f"Warning: {warning}")
        
        # Recursively analyze children
        if hasattr(node, '__dict__'):
            for attr_name, attr_value in node.__dict__.items():
                # Skip certain attributes to avoid cycles
                if attr_name in ('parent', 'scope', 'line_number'):
                    continue
                    
                if isinstance(attr_value, list):
                    for item in attr_value:
                        if hasattr(item, '__dict__'):
                            analyze_patterns(item, depth + 1)
                elif hasattr(attr_value, '__dict__') and not isinstance(attr_value, (str, int, float, bool)):
                    analyze_patterns(attr_value, depth + 1)
    
    analyze_patterns(ast)
    
    # Apply optimizations if requested
    if args.optimize > 0:
        print(f"Applying optimization level O{args.optimize}...")
        opt_level = OptimizationLevel(args.optimize)
        pipeline = create_optimization_pipeline(opt_level, verbose=False)
        ast = pipeline.run(ast)
        
        # Show optimization stats
        if args.optimize >= 2:
            pipeline.print_stats()
    
    # Get source directory for module imports
    source_dir = os.path.dirname(os.path.abspath(args.input))
    source_file = os.path.abspath(args.input)
    
    # LLVM Code Generator
    llvm_gen = LLVMIRGenerator()
    llvm_ir = llvm_gen.generate(ast, source_file=source_file, debug_info=args.debug)
    
    # Generate C header if requested
    if args.header:
        header_path = args.header
        if not os.path.isabs(header_path):
            header_path = os.path.join(os.path.dirname(output_file if args.output else args.input), header_path)
            
        print(f"Generating C header: {header_path}")
        llvm_gen.generate_c_header(header_path)
    
    # Show IR if requested
    if args.ir:
        print("\n=== LLVM IR ===")
        print(llvm_ir)
        return
    
    # Compile as module (just generate .ll file)
    if args.module:
        module_name = os.path.splitext(os.path.basename(args.input))[0]
        ll_file = os.path.join(source_dir, f"{module_name}.ll")
        with open(ll_file, 'w') as f:
            f.write(llvm_ir)
        print(f" Module IR file: {ll_file}")
        return
    
    # Compile to object file
    if args.obj:
        # For object files, just write the .ll file
        ll_file = args.obj.replace('.o', '.ll')
        with open(ll_file, 'w') as f:
            f.write(llvm_ir)
        print(f" LLVM IR file: {ll_file}")
        print(f"Compile with: llc -filetype=obj {ll_file} -o {args.obj}")
        return
    
    # Compile to executable (with module linking if imports present)
    if args.output:
        output_file = args.output
    else:
        # Default output name
        output_file = os.path.splitext(args.input)[0]
    
    # Check if there are imported modules
    if llvm_gen.imported_modules:
        # Save main IR to temporary file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ll', delete=False) as f:
            main_ll = f.name
            f.write(llvm_ir)
        
        # Link all modules with optimization level
        success = llvm_gen.link_modules(main_ll, output_file, opt_level=args.optimize)
        
        # Clean up
        if os.path.exists(main_ll):
            os.remove(main_ll)
    else:
        # No imports, compile normally with optimization level
        success = llvm_gen.compile_to_executable(output_file, opt_level=args.optimize)
    
    if success:
        print(f"\n Compilation successful!")
        print(f" Executable: {output_file}")
        print(f"\nRun with: ./{output_file}")
    else:
        print("\n Compilation failed")
        sys.exit(1)


if __name__ == '__main__':
    main()
