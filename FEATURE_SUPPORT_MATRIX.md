# NLPL Feature Support Matrix

Updated: 2026-04-02

Legend:

- ✅ complete / implemented
- ⚠️ partial / limited / inconsistent
- ❌ missing
- ➖ not applicable

Scope columns:

- Lexer: tokenization and keyword surface
- Parser+AST: syntax parse and node representation
- Interpreter: runtime execution path
- Typechecker: static checking in `TypeChecker`
- Compiler (LLVM/C): compilation support in backends
- Tooling (LSP/Fmt): language tooling support depth
- Grammar: formal grammar parity in `grammar/NLPL.g4`
- Tests: dedicated or strong coverage

| Feature Area | Lexer | Parser+AST | Interpreter | Typechecker | Compiler (LLVM/C) | Tooling (LSP/Fmt) | Grammar | Tests |
|---|---|---|---|---|---|---|---|---|
| Variables / assignment | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠️ | ✅ |
| Functions / calls | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠️ | ✅ |
| Classes / methods / inheritance | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠️ | ⚠️ | ✅ |
| Interfaces / traits / generics | ✅ | ✅ | ✅ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ✅ |
| Control flow basics (`if`, `while`, `for each`) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠️ | ✅ |
| Extended control flow (`switch`, labels, fallthrough) | ✅ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ |
| Error handling (`try/catch`, `raise`, `panic`) | ✅ | ✅ | ✅ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ✅ |
| Contracts / assertions (`expect`, `require/ensure/...`) | ✅ | ✅ | ✅ | ❌ | ❌ | ⚠️ | ⚠️ | ✅ |
| Ownership/borrowing/lifetimes | ✅ | ✅ | ✅ | ⚠️ (split passes) | ⚠️ | ⚠️ | ⚠️ | ✅ |
| Macros / comptime | ✅ | ✅ | ✅ | ❌ | ❌ | ⚠️ | ⚠️ | ⚠️ |
| Async / await / spawn | ✅ | ✅ | ✅ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ |
| Generators / `yield` | ✅ | ✅ | ✅ | ❌ | ⚠️ | ⚠️ | ⚠️ | ⚠️ |
| Parallel for | ✅ | ✅ | ✅ | ❌ | ❌ | ⚠️ | ⚠️ | ⚠️ |
| Channels (`create/send/receive`) | ✅ | ✅ | ✅ | ⚠️ | ❌ | ❌ | ⚠️ | ✅ |
| FFI / extern / unsafe | ✅ | ✅ | ✅ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ✅ |
| Inline assembly | ✅ | ✅ | ⚠️ (interp is NOP) | ⚠️ | ✅ | ⚠️ | ⚠️ | ✅ |
| LSP diagnostics | ➖ | ➖ | ➖ | ⚠️ (depends on checker) | ➖ | ⚠️ | ➖ | ✅ |
| Formatter | ➖ | ➖ | ➖ | ➖ | ➖ | ⚠️ (regex-based) | ➖ | ⚠️ |

## Immediate Priority Queue

1. Channels: add typechecker + compiler-path support.
2. Generators/yield: complete typechecker and compiled semantics.
3. Parallel-for: add compiler support.
4. Contracts/assertions: add typechecker and compiled enforcement path.
5. Macro/comptime: define static and compilation semantics.

## Notes

- This matrix complements, and should be maintained alongside, [FEATURE_COMPLETENESS_AUDIT.md](FEATURE_COMPLETENESS_AUDIT.md).
- For each row marked ❌ or ⚠️, create/track concrete implementation tasks with file-level targets.
