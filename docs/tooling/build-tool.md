# NexusLang Build Tool (nxl_build.py)

**Status**: ✅ Complete - Build Tool CLI + Incremental Compilation

---

## Overview

`nxl_build.py` is a Cargo-inspired build tool for NexusLang projects. It provides project-aware compilation, build orchestration, feature flag management, and profile support through `nlpl.toml` manifests.

**Key Features**:
- **Manifest-driven builds**: Reads `nlpl.toml` for project configuration
- **Incremental compilation**: Smart rebuilds only recompile changed files (see [INCREMENTAL_COMPILATION.md](INCREMENTAL_COMPILATION.md))
- **Build profiles**: Support for dev, release, and custom profiles
- **Feature flags**: Enable/disable capabilities at compile time
- **Multiple targets**: Build libraries and multiple binaries
- **Integrated testing**: Run test suites with `nxl_build.py test`
- **Clean builds**: Remove artifacts with `nxl_build.py clean`
- **Syntax checking**: Fast error checking without compilation

---

## Installation

The build tool is located at `dev_tools/nxl_build.py` and requires:
- Python 3.8+
- NexusLang compiler (`nlplc`)
- Access to `src/nlpl/` modules

**Make executable**:
```bash
chmod +x dev_tools/nxl_build.py
```

**Optional: Add to PATH**:
```bash
# Add to ~/.bashrc or ~/.zshrc
export PATH="$PATH:/path/to/NexusLang/dev_tools"

# Create alias
alias nlpl-build="python3 /path/to/NexusLang/dev_tools/nxl_build.py"
```

---

## Commands

### `build` - Compile Project

Build all targets defined in `nlpl.toml`.

**Usage**:
```bash
nxl_build.py build                    # Build with dev profile
nxl_build.py build --release          # Build with release profile
nxl_build.py build --profile custom   # Build with custom profile
nxl_build.py build --features f1,f2   # Enable specific features
nxl_build.py build --bin processor    # Build specific binary
```

**Options**:
- `--release` - Build with release profile (optimized)
- `--profile NAME` - Build with custom profile
- `--features LIST` - Comma-separated feature flags
- `--bin NAME` - Build specific binary (can be repeated)
- `--no-incremental` - Disable incremental compilation (force full rebuild)
- `--verbose` - Show detailed build information and rebuild reasons

**Examples**:
```bash
# Development build
nxl_build.py build

# Production-optimized build
nxl_build.py build --release

# Build with specific features
nxl_build.py build --features data-analytics,storage-backend

# Build specific binary
nxl_build.py build --bin analyzer
```

**Incremental Compilation**:

By default, `nxl_build.py build` uses incremental compilation to skip recompiling unchanged files. This dramatically improves build times for large projects.

```bash
# First build - compiles everything
nxl_build.py build --verbose
# Output: "Finished build [profile: dev] (5 compiled, 0 up-to-date)"

# Second build - skips unchanged files
nxl_build.py build --verbose
# Output: "Finished build [profile: dev] (0 compiled, 5 up-to-date)"

# After modifying a file
echo '# Modified' >> src/utils.nlpl
nxl_build.py build --verbose
# Output: "Rebuild reason: Dependency utils.nlpl changed"
#         "Finished build [profile: dev] (2 compiled, 3 up-to-date)"
```

**Disable incremental builds** (force full rebuild):
```bash
nxl_build.py build --no-incremental
```

See [INCREMENTAL_COMPILATION.md](INCREMENTAL_COMPILATION.md) for detailed documentation on the incremental compilation system.

**Build Artifacts**:
- **Location**: `build/<profile>/`
- **Structure**:
  ```
  build/
    dev/           # Development builds
      binary_name
      binary_name.ll
      binary_name.o
    release/       # Release builds
      binary_name
      ...
    .cache/        # Incremental compilation cache
      build_cache.json
  ```

---

### `clean` - Remove Build Artifacts

Remove all build outputs and intermediate files.

**Usage**:
```bash
nxl_build.py clean
```

**Removes**:
- `build/` directory (all profiles)
- `*.ll` (LLVM IR files in project root)
- `*.o` (Object files in project root)
- `*.bc` (LLVM bitcode files in project root)

---

### `check` - Syntax Check Without Building

Fast syntax checking without compilation. Useful for rapid feedback during development.

**Usage**:
```bash
nxl_build.py check                    # Check all sources
nxl_build.py check --features f1,f2   # Check with features enabled
```

