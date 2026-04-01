# NLPL Code Quality Audit Report

*Last updated: April 2026*

This document tracks code quality findings and what has been fixed.

---

## Current metrics

| Metric | Before Audit | After Audit |
|--------|-------------|-------------|
| Tests passing | 4,288 | 4,812 |
| Total functions >150 lines (all files) | 58 | 19 |
| parser.py functions >150 lines | 29 | 8 |
| llvm_ir_generator.py functions >150 lines | 29 | 8 |
| interpreter.py functions >150 lines | 8 | 4 |
| typechecker.py functions >150 lines | 3 | 1 |
| Duplicate 8-line blocks (parser) | 36 | 30 |
| Stale user-facing docs | 190 files | <5 files |
| `class_definition()` size | 487 lines | 9 lines |
| `primary()` size | 441 lines | 162 lines |
| `statement()` size | 250 lines | 172 lines |
| `trait_definition()` size | 298 lines | 88 lines |
| `_parse_trait_body()` size | 217 lines | 70 lines |
| `parse_type()` size | 212 lines | 115 lines |
| `_generate_variable_declaration()` size | 276 lines | 79 lines |
| `function_definition_short()` size | 219 lines | 36 lines |
| `extern_declaration()` size | 228 lines | 30 lines |
| `_parse_class_simple()` size | 228 lines | 31 lines |
| `_generate_function_call_expression()` size | 290 lines | ~50 lines |
| `_generate_inline_assembly()` size | 310 lines | ~60 lines |
| `_infer_expression_type()` size | 298 lines | 175 lines |
| `_generate_member_access()` size | 271 lines | ~50 lines |
| `_generate_pattern_bindings()` size | 228 lines | 59 lines |
| `_generate_foreach_loop()` size | 210 lines | 164 lines |
| `_generate_range_for_loop()` size | 181 lines | 146 lines |
| `_generate_array_function_call()` size | 221 lines | 119 lines |
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
- **`parse_type()`** reduced 212 → 115 lines by extracting:
  - `_parse_generic_type_suffix()` — consumes `<T, K, V>` generic arguments after a base type name
  - `_parse_list_dict_of_type()` — handles `List of T`, `Dictionary of K, V`/`K to V` forms; eliminated a near-identical duplicate block
- **`_parse_trait_body()`** reduced 217 → 70 lines by extracting:
  - `_parse_that_method_entry()` — handles the `that requires/provides a method called …` token path
  - `_parse_identifier_method_entry()` — handles the legacy single-token IDENTIFIER method spec path
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

### LLVM IR generator refactoring

- **`_generate_pattern_bindings()`** reduced 228 → 59 lines by extracting:
  - `_generate_variant_pattern_binding()` — handles `VariantPattern` with property getter resolution and generic type substitution
  - `_generate_list_pattern_binding()` — handles `ListPattern` with length checks, element matching, rest binding, and AND-combination
- **`_generate_foreach_loop()`** reduced 210 → 164 lines by extracting:
  - `_resolve_iterable()` — resolves iterable expression to `(array_ptr, array_type, array_size, length_reg)` for both variable-reference and arbitrary-expression iterables
- **`_generate_range_for_loop()`** reduced 181 → 146 lines by extracting:
  - `_detect_step_direction()` — analyses the step AST node and returns `(step_is_literal, step_value, step_reg)` at compile time vs runtime
- **`_generate_array_function_call()`** reduced 221 → 119 lines by extracting:
  - `_generate_arrpush_call()` — handles array push with size-alloca lookup, i8-variant handling, and size tracking update

---

## Remaining large functions (tracked, not yet split)

### parser.py

| Function | Lines | Notes |
|----------|-------|-------|
| `parse_expect_statement()` | 212 | Long but linear validation sequence |
| `type_alias_definition()` | 176 | Complex generics + constraint syntax |
| `_parse_class_verbose()` | 173 | Extracted from `class_definition()`, still large |
| `statement()` | 172 | Large dispatch table — low risk |
| `primary()` | 163 | Further extraction possible but stable |
| `abstract_class_definition()` | 162 | Mirrors `_parse_class_verbose` structure |
| `_primary_identifier()` | 157 | Extracted from `primary()`, still large |
| `interface_definition()` | 151 | Complex interface body parsing |

### llvm_ir_generator.py

| Function | Lines | Notes |
|----------|-------|-------|
| `_generate_member_assignment()` | 185 | Handles all struct/class/module member assignment forms |
| `_generate_list_comprehension_expression()` | 180 | Loop + conditional append inline |
| `_generate_async_function_definition()` | 177 | Complex async/await setup |
| `_infer_expression_type()` | 175 | Type inference for IR generation |
| `_generate_new_local_variable()` | 175 | Handles all variable declaration forms |
| `_generate_math_function_call()` | 168 | Dispatch for math built-ins |
| `_generate_binary_operation()` | 165 | All binary operator forms |
| `_generate_foreach_loop()` | 164 | Further extraction possible |

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
