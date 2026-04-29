# NexusLang Feature Gap Implementation Tracker

Updated: 2026-04-30

Purpose: Convert every matrix row with ⚠️ or ❌ into concrete implementation tasks with file-level targets.

## How To Use This Tracker

- Keep this file in sync with `docs/FEATURE_SUPPORT_MATRIX.md`.
- When a task is complete, switch `[ ]` to `[x]` and add a short completion note.
- Each task should be implemented with tests in `tests/` and at least one NLPL fixture in `test_programs/` when applicable.

## Priority Queue (Execution Order)

1. Channels compiler semantics + tooling
2. Generators/yield compiler semantics
3. Parallel-for compiled semantics
4. Contracts/assertions diagnostics + matcher depth
5. Macro/comptime typechecker/compiler semantics

## Task Backlog By Matrix Row

### 1) Classes / Methods / Inheritance (Tooling ⚠️, Grammar ⚠️)

- [ ] Add class-aware symbol hierarchy in LSP document/workspace symbols.
  - Files: `src/nexuslang/lsp/symbols.py`, `src/nexuslang/lsp/workspace_index.py`
  - Tests: `tests/tooling/test_lsp_document_symbol.py`, `tests/tooling/test_lsp_workspace_symbols.py`
- [ ] Improve method override navigation and references (base/derived linking).
  - Files: `src/nexuslang/lsp/definitions.py`, `src/nexuslang/lsp/references.py`
  - Tests: `tests/tooling/test_lsp_cross_file_navigation.py`
- [ ] Align grammar coverage for class members, inheritance clauses, and modifiers.
  - Files: `grammar/NLPL.g4`, `docs/reference/syntax-grammar.md`
  - Tests: `tests/unit/compiler/test_parser.py`

### 2) Interfaces / Traits / Generics (Typechecker ⚠️, Compiler ⚠️, Tooling ⚠️, Grammar ⚠️)

- [ ] Enforce trait/interface conformance diagnostics with precise member mismatch output.
  - Files: `src/nexuslang/typesystem/typechecker.py`, `src/nexuslang/typesystem/types.py`
  - Tests: `tests/unit/type_system/test_generics.py`, `tests/unit/type_system/test_typechecker.py`
- [ ] Implement generic constraint propagation through calls and method dispatch.
  - Files: `src/nexuslang/typesystem/type_inference.py`, `src/nexuslang/interpreter/interpreter.py`
  - Tests: `tests/unit/type_system/test_bidirectional_inference.py`
- [ ] Lower generic specializations consistently in LLVM/C backends.
  - Files: `src/nexuslang/compiler/backends/llvm_ir_generator.py`, `src/nexuslang/compiler/backends/c_generator.py`
  - Tests: `tests/unit/compiler/test_llvm_codegen.py`, `tests/unit/compiler/test_c_codegen.py`
- [ ] Add LSP hover/completion support for generic parameters and constraints.
  - Files: `src/nexuslang/lsp/hover.py`, `src/nexuslang/lsp/completions.py`
  - Tests: `tests/tooling/test_lsp_hover.py`, `tests/tooling/test_lsp_completions.py`
- [ ] Update grammar for generic bounds and trait composition syntax.
  - Files: `grammar/NLPL.g4`, `docs/reference/syntax-grammar.md`
  - Tests: `tests/unit/compiler/test_parser.py`

### 3) Extended Control Flow: switch / labels / fallthrough (Parser ⚠️, Interpreter ⚠️, Typechecker ⚠️, Compiler ⚠️, Tooling ⚠️, Grammar ⚠️, Tests ⚠️)

- [ ] Complete parser AST for labels and explicit fallthrough semantics.
  - Files: `src/nexuslang/parser/ast.py`, `src/nexuslang/parser/parser.py`
  - Tests: `tests/unit/language/test_switch_statement.py`
- [ ] Execute label resolution and fallthrough correctness in interpreter.
  - Files: `src/nexuslang/interpreter/interpreter.py`
  - Tests: `tests/unit/interpreter/test_control_flow.py`
- [ ] Add unreachable/case-type mismatch diagnostics in typechecker.
  - Files: `src/nexuslang/typesystem/typechecker.py`
  - Tests: `tests/unit/type_system/test_typechecker.py`
- [ ] Lower switch/labels/fallthrough into structured LLVM/C control-flow blocks.
  - Files: `src/nexuslang/compiler/backends/llvm_ir_generator.py`, `src/nexuslang/compiler/backends/c_generator.py`
  - Tests: `tests/unit/compiler/test_llvm_codegen.py`, `tests/unit/compiler/test_c_codegen.py`
