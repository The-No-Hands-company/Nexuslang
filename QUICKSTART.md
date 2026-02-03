# NLPL Quick Start Guide

**Get started with NLPL in 5 minutes!**

---

## Installation

### Prerequisites
- Python 3.8 or higher
- Git

### Clone the Repository

```bash
git clone https://github.com/Zajfan/NLPL.git
cd NLPL
```

### Verify Installation

```bash
python src/main.py --version
```

You should see the NLPL version information.

---

## Your First NLPL Program

### Hello World

Create a file `hello.nlpl`:

```nlpl
print text "Hello, world!"
```

Run it:

```bash
python src/main.py hello.nlpl
```

**Output:**
```
Hello, world!
```

Congratulations! You just ran your first NLPL program!

---

## Basic Concepts (5 Minutes)

### 1. Variables

```nlpl
# Declare and assign variables
set name to "Alice"
set age to 25
set height to 5.9
set is_student to true

# Print values
print text "Name: " plus name
print text "Age: " plus (age to_string)
```

**Natural language syntax:** Use `set...to` instead of `=`.

### 2. Functions

```nlpl
# Define a function
function greet with name as String
  print text "Hello, " plus name plus "!"
end

# Call the function
call greet with "Alice"
```

**Key points:**
- Use `function` keyword
- Parameters with `with` keyword
- Explicitly call with `call`
- End with `end` keyword

### 3. Control Flow

```nlpl
# If statement
set score to 85

if score is greater than or equal to 90
  print text "Grade: A"
else if score is greater than or equal to 80
  print text "Grade: B"
else
  print text "Grade: C"
end
```

**Natural comparisons:**
- `is greater than`
- `is less than`
- `equals` or `is equal to`
- `is not equal to`

### 4. Loops

```nlpl
# For each loop
set numbers to [1, 2, 3, 4, 5]

for each num in numbers
  print text "Number: " plus (num to_string)
end

# While loop
set count to 0
while count is less than 5
  print text count to_string
  set count to count plus 1
end

# Repeat loop
repeat 3 times
  print text "Hello!"
end
```

### 5. Lists and Dictionaries

```nlpl
# Lists
set fruits to ["apple", "banana", "cherry"]
print text fruits[0]  # "apple"

# Add to list
append "date" to fruits

# Dictionaries
set person to {
  "name": "Alice",
  "age": 25,
  "city": "New York"
}

print text person["name"]  # "Alice"
```

---

## Intermediate Features (10 Minutes)

### Classes and Objects

```nlpl
class Person
  name as String
  age as Integer
  
  function init with self, name as String, age as Integer
    set self.name to name
    set self.age to age
  end
  
  function greet with self
    print text "Hello, I'm " plus self.name
  end
  
  function is_adult with self returns Boolean
    return self.age is greater than or equal to 18
  end
end

# Create instance
set person to new Person with "Alice", 25
call person.greet
# Output: Hello, I'm Alice

if person.is_adult
  print text "Adult"
end
```

### Pattern Matching NEW!

```nlpl
function describe_number with n as Integer returns String
  match n with
    case 0 then return "zero"
    case 1 then return "one"
    case n if n is less than 0 then return "negative"
    case n if n is less than 10 then return "small"
    case n then return "large"
  end
end

print text describe_number with 5
# Output: small
```

**Why pattern matching?**
- Cleaner than nested if/else
- Exhaustive checking
- Variable binding
- Guards for conditions

### Error Handling

```nlpl
function safe_divide with a as Integer, b as Integer returns Integer
  try
    if b equals 0
      raise error "Division by zero"
    end
    return a divided by b
  catch error
    print text "Error: " plus error
    return 0
  end
end

set result to safe_divide with 10, 0
# Output: Error: Division by zero
```

---

## Using the Standard Library

### Math Module

```nlpl
import math

set result to sqrt of 16  # 4.0
set pi to PI  # 3.14159...
set angle to sin of 1.57  # ~1.0
set power to pow of 2, 8  # 256
```

### String Module

```nlpl
import string

set text to "  Hello World  "
set trimmed to trim of text  # "Hello World"
set upper to upper of text   # "  HELLO WORLD  "
set parts to split text, " "  # ["", "", "Hello", "World", "", ""]
```

### File I/O

```nlpl
import io

# Write to file
call write_file with "output.txt", "Hello, file!"

# Read from file
set content to read_file "output.txt"
print text content
# Output: Hello, file!

# Check if file exists
if file_exists "data.txt"
  print text "File found"
end
```

### JSON

```nlpl
import json_utils

# Parse JSON
set data to parse_json '{"name": "Alice", "age": 25}'
print text data["name"]  # Alice

# Convert to JSON
set person to {"name": "Bob", "age": 30}
set json_str to to_json person
print text json_str
# {"name":"Bob","age":30}
```

---

## Advanced Features

### Structs (C-style)

```nlpl
struct Point
  x as Integer
  y as Integer
end

set p to new Point
set p.x to 10
set p.y to 20

print text "Point: (" plus (p.x to_string) plus ", " plus (p.y to_string) plus ")"
# Output: Point: (10, 20)
```

**Use structs for:**
- C FFI interoperability
- Memory layout control
- Performance-critical code

### Inline Assembly

```nlpl
function fast_multiply with a as Integer, b as Integer returns Integer
  asm "
    mov rax, rdi     ; First argument
    imul rax, rsi    ; Multiply by second
    ret
  "
end

set result to fast_multiply with 6, 7  # 42
```

