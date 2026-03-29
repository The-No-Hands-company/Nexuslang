# Tutorial 1: Hello World

**Time:** ~10 minutes  
**Prerequisites:** NLPL installed ([installation guide](../../getting-started/installation.md))

---

## Your first program

Create a file called `hello.nlpl`:

```nlpl
print text "Hello, World!"
```

Run it:

```bash
PYTHONPATH=src python -m nlpl.main hello.nlpl
```

You should see:

```
Hello, World!
```

---

## Printing different types

```nlpl
print text "I am a string"
print number 42
print number 3.14
```

The `print text` and `print number` hints are optional — `print` alone works for anything:

```nlpl
print "Hello again"
print 100
```

---

## Comments

```nlpl
# This is a comment — ignored by NLPL
print text "Comments don't affect output"

# You can comment out code:
# print text "This line won't run"
```

---

## Multiline programs

```nlpl
print text "Line 1"
print text "Line 2"
print text "Line 3"
```

---

## Variables

```nlpl
set greeting to "Hello"
set name to "Alice"
print text greeting plus ", " plus name plus "!"
```

Output: `Hello, Alice!`

---

## Next steps

Continue to [Tutorial 2: Variables, Functions, and Control Flow](02-variables-functions-control-flow.md).