- [ ] Add LSP semantic tokens/outline entries for labels and switch cases.
  - Files: `src/nexuslang/lsp/semantic_tokens.py`, `src/nexuslang/lsp/symbols.py`
  - Tests: `tests/tooling/test_lsp_semantic_tokens.py`
- [ ] Align formal grammar with implemented switch variants.
  - Files: `grammar/NLPL.g4`, `docs/reference/syntax-grammar.md`

### 4) Error Handling: try/catch, raise, panic (Typechecker ⚠️, Compiler ⚠️, Tooling ⚠️, Grammar ⚠️)

- [ ] Typecheck thrown/raised values and catch variable typing.
  - Files: `src/nexuslang/typesystem/typechecker.py`
  - Tests: `tests/unit/errors/test_error_propagation.py`
- [ ] Lower try/catch/raise consistently in both backends with runtime-compatible semantics.
  - Files: `src/nexuslang/compiler/backends/llvm_ir_generator.py`, `src/nexuslang/compiler/backends/c_generator.py`
  - Tests: `tests/unit/compiler/test_llvm_codegen.py`, `tests/unit/compiler/test_c_codegen.py`
- [ ] Improve LSP diagnostics for exception scope and unreachable catch blocks.
  - Files: `src/nexuslang/lsp/diagnostics.py`
  - Tests: `tests/tooling/test_lsp_diagnostics.py`
- [ ] Update grammar for complete error-handling syntax parity.
  - Files: `grammar/NLPL.g4`, `docs/reference/syntax-grammar.md`

### 5) Contracts / Assertions (Typechecker ⚠️, Compiler ⚠️, Tooling ⚠️, Grammar ⚠️)

- [ ] Enforce contract expression type rules and side-effect restrictions.
  - Files: `src/nexuslang/typesystem/typechecker.py`
  - Tests: `tests/unit/language/test_contracts.py`
- [ ] Compile `expect`, `require`, `ensure`, `invariant` with clear failure paths.
  - Files: `src/nexuslang/compiler/backends/llvm_ir_generator.py`, `src/nexuslang/compiler/backends/c_generator.py`
  - Tests: `tests/unit/compiler/test_llvm_codegen.py`
- [ ] Add richer LSP diagnostics and quick-fix suggestions for contract failures.
  - Files: `src/nexuslang/lsp/diagnostics.py`, `src/nexuslang/lsp/code_actions.py`
  - Tests: `tests/tooling/test_lsp_code_actions.py`
- [ ] Align grammar contract forms and nesting rules.
  - Files: `grammar/NLPL.g4`, `docs/reference/syntax-grammar.md`

### 6) Ownership / Borrowing / Lifetimes (Typechecker ⚠️, Compiler ⚠️, Tooling ⚠️, Grammar ⚠️)

- [ ] Consolidate borrow/lifetime checking into deterministic pass boundaries.
  - Files: `src/nexuslang/typesystem/typechecker.py`, `src/nexuslang/typesystem/lifetime.py`
  - Tests: `tests/unit/memory/test_borrow_checker.py`
- [ ] Emit ownership-aware move/borrow semantics in compiled backends.
  - Files: `src/nexuslang/compiler/backends/llvm_ir_generator.py`, `src/nexuslang/compiler/backends/c_generator.py`
  - Tests: `tests/unit/memory/test_lifetimes.py`, `tests/unit/compiler/test_llvm_codegen.py`
- [ ] Add borrow conflict diagnostics + related ranges in LSP.
  - Files: `src/nexuslang/lsp/diagnostics.py`
  - Tests: `tests/tooling/test_lsp_diagnostics.py`
- [ ] Update grammar and reference docs for ownership syntax forms.
  - Files: `grammar/NLPL.g4`, `docs/reference/syntax-grammar.md`, `docs/guide/type-system.md`

### 7) Macros / Comptime (Typechecker ❌, Compiler ❌, Tooling ⚠️, Grammar ⚠️, Tests ⚠️)

- [ ] Define typechecker rules for macro expansion results and comptime expression typing.
  - Files: `src/nexuslang/typesystem/typechecker.py`, `src/nexuslang/parser/ast.py`
  - Tests: `tests/unit/type_system/test_typechecker.py`