**Use inline assembly for:**
- System programming
- Performance optimization
- Hardware access

### FFI (Foreign Function Interface)

```nlpl
# Call C library functions
extern function printf with format as String, ... returns Integer

call printf with "Hello from C: %d\n", 42
# Output: Hello from C: 42
```

---

## Command-Line Options

```bash
# Run program
python src/main.py program.nlpl

# Debug mode (show tokens and AST)
python src/main.py program.nlpl --debug

# Disable type checking
python src/main.py program.nlpl --no-type-check

# Profile performance
python src/main.py program.nlpl --profile
```

---

## Examples to Try

NLPL includes 24+ example programs in the `examples/` directory:

```bash
# Basic concepts
python src/main.py examples/01_basic_concepts.nlpl

# Functions
python src/main.py examples/02_functions.nlpl

# Classes and OOP
python src/main.py examples/04_classes.nlpl

# Pattern matching
python src/main.py examples/15_pattern_matching.nlpl

# Structs and unions
python src/main.py examples/24_struct_and_union.nlpl
```

**Browse all examples:**
```bash
ls examples/
```

---

## Common Patterns

### Reading User Input

```nlpl
import io

print text "Enter your name: "
set name to read_line

print text "Hello, " plus name plus "!"
```

### File Processing

```nlpl
import io

set lines to read_lines "data.txt"

for each line in lines
  set trimmed to trim of line
  if not is_empty trimmed
    print text trimmed
  end
end
```

### Working with Lists

```nlpl
set numbers to [1, 2, 3, 4, 5]

# Filter even numbers
set evens to []
for each num in numbers
  if (num modulo 2) equals 0
    append num to evens
  end
end

# Sum all numbers
set total to 0
for each num in numbers
  set total to total plus num
end

print text "Sum: " plus (total to_string)
```

### Configuration Loading

```nlpl
import json_utils

function load_config with path as String returns Dictionary
  try
    set config to parse_json_file path
    return config
  catch error
    print text "Failed to load config: " plus error
    return {}
  end
end

set config to load_config with "config.json"
print text config["app_name"]
```

---

## Troubleshooting

### "Module not found"

**Problem:** Import statement fails.

**Solution:** Check module name spelling and ensure it's in the stdlib.

```nlpl
# Correct
import math

# Wrong
import maths  # No 's'
```

### "Undefined variable"

**Problem:** Variable used before declaration.

**Solution:** Declare with `set` before using.

```nlpl
# Wrong
print text name

# Correct
set name to "Alice"
print text name
```

### "Type mismatch"

**Problem:** Type checker found incompatible types.

**Solution:** Ensure types match or convert explicitly.

```nlpl
# Wrong
set x to 5
set y to x plus "10"  # Can't add integer and string

# Correct
set x to 5
set y to x plus 10
```

To temporarily disable type checking:
```bash
python src/main.py program.nlpl --no-type-check
```

### "Syntax error"

**Problem:** Invalid NLPL syntax.

**Solution:** Check for:
- Missing `end` keywords
- Misspelled keywords (`fuction` vs `function`)
- Missing `to` in `set` statements

**Common mistakes:**
```nlpl
# Wrong
set x = 5  # Use 'to', not '='

# Correct
set x to 5
```

---

## Next Steps

### Learn More

- **Full Syntax Reference:** [docs/2_language_basics/syntax_overview.md](docs/2_language_basics/syntax_overview.md)
- **Pattern Matching Guide:** [docs/3_core_concepts/pattern_matching.md](docs/3_core_concepts/pattern_matching.md)
- **FFI Guide:** [docs/3_core_concepts/ffi.md](docs/3_core_concepts/ffi.md)
- **Inline Assembly:** [docs/3_core_concepts/inline_assembly.md](docs/3_core_concepts/inline_assembly.md)
- **Stdlib Reference:** [docs/STDLIB_API_REFERENCE.md](docs/STDLIB_API_REFERENCE.md)
- **Project Status:** [docs/STATUS.md](docs/STATUS.md)

### Explore Examples

All examples are in `examples/` with numbered progression:
- `01_basic_concepts.nlpl` - Variables, types, operators
- `02_functions.nlpl` - Function definitions and calls
- `03_control_flow.nlpl` - If/while/for loops
- `04_classes.nlpl` - OOP basics
- `15_pattern_matching.nlpl` - Pattern matching examples
- `24_struct_and_union.nlpl` - Low-level programming

### Join the Community

- **GitHub:** https://github.com/Zajfan/NLPL
- **Report Issues:** https://github.com/Zajfan/NLPL/issues
- **Contribute:** See `docs/7_development/`

---

## Quick Reference Card

| Task | NLPL Syntax |
|------|-------------|
| Variable | `set x to 10` |
| Print | `print text "Hello"` |
| Function | `function add with a, b returns a plus b end` |
| If | `if x is greater than 5 ... end` |
| Loop | `for each item in list ... end` |
| While | `while condition ... end` |
| Class | `class Person ... end` |
| Import | `import math` |
| Comment | `# This is a comment` |

---

## Summary

You now know:

✅ How to run NLPL programs  
✅ Basic syntax (variables, functions, control flow)  
✅ Using the standard library  
✅ Object-oriented programming  
✅ Pattern matching  
✅ Error handling  
✅ File I/O  
✅ Where to find examples and documentation  

**Start coding!** Try modifying the examples or create your own programs.

**Need help?** Check the comprehensive documentation in `docs/` or open an issue on GitHub.

**Welcome to NLPL!** 🚀
