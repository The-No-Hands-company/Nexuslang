# NLPL Language Server Protocol (LSP) Implementation

## Overview

The NLPL LSP server provides IDE integration for NLPL, enabling modern development features like auto-completion, error checking, go-to-definition, and more.

## Features

### ✅ Implemented

1. **Real-time Diagnostics**
   - Syntax error detection (integrated with NLPL parser)
   - Type error checking (integrated with NLPL type checker)
   - Unused variable warnings
   - Unclosed string detection

2. **Auto-Completion**
   - Keyword completion (function, class, set, etc.)
   - Context-aware completions:
     - Type suggestions after `as` and `returns`
     - Collection types after `create`
     - Value/expression suggestions after `set x to`
   - Standard library function completion
   - Variable and function name completion
   - Code snippets (function templates, class templates, etc.)

3. **Go-to-Definition**
   - Jump to function definitions
   - Jump to class definitions
   - Jump to variable declarations

4. **Hover Information**
   - Function signatures
   - Type information
   - Documentation for keywords and stdlib functions

5. **Code Formatting**
   - Basic NLPL code formatting

6. **Workspace Symbols**
   - Search for symbols across files

## Architecture

```
┌─────────────────┐
│   VSCode/IDE    │
│     Client      │
└────────┬────────┘
         │ JSON-RPC
         │ (stdio)
┌────────▼────────┐
│  NLPL LSP       │
│   Server        │
│  (src/nlpl_lsp.py) │
└────────┬────────┘
         │
    ┌────┴─────┬──────────┬───────────┬────────────┐
    │          │          │           │            │
┌───▼──┐  ┌───▼──┐  ┌────▼────┐ ┌────▼─────┐ ┌───▼───┐
│Diag- │  │Comp- │  │Defin-   │ │Hover     │ │Symbol │
│nostic│  │letion│  │itions   │ │Provider  │ │Provider│
│Provider│  │Provider│  │Provider │ │         │ │       │
└───┬──┘  └──────┘  └─────────┘ └──────────┘ └───────┘
    │
┌───▼──────────────┐
│   NLPL Parser    │
│   Type Checker   │
└──────────────────┘
```

## Installation & Setup

### Option 1: Manual Testing (No IDE Integration)

Test the LSP diagnostics directly:

```bash
python dev_tools/test_lsp_diagnostics.py
```

### Option 2: VSCode Extension (Full IDE Integration)

#### Step 1: Build the VSCode Extension

```bash
cd .vscode/nlpl-extension
npm install
npm run compile
```

#### Step 2: Install the Extension

1. Press `F5` in VSCode to open Extension Development Host
2. Or package and install:
   ```bash
   npm install -g vsce
   vsce package
   code --install-extension nlpl-language-support-0.1.0.vsix
   ```

#### Step 3: Configure

Add to your `.vscode/settings.json`:

```json
{
  "nlpl.languageServer.enabled": true,
  "nlpl.languageServer.path": "/absolute/path/to/NLPL/src/nlpl_lsp.py",
  "nlpl.trace.server": "verbose"
}
```

### Option 3: Use with Other LSP Clients

The NLPL LSP server implements the standard LSP protocol and works with any LSP client:

**Neovim (with nvim-lspconfig):**
```lua
local lspconfig = require('lspconfig')
local configs = require('lspconfig.configs')

configs.nlpl = {
  default_config = {
    cmd = {'python3', '/path/to/NLPL/src/nlpl_lsp.py'},
    filetypes = {'nlpl'},
    root_dir = lspconfig.util.root_pattern('.git'),
  },
}

lspconfig.nlpl.setup{}
```

**Emacs (with lsp-mode):**
```elisp
(add-to-list 'lsp-language-id-configuration '(nlpl-mode . "nlpl"))
(lsp-register-client
 (make-lsp-client :new-connection (lsp-stdio-connection '("python3" "/path/to/NLPL/src/nlpl_lsp.py"))
                  :major-modes '(nlpl-mode)
                  :server-id 'nlpl-lsp))
```

**Sublime Text (with LSP package):**
```json
{
  "clients": {
    "nlpl": {
      "enabled": true,
      "command": ["python3", "/path/to/NLPL/src/nlpl_lsp.py"],
      "selector": "source.nlpl"
    }
  }
}
```

## Usage Examples

### Diagnostics in Action

When you type invalid NLPL code:

```nlpl
set x to "unclosed string
```

You'll see:
- **ERROR (line 1)**: `Syntax error: Unterminated string`
- **Source**: `nlpl-parser`

### Auto-Completion

Type `set x to ` and get suggestions:
- `create` - Create collection
- `new` - Create object
- `true`, `false`, `null` - Constants
- All variables and functions in scope

Type `function greet that takes ` and get:
- `param_name as Type` - Parameter declaration template

