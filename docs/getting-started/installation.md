# Installation

## Requirements

- Python 3.11 or newer
- pip

### Optional (for compiled mode)

- LLVM and clang (for native code generation via `--compile`)

## Install

```bash
git clone https://github.com/Zajfan/NLPL
cd NLPL
pip install -r requirements.txt
```

## Verify

```bash
PYTHONPATH=src python -m nlpl.main examples/01_basics/01_basic_concepts.nlpl
```

You should see output from the basic concepts example.

## Running programs

```bash
# Standard interpreter mode
PYTHONPATH=src python -m nlpl.main my_program.nlpl

# Disable type checking (faster startup)
PYTHONPATH=src python -m nlpl.main --no-type-check my_program.nlpl

# Compiled mode (requires llvm + clang)
PYTHONPATH=src python -m nlpl.main --compile my_program.nlpl
```

## REPL

```bash
PYTHONPATH=src python -m nlpl.repl
```

## Editor integration

### VS Code

Install the extension from `vscode-extension/`. It provides syntax highlighting and connects to the LSP server automatically.

### Neovim

See `editors/neovim/` for configuration.

### Any LSP-capable editor

Point your editor at:
```
PYTHONPATH=/path/to/NLPL/src python -m nlpl.lsp --stdio
```
