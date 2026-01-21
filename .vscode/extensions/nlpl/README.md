# NLPL Language Support for Visual Studio Code

Complete language support for **NLPL** (Natural Language Programming Language) - a revolutionary programming language that reads like English but works like a professional programming language.

## Features

### Syntax Highlighting
Beautiful, semantic syntax highlighting for NLPL code:
- Keywords: `function`, `set`, `to`, `if`, `while`, `for each`, `class`, `struct`
- Types: `Integer`, `String`, `Float`, `Boolean`, `List`, `Dict`
- Operators: Natural language operators like `plus`, `minus`, `is equal to`, `is greater than`
- Comments and strings with proper escaping

### Real-time Diagnostics
- **Syntax errors** with precise line/column positioning
- **Type errors** with helpful suggestions
- **Undefined variable** detection with "did you mean?" suggestions
- **Import validation** - catch missing modules early
- **Unused variable** warnings

### Intelligent Code Completion
Smart auto-completion (Ctrl+Space) for:
- Language keywords (`function`, `class`, `if`, etc.)
- Built-in types (`Integer`, `String`, `List`, etc.)
- Standard library functions (`sqrt`, `max`, `split`, `append`, etc.)
- Variable names in scope
- Function and class names

### Signature Help
Parameter hints as you type function calls:
- **What parameters** a function expects
- **Parameter types** and descriptions
- **Active parameter** highlighting
- Works with stdlib and user-defined functions

### Code Actions (Quick Fixes)
Automatic fixes for common issues:
- Fix unclosed strings
- Remove unused variables
- Add missing type annotations
- Extract code to function
- Convert loops to comprehensions

### Go to Definition
Jump to definitions (F12):
- Function definitions
- Class definitions
- Variable declarations
- Imported modules

### Hover Information
Hover over symbols to see:
- Function signatures and return types
- Variable types and values
- Class/struct definitions
- Documentation strings

### Document Symbols & Outline
- Navigate your code structure
- Jump to functions, classes, variables
- Document outline in Explorer

## Quick Start

### Installation

1. **Install the extension:**
 - Open VSCode
 - Go to Extensions (Ctrl+Shift+X)
 - Search for "NLPL"
 - Click Install

2. **Install NLPL language:**
 ```bash
 pip install nlpl
 ```

3. **Create a `.nlpl` file:**
 ```nlpl
 # hello.nlpl
 function greet that takes name as String returns String
 return "Hello, " plus name plus "!"
 
 set message to call greet with "World"
 print text message
 ```

4. **Run your code:**
 ```bash
 nlpl run hello.nlpl
 ```

### Configuration

The extension auto-detects your NLPL installation. For custom setups, configure in `.vscode/settings.json`:

```json
{
 "nlpl.languageServer.enabled": true,
 "nlpl.languageServer.path": "/custom/path/to/nlpl_lsp.py",
 "nlpl.trace.server": "off"
}
```

## Examples

### Variables and Functions
```nlpl
set counter to 0
set name to "Alice"
set scores to list of 95, 87, 92

function calculate_average with numbers as List of Float returns Float
 if numbers is empty
 return 0.0
 
 set total to 0.0
 for each num in numbers
 set total to total plus num
 
 return total divided by length of numbers
```

### Object-Oriented Programming
```nlpl
class Person
 property name as String
 property age as Integer
 
 constructor that takes n as String and a as Integer
 set name to n
 set age to a
 
 method greet returns String
 return "Hi, I'm " plus name

set person to create Person with "Bob" and 30
print text call greet on person
```

### Low-Level Features
```nlpl
struct Point
 x as Integer
 y as Integer
end

set p to Point with x as 10 and y as 20
set ptr to address of p
set value to dereference ptr
set size to sizeof Point
```

## Configuration Options

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `nlpl.languageServer.enabled` | boolean | `true` | Enable/disable language server |
| `nlpl.languageServer.path` | string | `""` | Custom path to LSP server |
| `nlpl.trace.server` | string | `"off"` | LSP trace level: `off`, `messages`, `verbose` |

## Troubleshooting

### Extension not activating?
1. Check Output panel: `View Output "NLPL Language Server"`
2. Verify NLPL is installed: `nlpl --version`
3. Reload VSCode: `Ctrl+Shift+P Developer: Reload Window`

### No auto-completion?
1. Ensure language server is running (check Output panel)
2. Try triggering manually: `Ctrl+Space`
3. Check for errors in Problems panel (`Ctrl+Shift+M`)

### Custom installation path?
Set in `.vscode/settings.json`:
```json
{
 "nlpl.languageServer.path": "/your/custom/path/to/nlpl_lsp.py"
}
```

### Enable debug logging?
```json
{
 "nlpl.trace.server": "verbose"
}
```
Then check Output panel for detailed LSP communication.

## Resources

- **Documentation:** [NLPL Language Guide](https://github.com/Zajfan/NLPL/tree/main/docs)
- **Examples:** [Example Programs](https://github.com/Zajfan/NLPL/tree/main/examples)
- **Issues:** [Report bugs](https://github.com/Zajfan/NLPL/issues)
- **GitHub:** [Source code](https://github.com/Zajfan/NLPL)

## Contributing

Contributions are welcome! See our [Contributing Guide](https://github.com/Zajfan/NLPL/blob/main/CONTRIBUTING.md).

## License

MIT License - see [LICENSE](https://github.com/Zajfan/NLPL/blob/main/LICENSE) for details.

## What is NLPL?

NLPL (Natural Language Programming Language) is an ambitious project to create a programming language that:

- **Reads like English** - Code is intuitive and accessible
- **Works like C++** - Full OOP, low-level control, high performance
- **Universal application** - From OS kernels to web apps
- **Modern features** - Strong typing, generics, pattern matching, async/await

**Vision:** One language for everything - system programming, application development, scripting, and beyond.

---

**Enjoy coding in natural language!** 