**Checks**:
- Lexical analysis (tokenization)
- Syntax parsing
- AST generation
- **Does NOT**: Generate code, compile, or link

**Performance**: 10-100x faster than full build for large projects.

---

### `run` - Build and Execute Binary

Build and immediately run a binary target.

**Usage**:
```bash
nxl_build.py run                      # Run default binary
nxl_build.py run --bin analyzer       # Run specific binary
nxl_build.py run --release            # Run release build
nxl_build.py run -- arg1 arg2         # Pass arguments to binary
```

**Options**:
- `--bin NAME` - Which binary to run (default: first in manifest)
- `--release` - Run release build
- `--profile NAME` - Run with custom profile
- `--features LIST` - Enable features
- `-- ARGS` - Arguments to pass to binary (after `--`)

**Examples**:
```bash
# Run default binary (dev profile)
nxl_build.py run

# Run optimized binary
nxl_build.py run --release

# Run with features and arguments
nxl_build.py run --features data-analytics -- input.csv

# Run specific binary
nxl_build.py run --bin analyzer -- --verbose
```

---

### `test` - Run Test Suite

Run all tests in the project.

**Usage**:
```bash
nxl_build.py test                     # Run tests (dev profile)
nxl_build.py test --release           # Run tests (release profile)
nxl_build.py test --features f1,f2    # Run tests with features
```

**Test Discovery**:
- Searches `tests/` directory
- Compiles all `*.nlpl` files
- Runs each test binary
- Reports pass/fail status

**Test Output**:
```
Running tests...
Running 5 test(s)...
  Testing test_parser... ok
  Testing test_lexer... ok
  Testing test_runtime... FAILED
  Testing test_stdlib... ok
  Testing test_integration... ok

Test result: 4 passed, 1 failed
```

**Test Conventions**:
- Place tests in `tests/` directory
- Name files `test_*.nlpl`
- Exit code 0 = pass, non-zero = fail
- Use `assert` statements or explicit error handling

---

## nlpl.toml Configuration

### Package Metadata

```toml
[package]
name = "my-project"
version = "0.1.0"
authors = ["Developer <dev@example.com>"]
license = "MIT"
description = "Project description"
repository = "https://github.com/user/project"
keywords = ["keyword1", "keyword2"]
```

### Binary Targets

```toml
# Single binary
[[bin]]
name = "my-app"
path = "src/main.nxl"

# Multiple binaries
[[bin]]
name = "processor"
path = "src/bin/processor.nxl"

[[bin]]
name = "analyzer"
path = "src/bin/analyzer.nxl"
required-features = ["data-analytics"]  # Only built if feature enabled
```

### Library Target

```toml
[lib]
name = "my_lib"
path = "src/lib.nxl"
crate-type = ["lib"]  # or ["staticlib", "dylib", "cdylib"]
```

### Build Profiles

```toml
[profile.dev]
opt-level = 0       # No optimization
debug = true        # Include debug symbols
incremental = true  # Faster rebuilds

[profile.release]
opt-level = 3       # Maximum optimization
lto = true          # Link-time optimization
strip = true        # Remove debug symbols
panic = "abort"     # Abort on panic (no unwinding)

[profile.custom]
inherits = "release"
opt-level = 2       # Moderate optimization
```

**Profile Fields**:
- `opt-level`: 0-3 (optimization level)
- `debug`: Include debug information
- `lto`: Link-time optimization (true, false, "thin")
- `strip`: Remove symbols (true, false, "symbols")
- `panic`: Panic strategy ("unwind", "abort")
- `incremental`: Incremental compilation
- `codegen-units`: Parallelization (1-256)

### Feature Flags

**Domain-neutral feature examples**:
```toml
[features]
default = ["text-processing"]
text-processing = []                    # Text/string manipulation
data-analytics = ["nlpl-math/stats"]    # Statistical analysis
storage-backend = ["dep:nlpl-database"] # Persistent storage
concurrent-execution = []                # Multi-threading
network-support = ["nlpl-network"]      # Networking capabilities
serialization = ["json", "binary"]      # Data serialization
compression = []                        # Data compression
encryption = []                         # Cryptographic features
ui-support = []                         # User interface capabilities
scripting = []                          # Embedded scripting
```

**Feature Dependencies**:
- `[]` - No dependencies (just a flag)
- `["other-feature"]` - Depends on another feature
- `["dep:package"]` - Enables optional dependency
- `["package/feature"]` - Enables feature in dependency

