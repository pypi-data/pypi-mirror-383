# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

xvcl is a VCL transpiler/preprocessor that extends Fastly VCL with metaprogramming features. It compiles `.xvcl` files (extended VCL source) into standard `.vcl` files (valid Fastly VCL) by processing directives like loops, conditionals, constants, macros, and functions. The output VCL works with Fastly and can be validated/tested with the Falco tool.

**Key concept**: xvcl is a build step for VCL. Write enhanced VCL source files, run xvcl, get clean VCL output.

## Build and Development Commands

### Setup and Installation

```bash
# Install dependencies using uv (preferred) or pip
uv pip install -e ".[dev]"

# Or using pip
pip install -e ".[dev]"

# Run xvcl directly after installation
xvcl input.xvcl -o output.vcl
```

### Development and Testing

```bash
# Run the compiler directly (during development)
python -m xvcl.compiler input.xvcl -o output.vcl

# Or use uv to run it
uv run xvcl input.xvcl -o output.vcl

# Run with debug mode to trace expansion
xvcl input.xvcl -o output.vcl --debug

# With include paths
xvcl input.xvcl -o output.vcl -I ./includes -I ./shared

# With source maps (adds comments showing where code came from)
xvcl input.xvcl -o output.vcl --source-maps
```

### Code Quality

```bash
# Format code with ruff
ruff format .

# Lint code
ruff check .

# Type check with mypy
mypy src/xvcl

# Fix auto-fixable linting issues
ruff check --fix .
```

### Testing Workflow

Since xvcl generates VCL, test the generated output:

```bash
# 1. Compile xvcl to vcl
xvcl example.xvcl -o example.vcl

# 2. Validate generated VCL with Falco (if available)
falco lint example.vcl

# 3. Test generated VCL with Falco
falco test example.vcl

# 4. Simulate generated VCL with Falco
falco simulate example.vcl
```

## Architecture

### Single-File Compiler Design

The entire compiler is implemented in `src/xvcl/compiler.py` (~1380 lines). This is intentional - xvcl is a standalone tool with no external dependencies beyond Python stdlib.

### Core Components

**XVCLCompiler Class** (`src/xvcl/compiler.py`):
- Main compiler orchestrator
- Manages state: constants, macros, functions, include tracking, output
- Multi-pass compilation strategy

**Data Structures**:
- `Macro`: Represents inline macros for zero-overhead text substitution
- `Function`: Represents user-defined functions that compile to VCL subroutines
- `SourceLocation`: Tracks file/line for error reporting
- `PreprocessorError`: Exception with rich context and formatting

### Compilation Pipeline (Multi-Pass)

The compiler processes xvcl source files in **6 passes**:

1. **Pass 1 - Extract Constants**: Parse `#const NAME TYPE = value` declarations and store them. Constants are removed from output and available for template substitution.

2. **Pass 2 - Process Includes**: Process `#include "file.xvcl"` directives. Supports include-once semantics (files only included once even if referenced multiple times) and cycle detection. Include path resolution: relative to current file first, then search include paths specified with `-I`.

3. **Pass 3 - Extract Inline Macros**: Parse `#inline...#endinline` blocks. Macros are zero-overhead text substitution that expand at compile time. Automatically handles operator precedence by wrapping arguments in parentheses when needed.

4. **Pass 4 - Extract Functions**: Parse `#def...#enddef` blocks. Functions compile to VCL subroutines that use global HTTP headers for parameter passing and return values. Supports single return values and tuple returns.

5. **Pass 4.5 - Join Multi-line Function Calls**: Normalize multi-line function calls into single lines to simplify pattern matching in the next pass.

6. **Pass 5 - Process Directives**: Process `#for` loops, `#if` conditionals, `#let` variable declarations, function calls, macro expansions, and template expressions (`{{expr}}`). This is the main code generation pass.

7. **Pass 6 - Generate Function Subroutines**: Append VCL subroutine implementations for all user-defined functions. Each function becomes a VCL subroutine with scope annotations.

### Key Implementation Details

**Function Compilation Strategy**:
- Functions are compiled into VCL subroutines with scope annotations (`//@recv, hash, hit, miss, pass, fetch, error, deliver, log`)
- Parameters are passed via global HTTP headers: `req.http.X-Func-{funcname}-{paramname}`
- Return values use global headers: `req.http.X-Func-{funcname}-Return` (or `Return0`, `Return1` for tuples)
- Type conversions are automatic: INTEGER/FLOAT/BOOL converted to/from STRING using `std.itoa()`, `std.atoi()`, `std.atof()`, etc.

