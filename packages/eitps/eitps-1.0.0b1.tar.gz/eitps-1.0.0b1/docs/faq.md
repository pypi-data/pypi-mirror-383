# ❓ Frequently Asked Questions (FAQ)

Common questions about PowerScript (TPS) answered.

---

## 📖 General Questions

### What is PowerScript?

PowerScript (TPS — **T**yped **P**ower**S**cript) is a modern programming language that transpiles to clean Python code. It combines JavaScript-familiar syntax with Python's powerful ecosystem, adding static type checking and modern language features.

### Why use PowerScript instead of Python?

**PowerScript offers:**

- ✅ **Modern Syntax** - Cleaner, more familiar syntax inspired by JavaScript/TypeScript
- ✅ **Type Safety** - Static type checking catches errors before runtime
- ✅ **Better Tooling** - VS Code extension with syntax highlighting and snippets
- ✅ **Cleaner Code** - More expressive and maintainable code
- ✅ **Full Python Ecosystem** - Access to all Python libraries (NumPy, TensorFlow, Django, etc.)

### Why use PowerScript instead of JavaScript/TypeScript?

**Use PowerScript when:**

- You need Python's ecosystem (AI/ML, data science libraries)
- You want to avoid Node.js and npm complexity
- You prefer Python's runtime and deployment simplicity
- You need better scientific computing support

### Is PowerScript production-ready?

**Yes!** PowerScript v1.0 Beta is production-ready with:

- ✅ Complete core language features
- ✅ Comprehensive type system
- ✅ Full runtime libraries
- ✅ CLI tools and VS Code extension
- ✅ 100% passing core tests
- ✅ Extensive documentation

---

## 🔧 Installation & Setup

### How do I install PowerScript?

Simple one-line install:

```bash
pip install tps
```

See [Installation Guide](installation.md) for detailed instructions.

### What are the system requirements?

**Minimum:**
- Python 3.8+
- pip package manager
- 512 MB RAM
- 50 MB disk space

**Recommended:**
- Python 3.9+
- VS Code editor
- 2 GB RAM
- 200 MB disk space

### Can I use PowerScript without VS Code?

Yes! PowerScript works with any text editor. VS Code extension provides extra features like syntax highlighting and snippets, but it's optional.

### How do I update PowerScript?

```bash
pip install --upgrade tps
```

---

## 💻 Language Features

### Does PowerScript support all Python libraries?

Yes! PowerScript transpiles to Python, so you have full access to:
- NumPy, Pandas, Matplotlib (data science)
- TensorFlow, PyTorch (machine learning)
- Django, Flask (web development)
- Requests, BeautifulSoup (web scraping)
- Any other Python package

### Can I mix PowerScript and Python code?

Yes! You can:
- Import Python modules in PowerScript
- Use PowerScript-compiled files in Python projects
- Gradually migrate Python projects to PowerScript

### What types does PowerScript support?

**Basic Types:**
- `string`, `number`, `boolean`, `void`, `any`
- `null`, `undefined`

**Complex Types:**
- Arrays: `string[]`, `number[]`
- Function types with parameters and return types
- Union types: `string | number`
- Type inference

**Coming Soon:**
- Generics
- Advanced union types
- Mapped types

### Does PowerScript have classes?

Yes! Full OOP support:

```powerscript
class Person {
    constructor(public name: string, private age: number) {}
    
    greet(): string {
        return "Hello, I'm " + this.name;
    }
}
```

### Does PowerScript support async/await?

Yes! Full async/await support:

```powerscript
async function fetchData(url: string): Promise<any> {
    let response = await fetch(url);
    return await response.json();
}
```

---

## 🛠️ Development

### What IDE should I use?

**Recommended:** VS Code with PowerScript extension
- Syntax highlighting
- Code snippets
- Error detection
- Auto-formatting

**Also works with:** Any text editor (Sublime, Atom, Vim, etc.)

### How do I compile PowerScript files?

```bash
# Compile single file
tps-compile myfile.ps

# Compile to specific directory
tps-compile myfile.ps -d build/

# Compile and run
tps-run myfile.ps
```

### Can I see the generated Python code?

Yes! Compiled `.py` files are human-readable:

```bash
tps-compile app.ps
cat app.py  # View generated Python
```

### How do I debug PowerScript code?

Two options:

1. **Debug Python output:**
   ```bash
   tps-compile app.ps
   python -m pdb app.py
   ```

2. **Use print debugging:**
   ```powerscript
   console.log("Debug:", variable);
   ```

### Does PowerScript have a REPL?

Not yet. Coming in v2.0 (Q3 2026). For now:

```bash
# Quick testing
tps-run test.ps
```

---

## 🚀 Performance

### Is PowerScript faster than Python?

PowerScript transpiles to Python, so **performance is identical to Python**. The type system adds no runtime overhead.