- [ ] Implement compiler lowering for compile-time evaluation and expansion barriers.
  - Files: `src/nexuslang/compiler/backends/llvm_ir_generator.py`, `src/nexuslang/compiler/compiler.py`
  - Tests: `tests/unit/compiler/test_llvm_codegen.py`, `tests/integration/test_compiler_pipeline.py`
- [ ] Add macro/comptime awareness to hover, completion, and diagnostics.
  - Files: `src/nexuslang/lsp/hover.py`, `src/nexuslang/lsp/completions.py`, `src/nexuslang/lsp/diagnostics.py`
  - Tests: `tests/tooling/test_lsp_hover.py`, `tests/tooling/test_lsp_completions.py`
- [ ] Expand grammar for macro definitions, hygienic params, and comptime blocks.
  - Files: `grammar/NLPL.g4`, `docs/reference/syntax-grammar.md`
- [ ] Add NLPL fixtures for macro/comptime regression coverage.
  - Files: `test_programs/integration/features/`, `tests/unit/language/test_macros.py`

### 8) Async / Await / Spawn (Typechecker ⚠️, Compiler ⚠️, Tooling ⚠️, Grammar ⚠️, Tests ⚠️)

- [ ] Typecheck awaitable contracts and task result typing across nested awaits.
  - Files: `src/nexuslang/typesystem/typechecker.py`
  - Tests: `tests/unit/runtime/test_async_runtime.py`
- [ ] Compile async state machines/coroutine frames consistently.
  - Files: `src/nexuslang/compiler/backends/llvm_ir_generator.py`, `src/nexuslang/runtime/runtime.py`
  - Tests: `tests/unit/runtime/test_async_runtime.py`, `tests/unit/compiler/test_llvm_codegen.py`
- [ ] Add LSP diagnostics/completions for await/spawn contexts.
  - Files: `src/nexuslang/lsp/diagnostics.py`, `src/nexuslang/lsp/completions.py`
  - Tests: `tests/tooling/test_lsp_diagnostics.py`
- [ ] Align grammar async forms with parser behavior.
  - Files: `grammar/NLPL.g4`, `docs/reference/syntax-grammar.md`

### 9) Generators / yield (Typechecker ⚠️, Compiler ⚠️, Tooling ⚠️, Grammar ⚠️, Tests ⚠️)

- [ ] Typecheck yield/send/return interplay and generator function signatures.
  - Files: `src/nexuslang/typesystem/typechecker.py`, `src/nexuslang/typesystem/types.py`
  - Tests: `tests/unit/type_system/test_typechecker.py`
- [ ] Implement full generator frame lowering in LLVM backend (not baseline-only).
  - Files: `src/nexuslang/compiler/backends/llvm_ir_generator.py`
  - Tests: `tests/unit/compiler/test_llvm_codegen.py`, `tests/integration/test_compiler_pipeline.py`
- [ ] Improve tooling awareness for generator symbols and yield flow hints.
  - Files: `src/nexuslang/lsp/hover.py`, `src/nexuslang/lsp/symbols.py`
  - Tests: `tests/tooling/test_lsp_hover.py`
- [ ] Align grammar for generator declarations and yield expressions.
  - Files: `grammar/NLPL.g4`, `docs/reference/syntax-grammar.md`

### 10) Parallel for (Typechecker ⚠️, Compiler ⚠️, Tooling ⚠️, Grammar ⚠️, Tests ⚠️)

- [ ] Typecheck loop-carried dependencies and reduction variable constraints.
  - Files: `src/nexuslang/typesystem/typechecker.py`
  - Tests: `tests/unit/language/test_loops.py`
- [ ] Replace sequential fallback with true parallel lowering (work partitioning + join).
  - Files: `src/nexuslang/compiler/backends/llvm_ir_generator.py`, `src/nexuslang/runtime/runtime.py`
  - Tests: `tests/unit/runtime/test_parallel_runtime.py`, `tests/unit/compiler/test_llvm_codegen.py`
- [ ] Add diagnostics for unsafe captures in parallel regions.
  - Files: `src/nexuslang/lsp/diagnostics.py`
  - Tests: `tests/tooling/test_lsp_diagnostics.py`
- [ ] Align grammar for parallel loop clauses/options.
  - Files: `grammar/NLPL.g4`, `docs/reference/syntax-grammar.md`

### 11) Channels create/send/receive (Compiler ⚠️, Tooling ❌, Grammar ⚠️)

