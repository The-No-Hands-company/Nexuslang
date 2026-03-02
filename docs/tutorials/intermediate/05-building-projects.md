# Tutorial 10: Building Projects with nlpl build

**Time:** ~30 minutes  
**Prerequisites:** [Modules and Imports](../beginner/05-modules-and-imports.md)

---

## Part 1 — Project Structure

A NLPL project is a directory containing a manifest file (`nlpl.toml`) and
one or more `.nlpl` source files.

```
my-project/
  nlpl.toml        -- project manifest
  src/
    main.nlpl      -- entry point
    utils.nlpl     -- helper module
  tests/
    test_utils.nlpl
```

---

## Part 2 — The nlpl.toml Manifest

```toml
[package]
name    = "my-project"
version = "0.1.0"
authors = ["Your Name <you@example.com>"]
license = "MIT"
edition = "2026"

[dependencies]
nlpl-math = "1.0"

[[bin]]
name = "my-project"
path = "src/main.nlpl"
```

| Key | Meaning |
|-----|---------|
| `[package]` | Package metadata |
| `[dependencies]` | Runtime library dependencies |
| `[dev-dependencies]` | Test / benchmark dependencies |
| `[[bin]]` | Executable entry point definition |
| `[lib]` | Library target (omit for apps) |

---

## Part 3 — Common Build Commands

```bash
# Run the project (interprets src/main.nlpl)
nlpl build run

# Run with capabilities
nlpl build run -- --allow-read=./data --allow-net=api.example.com

# Run tests
nlpl build test

# Run a specific test file
nlpl build test tests/test_utils.nlpl

# Check for errors without running
nlpl build check

# Format all source files
nlpl build fmt

# Lint
nlpl build lint
```

---

## Part 4 — Build Profiles

Profiles control optimisation and debug output:

```toml
[profile.dev]
opt-level  = 0      # No optimisation; fast rebuilds
debug      = true

[profile.release]
opt-level  = 3      # Full optimisation
lto        = true   # Link-time optimisation
strip      = true   # Strip debug symbols
```

```bash
# Run under dev profile (default)
nlpl build run

# Run under release profile
nlpl build run --profile release
```

---

## Part 5 — Dependencies

Add a library to `[dependencies]` and import it in your code:

```toml
[dependencies]
nlpl-csv = "2.0"
nlpl-http = "1.3"
```

```nlpl
import nlpl_csv
import nlpl_http

set rows to nlpl_csv.parse_file with "data.csv"
set response to nlpl_http.get with "https://api.example.com"
```

Install dependencies (fetches from the registry):

```bash
nlpl build fetch
```

---

## Part 6 — Multiple Binaries

A single project can produce several executables:

```toml
[[bin]]
name = "server"
path = "src/server.nlpl"

[[bin]]
name = "worker"
path = "src/worker.nlpl"

[[bin]]
name = "cli"
path = "src/cli.nlpl"
```

```bash
nlpl build run --bin server
nlpl build run --bin worker
```

---

## Part 7 — Writing Tests

Test files live in `tests/` and start with `test_`:

```nlpl
# tests/test_math.nlpl
import math

function test_sqrt
    set result to math.sqrt with 9.0
    assert result equals 3.0 with message "sqrt(9) should be 3"
end

function test_abs
    assert math.abs with -5 equals 5 with message "abs(-5) should be 5"
end
```

Run them:

```bash
nlpl build test
```

Output:

```
Running tests/test_math.nlpl
  test_sqrt ... ok
  test_abs  ... ok
2 tests passed
```

---

## Summary

| Command | Effect |
|---------|--------|
| `nlpl build run` | Interpret + run `src/main.nlpl` |
| `nlpl build test` | Run all test files |
| `nlpl build check` | Type-check without running |
| `nlpl build fmt` | Auto-format source files |
| `nlpl build fetch` | Download declared dependencies |

**You have completed the Intermediate Track!**

**Next steps:**
- [Advanced Track: Inline Assembly](../advanced/01-inline-assembly.md)
- [Cookbook: Common Tasks](../../cookbook/common-tasks.md)
