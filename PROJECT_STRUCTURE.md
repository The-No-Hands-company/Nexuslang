# NLPL Project Structure

This document describes the reorganized directory structure of the NLPL project.

## Root Directory

```
NLPL/
 .github/              # GitHub-specific files
 .vscode/              # VS Code extension
 benchmarks/           # Performance benchmarks
 build/                # Build artifacts (LLVM IR, executables)
 dev_tools/            # Development utilities
 docs/                 # Documentation (organized by category)
 examples/             # Tutorial examples (numbered)
 grammar/              # Grammar definitions
 logs/                 # Runtime logs
 scripts/              # Utility scripts
 src/                  # Source code
 test_programs/        # NLPL test programs
 tests/                # Python unit tests
 .gitignore
 Makefile              # Build automation
 NLPL.code-workspace   # VS Code workspace
 pyproject.toml        # Python project configuration
 python_version.txt    # Python version requirement
 README.md             # Main project documentation
 requirements.txt      # Python dependencies
 GEMINI.md             # AI instructions
```

## Documentation Structure (`docs/`)

```
docs/
 completion-reports/    # Feature completion summaries
    FIELD_TESTING_SUMMARY.md
    GUI_FEATURES_ROADMAP.md
    INLINE_ASSEMBLY_COMPLETE.md
    OPTIMIZATION_COMPLETE.md
    PERFORMANCE_OPTIMIZATION_COMPLETE.md
    PHASE3_COMPLETE.md
    STDLIB_EXPANSION_COMPLETE.md
    TYPE_SYSTEM_COMPLETION.md
    VSCODE_EXTENSION_GUIDE.md

 guides/                # User-facing guides
    COMPILER_GUIDE.md
    DEPLOYMENT_GUIDE.md
    DISTRIBUTION_SUMMARY.md
    QUICK_START.md
    VISUAL_GUIDE.md

 1_introduction/        # Project overview
 2_language_basics/     # Syntax and grammar
 3_core_concepts/       # OOP, error handling
 4_architecture/        # Compiler design
 5_type_system/         # Type system docs
 6_module_system/       # Module loading
 7_development/         # Development workflows
 8_planning/            # Roadmaps and planning
 9_status_reports/      # Session summaries
 10_assessments/        # Analysis documents
 project_status/        # Feature status tracking
 session_reports/       # Detailed session logs
```

## Scripts Directory (`scripts/`)

```
scripts/
 cleanup_project.py           # Project cleanup automation
 debug_ffi.py                # FFI debugging
 debug_fstring.py            # F-string debugging
 install_extension_globally.sh
 nlplc                       # Compiler wrapper
 nlpllint                    # Linter wrapper
 nlpl_debug.py               # Debugger entry point
 nlpl_repl.py                # REPL entry point
 package_extension.sh
 setup_vscode_extension.sh
 test_debugger.py
 test_repl.py
 test_repl_manual.py
 utility/                    # Utility scripts collection
```

## Source Code Structure (`src/nlpl/`)

```
src/nlpl/
 main.py                   # Entry point
 parser/
    lexer.py             # Tokenization
    parser.py            # AST generation
    ast.py               # AST node definitions
    bnf_grammar.txt
 interpreter/
    interpreter.py       # AST execution
    scope_optimizer.py   # Scope optimization
 compiler/
    optimizer.py         # IR optimization
    backends/
        llvm_generator.py
        c_generator.py
        cpp_generator.py
 runtime/
    runtime.py           # Execution environment
    memory.py            # Memory management
 typesystem/
    typechecker.py       # Type validation
    type_inference.py    # Type inference engine
    generics_system.py   # Generic types
 stdlib/                  # Standard library
    math/
    string/
    io/
    collections/
    network/
    system/
    ffi/                 # FFI support
    testing/
 modules/
    module_loader.py     # Module system
 decorators.py            # Decorator implementations
 errors.py                # Error handling
 safety/                  # Null safety, ownership
 debugger/                # Debugger implementation
 diagnostics/             # Error formatting
 lsp/                     # Language Server Protocol
 optimizer/               # Optimization passes
 tooling/                 # Build tools, analyzer
 build_system/            # Build system
```

