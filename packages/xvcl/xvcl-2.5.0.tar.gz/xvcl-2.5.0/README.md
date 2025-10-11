# xvcl

Supercharge your Fastly VCL with programming constructs like loops, functions, constants, and more.

**📖 [Quick Reference Guide](xvcl-quick-reference.md)** - One-page syntax reference for all xvcl features

## Table of Contents

- [Introduction](#introduction)
- [Why Use xvcl?](#why-use-xvcl)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Core Features](#core-features)
  - [Constants](#constants)
  - [Template Expressions](#template-expressions)
  - [For Loops](#for-loops)
  - [Conditionals](#conditionals)
  - [Variables](#variables)
  - [File Includes](#file-includes)
- [Advanced Features](#advanced-features)
  - [Inline Macros](#inline-macros)
  - [Functions](#functions)
- [Command-Line Usage](#command-line-usage)
- [Integration with Falco](#integration-with-falco)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Introduction

xvcl is VCL transpiler that extends Fastly VCL with programming constructs that generate standard VCL code.

Think of it as a build step for your VCL: write enhanced VCL source files, run xvcl, and get clean, valid VCL output.

> **💡 Tip:** For a quick syntax reference, see the [xvcl Quick Reference Guide](xvcl-quick-reference.md).

**What you can do:**

- Define constants once, use them everywhere
- Generate repetitive code with for loops
- Create reusable functions with return values
- Build zero-overhead macros for common patterns
- Conditionally compile code for different environments
- Split large VCL files into modular includes

**What you get:**

- Standard VCL output that works with Fastly
- Compile-time safety and error checking
- Reduced code duplication
- Better maintainability

## Why Use xvcl?

VCL is powerful but limited by design. You can't define functions with return values, you can't use loops, and managing constants means find-and-replace. This leads to:

- **Copy-paste errors:** Similar backends? Copy, paste, modify, repeat, make mistakes
- **Magic numbers:** Hardcoded values scattered throughout your code
- **Duplication:** Same logic repeated in multiple subroutines
- **Poor maintainability:** Change one thing, update it in 20 places

xvcl solves these problems by adding programming constructs that compile down to clean VCL.

### Real-World Example

**Without xvcl (manual, error-prone):**

```vcl
backend web1 {
  .host = "web1.example.com";
  .port = "80";
}

backend web2 {
  .host = "web2.example.com";
  .port = "80";
}

backend web3 {
  .host = "web3.example.com";
  .port = "80";
}

sub vcl_recv {
  if (req.http.Host == "web1.example.com") {
    set req.backend = web1;
  }
  if (req.http.Host == "web2.example.com") {
    set req.backend = web2;
  }
  if (req.http.Host == "web3.example.com") {
    set req.backend = web3;
  }
}
```

**With xvcl (clean, maintainable):**

```vcl
#const BACKENDS = ["web1", "web2", "web3"]

#for backend in BACKENDS
backend {{backend}} {
  .host = "{{backend}}.example.com";
  .port = "80";
}
#endfor

sub vcl_recv {
#for backend in BACKENDS
  if (req.http.Host == "{{backend}}.example.com") {
    set req.backend = {{backend}};
  }
#endfor
}
```

Adding a new backend? Just update the list. xvcl generates all the code.

## Installation

xvcl is a Python package. You need Python 3.9 or later.

```bash
# Using pip
pip install xvcl

# Or install from source
pip install .

# Development installation with dev dependencies
pip install -e ".[dev]"

# Using uv (recommended for faster installation)
uv pip install xvcl
```

After installation, the `xvcl` command is available globally.

**No external dependencies** - uses only Python standard library.

## Quick Start

Create an xvcl source file (use `.xvcl` extension by convention):

**`hello.xvcl`:**

```vcl
#const MESSAGE = "Hello from xvcl!"

sub vcl_recv {
  set req.http.X-Message = "{{MESSAGE}}";
}
```

Run xvcl:

```bash
xvcl hello.xvcl -o hello.vcl
```

Output **`hello.vcl`:**

```vcl
sub vcl_recv {
  set req.http.X-Message = "Hello from xvcl!";
}
```

Validate with Falco:

```bash
falco lint hello.vcl
```

## Core Features

### Constants

Define named constants with type checking. Constants are evaluated at preprocessing time and substituted into your code.

**Syntax:**

```vcl
#const NAME TYPE = value
```

**Supported types:**
- `INTEGER` - Whole numbers
- `STRING` - Text strings
- `FLOAT` - Decimal numbers
- `BOOL` - True/False

**Example:**

```vcl
#const MAX_AGE INTEGER = 3600
#const ORIGIN STRING = "origin.example.com"
#const PRODUCTION BOOL = True
#const CACHE_VERSION FLOAT = 1.5
```

**Using constants in templates:**

```vcl
#const TTL = 300
#const BACKEND_HOST = "api.example.com"

backend F_api {
  .host = "{{BACKEND_HOST}}";
  .port = "443";
}

sub vcl_fetch {
  set beresp.ttl = {{TTL}}s;
}
```

**Why use constants?**

- Single source of truth for configuration values
- Easy to update across entire VCL
- Type safety prevents mistakes
- Self-documenting code

### Template Expressions

Embed Python expressions in your VCL using `{{expression}}` syntax. Expressions are evaluated at preprocessing time.

**Example:**

```vcl
#const PORT = 8080

sub vcl_recv {
  set req.http.X-Port = "{{PORT}}";
  set req.http.X-Double = "{{PORT * 2}}";
  set req.http.X-Hex = "{{hex(PORT)}}";
}
```

**Output:**

```vcl
sub vcl_recv {
  set req.http.X-Port = "8080";
  set req.http.X-Double = "16160";
  set req.http.X-Hex = "0x1f90";
}
```

**Available functions:**

- `range(n)` - Generate number sequences
- `len(list)` - Get list length
- `str(x)`, `int(x)` - Type conversions
- `hex(n)` - Hexadecimal conversion
- `format(x, fmt)` - Format values
- `enumerate(iterable)` - Enumerate with indices
- `min(...)`, `max(...)` - Min/max values
- `abs(n)` - Absolute value

**String formatting:**

```vcl
#const REGION = "us-east"
#const INDEX = 1

set req.backend = F_backend_{{REGION}}_{{INDEX}};
```

### For Loops

Generate repetitive VCL code by iterating over ranges or lists.

**Syntax:**

```vcl
#for variable in iterable
  // Code to repeat
#endfor
```

**Example 1: Range-based loop**

```vcl
#for i in range(5)
backend web{{i}} {
  .host = "web{{i}}.example.com";
  .port = "80";
}
#endfor
```

**Output:**

```vcl
backend web0 {
  .host = "web0.example.com";
  .port = "80";
}
backend web1 {
  .host = "web1.example.com";
  .port = "80";
}
// ... continues through web4
```

**Example 2: List iteration**

```vcl
#const REGIONS = ["us-east", "us-west", "eu-west"]

#for region in REGIONS
backend F_{{region}} {
  .host = "{{region}}.example.com";
  .port = "443";
  .ssl = true;
}
#endfor
```

**Example 3: Nested loops**

```vcl
#const REGIONS = ["us", "eu"]
#const ENVS = ["prod", "staging"]

#for region in REGIONS
  #for env in ENVS
backend {{region}}_{{env}} {
  .host = "{{env}}.{{region}}.example.com";
  .port = "443";
}
  #endfor
#endfor
```

**Why use for loops?**

- Generate multiple similar backends
- Create ACL entries from lists
- Build routing logic programmatically
- Reduce copy-paste errors

### Conditionals

Conditionally include or exclude code based on compile-time conditions.

**Syntax:**

```vcl
#if condition
  // Code when true
#else
  // Code when false (optional)
#endif
```

**Example 1: Environment-specific configuration**

```vcl
#const PRODUCTION = True
#const DEBUG = False

sub vcl_recv {
#if PRODUCTION
  set req.http.X-Environment = "production";
  unset req.http.X-Debug-Info;
#else
  set req.http.X-Environment = "development";
  set req.http.X-Debug-Info = "Enabled";
#endif

#if DEBUG
  set req.http.X-Request-ID = randomstr(16, "0123456789abcdef");
#endif
}
```

**Example 2: Feature flags**

```vcl
#const ENABLE_NEW_ROUTING = True
#const ENABLE_RATE_LIMITING = False

sub vcl_recv {
#if ENABLE_NEW_ROUTING
  call new_routing_logic;
#else
  call legacy_routing_logic;
#endif

#if ENABLE_RATE_LIMITING
  if (ratelimit.check_rate("client_" + client.ip, 1, 100, 60s, 1000s)) {
    error 429 "Too Many Requests";
  }
#endif
}
```

**Why use conditionals?**

- Single codebase for multiple environments
- Easy feature flag management
- Dead code elimination (code in false branches isn't generated)
- Compile-time optimization

### Variables

Declare and initialize local variables in one step.

**Syntax:**

```vcl
#let name TYPE = expression;
```

**Example:**

```vcl
sub vcl_recv {
  #let timestamp STRING = std.time(now, now);
  #let cache_key STRING = req.url.path + req.http.Host;

  set req.http.X-Timestamp = var.timestamp;
  set req.hash = var.cache_key;
}
```

**Expands to:**

```vcl
sub vcl_recv {
  declare local var.timestamp STRING;
  set var.timestamp = std.time(now, now);
  declare local var.cache_key STRING;
  set var.cache_key = req.url.path + req.http.Host;

  set req.http.X-Timestamp = var.timestamp;
  set req.hash = var.cache_key;
}
```

**Why use #let?**

- Shorter syntax than separate declare + set
- Clear initialization point
- Reduces boilerplate

### File Includes

Split large VCL files into modular, reusable components.

**Syntax:**

```vcl
#include "path/to/file.xvcl"
```

**Example project structure:**

```
vcl/
├── main.xvcl
├── includes/
│   ├── backends.xvcl
│   ├── security.xvcl
│   └── routing.xvcl
```

**`main.xvcl`:**

```vcl
#include "includes/backends.xvcl"
#include "includes/security.xvcl"
#include "includes/routing.xvcl"

sub vcl_recv {
  call security_checks;
  call routing_logic;
}
```

**`includes/backends.xvcl`:**

```vcl
#const BACKENDS = ["web1", "web2", "web3"]

#for backend in BACKENDS
backend F_{{backend}} {
  .host = "{{backend}}.example.com";
  .port = "443";
}
#endfor
```

**Include path resolution:**

1. Relative to the current file
2. Relative to include paths specified with `-I`

**Run with include paths:**

```bash
xvcl main.xvcl -o main.vcl -I ./vcl/includes
```

**Features:**

- **Include-once semantics:** Files are only included once even if referenced multiple times
- **Cycle detection:** Prevents circular includes
- **Shared constants:** Constants defined in included files are available to the parent

**Why use includes?**

- Organize large VCL projects
- Share common configurations across multiple VCL files
- Team collaboration (different files for different concerns)
- Reusable components library

## Advanced Features

### Inline Macros

Create zero-overhead text substitution macros. Unlike functions, macros are expanded inline at compile time with no runtime cost.

**Syntax:**

```vcl
#inline macro_name(param1, param2, ...)
expression
#endinline
```

**Example 1: String concatenation**

```vcl
#inline add_prefix(s)
"prefix-" + s
#endinline

#inline add_suffix(s)
s + "-suffix"
#endinline

sub vcl_recv {
  set req.http.X-Modified = add_prefix("test");
  set req.http.X-Both = add_prefix(add_suffix("middle"));
}
```

**Output:**

```vcl
sub vcl_recv {
  set req.http.X-Modified = "prefix-" + "test";
  set req.http.X-Both = "prefix-" + "middle" + "-suffix";
}
```

**Example 2: Common patterns**

```vcl
#inline normalize_host(host)
std.tolower(regsub(host, "^www\.", ""))
#endinline

#inline cache_key(url, host)
digest.hash_md5(url + "|" + host)
#endinline

sub vcl_recv {
  set req.http.X-Normalized = normalize_host(req.http.Host);
  set req.hash = cache_key(req.url, req.http.Host);
}
```

**Output:**

```vcl
sub vcl_recv {
  set req.http.X-Normalized = std.tolower(regsub(req.http.Host, "^www\.", ""));
  set req.hash = digest.hash_md5(req.url + "|" + req.http.Host);
}
```

**Example 3: Operator precedence handling**

xvcl automatically handles operator precedence:

```vcl
#inline double(x)
x + x
#endinline

sub vcl_recv {
  declare local var.result INTEGER;
  set var.result = double(5) * 10;  // Correctly expands to (5 + 5) * 10
}
```

**Macros vs Functions:**

| Feature       | Macros              | Functions                     |
| ------------- | ------------------- | ----------------------------- |
| Expansion     | Compile-time inline | Runtime subroutine call       |
| Overhead      | None                | Subroutine call + global vars |
| Return values | Expression only     | Single or tuple               |
| Use case      | Simple expressions  | Complex logic                 |

**When to use macros:**

- String manipulation patterns
- Simple calculations
- Common expressions repeated throughout code
- When you need zero runtime overhead

**When to use functions:**

- Complex logic with multiple statements
- Need to return multiple values
- Conditional logic or loops inside the reusable code

### Functions

Define reusable functions with parameters and return values. Functions are compiled into VCL subroutines.

**Syntax:**

```vcl
#def function_name(param1 TYPE, param2 TYPE, ...) -> RETURN_TYPE
  // Function body
  return value;
#enddef
```

**Example 1: Simple function**

```vcl
#def add(a INTEGER, b INTEGER) -> INTEGER
  declare local var.sum INTEGER;
  set var.sum = a + b;
  return var.sum;
#enddef

sub vcl_recv {
  declare local var.result INTEGER;
  set var.result = add(5, 10);
  set req.http.X-Sum = var.result;
}
```

**Example 2: String processing**

```vcl
#def normalize_path(path STRING) -> STRING
  declare local var.result STRING;
  set var.result = std.tolower(path);
  set var.result = regsub(var.result, "/$", "");
  return var.result;
#enddef

sub vcl_recv {
  declare local var.clean_path STRING;
  set var.clean_path = normalize_path(req.url.path);
  set req.url = var.clean_path;
}
```

**Example 3: Functions with conditionals**

```vcl
#def should_cache(url STRING) -> BOOL
  declare local var.cacheable BOOL;

  if (url ~ "^/api/") {
    set var.cacheable = false;
  } else if (url ~ "\.(jpg|png|css|js)$") {
    set var.cacheable = true;
  } else {
    set var.cacheable = false;
  }

  return var.cacheable;
#enddef

sub vcl_recv {
  declare local var.can_cache BOOL;
  set var.can_cache = should_cache(req.url.path);

  if (var.can_cache) {
    return(lookup);
  } else {
    return(pass);
  }
}
```

**Example 4: Tuple returns (multiple values)**

```vcl
#def parse_user_agent(ua STRING) -> (STRING, STRING)
  declare local var.browser STRING;
  declare local var.os STRING;

  if (ua ~ "Chrome") {
    set var.browser = "chrome";
  } else if (ua ~ "Firefox") {
    set var.browser = "firefox";
  } else {
    set var.browser = "other";
  }

  if (ua ~ "Windows") {
    set var.os = "windows";
  } else if (ua ~ "Mac") {
    set var.os = "macos";
  } else {
    set var.os = "other";
  }

  return var.browser, var.os;
#enddef

sub vcl_recv {
  declare local var.browser STRING;
  declare local var.os STRING;

  set var.browser, var.os = parse_user_agent(req.http.User-Agent);

  set req.http.X-Browser = var.browser;
  set req.http.X-OS = var.os;
}
```

**Behind the scenes:**

Functions are compiled into VCL subroutines using global headers for parameter passing:

```vcl
// Your code:
set var.result = add(5, 10);

// Becomes:
set req.http.X-Func-add-a = std.itoa(5);
set req.http.X-Func-add-b = std.itoa(10);
call add;
set var.result = std.atoi(req.http.X-Func-add-Return);
```

xvcl generates the `sub add { ... }` implementation and handles all type conversions automatically.

**Function features:**

- **Type safety:** Parameters and returns are type-checked
- **Multiple returns:** Use tuple syntax to return multiple values
- **Automatic conversions:** INTEGER/FLOAT/BOOL are converted to/from STRING automatically
- **Scope annotations:** Generated subroutines work in all VCL scopes

**Why use functions?**

- Reusable complex logic
- Reduce code duplication
- Easier testing (test the function once)
- Better code organization

## Command-Line Usage

**Basic usage:**

```bash
xvcl input.xvcl -o output.vcl
```

**Options:**

| Option          | Description                                         |
| --------------- | --------------------------------------------------- |
| `input`         | Input xvcl source file (required)                   |
| `-o, --output`  | Output VCL file (default: replaces .xvcl with .vcl) |
| `-I, --include` | Add include search path (repeatable)                |
| `--debug`       | Enable debug output with expansion traces           |
| `--source-maps` | Add source map comments to output                   |
| `-v, --verbose` | Verbose output (alias for --debug)                  |

**Examples:**

```bash
# Basic compilation
xvcl main.xvcl -o main.vcl

# With include paths
xvcl main.xvcl -o main.vcl \
  -I ./includes \
  -I ./shared

# Debug mode (see expansion traces)
xvcl main.xvcl -o main.vcl --debug

# With source maps (track generated code origin)
xvcl main.xvcl -o main.vcl --source-maps
```

**Automatic output naming:**

If you don't specify `-o`, xvcl replaces `.xvcl` with `.vcl`:

```bash
# These are equivalent:
xvcl main.xvcl
xvcl main.xvcl -o main.vcl
```

**Debug mode output:**

```bash
$ xvcl example.xvcl --debug

[DEBUG] Processing file: example.xvcl
[DEBUG] Pass 1: Extracting constants
[DEBUG]   Defined constant: MAX_AGE = 3600
[DEBUG] Pass 2: Processing includes
[DEBUG] Pass 3: Extracting inline macros
[DEBUG]   Defined macro: add_prefix(s)
[DEBUG] Pass 4: Extracting functions
[DEBUG] Pass 5: Processing directives and generating code
[DEBUG]   Processing #for at line 10
[DEBUG]     Loop iterating 3 times
[DEBUG]       Iteration 0: backend = web1
[DEBUG]       Iteration 1: backend = web2
[DEBUG]       Iteration 2: backend = web3
[DEBUG] Pass 6: Generating function subroutines
✓ Compiled example.xvcl -> example.vcl
  Constants: 1
  Macros: 1 (add_prefix)
  Functions: 0
```

## Integration with Falco

xvcl generates standard VCL that you can use with Falco's full toolset.

**Recommended workflow:**

```bash
# 1. Write your xvcl source
vim main.xvcl

# 2. Compile with xvcl
xvcl main.xvcl -o main.vcl

# 3. Lint with Falco
falco lint main.vcl

# 4. Test with Falco
falco test main.vcl

# 5. Simulate with Falco
falco simulate main.vcl
```

**Makefile integration:**

```makefile
# Makefile
.PHONY: build lint test clean

XVCL = xvcl
SOURCES = $(wildcard *.xvcl)
OUTPUTS = $(SOURCES:.xvcl=.vcl)

build: $(OUTPUTS)

%.vcl: %.xvcl
	$(XVCL) $< -o $@ -I ./includes

lint: build
	falco lint *.vcl

test: build
	falco test *.vcl

clean:
	rm -f $(OUTPUTS)
```

**CI/CD integration:**

```yaml
# .github/workflows/vcl.yml
name: VCL CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install Falco
        run: |
          wget https://github.com/ysugimoto/falco/releases/latest/download/falco_linux_amd64
          chmod +x falco_linux_amd64
          sudo mv falco_linux_amd64 /usr/local/bin/falco

      - name: Compile xvcl
        run: |
          xvcl main.xvcl -o main.vcl

      - name: Lint VCL
        run: falco lint main.vcl

      - name: Test VCL
        run: falco test main.vcl
```

**Testing compiled VCL:**

You can write Falco tests for your generated VCL:

**`main.test.vcl`:**

```vcl
// @suite: Backend routing tests

// @test: Should route to correct backend
sub test_backend_routing {
  set req.http.Host = "web1.example.com";
  call vcl_recv;

  assert.equal(req.backend, "web1");
}
```

Run tests after compilation:

```bash
xvcl main.xvcl -o main.vcl
falco test main.vcl
```

## Best Practices

### 1. Use the `.xvcl` extension

Makes it clear which files are xvcl source files:

```
✓ main.xvcl → main.vcl
✗ main.vcl → main.vcl.processed
```

### 2. Keep constants at the top

```vcl
// Good: Constants first, easy to find
#const MAX_BACKENDS = 10
#const PRODUCTION = True

#for i in range(MAX_BACKENDS)
  // ... use constant
#endfor
```

### 3. Use descriptive constant names

```vcl
// Good
#const CACHE_TTL_SECONDS = 3600
#const API_BACKEND_HOST = "api.example.com"

// Bad
#const X = 3600
#const B = "api.example.com"
```

### 4. Comment your macros and functions

```vcl
// Normalizes a hostname by removing www prefix and converting to lowercase
#inline normalize_host(host)
std.tolower(regsub(host, "^www\.", ""))
#endinline

// Parses User-Agent and returns (browser, os) tuple
#def parse_user_agent(ua STRING) -> (STRING, STRING)
  // ...
#enddef
```

### 5. Prefer macros for simple expressions, functions for complex logic

```vcl
// Good: Simple expression = macro
#inline cache_key(url, host)
digest.hash_md5(url + "|" + host)
#endinline

// Good: Complex logic = function
#def should_cache(url STRING, method STRING) -> BOOL
  declare local var.result BOOL;
  if (method != "GET" && method != "HEAD") {
    set var.result = false;
  } else if (url ~ "^/api/") {
    set var.result = false;
  } else {
    set var.result = true;
  }
  return var.result;
#enddef
```

### 6. Use includes for organization

```
vcl/
├── main.xvcl          # Main entry point
├── config.xvcl        # Constants and configuration
├── includes/
│   ├── backends.xvcl
│   ├── security.xvcl
│   ├── routing.xvcl
│   └── caching.xvcl
```

### 7. Version control both source and output

```gitignore
# Include both in git
*.xvcl
*.vcl

# But gitignore generated files in CI
# (if you regenerate on deploy)
```

**Or** only version control source files and regenerate on deployment:

```gitignore
# Version control xvcl source only
*.xvcl

# Ignore generated VCL
*.vcl
```

Choose based on your deployment process.

### 8. Add source maps in development

```bash
# Development: easier debugging
xvcl main.xvcl -o main.vcl --source-maps

# Production: cleaner output
xvcl main.xvcl -o main.vcl
```

Source maps add comments like:

```vcl
// BEGIN INCLUDE: includes/backends.xvcl
backend F_web1 { ... }
// END INCLUDE: includes/backends.xvcl
```

### 9. Test incrementally

Don't write a massive source file and compile once. Test as you go:

```bash
# Write a bit
vim main.xvcl

# Compile
xvcl main.xvcl

# Check output
cat main.vcl

# Lint
falco lint main.vcl

# Repeat
```

### 10. Use debug mode when things go wrong

```bash
xvcl main.xvcl --debug
```

Shows exactly what xvcl is doing.

## Troubleshooting

### Error: "Name 'X' is not defined"

**Problem:** You're using a variable or constant that doesn't exist.

```vcl
#const PORT = 8080

set req.http.X-Value = "{{PROT}}";  // Typo!
```

**Error:**

```
Error at main.xvcl:3:
  Name 'PROT' is not defined
  Did you mean: PORT?
```

**Solution:** Check spelling. xvcl suggests similar names.

### Error: "Invalid #const syntax"

**Problem:** Malformed constant declaration.

```vcl
#const PORT 8080        // Missing = sign
#const = 8080           // Missing name
#const PORT = STRING    // Missing value
```

**Solution:** Use correct syntax:

```vcl
#const PORT INTEGER = 8080
```

### Error: "No matching #endfor for #for"

**Problem:** Missing closing keyword.

```vcl
#for i in range(10)
  backend web{{i}} { ... }
// Missing #endfor
```

**Solution:** Add the closing keyword:

```vcl
#for i in range(10)
  backend web{{i}} { ... }
#endfor
```

### Error: "Circular include detected"

**Problem:** File A includes file B which includes file A.

```
main.xvcl includes util.xvcl
util.xvcl includes main.xvcl
```

**Solution:** Restructure your includes. Create a shared file:

```
main.xvcl includes shared.xvcl
util.xvcl includes shared.xvcl
```

### Error: "Cannot find included file"

**Problem:** Include path is wrong or file doesn't exist.

```vcl
#include "includes/backends.xvcl"
```

**Solution:** Check path and use `-I` flag:

```bash
xvcl main.xvcl -o main.vcl -I ./includes
```

### Generated VCL has syntax errors

**Problem:** xvcl generated invalid VCL.

**Solution:**

1. Check the generated output:
   ```bash
   cat main.vcl
   ```

2. Find the problematic section

3. Trace back to source with `--source-maps`:

   ```bash
   xvcl main.xvcl -o main.vcl --source-maps
   ```

4. Fix the source file

### Macro expansion issues

**Problem:** Macro expands incorrectly.

```vcl
#inline double(x)
x + x
#endinline

set var.result = double(1 + 2);
// Expands to: (1 + 2) + (1 + 2)  ✓ Correct
```

xvcl automatically adds parentheses when needed.

**If you see issues:** Check operator precedence in your macro definition.

### Function calls not working

**Problem:** Function call doesn't get replaced.

```vcl
#def add(a INTEGER, b INTEGER) -> INTEGER
  return a + b;
#enddef

set var.result = add(5, 10);
```

**Common causes:**

1. **Missing semicolon:** Function calls must end with `;`
   ```vcl
   set var.result = add(5, 10);  // ✓ Correct
   set var.result = add(5, 10)   // ✗ Won't match
   ```

2. **Wrong number of arguments:**
   ```vcl
   set var.result = add(5);      // ✗ Expects 2 args
   ```

3. **Typo in function name:**
   ```vcl
   set var.result = addr(5, 10); // ✗ Function 'addr' not defined
   ```

### Performance issues

**Problem:** Compilation is slow.

**Common causes:**

1. **Large loops:** `#for i in range(10000)` generates 10,000 copies
2. **Deep nesting:** Multiple nested loops or includes
3. **Complex macros:** Heavily nested macro expansions

**Solutions:**

1. Reduce loop iterations if possible
2. Use functions instead of generating everything inline
3. Split into multiple source files
4. Profile with `--debug` to see what's slow

### Getting help

**Check the error context:**

Errors show surrounding lines:

```
Error at main.xvcl:15:
  Invalid #for syntax: #for in range(10)

  Context:
    13: sub vcl_recv {
    14:   // Generate backends
  → 15:   #for in range(10)
    16:     backend web{{i}} { ... }
    17:   #endfor
    18: }
```

**Enable debug mode:**

```bash
xvcl main.xvcl --debug
```

**Validate generated VCL:**

```bash
falco lint main.vcl -vv
```

The `-vv` flag shows detailed Falco errors.

---

## Examples Gallery

Here are complete, working examples you can use as starting points.

### Example 1: Multi-region backends

**`multi-region.xvcl`:**

```vcl
#const REGIONS = ["us-east", "us-west", "eu-west", "ap-south"]
#const DEFAULT_REGION = "us-east"

#for region in REGIONS
backend F_origin_{{region}} {
  .host = "origin-{{region}}.example.com";
  .port = "443";
  .ssl = true;
  .connect_timeout = 5s;
  .first_byte_timeout = 30s;
  .between_bytes_timeout = 10s;
}
#endfor

sub vcl_recv {
  declare local var.region STRING;

  // Detect region from client IP or header
  if (req.http.X-Region) {
    set var.region = req.http.X-Region;
  } else {
    set var.region = "{{DEFAULT_REGION}}";
  }

  // Route to appropriate backend
#for region in REGIONS
  if (var.region == "{{region}}") {
    set req.backend = F_origin_{{region}};
  }
#endfor
}
```

### Example 2: Feature flag system

**`feature-flags.xvcl`:**

```vcl
#const ENABLE_NEW_CACHE_POLICY = True
#const ENABLE_WEBP_CONVERSION = True
#const ENABLE_ANALYTICS = False
#const ENABLE_DEBUG_HEADERS = False

sub vcl_recv {
#if ENABLE_NEW_CACHE_POLICY
  // New cache policy with fine-grained control
  if (req.url.path ~ "\.(jpg|png|gif|css|js)$") {
    set req.http.X-Cache-Policy = "static";
  } else {
    set req.http.X-Cache-Policy = "dynamic";
  }
#else
  // Legacy cache policy
  set req.http.X-Cache-Policy = "default";
#endif

#if ENABLE_WEBP_CONVERSION
  if (req.http.Accept ~ "image/webp") {
    set req.http.X-Image-Format = "webp";
  }
#endif

#if ENABLE_ANALYTICS
  set req.http.X-Analytics-ID = uuid.generate();
#endif
}

sub vcl_deliver {
#if ENABLE_DEBUG_HEADERS
  set resp.http.X-Cache-Status = resp.http.X-Cache;
  set resp.http.X-Backend = req.backend;
  set resp.http.X-Region = req.http.X-Region;
#endif
}
```

### Example 3: URL normalization library

**`url-utils.xvcl`:**

```vcl
// Inline macros for common URL operations
#inline strip_www(host)
regsub(host, "^www\.", "")
#endinline

#inline lowercase_host(host)
std.tolower(host)
#endinline

#inline normalize_host(host)
lowercase_host(strip_www(host))
#endinline

#inline remove_trailing_slash(path)
regsub(path, "/$", "")
#endinline

#inline remove_query_string(url)
regsub(url, "\?.*$", "")
#endinline

// Function for complex normalization
#def normalize_url(url STRING, host STRING) -> STRING
  declare local var.result STRING;
  declare local var.clean_host STRING;
  declare local var.clean_path STRING;

  set var.clean_host = normalize_host(host);
  set var.clean_path = remove_trailing_slash(url);
  set var.result = "https://" + var.clean_host + var.clean_path;

  return var.result;
#enddef

sub vcl_recv {
  declare local var.canonical_url STRING;
  set var.canonical_url = normalize_url(req.url.path, req.http.Host);
  set req.http.X-Canonical-URL = var.canonical_url;
}
```

### Example 4: A/B testing framework

**`ab-testing.xvcl`:**

```vcl
#const EXPERIMENTS = [
  ("homepage_hero", 50),
  ("checkout_flow", 30),
  ("pricing_page", 25)
]

#def assign_experiment(exp_id STRING, percentage INTEGER) -> BOOL
  declare local var.hash STRING;
  declare local var.value INTEGER;
  declare local var.assigned BOOL;

  set var.hash = digest.hash_md5(client.ip + exp_id);
  set var.value = std.atoi(substr(var.hash, 0, 2)) % 100;
  set var.assigned = (var.value < percentage);

  return var.assigned;
#enddef

sub vcl_recv {
  declare local var.in_experiment BOOL;

#for exp_id, percentage in EXPERIMENTS
  set var.in_experiment = assign_experiment("{{exp_id}}", {{percentage}});
  if (var.in_experiment) {
    set req.http.X-Experiment-{{exp_id}} = "variant";
  } else {
    set req.http.X-Experiment-{{exp_id}} = "control";
  }
#endfor
}
```

---

## Summary

xvcl extends Fastly VCL with powerful programming constructs:

**Core features:**

- Constants - Single source of truth for configuration
- Template expressions - Dynamic value substitution
- For loops - Generate repetitive code
- Conditionals - Environment-specific builds
- Variables - Cleaner local variable syntax
- Includes - Modular code organization

**Advanced features:**

- Inline macros - Zero-overhead text substitution
- Functions - Reusable logic with return values

**Benefits:**

- Less code duplication
- Fewer copy-paste errors
- Better maintainability
- Easier testing
- Faster development

**Integration:**

- Works with Falco's full toolset
- Standard VCL output
- No runtime overhead
- Easy CI/CD integration

Start simple, add complexity as needed. xvcl grows with your VCL projects.
