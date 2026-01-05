# Changelog

All notable changes to the NLPL VSCode extension will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-01-05

### Added
- Initial release of NLPL Language Support extension
- Syntax highlighting for `.nlpl` files
- Language Server Protocol (LSP) integration
- Real-time diagnostics with enhanced error positioning
- Intelligent code completion (variables, functions, keywords, stdlib)
- Signature help for function calls
- Code actions (quick fixes):
  - Fix unclosed strings
  - Remove unused variables
  - Add type annotations
  - Extract function
  - Convert to comprehension
- Go to definition (F12)
- Hover information for symbols
- Document symbols and outline view
- Multi-file diagnostics with import validation
- Auto-detection of NLPL LSP server
- Configurable LSP server path
- Trace logging for debugging

### Features by Category

#### Editor Features
- Syntax highlighting for NLPL keywords, types, operators, strings, comments
- Auto-closing brackets and quotes
- Comment toggling (Ctrl+/)
- Bracket matching
- Auto-indentation

#### Language Server Features
- Token-level error positioning using AST
- Type checking with inference
- Unused variable detection
- Import validation
- Fuzzy matching for "did you mean?" suggestions
- Function signature parsing for stdlib and user functions

#### Developer Experience
- Zero-configuration setup (auto-detects LSP server)
- Verbose logging option for troubleshooting
- Works in workspace-local or global installation
- Compatible with VSCode 1.75.0+

### Technical Details
- Language Server: Python-based LSP server
- Language Client: vscode-languageclient@^8.1.0
- Supported VSCode version: ^1.75.0
- File extension: `.nlpl`
- Language ID: `nlpl`

### Known Issues
- Extension requires Python 3.11+ for LSP server
- LSP server must be installed separately (via pip or from source)
- Some edge cases in signature help for complex nested calls
- Performance optimization needed for large files (>10k lines)

### Dependencies
- vscode-languageclient: ^8.1.0
- Python 3.11+ (runtime dependency for LSP server)

---

## [Unreleased]

### Planned for 0.2.0
- Semantic token highlighting
- Code formatting support
- Refactoring tools (rename symbol, extract variable)
- Debugging support (DAP integration)
- IntelliSense improvements (parameter hints in string templates)
- Performance optimizations (caching, incremental parsing)
- Test runner integration
- Snippet library for common patterns

### Future Enhancements
- Interactive REPL in terminal
- Code lens for running individual functions
- Inline type hints
- Call hierarchy view
- Reference finding (find all usages)
- Workspace symbol search
- Code folding improvements
- Bracket pair colorization
- Import management (auto-import, organize imports)
