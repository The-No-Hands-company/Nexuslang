# NLPL Codebase Instructions for AI Agents

## Project Vision & Overview
NLPL (Natural Language Programming Language) is an **ambitious general-purpose language** designed to be:
- **As natural as English**: Code reads like prose, making programming accessible
- **As low-level as Assembly**: Direct hardware access, memory manipulation, OS development
- **As comprehensive as C++**: Full OOP, generics, standard library, advanced features
- **Truly universal**: One language for OS kernels, system software, web apps, and everything between

**Current State**: Interpreter-based implementation with compiler pipeline: Lexer → Parser → AST → Interpreter → Runtime. Starting small (hello world works), expanding iteratively toward the full vision.

## Development Philosophy ⚠️ CRITICAL

**NO SHORTCUTS. NO COMPROMISES.**

This is a **full programming language development project**, not an MVP or prototype. Every feature must be:

- ✅ **Complete** - Full implementation, not placeholders or stubs
- ✅ **Production-ready** - Robust error handling, edge cases covered
- ✅ **No simplifications** - Don't cut corners to "save time" or "make it easier"
- ✅ **No workarounds** - Solve the real problem, not symptoms
- ✅ **No quickfixes** - Proper architectural solutions, not hacks
- ✅ **Real implementations** - Actual working code, not TODO comments

**When implementing features:**
- Do NOT use placeholder implementations ("TODO: implement later")
- Do NOT simplify complex features to make them "easier"
- Do NOT skip edge cases or error conditions
- Do NOT use workarounds instead of proper solutions
- Do NOT leave stub functions with mock data

**Remember**: We're building a language that will compete with C++, Python, and Rust. Act accordingly.

## File Organization Rules ⚠️ CRITICAL

**Always follow this structure when creating files:**

- **`examples/`** - Numbered tutorial/demonstration programs ONLY
  - Naming: `01_basic_concepts.nlpl`, `02_object_oriented.nlpl`, etc.
  - Purpose: Documentation, learning materials, feature showcases
  - DO NOT put test files here

- **`test_programs/`** - Test programs organized by category
  - Structure: `test_programs/features/`, `test_programs/control_flow/`, etc.
  - Purpose: Feature testing, validation programs
  - Naming: `test_*.nlpl`, descriptive names

- **`tests/`** - Python unit/integration tests
  - Purpose: pytest test files for the interpreter/compiler
  - Naming: `test_*.py`

- **`dev_tools/`** - Development scripts and utilities
  - Purpose: Helper scripts, debugging tools, development aids
  - Naming: `*.py` development scripts

- **`src/nlpl/`** - Source code ONLY
  - No test files, no examples, only implementation code

- **Root directory** - Configuration files ONLY
  - Allowed: `README.md`, `ROADMAP.md`, `requirements.txt`, `pyproject.toml`, `.gitignore`, etc.
  - NOT allowed: Test files, example programs, demo scripts

**Before creating ANY file, determine correct location using these rules.**

## Architecture & Core Components

### Pipeline Flow
```
Source (.nlpl) → Lexer (tokens) → Parser (AST) → Interpreter → Runtime (execution)
                                         ↓
                                 Type System (optional type checking)
```

### Key Modules (src/)
- **`parser/lexer.py`**: Natural language tokenization (English-like keywords: `set`, `to`, `called`, `function`, etc.)
- **`parser/parser.py`**: Recursive descent parser, converts tokens to AST (3800+ lines - handles complex natural syntax)
- **`parser/ast.py`**: AST node definitions (Program, VariableDeclaration, FunctionDefinition, StructDefinition, etc.)
- **`interpreter/interpreter.py`**: AST execution engine with scope management and lazy module loading
- **`runtime/runtime.py`**: Execution environment (memory management, object creation, concurrency via ThreadPoolExecutor)
- **`runtime/memory.py`**: Low-level memory management (MemoryManager, MemoryAddress, pointer operations)
- **`errors.py`**: Enhanced error reporting (fuzzy matching, caret pointers, contextual suggestions)
- **`typesystem/`**: Optional strong typing system (type inference, generics, user-defined types)
- **`modules/module_loader.py`**: Module imports with circular dependency detection, caching
- **`stdlib/`**: Standard library organized by domain (math, string, io, collections, network, system)

### NLPL Syntax Essentials
```nlpl
# Variables: natural assignment
set name to "value"
set counter to 0

# Functions: English-style definitions
function calculate_average with numbers as List of Float returns Float
    if numbers is empty
        return 0.0
    # ... function body

# Control flow: readable conditionals
if age is greater than or equal to 18
    print text "Adult"
else if age is greater than or equal to 13
    print text "Teen"

# Loops: for each, while
for each item in collection
    print text item

while counter is less than 5
    set counter to counter plus 1

# Low-level features: structs, pointers, memory
struct Point
    x as Integer
    y as Integer
end

set ptr to address of my_variable
set value to dereference ptr
set size to sizeof Integer
```

