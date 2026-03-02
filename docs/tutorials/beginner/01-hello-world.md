# Tutorial 1: Hello World — Your First Program

**Time:** ~15 minutes  
**Prerequisites:** NLPL installed ([installation guide](../../getting-started/installation.md))

---

## What You Will Learn

- How to run a NLPL program
- How to print output to the screen
- The basic structure of a NLPL source file

---

## 1. Your First Program

Open a text editor and create a file called `hello.nlpl`.  Write this single
line inside it:

```nlpl
print text "Hello, World!"
```

Now run it from your terminal:

```
nlpl hello.nlpl
```

You should see:

```
Hello, World!
```

Congratulations — that is a complete NLPL program.

---

## 2. Printing Multiple Lines

You can call `print text` as many times as you like:

```nlpl
print text "Hello, World!"
print text "Welcome to NLPL."
print text "This is my first program."
```

---

## 3. Comments

Lines that start with `#` are comments.  The interpreter ignores them, but
they help human readers understand the code.

```nlpl
# This is a comment. The interpreter ignores it.
print text "Comments make code easier to read."
```

You can also put a comment at the end of a line:

```nlpl
print text "Inline comment follows"  # this part is ignored
```

---

## 4. Printing Numbers

`print text` expects text.  To print a number, convert it first:

```nlpl
print text convert 42 to string
print text convert 3.14 to string
```

Or build a sentence:

```nlpl
set count to 5
print text "The count is: " plus convert count to string
```

---

## 5. Your Turn

Try making the program greet you by name.  Replace `"World"` with your name:

```nlpl
set my_name to "Your Name Here"
print text "Hello, " plus my_name plus "!"
```

---

## Summary

| Concept | Syntax |
|---------|--------|
| Print a line | `print text "…"` |
| Comment | `# comment text` |
| Store a value | `set name to value` |
| Join strings | `"text" plus more_text` |
| Convert number to text | `convert number to string` |

**Next:** [Variables, Functions, and Control Flow](02-variables-functions-control-flow.md)