## Test Programs Structure (`test_programs/`)

```
test_programs/
 unit/                    # Single-feature tests
    basic/
    stdlib/
    parser/
    ffi/
    type_system/
 integration/             # Multi-feature tests
    compiler/
    features/
    pattern_matching/
    type_system/
 regression/              # Bug fix validation
     error_tests/
```

## Development Tools Structure (`dev_tools/`)

```
dev_tools/
 README.md
 SUMMARY.md
 VALIDATION_REPORT.md
 lexer_tools/             # Lexer debugging
 parser_tools/            # Parser analysis
    grammar_coverage.py
    statement_validator.py
    loop_detector.py
 scripts/                 # Tool scripts
 verification scripts     # Feature verification
```

## Examples Structure (`examples/`)

```
examples/
 README.md
 01_basic_concepts.nlpl
 02_object_oriented.nlpl
 03_functions.nlpl
 ...
 27_testing.nlpl
```

## File Naming Conventions

### NLPL Source Files
- Examples: `01_basic_concepts.nlpl`, `02_object_oriented.nlpl`
- Test programs: `test_*.nlpl`
- Always use descriptive names with underscores

### Python Files
- Entry points: `main.py`, `nlpl_debug.py`, `nlpl_repl.py`
- Modules: lowercase with underscores `lexer.py`, `parser.py`
- Tests: `test_*.py`

### Markdown Documentation
- README files: `README.md` (capitalized)
- Status reports: `UPPERCASE_WITH_UNDERSCORES.md`
- Guides: `Title_Case_With_Underscores.md`

### Scripts
- Shell scripts: `*.sh` (lowercase, executable)
- Python scripts: `*.py` (lowercase)
- Wrapper scripts: lowercase names without extension (`nlplc`, `nlpllint`)

## Key Principles

1. **Separate concerns**: Source code, tests, documentation, and utilities are in separate directories
2. **Clear hierarchy**: Documentation organized by category (10 main categories)
3. **No emojis**: All emojis removed from source files, documentation, and comments
4. **Professional structure**: Follows Python/open-source project conventions
5. **Logical organization**: Related files grouped together
6. **Clean root**: Only essential configuration files in root directory

## Migration Summary

### Files Moved to `scripts/`
- `*.sh` files (shell scripts)
- `debug_*.py` files
- `test_*.py` files (test runners, not unit tests)
- `nlplc`, `nlpllint` (compiler/linter wrappers)
- `nlpl_debug.py`, `nlpl_repl.py`
- `utility/` directory

### Files Moved to `docs/guides/`
- `COMPILER_GUIDE.md`
- `DEPLOYMENT_GUIDE.md`
- `DISTRIBUTION_SUMMARY.md`
- `QUICK_START.md`
- `VISUAL_GUIDE.md`

### Files Moved to `docs/completion-reports/`
- `FIELD_TESTING_SUMMARY.md`
- `GUI_FEATURES_ROADMAP.md`
- `GUI_QUICK_START.md`
- `INLINE_ASSEMBLY_COMPLETE.md`
- `OPTIMIZATION_COMPLETE.md`
- `PERFORMANCE_OPTIMIZATION_COMPLETE.md`
- `PHASE3_COMPLETE.md`
- `STDLIB_EXPANSION_COMPLETE.md`
- `TYPE_SYSTEM_COMPLETION.md`
- `VSCODE_EXTENSION_GUIDE.md`

### Files Removed
- `-o` (build artifact)

## Emoji Cleanup

All emojis have been removed from:
- 228 files modified
- 891 files scanned
- 100% compliance with no-emoji policy

Affected file types:
- Python source files (`.py`)
- NLPL source files (`.nlpl`)
- Markdown documentation (`.md`)

## Future Organization

As the project grows, consider:
- Separate repository for VS Code extension
- Separate repository for standard library
- Package distribution structure
- CI/CD pipeline organization