## Development Workflows

### Running NLPL Programs
```bash
python src/main.py examples/01_basic_concepts.nlpl
python src/main.py path/to/file.nlpl --debug  # Enable debug output (tokens + AST)
python src/main.py path/to/file.nlpl --no-type-check  # Disable type checking
```

### Testing
```bash
pytest tests/                           # Run all tests
pytest tests/test_parser.py            # Specific test file
pytest -v tests/test_comprehensive_errors.py  # Verbose mode

# Convenience test runners
python run_comprehensive_test.py       # Comprehensive error reporting tests
python run_error_test.py               # Error handling tests
```

### Code Quality
```bash
black src/ tests/       # Format code
isort src/ tests/       # Sort imports
flake8 src/ tests/      # Lint
```

## Critical Patterns & Conventions

### 1. Parser Extension Pattern
When adding new language constructs to `parser/parser.py`:
```python
# 1. Add token type to parser/lexer.py TokenType enum
# 2. Update lexer keyword mappings (keyword_map dictionary)
# 3. Add AST node class to parser/ast.py with proper __init__
# 4. Add parser method following naming: <construct>_definition() or <construct>_expression()
#    Examples: struct_definition(), union_definition(), class_definition()
# 5. Add to statement() or primary()/unary() switch based on construct type
# 6. Import new AST nodes in parser.py imports
# 7. Add interpreter execution: execute_<NodeClassName>() in interpreter/interpreter.py
```

### 2. Scope Management (Interpreter)
The interpreter uses a **scope stack** (`current_scope` list):
```python
self.enter_scope()  # Push new scope
# ... execute block
self.exit_scope()   # Pop scope
```
Variables are resolved from **innermost to outermost** scope (see `get_variable()`).

### 3. Standard Library Registration
All stdlib modules follow this pattern (see `src/stdlib/__init__.py`):
```python
def register_<module>_functions(runtime: Runtime) -> None:
    """Register functions with the runtime."""
    runtime.register_function("function_name", python_implementation)
```
Called via `register_stdlib(runtime)` in `main.py` before interpretation.

### 4. Lazy Module Loading (Avoid Circular Imports)
The interpreter uses **lazy initialization** for ModuleLoader:
```python
def _get_module_loader(self):
    if self.module_loader is None:
        from nlpl.modules.module_loader import ModuleLoader  # Import here
        self.module_loader = ModuleLoader(self.runtime, [os.getcwd()])
    return self.module_loader
```
This pattern prevents circular dependency between `interpreter.py` and `module_loader.py`.

### 5. Error Handling Philosophy
- **Lexer errors**: Invalid characters, malformed tokens
- **Parser errors**: Include line/column context + caret pointer (see `Parser.error()`)
- **Runtime errors**: Type errors, undefined variables, memory errors
- **Enhanced error system** (`src/nlpl/errors.py`):
  - `NLPLSyntaxError`: Fuzzy matching suggestions for typos
  - `NLPLRuntimeError`: Stack traces and variable context
  - `NLPLNameError`: "Did you mean" suggestions for undefined names
  - `NLPLTypeError`: Type mismatch details with expected vs actual
- See `tests/test_comprehensive_errors.py` for expected error message format

### 6. Type System Integration
Type checking is **optional** (controlled by `--no-type-check` flag):
- Types defined in `typesystem/types.py` (PrimitiveType, ListType, DictType, FunctionType, etc.)
- Type compatibility via `is_compatible_with()` method
- Type inference in `typesystem/type_inference.py`
- Integration point: `interpreter.py` calls type checker before execution

## File Organization Conventions

### Documentation Structure (`docs/`)
Organized into 10 categories (44+ documents):
- **`1_introduction/`**: Project overview, vision, getting started
- **`2_language_basics/`**: Syntax, grammar, specification
- **`3_core_concepts/`**: OOP, error handling, examples
- **`4_architecture/`**: Compiler pipeline, backend strategies
- **`5_type_system/`**: Type system design, generics, inference
- **`6_module_system/`**: Module loading, imports, enhancements
- **`7_development/`**: Style guide, development workflows
- **`8_planning/`**: Roadmaps, priorities, feature plans
- **`9_status_reports/`**: Session summaries, progress tracking
- **`10_assessments/`**: Analysis, requirements, comparisons

### Example Programs (`examples/`)
Numbered by complexity: `01_basic_concepts.nlpl` → `24_struct_and_union.nlpl`
Recent additions: `23_pointer_operations.nlpl`, `24_struct_and_union.nlpl`
Use these as **integration test references** when validating new features.

### Test Organization (`tests/`)
- `test_lexer.py`: Tokenization tests
- `test_parser.py`: AST generation tests
- `test_interpreter.py`: Execution tests
- `test_stdlib.py`: Standard library tests
- `test_comprehensive_errors.py`: Error reporting validation