**Macro Expansion**:
- Macros expand inline (no function call overhead)
- Nested macros are supported (up to 10 iterations)
- Arguments containing operators are automatically wrapped in parentheses to preserve precedence
- Expansion happens during Pass 5 before other processing

**Error Reporting**:
- Tracks source location (file, line) throughout compilation
- Shows context lines around errors (3 lines before/after)
- Provides "did you mean" suggestions for undefined names
- Color-coded terminal output for readability

**Include System**:
- Include-once semantics prevent duplicate inclusion
- Circular include detection with stack tracking
- Path resolution order: relative to current file → include paths (`-I`)
- Optional source map comments (`--source-maps`) mark included file boundaries

## Feature Directives

### Constants (`#const`)
```vcl
#const MAX_AGE INTEGER = 3600
#const ORIGIN STRING = "origin.example.com"
```
Constants are compile-time values substituted into templates. Type-checked when type is specified.

### Template Expressions (`{{expr}}`)
```vcl
set req.http.X-Port = "{{PORT}}";
backend F_{{REGION}}_{{ENV}} { ... }
```
Evaluated at compile time using Python's `eval()`. Has access to constants, loop variables, and safe built-ins (`range`, `len`, `str`, `int`, `hex`, `min`, `max`, `abs`).

### For Loops (`#for...#endfor`)
```vcl
#for i in range(5)
  backend web{{i}} { .host = "web{{i}}.example.com"; }
#endfor
```
Generate repetitive code. Can iterate over ranges or lists.

### Conditionals (`#if...#else...#endif`)
```vcl
#if PRODUCTION
  set req.http.X-Env = "prod";
#else
  set req.http.X-Env = "dev";
#endif
```
Conditional compilation based on compile-time conditions.

### Variables (`#let`)
```vcl
#let timestamp STRING = std.time(now, now);
```
Shorthand for `declare local` + `set`. Expands to two VCL statements.

### Inline Macros (`#inline...#endinline`)
```vcl
#inline normalize_host(host)
std.tolower(regsub(host, "^www\.", ""))
#endinline
```
Zero-overhead text substitution. Use for simple expressions repeated throughout code.

### Functions (`#def...#enddef`)
```vcl
#def normalize_path(path STRING) -> STRING
  declare local var.result STRING;
  set var.result = std.tolower(path);
  return var.result;
#enddef
```
Reusable logic that compiles to VCL subroutines. Supports single and tuple returns.

### File Includes (`#include`)
```vcl
#include "includes/backends.xvcl"
```
Include other xvcl files. Include-once semantics and cycle detection.

## Code Organization

```
.
├── src/xvcl/
│   ├── __init__.py         # Package exports (XVCLCompiler, __version__)
│   └── compiler.py         # Single-file compiler implementation (~1380 lines)
├── pyproject.toml          # Project metadata, dependencies, build config
├── README.md               # Comprehensive user documentation with examples
├── xvcl-quick-reference.md # Quick syntax reference for users
└── .python-version         # Python version (3.9)
```

**No tests directory**: xvcl is tested by compiling example files and validating the generated VCL with Falco. The project relies on Falco for VCL validation rather than unit tests.

## Configuration

Configured via `pyproject.toml`:
- **Build system**: Hatchling (PEP 517)
- **Entry point**: `xvcl` command → `xvcl.compiler:main`
- **Linting**: Ruff (replaces flake8, isort, pyupgrade)
- **Type checking**: mypy (lenient config, not strict)
- **Python version**: 3.9+ required

## Integration with Falco

xvcl is designed to work with Falco (VCL linter/tester/simulator). Typical workflow:

1. Write xvcl source (`.xvcl` files)
2. Compile with xvcl → generates `.vcl` files
3. Validate with Falco: `falco lint output.vcl`
4. Test with Falco: `falco test output.vcl`
5. Deploy the generated `.vcl` to Fastly

## Notes

- **No backwards compatibility concerns**: The user has explicitly stated they don't care about backwards compatibility for the VCL preprocessor
- **Standalone tool**: xvcl has zero external dependencies (only Python stdlib)
- **Single-file design**: The entire compiler is intentionally in one file for portability
- **Debug mode**: Always use `--debug` flag when troubleshooting compilation issues
- **Source maps**: Use `--source-maps` during development to track code origin