**Using Features**:
```bash
# Enable single feature
nxl_build.py build --features data-analytics

# Enable multiple features
nxl_build.py build --features data-analytics,storage-backend

# Features are transitive (dependencies enabled automatically)
```

---

## Directory Structure

**Expected Project Layout**:
```
my-project/
  nlpl.toml                 # Project manifest (required)
  src/
    main.nlpl               # Default binary entry point
    lib.nlpl                # Library entry point (if [lib] defined)
    bin/
      tool1.nlpl            # Additional binaries
      tool2.nlpl
  tests/
    test_module1.nlpl       # Test files
    test_module2.nlpl
  build/                    # Build artifacts (auto-generated)
    dev/
      binary_name
    release/
      binary_name
```

---

## Integration with Compiler

`nxl_build.py` integrates with the existing `nlplc` compiler:

1. **Parsing**: Uses `nlpl.parser.lexer.Lexer` and `nlpl.parser.parser.Parser`
2. **Compilation**: Shells out to `dev_tools/nlplc` for code generation
3. **Build Profiles**: Maps manifest profiles to compiler flags

**Compiler Invocation**:
```bash
# Internal call (dev profile)
nlplc source.nlpl -o output -O0 --debug

# Internal call (release profile)
nlplc source.nlpl -o output -O2
```

**Future Enhancement**: Direct API integration with `nlpl.compiler.Compiler` class.

---

## Examples

### Example 1: Simple Hello World

**nlpl.toml**:
```toml
[package]
name = "hello"
version = "0.1.0"

[[bin]]
name = "hello"
path = "main.nxl"

[profile.dev]
opt-level = 0
debug = true

[profile.release]
opt-level = 2
```

**main.nlpl**:
```nlpl
print text "Hello from NLPL!"
```

**Build and Run**:
```bash
$ nxl_build.py build
Building hello [profile: dev, features: none]
  Compiling binary hello...
Finished build [profile: dev]

$ nxl_build.py run
Running hello...
Hello from NLPL!
```

---

### Example 2: Data Processing Tool

**nlpl.toml**:
```toml
[package]
name = "data-tool"
version = "1.0.0"

[[bin]]
name = "processor"
path = "src/main.nxl"

[[bin]]
name = "analyzer"
path = "src/bin/analyzer.nxl"
required-features = ["data-analytics"]

[dependencies]
nlpl-csv = "1.0"
nlpl-math = "2.0"

[features]
default = ["text-processing"]
text-processing = []
data-analytics = ["nlpl-math/statistics"]
storage-backend = []

[profile.release]
opt-level = 3
lto = true
```

**Build Commands**:
```bash
# Build default binary (text-processing enabled)
nxl_build.py build

# Build with analytics (includes analyzer binary)
nxl_build.py build --features data-analytics

# Production build
nxl_build.py build --release --features data-analytics,storage-backend

# Run specific binary
nxl_build.py run --bin analyzer --features data-analytics -- input.csv
```

---

### Example 3: Library + Binaries

**nlpl.toml**:
```toml
[package]
name = "my-lib"
version = "0.2.0"

[lib]
name = "my_lib"
path = "src/lib.nxl"

[[bin]]
name = "cli-tool"
path = "src/bin/cli.nxl"

[[bin]]
name = "benchmark"
path = "src/bin/bench.nxl"

[features]
default = []
performance-optimizations = []

[profile.dev]
opt-level = 0
debug = true

[profile.release]
opt-level = 3
```

**Build Commands**:
```bash
# Build library + all binaries
nxl_build.py build

# Build only specific binary
nxl_build.py build --bin cli-tool

# Check library without building
nxl_build.py check

# Clean everything
nxl_build.py clean
```

---

## Error Handling

**Common Errors**:

1. **No nlpl.toml found**:
   ```
   Error: Could not find nlpl.toml in current directory or any parent directory
   Run this command from a directory containing nlpl.toml
   ```
   **Solution**: Create `nlpl.toml` or `cd` to project directory.

2. **Source file not found**:
   ```
   Error: Source file not found: src/main.nlpl
   ```
   **Solution**: Create missing file or fix path in `[[bin]]` section.

3. **Unknown feature**:
   ```
   Warning: Unknown feature 'invalid-feature'
   ```
   **Solution**: Check feature name spelling in `[features]` section.

4. **Unknown binary**:
   ```
   Error: Binary 'unknown' not found
   ```
   **Solution**: Check binary name in `[[bin]]` sections.

5. **Missing feature dependencies**:
   ```
   Skipping analyzer (missing features: data-analytics)
   ```
   **Solution**: Add `--features data-analytics` to command.