- [ ] Harden compiler-level channel semantics: blocking/wakeup, close behavior, payload ownership.
  - Files: `src/nexuslang/compiler/backends/llvm_ir_generator.py`, `src/nexuslang/runtime/runtime.py`
  - Tests: `tests/unit/runtime/test_channels.py`, `tests/unit/compiler/test_llvm_codegen.py`
- [ ] Add first-class LSP tooling for channels: completion, hover, diagnostics.
  - Files: `src/nexuslang/lsp/completions.py`, `src/nexuslang/lsp/hover.py`, `src/nexuslang/lsp/diagnostics.py`
  - Tests: `tests/tooling/test_lsp_completions.py`, `tests/tooling/test_lsp_hover.py`
- [ ] Align grammar channel operation variants and pipeline syntax.
  - Files: `grammar/NLPL.g4`, `docs/reference/syntax-grammar.md`

### 12) FFI / extern / unsafe (Typechecker ⚠️, Compiler ⚠️, Tooling ⚠️, Grammar ⚠️)

- [ ] Strengthen typechecker ABI checks (size/layout/calling convention mismatches).
  - Files: `src/nexuslang/typesystem/typechecker.py`, `src/nexuslang/stdlib/ffi/__init__.py`
  - Tests: `tests/unit/memory/test_ffi_safety.py`
- [ ] Harden backend lowering for pointers, structs, callbacks, and variadics.
  - Files: `src/nexuslang/compiler/backends/llvm_ir_generator.py`, `src/nexuslang/compiler/backends/c_generator.py`
  - Tests: `tests/unit/compiler/test_ffi_codegen.py`
- [ ] Improve LSP diagnostics for unsafe blocks and FFI signatures.
  - Files: `src/nexuslang/lsp/diagnostics.py`, `src/nexuslang/lsp/hover.py`
  - Tests: `tests/tooling/test_lsp_diagnostics.py`
- [ ] Align grammar for extern declarations and unsafe regions.
  - Files: `grammar/NLPL.g4`, `docs/reference/syntax-grammar.md`

### 13) Inline Assembly (Interpreter ⚠️, Typechecker ⚠️, Tooling ⚠️, Grammar ⚠️)

- [ ] Replace interpreter NOP behavior with explicit runtime policy (error or simulated execution mode).
  - Files: `src/nexuslang/interpreter/interpreter.py`
  - Tests: `tests/unit/systems/test_inline_assembly.py`
- [ ] Add operand constraint and clobber validation in typechecker.
  - Files: `src/nexuslang/typesystem/typechecker.py`
  - Tests: `tests/unit/systems/test_inline_assembly_validation.py`
- [ ] Add asm-aware diagnostics and hover docs for constraints.
  - Files: `src/nexuslang/lsp/diagnostics.py`, `src/nexuslang/lsp/hover.py`
  - Tests: `tests/tooling/test_lsp_hover.py`
- [ ] Align grammar for labels, templates, operands, and clobbers.
  - Files: `grammar/NLPL.g4`, `docs/reference/syntax-grammar.md`

### 14) LSP Diagnostics (Typechecker ⚠️ dependency, Tooling ⚠️)

- [ ] Split parser/typechecker diagnostic sources with deterministic merge and deduplication.
  - Files: `src/nexuslang/lsp/diagnostics.py`, `src/nexuslang/lsp/server.py`
  - Tests: `tests/tooling/test_lsp_diagnostics.py`
- [ ] Add stable diagnostic codes and documentation mapping.
  - Files: `src/nexuslang/lsp/diagnostics.py`, `docs/reference/error-codes.md`
  - Tests: `tests/tooling/test_lsp_diagnostics.py`

### 15) Formatter (Tooling ⚠️, Tests ⚠️)

- [ ] Replace regex-only formatter passes with AST-aware formatting pipeline.
  - Files: `src/nexuslang/lsp/formatter.py`, `src/nexuslang/parser/parser.py`
  - Tests: `tests/tooling/test_formatter.py`
- [ ] Add idempotency and style-profile regression suite.
  - Files: `tests/tooling/test_formatter.py`, `tests/fixtures/`
- [ ] Add formatter quick-fix integration in LSP code actions.
  - Files: `src/nexuslang/lsp/code_actions.py`
  - Tests: `tests/tooling/test_lsp_code_actions.py`

## Suggested Milestones

- Milestone A: Channels + LSP diagnostics foundation
- Milestone B: Generators + Parallel-for backend semantics
- Milestone C: Contracts + Macro/comptime semantic completeness
- Milestone D: FFI/Inline-asm hardening + Formatter modernization