### Does type checking slow down compilation?

Type checking happens at compile-time only. Runtime performance is unaffected.

### Can I optimize PowerScript code?

Use the same optimization techniques as Python:
- Use NumPy for numerical operations
- Leverage Cython for critical sections
- Profile with Python tools

---

## 🔄 Migration

### How do I migrate from Python?

1. Rename `.py` to `.ps`
2. Add type annotations
3. Update syntax (optional)

See [Migration Guide](migration_guide.md) for details.

### How do I migrate from TypeScript?

PowerScript syntax is similar! Main changes:
- Import Python libraries instead of npm packages
- Use PowerScript runtime libraries
- Adjust for Python's runtime behavior

### Can I gradually migrate a project?

Yes! You can:
- Keep Python files alongside PowerScript
- Import Python modules in PowerScript
- Compile PowerScript to Python and use together

---

## 🐛 Troubleshooting

### "Command not found: tps"

**Solution:**
```bash
# Add pip to PATH
export PATH="$HOME/.local/bin:$PATH"

# Or reinstall
pip install --user tps
```

### "Module not found: powerscript"

**Solution:**
```bash
# Activate virtual environment if using one
source .venv/bin/activate

# Or reinstall
pip install --force-reinstall tps
```

### VS Code syntax highlighting not working

**Solution:**
1. Reload VS Code: `Cmd/Ctrl+Shift+P` → "Reload Window"
2. Check file extension is `.ps`
3. Reinstall extension from VSIX
4. Manually set language: `Cmd/Ctrl+K M` → "PowerScript"

### Type errors at compile time

**Solution:**
```bash
# Check types without compiling
tps-check myfile.ps

# Use verbose mode
tps-compile myfile.ps --verbose
```

---

## 📚 Learning Resources

### Where can I learn PowerScript?

1. **[Quick Start](quickstart.md)** - 5-minute introduction
2. **[Language Reference](language_reference.md)** - Complete syntax guide
3. **[Tutorial](tutorial.md)** - Step-by-step learning
4. **[Examples](../test_suits/)** - Real code examples

### Are there video tutorials?

Coming soon! For now, follow the written documentation.

### Can I contribute examples?

Yes! Submit pull requests with:
- Example code
- Use case demonstrations
- Tutorial content

---

## 🤝 Contributing

### How can I contribute?

See [Contributing Guide](contributing.md) for:
- Bug reports
- Feature requests
- Code contributions
- Documentation improvements

### Where is the source code?

GitHub: https://github.com/SaleemLww/Python-PowerScript

### How do I report bugs?

Open an issue: https://github.com/SaleemLww/Python-PowerScript/issues

Include:
- PowerScript version (`tps --version`)
- Python version (`python --version`)
- Minimal code example
- Error message

---

## 📦 Packages & Libraries

### Is there a package manager?

Coming in v1.2 (Q2 2026). For now, use pip for Python dependencies.

### How do I use Python packages?

```powerscript
// Import any Python package
import { numpy as np, pandas as pd } from "python";

function main(): void {
    let arr = np.array([1, 2, 3]);
    console.log(arr);
}
```

### What built-in libraries does PowerScript have?

**Runtime Libraries:**
- `Console` - Logging and output
- `FileSystem` - File operations
- `JSON` - JSON parsing
- `CSV` - CSV operations
- `Database` - SQLite support
- `GUI` - Basic GUI (tkinter wrapper)
- `Networking` - HTTP requests
- `Math` - Mathematical utilities

See [API Reference](api_reference.md) for details.

---

## 🔮 Future Plans

### What's coming in v1.1 (Q1 2026)?

- 🔄 Advanced generics
- 🔄 Decorators
- 🔄 Namespace support
- 🔄 Spread operator
- 🔄 Optional chaining

### What's coming in v1.2 (Q2 2026)?

- 🔄 Language Server Protocol (LSP)
- 🔄 IntelliSense in VS Code
- 🔄 Code refactoring tools
- 🔄 Package manager
- 🔄 Test framework

### What's coming in v2.0 (Q3 2026)?

- 🔄 REPL environment
- 🔄 Debugger integration
- 🔄 Hot reloading
- 🔄 Plugin system
- 🔄 Advanced optimizations

---

## 📧 Support

### How do I get help?

1. **Check [Documentation](README.md)**
2. **Search [GitHub Issues](https://github.com/SaleemLww/Python-PowerScript/issues)**
3. **Ask in [GitHub Discussions](https://github.com/SaleemLww/Python-PowerScript/discussions)**
4. **Read [Troubleshooting Guide](troubleshooting.md)**

### Is there a community?

Yes! Join us on:
- GitHub Discussions
- GitHub Issues
- Repository Stars & Watchers

---

**Still have questions? Ask in [GitHub Discussions](https://github.com/SaleemLww/Python-PowerScript/discussions)! 💬**