6. **Compilation failed**:
   ```
   Error compiling source.nlpl: Parse error: ...
   Build failed
   ```
   **Solution**: Fix syntax errors in source code.

---

## Performance Tips

1. **Use `check` for rapid feedback**: 10-100x faster than full build
   ```bash
   nxl_build.py check  # Fast syntax checking
   ```

2. **Incremental builds**: Only recompile changed files (future)
   ```bash
   nxl_build.py build  # Smart rebuild
   ```

3. **Profile-specific builds**: Keep dev and release separate
   ```bash
   nxl_build.py build               # Fast dev build
   nxl_build.py build --release     # Optimized release
   ```

4. **Feature flags**: Disable unused features
   ```toml
   [features]
   default = []  # Minimal by default
   ```

---

## Future Enhancements

**Planned Features** (Task 4+):

1. **Incremental Compilation**:
   - Track file modification times
   - Build dependency graph
   - Only recompile changed files

2. **Dependency Resolution**:
   - Parse version constraints (`^1.0`, `~0.5`, `>=2.0`)
   - Validate compatibility
   - Detect conflicts

3. **Package Registry Integration**:
   - Download dependencies
   - Cache packages locally
   - Lock file support

4. **Workspace Support**:
   - Multi-project workspaces
   - Shared dependencies
   - Unified builds

5. **Documentation Generation**:
   - Extract doc comments
   - Generate API docs
   - Publish to registry

6. **Code Coverage**:
   - Instrument tests
   - Generate coverage reports
   - CI/CD integration

---

## Technical Details

### Implementation

**Language**: Python 3.8+  
**Size**: ~700 lines  
**Dependencies**:
- `nlpl.build.manifest` - Manifest parsing
- `nlpl.parser.lexer` - Tokenization
- `nlpl.parser.parser` - AST generation
- `nlpl.compiler` - Code generation (future)

**Architecture**:
```
BuildTool
  ├── build()          # Build orchestration
  ├── clean()          # Artifact removal
  ├── check()          # Syntax checking
  ├── run()            # Build + execute
  ├── test()           # Test runner
  ├── _resolve_features()    # Feature dependency resolution
  ├── _build_binary()        # Binary compilation
  ├── _build_library()       # Library compilation
  ├── _compile_single_file() # File compilation
  └── _check_file()          # Syntax validation
```

### Build Context

Each build creates a `BuildContext`:
- Manifest reference
- Build profile (opt level, debug, etc.)
- Enabled features
- Build directory
- Verbose flag

### Feature Resolution

Features are resolved transitively:
```python
requested = ["data-analytics"]
resolved = ["data-analytics", "nlpl-math/statistics"]  # Includes deps
```

---

## Comparison with Cargo

| Feature | nxl_build.py | Cargo |
|---------|---------------|-------|
| Manifest format | `nlpl.toml` | `Cargo.toml` |
| Build profiles | ✅ dev, release, custom | ✅ dev, release, custom |
| Feature flags | ✅ Transitive | ✅ Transitive |
| Multiple targets | ✅ Bins + lib | ✅ Bins + lib |
| Incremental compilation | ⏳ Planned | ✅ |
| Dependency resolution | ⏳ Planned | ✅ |
| Package registry | ⏳ Planned | ✅ crates.io |
| Workspace support | ⏳ Planned | ✅ |
| Documentation | ⏳ Planned | ✅ cargo doc |
| Testing | ✅ Basic | ✅ Advanced |

---

## See Also

- **Manifest Specification**: `docs/build/NLPL_TOML_SPECIFICATION.md`
- **Compiler Guide**: `COMPILER_GUIDE.md`
- **Development Guide**: `docs/7_development/`
- **Build System Architecture**: `docs/4_architecture/`

---

## Status

✅ **Task 3 Complete** - Build Tool CLI (February 14, 2026)

**Implemented**:
- ✅ All 5 commands: build, clean, check, run, test
- ✅ Build profile support (dev, release, custom)
- ✅ Feature flag resolution (transitive dependencies)
- ✅ Multiple binary targets
- ✅ Library target support
- ✅ Integration with nlplc compiler
- ✅ Comprehensive error handling
- ✅ Verbose mode for debugging

**Validated**:
- ✅ Build with dev profile
- ✅ Build with release profile
- ✅ Feature flag enabling
- ✅ Clean artifacts
- ✅ Run binaries
- ✅ Check syntax without compilation

**Next Steps**: Task 4 - Incremental Compilation System
