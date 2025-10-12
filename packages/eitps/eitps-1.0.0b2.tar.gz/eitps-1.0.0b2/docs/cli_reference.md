# ⚙️ CLI Reference

Complete reference for PowerScript command-line tools.

---

## 📦 Available Commands

TPS provides 4 main CLI commands:

| Command | Purpose | Status |
|---------|---------|--------|
| `tps-compile` | Compile `.ps` to `.py` | ✅ Stable |
| `tps-run` | Compile and execute | ✅ Stable |
| `tps-create` | Create new projects | ✅ Stable |
| `tps-check` | Type check without compiling | ✅ Stable |

---

## 🔧 tps-compile

Compile PowerScript files to Python.

### Basic Usage

```bash
# Compile single file
tps-compile myfile.ps

# Output: myfile.py
```

### Options

```bash
tps-compile [OPTIONS] <input_file>
```

| Option | Description | Default |
|--------|-------------|---------|
| `-o, --output <file>` | Output file path | `<input>.py` |
| `-d, --output-dir <dir>` | Output directory | Current dir |
| `--strict` | Enable strict type checking | `false` |
| `--verbose` | Verbose output | `false` |
| `--help` | Show help message | - |

### Examples

**Custom Output:**
```bash
tps-compile main.ps -o build/main.py
```

**Output Directory:**
```bash
tps-compile src/app.ps -d build/
# Creates: build/app.py
```

**Strict Mode:**
```bash
tps-compile app.ps --strict
# Enables strict type checking
```

**Verbose Compilation:**
```bash
tps-compile app.ps --verbose
# Shows detailed compilation steps
```

### Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | Compilation error |
| `2` | File not found |
| `3` | Invalid options |

---

## 🚀 tps-run

Compile and execute PowerScript files immediately.

### Basic Usage

```bash
tps-run myfile.ps
# Compiles and runs in one step
```

### Options

```bash
tps-run [OPTIONS] <input_file> [-- <args>]
```

| Option | Description | Default |
|--------|-------------|---------|
| `--no-cache` | Don't cache compiled output | `false` |
| `--keep` | Keep compiled `.py` file | `false` |
| `--strict` | Enable strict type checking | `false` |
| `--verbose` | Verbose output | `false` |
| `--help` | Show help message | - |

### Examples

**Run with Arguments:**
```bash
tps-run script.ps -- arg1 arg2 arg3
```

**Keep Compiled File:**
```bash
tps-run app.ps --keep
# Keeps app.py after execution
```

**No Cache:**
```bash
tps-run app.ps --no-cache
# Force recompilation
```

### How It Works

1. Compiles `.ps` to `.py` (in memory or temp file)
2. Executes Python code
3. Cleans up temp files (unless `--keep`)

---

## 🏗️ tps-create

Create new PowerScript projects with boilerplate.

### Basic Usage

```bash
tps-create my-project
cd my-project
```

### Options

```bash
tps-create [OPTIONS] <project_name>
```

| Option | Description | Default |
|--------|-------------|---------|
| `-t, --template <name>` | Project template | `basic` |
| `--no-git` | Don't initialize git | `false` |
| `-f, --force` | Overwrite existing | `false` |
| `--help` | Show help message | - |

### Templates

#### `basic` (Default)
Simple project with one file:

```
my-project/
├── src/
│   └── main.ps
├── build/
├── powerscript.toml
└── README.md
```

**main.ps:**
```powerscript
function main(): void {
    console.log("Hello from PowerScript!");
}
```

### Examples

**Basic Project:**
```bash
tps-create my-app
```

**No Git Init:**
```bash
tps-create my-app --no-git
```

**Force Overwrite:**
```bash
tps-create my-app -f
```

### Generated Files

**powerscript.toml:**
```toml
[project]
name = "my-project"
version = "0.1.0"
entry = "src/main.ps"

[compiler]
output_dir = "build"
strict_types = true
```

---

## ✅ tps-check

Type check PowerScript files without compiling.

### Basic Usage

```bash
tps-check myfile.ps
# Validates types only
```

### Options

```bash
tps-check [OPTIONS] <input_file>
```

| Option | Description | Default |
|--------|-------------|---------|
| `--strict` | Strict type checking | `false` |
| `--warnings` | Show warnings | `true` |
| `--json` | JSON output | `false` |
| `--verbose` | Verbose output | `false` |
| `--help` | Show help message | - |

### Examples

**Basic Check:**
```bash
tps-check app.ps
```

**Strict Mode:**
```bash
tps-check app.ps --strict
```

**JSON Output:**
```bash
tps-check app.ps --json
```

### Output Format

**Success:**
```
✓ Type check passed: app.ps
  No issues found.
```

**With Errors:**
```
✗ Type check failed: app.ps

Line 5: Type mismatch
  Expected: number
  Got: string
  
2 errors found.
```

---

## 🔧 Global Options

Available for all commands:

```bash
--version    # Show TPS version
--help       # Show command help
--verbose    # Verbose output
```

### Version Check

```bash
tps-compile --version
# Output: TPS 1.0.0b1
```

---

## 📁 Configuration Files

### powerscript.toml

Project-level configuration:

```toml
[project]
name = "my-project"
version = "1.0.0"
entry = "src/main.ps"
author = "Your Name"

[compiler]
output_dir = "build"
strict_types = true
target_version = "3.9"

[runtime]
include_builtins = true
```

---

## 🔗 Command Chaining

### Build Pipeline

```bash
# Type check → Compile → Run
tps-check app.ps && tps-compile app.ps && python app.py
```

### Batch Compilation

```bash
# Compile all .ps files
for file in src/*.ps; do
    tps-compile "$file" -d build/
done
```

---

## 🎯 Best Practices

### Development Workflow

```bash
# 1. Type check first
tps-check src/main.ps

# 2. Compile if no errors
tps-compile src/main.ps -d build/

# 3. Run compiled code
python build/main.py
```

### Production Build

```bash
# Strict type checking + optimized build
tps-compile src/main.ps --strict -d dist/
```

---

## 🐛 Troubleshooting

### Command Not Found

```bash
# Check installation
pip list | grep tps

# Reinstall if missing
pip install --force-reinstall tps

# Add to PATH
export PATH="$HOME/.local/bin:$PATH"
```

### Permission Denied

```bash
# On macOS/Linux
chmod +x $(which tps-compile)
```

### Import Errors

```bash
# Ensure TPS installed
python -c "import powerscript; print(powerscript.__version__)"
```

---

## 📚 See Also

- **[Quick Start](quickstart.md)** - Basic usage examples
- **[Language Reference](language_reference.md)** - PowerScript syntax
- **[API Reference](api_reference.md)** - Built-in functions

---

**Master the CLI? Build amazing things with [Quick Start](quickstart.md)! 🚀**
