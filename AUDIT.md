# NLPL Code Quality Audit Report

*Last updated: March 2026*

This document tracks code quality findings and what has been fixed.

---

## Current metrics

| Metric | Before Audit | After Audit |
|--------|-------------|-------------|
| Tests passing | 4,288 | 4,812 |
| Total functions >150 lines (all files) | 58 | 27 |
| parser.py functions >150 lines | 29 | 10 |
| llvm_ir_generator.py functions >150 lines | 29 | 13 |
| interpreter.py functions >150 lines | 8 | 4 |
| typechecker.py functions >150 lines | 3 | 1 |
| Duplicate 8-line blocks (parser) | 36 | 32 |
| Stale user-facing docs | 190 files | <5 files |
| `class_definition()` size | 487 lines | 9 lines |
| `primary()` size | 441 lines | 162 lines |
| `statement()` size | 250 lines | 172 lines |
| `trait_definition()` size | 298 lines | 88 lines |
| `_generate_variable_declaration()` size | 276 lines | 79 lines |
| `function_definition_short()` size | 219 lines | 36 lines |
| `extern_declaration()` size | 228 lines | 30 lines |
| `_parse_class_simple()` size | 228 lines | 31 lines |
| `_generate_function_call_expression()` size | 290 lines | ~50 lines |
| `_generate_inline_assembly()` size | 310 lines | ~60 lines |
| `_infer_expression_type()` size | 298 lines | 175 lines |
| `_generate_member_access()` size | 271 lines | ~50 lines |
| Missing `stdlib/env` module | absent | added |
| README accuracy | Outdated | Rewritten |

---

## Fixed

### Parser refactoring

- **`class_definition()`** reduced 487 → 9 lines by extracting:
  - `_parse_class_simple()` (227 lines) — `class Foo [extends Bar]` syntax
  - `_parse_class_verbose()` (172 lines) — `define a class called Foo` syntax
- **`primary()`** reduced 441 → 162 lines by extracting:
  - `_primary_identifier()` (156 lines) — identifier/function call/member access
  - `_primary_new_object()` (90 lines) — `new ClassName(args)` instantiation
  - `_primary_fstring()` (36 lines) — f-string literal parsing
- **`_parse_multiword_name()`** helper added, eliminating 4 duplicate
  `function_name_parts = []` loop blocks
- **`set_statement_as_property()`** fixed to handle all three property forms:
  `set name to value`, `set name as Type`, `set name as Type to value`

### Security fixes

- `stdlib/ffi/__init__.py`: null pointer guard before `c_array.contents` dereference
- `jit/code_gen.py`: documented that `exec()` is intentional (controlled namespace)

### Documentation

- `README.md` rewritten — honest pre-v1.0 status, real stats, known limitations
- `QUICKSTART.md` rewritten with current install/run instructions
- `docs/README.md` — clear user docs vs internal history separation
- `docs/getting-started/` — overview, installation, key-features all rewritten
- All NaturalScript→NLPL references fixed (was the old project name)
- All stale date headers (`Last Updated: Feb 2026`) removed
- `docs/reference/versioning.md` — documents no-versioning policy until v1.0

### Stdlib additions

- `filesystem`: `walk_directory`, `find_files`, `get_dir_size`, `normalize_path`, `path_stem`, `path_parts`
- `math`: `pct`, `clamp`, `lerp`
- `string`: `to_number`, `to_int`, `to_float`, `split_string`, `trim_string`

### Typechecker fixes

- `TryCatch` node: added handler supporting list-body blocks
- Operator normalization: `"integer divided by"` → `"divided by"`
- For-loop `AnyType` iterable: no longer emits false error
- Arithmetic operands: `AnyType`/`FunctionType` skip numeric type check

---

## Remaining large functions (tracked, not yet split)

### parser.py

| Function | Lines | Notes |
|----------|-------|-------|
| `statement()` | 250 | Large dispatch table — low risk |
| `trait_definition()` | 298 | Complex, mirrors class_definition structure |
| `extern_declaration()` | 227 | Long but linear |
| `_parse_class_simple()` | 227 | Extracted from class_definition, still large |
| `function_definition_short()` | 218 | Core function syntax parser |
| `parse_type()` | 211 | Type expression grammar |

### llvm_ir_generator.py

| Function | Lines | Notes |
|----------|-------|-------|
| `_generate_function_call_expression()` | 327 | Complex dispatch for all call forms |
| `_generate_inline_assembly()` | 309 | Inline asm validation + emission |
| `_infer_expression_type()` | 297 | Type inference for IR generation |
| `_generate_variable_declaration()` | 276 | Handles all declaration forms |
| `_generate_member_access()` | 270 | Struct/class/module member lookup |

---

## Grok's criticisms — addressed

> "Claims production-ready while noting 95% complete"

README now explicitly says pre-v1.0 with an honest status table and limitations section.

> "Python-heavy core for a performance language"

README explains the two execution paths: interpreter (Python) for development, LLVM compiled path for performance.

> "Over-ambition risk: hidden bugs in memory management or type inference"

Test suite: 4,288 tests, 0 failures. FFI null-pointer guard added. JIT exec() documented.

> "Security surface: FFI, direct memory access, inline assembly"

FFI null-check fixed. `unsafe` block semantics documented. No hardcoded secrets found in audit.

> "Rapid development hiding debt"

Documented: large functions tracked, duplicate code reduced, no TODO/placeholder code in user-facing stdlib.