## Common Pitfalls

1. **Don't directly import ModuleLoader in interpreter.py** → Use lazy initialization pattern
2. **Parser changes require AST node updates** → Always add corresponding AST class
3. **New keywords need TokenType + lexer mapping** → Update both `TokenType` enum and keyword dict
4. **Scope violations** → Remember to `enter_scope()` before blocks, `exit_scope()` after
5. **stdlib registration** → New stdlib modules must be registered in `src/stdlib/__init__.py`
6. **Natural language ambiguity** → NLPL uses "structured natural language" - maintain English readability while avoiding parser ambiguities
7. **Incremental development** → Start small, validate thoroughly before adding complexity

## Vision vs. Implementation Gap

NLPL aims to support everything from OS kernel development to web apps, but it's being built **incrementally**:

**Future Capabilities** (not yet implemented):
- **Low-level hardware access**: Inline assembly generation, I/O port operations, interrupt handling
- **OS development**: Bootloader generation, kernel primitives, direct memory access
- **Platform independence**: Multi-architecture code generation (x86, ARM, etc.)
- **Web compilation**: Transpilation to JavaScript/TypeScript or WASM
- **Performance optimization**: LLVM-based optimizing compiler backend

**Current Approach**: When adding features, maintain backward compatibility and ensure the natural language syntax remains intuitive. Reference `examples/` for syntax patterns that work.

## Current Development State (from ROADMAP.md)
**Phase: Foundation Building** - Starting small, expanding incrementally

- ✅ **Basic Interpreter Pipeline**: Lexer → Parser → AST → Interpreter → Runtime
- ✅ **Core Language Features**: Variables, functions, classes, control flow
- ✅ **Enhanced Error Reporting**: Fuzzy matching, caret pointers, contextual suggestions (errors.py)
- ✅ **Memory Management**: allocate/free primitives, MemoryManager, MemoryAddress
- ✅ **Pointer Operations**: address-of, dereference, sizeof (low-level memory access)
- ✅ **Index Assignment**: set array[0] to value, set dict["key"] to value
- 🚧 **Struct/Union Types**: Tokens/AST complete, parser implemented, interpreter pending
- ✅ **Module System**: Circular import detection, namespace management
- ✅ **Standard Library** (6 modules): math, string, io, system, collections, network
- ✅ **Type System Foundation**: Primitives, lists, dicts, functions, optional type checking
- 🚧 **Type Inference**: Partial implementation
- 🚧 **Generic Types**: In progress
- ❌ **Bitwise Operations**: Tokens exist, parser/interpreter pending
- ❌ **FFI (Foreign Function Interface)**: Planned (C library interop)
- ❌ **Inline Assembly**: Planned (direct hardware control)
- ❌ **Web Extension**: Planned (future: compile to WASM or generate JS/TS)
- ❌ **Optimizing Compiler**: Planned (future: LLVM backend for native performance)

**Development Philosophy**: Build incrementally. Current focus is on making the high-level language features robust before tackling low-level hardware access and cross-platform compilation.

## Quick Reference: Key Files by Task

| Task | Files to Modify |
|------|----------------|
| Add keyword | `parser/lexer.py` (TokenType, keyword_map) |
| Add syntax construct | `parser/ast.py`, `parser/parser.py`, `interpreter/interpreter.py` |
| Add stdlib function | `src/stdlib/<module>/__init__.py` |
| Add type | `typesystem/types.py`, `typesystem/typechecker.py` |
| Fix parser bug | Check `parser/parser.py` error recovery, AST construction |
| Debug runtime issue | Add `--debug` flag, inspect scope stack in `interpreter.py` |

## References
- Grammar definition: `grammar/NLPL.g4` (ANTLR-style, aspirational reference - actual parser is hand-written in Python)
- BNF grammar: `src/nlpl/parser/bnf_grammar.txt`
- Style guide: `docs/7_development/style_guide.md` (NLPL code conventions)
- Architecture docs: `docs/4_architecture/compiler_architecture.md` (design vision)
- Type system: `docs/5_type_system/` (type system design and implementation)
- Module system: `docs/6_module_system/` (module loading and imports)
- Project roadmap: `ROADMAP.md` (tracks current vs. planned features)
- Documentation guide: `docs/_ORGANIZATION_GUIDE.md` (10-category structure)

## AI-Assisted Development Notes

NLPL's long-term vision includes using AI/LLMs to handle natural language ambiguity resolution and code generation. The current implementation uses deterministic parsing, but future enhancements may incorporate:
- AI-driven intent inference for ambiguous natural language constructs
- Code generation backends that produce assembly, C++, JavaScript, or WASM
- Context-aware error suggestions that explain intent mismatches

When developing NLPL features, keep this dual nature in mind: strict syntax rules now, flexible AI interpretation later.
