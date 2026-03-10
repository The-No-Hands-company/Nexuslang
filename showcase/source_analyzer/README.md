# Source Code Analyzer -- NLPL Showcase Project

A practical CLI tool written entirely in NLPL (~590 lines) that scans a directory of source files and produces a detailed analysis report with formatted tables and visual bars.

## Running

```bash
# From the NLPL repo root:
PYTHONPATH=src python -m nlpl.main showcase/source_analyzer/analyze.nlpl --no-type-check
```

By default, the analyzer scans `src/nlpl/parser`. To change the target, edit the `target_directory` variable at the top of `analyze.nlpl`.

## Report Sections

- **Summary** -- total files, lines, size, and a code/comment/blank breakdown with visual bars
- **Language Breakdown** -- per-language table (files, lines, code, comments, blank, size)
- **Language Distribution** -- visual bar chart comparing languages by line count
- **Largest Files** -- top 10 files ranked by size
- **Comment Density by Language** -- visual bars showing comment ratio per language

## Sample Output

```
================================================================================
  NLPL Source Code Analyzer
  Scanning: src/nlpl/parser
================================================================================

  Found 9 files. Analyzing...

--------------------------------------------------------------------------------
  SUMMARY
--------------------------------------------------------------------------------

  Directory:     src/nlpl/parser
  Files found:   9
  Files analyzed: 9
  Total size:    571.0 KB

  Total lines:   13637
  Code lines:    9598
  Comment lines: 1693
  Blank lines:   2346

  Code:     [#####################.........] 70%
  Comments: [###...........................] 12%
  Blank:    [#####.........................] 17%

--------------------------------------------------------------------------------
  LANGUAGE BREAKDOWN
--------------------------------------------------------------------------------

  Language           Files     Lines      Code  Comments   Blank        Size
  --------------------------------------------------------------------------------
  Python                 7     13470      9455      1693    2322    564.8 KB
  Text                   1        78        64         0      14      3.8 KB
  Other                  1        89        79         0      10      2.3 KB
  --------------------------------------------------------------------------------
  TOTAL                  9     13637      9598      1693    2346    571.0 KB
```

## NLPL Features Exercised

This program demonstrates a wide range of NLPL language capabilities:

| Feature | Usage |
|---------|-------|
| **File I/O** | `walk_directory`, `read_file`, `get_file_size`, `get_extension`, `join_path` |
| **String Processing** | `strip`, `str_split`, `contains`, `substring`, `length` |
| **Type Conversion** | `convert X to integer`, `convert X to string` |
| **Control Flow** | `if`/`else`/`end`, `for each`/`end`, `while`/`end` |
| **Functions** | 7 user-defined functions with typed parameters and return types |
| **Collections** | Dict literals, dict access/mutation, list literals, `append` |
| **Error Handling** | `try`/`catch`/`end` for graceful dict-key misses and file I/O errors |
| **Arithmetic** | Integer math, division, modulo, comparison operators |
| **Formatted Output** | Aligned tables, visual bar charts, padded columns |

## Usability Findings

Building this tool revealed several practical NLPL usability insights:

1. **Reserved word collisions** -- `label`, `split`, `repeat`, `starts_with`, `ends_with` are keywords that conflict with common variable/function names. Workarounds: `str_split()` instead of `split()`, rename variables.
2. **Return inside try** -- `return` statements inside `try` blocks are caught as exceptions. Workaround: assign to a variable inside `try`, then `return` after the block.
3. **Float division** -- NLPL uses true division (Python semantics), so integer division requires explicit `convert X to integer` truncation.
4. **No string multiplication** -- `"#" * 10` is not available; use a while loop to build repeated strings.
5. **No dict iteration** -- Cannot iterate directly over dict keys; must maintain a parallel list of expected keys.
