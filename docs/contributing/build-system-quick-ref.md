# NexusLang Build System - Quick Reference

## Installation

The build system is included with NexusLang. Make sure you have the dependencies installed:

```bash
pip install toml
```

## Quick Start

### Create a New Project

```bash
./nlplbuild init my_project
cd my_project
```

This creates:
```
my_project/
 src/
 main.nlpl # Main source file
 build/ # Build artifacts
 bin/ # Compiled executables
 tests/ # Test files
 nlpl.toml # Project configuration
 .gitignore # Git ignore file
```

### Build Your Project

```bash
# Build all targets
./nlplbuild build

# Build specific target
./nlplbuild build main

# Build with optimization
./nlplbuild build -O3

# Build with debug info
./nlplbuild build -g

# Verbose output
./nlplbuild build -v

# Use release profile
./nlplbuild build --profile release
```

### Run Your Project

```bash
# Build and run
./nlplbuild run

# Run with arguments
./nlplbuild run -- arg1 arg2

# Run with optimization
./nlplbuild run -O2
```

### Clean Build Artifacts

```bash
./nlplbuild clean
```

## Project Configuration (nlpl.toml)

### Basic Configuration

```toml
[package]
name = "my_app"
version = "0.1.0"
authors = ["Your Name <you@example.com>"]
description = "My awesome NexusLang application"
license = "MIT"

[build]
source_dir = "src"
build_dir = "build"
output_dir = "bin"
```

### Adding Dependencies

```toml
[dependencies]
# Registry dependency (future)
math_utils = "1.0.0"

# Git dependency
json_parser = { version = "^2.0", source = "git", git = "https://github.com/user/json.git", branch = "main" }

# Local path dependency
my_lib = { version = "*", source = "path", path = "../my_lib" }
```

### Defining Targets

```toml
[target.main]
source = "src/main.nxl"
type = "executable"
dependencies = []
optimization = 0
debug = false

[target.lib]
source = "src/lib.nxl"
type = "library"
dependencies = []
optimization = 2
debug = false
```

### Build Profiles

```toml
[profile.dev]
optimization = 0
debug = true

[profile.release]
optimization = 3
debug = false
```

## Command Reference

### nlplbuild init

Initialize a new NexusLang project.

```bash
nlplbuild init [NAME]
 --version VERSION Set initial version (default: 0.1.0)
 --authors AUTHOR... Set authors
 --license LICENSE Set license (default: MIT)
```

**Examples:**
```bash
nlplbuild init my_app
nlplbuild init my_lib --version 1.0.0 --license Apache-2.0
```

### nlplbuild build

Build the project or a specific target.

```bash
nlplbuild build [TARGET]
 -O, --optimization LEVEL Optimization level (0-3)
 -g, --debug Include debug information
 --profile PROFILE Build profile (dev/release)
 --no-incremental Disable incremental compilation
 -v, --verbose Verbose output
```

**Examples:**
```bash
nlplbuild build # Build all targets
nlplbuild build main # Build specific target
nlplbuild build -O3 # Build with optimization
nlplbuild build --profile release # Use release profile
nlplbuild build -v # Verbose output
```

### nlplbuild run

Build and run a target.

```bash
nlplbuild run [TARGET] [PROGRAM_ARGS...]
 -O, --optimization LEVEL Optimization level (0-3)
 -g, --debug Include debug information
 --profile PROFILE Build profile (dev/release)
 --no-incremental Disable incremental compilation
 -v, --verbose Verbose output
```

**Examples:**
```bash
nlplbuild run # Run default target
nlplbuild run main # Run specific target
nlplbuild run -- arg1 arg2 # Pass arguments to program
nlplbuild run -O2 # Run with optimization
```

### nlplbuild clean

Remove build artifacts.

```bash
nlplbuild clean
 -v, --verbose Verbose output
```

**Examples:**
```bash
nlplbuild clean
```

## Build Profiles

### Development Profile (default)

