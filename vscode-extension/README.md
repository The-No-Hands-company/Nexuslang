# NLPL Language Support for VS Code

Language support extension for NLPL (Natural Language Programming Language) with full LSP features.

## Features

- **Syntax Highlighting**: Natural language keywords, types, operators
- **IntelliSense**: Code completion with suggestions
- **Go to Definition**: Navigate to symbol definitions
- **Find References**: Find all references to a symbol
- **Hover Information**: Type and documentation on hover
- **Diagnostics**: Real-time error and warning reporting
- **Document Symbols**: Outline view of functions, classes, methods
- **Code Actions**: Quick fixes and refactorings

## Requirements

The NLPL language server must be installed:

```bash
pip install nlpl-compiler
```

Or use the bundled server if included with the extension.

## Extension Settings

This extension contributes the following settings:

- `nlpl.languageServer.enabled`: Enable/disable the language server (default: `true`)
- `nlpl.languageServer.path`: Path to language server executable (leave empty for auto-detect)
- `nlpl.languageServer.arguments`: Arguments passed to the server (default: `["--stdio"]`)
- `nlpl.languageServer.debug`: Enable debug mode (default: `false`)
- `nlpl.languageServer.logFile`: Path to log file for server output
- `nlpl.trace.server`: Trace communication between client and server (`off`, `messages`, `verbose`)

## Usage

1. Install the extension
2. Open a `.nlpl` file
3. The language server will start automatically
4. Start coding with IntelliSense support

## Examples

```nlpl
# Function with type annotations
function calculate_average with numbers as List of Integer returns Float
    if numbers is empty
        return 0.0
    end
    
    set total to 0
    for each num in numbers
        set total to total plus num
    end
    
    return total divided by length of numbers
end

# Class with properties and methods
class Rectangle
    property width as Integer
    property height as Integer
    
    method area returns Integer
        return width times height
    end
    
    method perimeter returns Integer
        return 2 times (width plus height)
    end
end
```

## Development

To build the extension from source:

```bash
cd vscode-extension
npm install
npm run compile
```

To package the extension:

```bash
npm run package
```

To publish (requires publisher account):

```bash
npm run publish
```

## Known Issues

- Some advanced features are still in development
- Semantic tokens support coming soon
- Code actions for refactoring in progress

## Release Notes

### 0.1.0

Initial release with:
- Syntax highlighting
- LSP integration
- Basic IDE features

## Contributing

Contributions are welcome! Visit [https://github.com/Zajfan/NLPL](https://github.com/Zajfan/NLPL)

## License

MIT
