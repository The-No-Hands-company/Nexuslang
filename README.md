# Natural Language Programming Language (NLPL)

A general-purpose programming language with English-like syntax that matches or exceeds the power of ASM, C/C#/C++.

## Overview

NLPL is designed to make programming more accessible by using natural English-like syntax while maintaining the power and performance of traditional programming languages like C++. It combines readability with powerful features including:

- Low-level memory management
- Object-oriented programming
- Concurrency and parallel processing
- Natural error handling
- Strong typing with clear semantics

## Language Features

### Natural English Syntax

NLPL uses verb-based commands and contextual keywords to create code that reads like English sentences:

```
Create an integer called counter and set it to 0
```

instead of:

```c++
int counter = 0;
```

### Core Language Constructs

#### Variable Declaration and Assignment

```
Create a <type> called <name> [and set it to <value>]
```

#### Functions

```
Define a function called <name> that takes <parameters> and returns <type>
    <function body>
End
```

#### Control Flow

```
If <condition> [then]
    <statements>
Otherwise
    <statements>
End

While <condition>
    <statements>
End

Repeat for each <item> in <collection>
    <statements>
End
```

#### Memory Management

```
Allocate a new <type> in memory [with value <expression>] and name it <identifier>
Free the memory at <identifier>
```

#### Classes and Objects

```
Define a class called <name>
    It has a <type> property called <name>
    
    Define a method called <name> that takes <parameters> and returns <type>
        <method body>
    End
End

Create a <class> called <object>
```

#### Concurrency

```
Run these tasks at the same time:
    <task 1>
    <task 2>
    ...
End
```

#### Error Handling

```
Try to
    <statement>
But if it fails
    <error handling>
End
```

## Implementation

NLPL is implemented in Python and consists of several components:

1. **Lexer**: Tokenizes the natural language input
2. **Parser**: Converts tokens into an Abstract Syntax Tree (AST)
3. **Interpreter**: Executes the AST
4. **Runtime**: Provides the execution environment

## Getting Started

### Prerequisites

- Python 3.8+
- Required packages (install via `pip install -r requirements.txt`)

### Installation

```bash
git clone https://github.com/yourusername/nlpl.git
cd nlpl
pip install -r requirements.txt
```

### Running NLPL Programs

**Execute a file:**

```bash
python -m nlpl.main path/to/your/program.nlpl
```

**Start interactive REPL:**

```bash
python -m nlpl.main
# or
python nlpl_repl.py
```

**With options:**

```bash
python -m nlpl.main --debug              # Enable debug mode
python -m nlpl.main --no-type-check      # Disable type checking
python -m nlpl.main program.nlpl --repl  # Run file then enter REPL
```

### Interactive REPL

NLPL includes a powerful interactive REPL (Read-Eval-Print Loop) with:

- **Multi-line input**: Automatic detection of incomplete statements
- **Command history**: Navigate previous commands with arrow keys (persistent)
- **Auto-completion**: Tab completion for keywords, variables, functions
- **Error recovery**: Catch exceptions and continue running
- **Special commands**: `:help`, `:vars`, `:funcs`, `:debug`, `:reset`, etc.

Example REPL session:

```nlpl
>>> set x to 42
=> 42
>>> function greet with name as String returns String
... return "Hello, " plus name
... end
=> greet
>>> greet with "World"
=> Hello, World
>>> :vars
Variables:
  x = 42
  greet = <function>
```

See `docs/7_development/repl.md` for full REPL documentation.

## Examples

### Simple Calculator

```
# Define a calculator class
Define a class called Calculator
    It has a float property called result
    
    Define a method called add that takes float a and float b and returns float
        Create a float called sum and set it to a plus b
        Return sum
    End
End

# Use the calculator
Create a Calculator called calc
Call calc.add with 5, 3
Print calc.result  # Outputs: 8
```

See the `src/examples` directory for more comprehensive examples.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Inspired by natural language processing and traditional programming languages
- Designed to bridge the gap between human language and computer code 