Optimized for fast compilation and debugging:
- Optimization: O0 (none)
- Debug info: enabled
- Use with: `--profile dev` or default

### Release Profile

Optimized for production deployment:
- Optimization: O3 (maximum)
- Debug info: disabled 
- Use with: `--profile release`

**Example:**
```bash
nlplbuild build --profile release
```

## Optimization Levels

- **O0** - No optimization (fastest compilation)
- **O1** - Basic optimization
- **O2** - Moderate optimization
- **O3** - Maximum optimization (best performance)

**Example:**
```bash
nlplbuild build -O3
```

## Incremental Compilation

The build system automatically tracks:
- Source file changes (SHA-256 hashing)
- Modification times
- Dependency changes

Only changed files are recompiled. To force full rebuild:
```bash
nlplbuild clean
nlplbuild build
```

Or disable incremental compilation:
```bash
nlplbuild build --no-incremental
```

## Target Types

### Executable
```toml
[target.my_app]
source = "src/main.nxl"
type = "executable"
```

### Library 
```toml
[target.my_lib]
source = "src/lib.nxl"
type = "library"
```

### Module (LLVM IR only)
```toml
[target.my_module]
source = "src/module.nxl"
type = "module"
```

## Dependency Version Constraints

- **Exact:** `"1.2.3"` - Must be exactly 1.2.3
- **Caret:** `"^1.2.3"` - Compatible with 1.2.3 (same major version)
- **Tilde:** `"~1.2.3"` - Approximately 1.2.3 (same major and minor)
- **Greater:** `">=1.0.0"` - At least 1.0.0
- **Less:** `"<2.0.0"` - Below 2.0.0
- **Any:** `"*"` - Any version

**Examples:**
```toml
[dependencies]
exact_dep = "1.2.3"
compatible_dep = "^1.0.0"
approx_dep = "~2.1.0"
range_dep = ">=1.0.0"
any_dep = "*"
```

## Workflow Examples

### Basic Development Workflow

```bash
# Create project
./nlplbuild init my_app
cd my_app

# Edit src/main.nlpl
# ... make changes ...

# Build and run
./nlplbuild run

# Make more changes
# ... edit files ...

# Incremental rebuild (fast!)
./nlplbuild run
```

### Release Build Workflow

```bash
# Build optimized release
./nlplbuild build --profile release

# Or with explicit optimization
./nlplbuild build -O3

# Run release build
./bin/main
```

### Multi-Target Project

```nlpl.toml
[target.server]
source = "src/server.nxl"
type = "executable"

[target.client]
source = "src/client.nxl"
type = "executable"

[target.common]
source = "src/common.nxl"
type = "library"
dependencies = []
```

```bash
# Build all targets
./nlplbuild build

# Build specific target
./nlplbuild build server
./nlplbuild build client

# Run specific target
./nlplbuild run server
```

## Troubleshooting

### Build Fails

```bash
# Clean and rebuild
./nlplbuild clean
./nlplbuild build -v # Verbose output shows details
```

### Incremental Build Issues

```bash
# Force full rebuild
./nlplbuild build --no-incremental
```

### Cache Problems

```bash
# Clear cache
rm -rf build/.cache
./nlplbuild build
```

## Tips & Tricks

1. **Use `-v` for debugging:** See exactly what the build system is doing
2. **Leverage incremental builds:** Only changed files rebuild
3. **Use profiles:** Quick `dev` builds, optimized `release` builds
4. **Cache is smart:** Automatically invalidates on changes
5. **Multiple targets:** Organize large projects into components

## Next Steps

- Learn NexusLang syntax in `docs/`
- Check `examples/` for sample programs
- Read `BUILD_SYSTEM_IMPLEMENTATION_STATUS.md` for technical details
- Explore dependency management features
- Try creating multi-target projects

## Support

- Documentation: `docs/`
- Examples: `examples/`
- Issues: GitHub repository
- Status files: `*_STATUS.md` files in project root