### Go-to-Definition

Ctrl+Click (or F12) on a function name:
```nlpl
set result to calculate with 5, 10  # Jump to calculate function definition
```

### Hover Information

Hover over `sqrt`:
```nlpl
set root to sqrt with 16
```

Shows:
```
**sqrt** - Square root function

From: math

Syntax:
set result to sqrt with number
```

## Testing

### Test Diagnostics Integration

```bash
python dev_tools/test_lsp_diagnostics.py
```

Expected output:
```
============================================================
Testing NLPL LSP Server Diagnostics
============================================================

Diagnostics found: 5

1. [ERROR] Line 9:1
   Source: nlpl
   Unclosed string

2. [WARNING] Line 6:5
   Source: nlpl
   Unused variable 'age'
...
```

### Test LSP Server Manually

Start the server in debug mode:

```bash
python src/nlpl_lsp.py > /tmp/nlpl-lsp-test.log 2>&1
```

Send LSP messages via stdin (JSON-RPC format):

```json
Content-Length: 123

{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"capabilities":{}}}
```

## Implementation Details

### Parser Integration

The diagnostics provider integrates directly with NLPL's parser:

```python
from nlpl.parser.lexer import Lexer
from nlpl.parser.parser import Parser

lexer = Lexer(text)
tokens = lexer.tokenize()
parser = Parser(tokens)
ast = parser.parse()  # Throws exception on syntax error
```

Syntax errors are caught and converted to LSP diagnostics with line/column information.

### Type Checker Integration

Type errors are detected using NLPL's type checker:

```python
from nlpl.typesystem.typechecker import TypeChecker

typechecker = TypeChecker()
typechecker.check_program(ast)

for error in typechecker.errors:
    # Convert to LSP diagnostic
    ...
```

### Context-Aware Completions

The completion provider analyzes the current line prefix to provide relevant suggestions:

- After `set x to`: Values, expressions, constructors
- After `as`/`returns`: Type names
- After `create`: Collection types (list, dict, set, etc.)
- After `function x that takes`: Parameter patterns

## LSP Capabilities

The NLPL LSP server reports these capabilities to clients:

```json
{
  "textDocumentSync": {
    "openClose": true,
    "change": 1,  // Full document sync
    "save": {"includeText": true}
  },
  "completionProvider": {
    "resolveProvider": false,
    "triggerCharacters": [" ", "."]
  },
  "definitionProvider": true,
  "hoverProvider": true,
  "documentFormattingProvider": true,
  "workspaceSymbolProvider": true,
  "renameProvider": true
}
```

## Logging

The LSP server logs to `/tmp/nlpl-lsp.log` for debugging:

```bash
tail -f /tmp/nlpl-lsp.log
```

## Performance

- **Diagnostics**: Real-time parsing on every keystroke
- **Completions**: Cached keyword/stdlib data, dynamic variable extraction
- **Go-to-definition**: Fast regex-based search (upgradable to AST-based)

## Future Enhancements

### Short Term (Session 2-3)
- [ ] Semantic token highlighting
- [ ] Code action providers (quick fixes)
- [ ] Signature help for function calls
- [ ] Document outline/symbols

### Medium Term
- [ ] Incremental parsing for better performance
- [ ] Workspace-wide type checking
- [ ] Refactoring support (rename, extract function)
- [ ] Call hierarchy

### Long Term
- [ ] Debugger integration (DAP)
- [ ] Test adapter integration
- [ ] AI-assisted completions
- [ ] Snippet library expansion

## Troubleshooting

### LSP server not starting

Check Python path:
```bash
which python3
python3 --version  # Should be 3.8+
```

Check dependencies:
```bash
cd /path/to/NLPL
python3 -c "from nlpl.parser.lexer import Lexer; print('OK')"
```

### No diagnostics appearing

1. Check log file: `cat /tmp/nlpl-lsp.log`
2. Verify file extension is `.nlpl`
3. Ensure language ID is set to `nlpl` in VSCode

### Completions not working

1. Check trigger characters: completions trigger after space or dot
2. Manual trigger: `Ctrl+Space` (VSCode) or `Ctrl+X Ctrl+O` (Neovim)
3. Check log for errors

## Contributing

To extend the LSP server:

1. **Add new diagnostics**: Edit `src/nlpl/lsp/diagnostics.py`
2. **Add completions**: Edit `src/nlpl/lsp/completions.py`
3. **Add hover info**: Edit `src/nlpl/lsp/hover.py`
4. **Test changes**: Run `python dev_tools/test_lsp_diagnostics.py`

## References

- [LSP Specification](https://microsoft.github.io/language-server-protocol/)
- [VSCode Extension API](https://code.visualstudio.com/api)
- [NLPL Documentation](../../docs/README.md)

## License

Same as NLPL project - see main repository license.
