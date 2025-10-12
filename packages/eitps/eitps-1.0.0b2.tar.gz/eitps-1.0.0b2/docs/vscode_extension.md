# 🎨 VS Code Extension Guide

Complete guide to the PowerScript VS Code extension.

---

## 📦 Installation

### Method 1: Install from VSIX (Recommended)

1. **Locate Extension File**
   ```bash
   # In PowerScript repository
   cd vscode-extension
   # File: powerscript-1.0.0.vsix (550.28 KB)
   ```

2. **Install in VS Code**
   - Open VS Code
   - Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
   - Type: `Extensions: Install from VSIX`
   - Navigate to `powerscript-1.0.0.vsix`
   - Click "Install"

3. **Verify Installation**
   - Create file: `test.ps`
   - Should see PowerScript syntax highlighting
   - Check Extensions panel for "PowerScript"

### Method 2: Command Line

```bash
# Using command line
code --install-extension powerscript-1.0.0.vsix
```

---

## ✨ Features

### 1. Syntax Highlighting ✅

Beautiful, semantic highlighting for PowerScript code:

**Keywords:**
- Control flow: `if`, `else`, `for`, `while`, `switch`, `case`
- Types: `string`, `number`, `boolean`, `void`, `any`, `null`, `undefined`
- Modifiers: `public`, `private`, `protected`, `static`, `async`, `const`, `let`
- Classes: `class`, `interface`, `abstract`, `extends`, `implements`
- Functions: `function`, `return`, `constructor`
- Modules: `import`, `export`, `from`, `as`

**Operators & Symbols:**
- Arithmetic: `+`, `-`, `*`, `/`, `%`
- Comparison: `==`, `!=`, `<`, `>`, `<=`, `>=`
- Logical: `&&`, `||`, `!`
- Assignment: `=`, `+=`, `-=`, `*=`, `/=`

**Literals:**
- Strings: `"double quotes"`, `'single quotes'`
- Numbers: `42`, `3.14`, `0xFF`
- Booleans: `true`, `false`
- Null: `null`, `undefined`

### 2. Code Snippets ✅

13 intelligent snippets for common patterns:

#### Basic Snippets

**`func`** - Function Declaration
```powerscript
function functionName(param: type): returnType {
    // function body
}
```

**`arrow`** - Arrow Function
```powerscript
const name = (param: type): returnType => {
    // function body
};
```

**`class`** - Class with Constructor
```powerscript
class ClassName {
    constructor(param: type) {
        // constructor body
    }
    
    methodName(): returnType {
        // method body
    }
}
```

**`interface`** - Interface Declaration
```powerscript
interface InterfaceName {
    property: type;
    method(): returnType;
}
```

#### Control Flow Snippets

**`if`** - If Statement
```powerscript
if (condition) {
    // true block
}
```

**`ife`** - If-Else Statement
```powerscript
if (condition) {
    // true block
} else {
    // false block
}
```

**`for`** - For Loop
```powerscript
for (let i = 0; i < length; i++) {
    // loop body
}
```

**`while`** - While Loop
```powerscript
while (condition) {
    // loop body
}
```

**`switch`** - Switch Statement
```powerscript
switch (expression) {
    case value1:
        // case 1
        break;
    case value2:
        // case 2
        break;
    default:
        // default case
}
```

#### Module Snippets

**`import`** - Import Statement
```powerscript
import { symbol } from "module";
```

**`export`** - Export Statement
```powerscript
export class ClassName {
    // class body
}
```

#### Advanced Snippets

**`async`** - Async Function
```powerscript
async function functionName(): Promise<type> {
    // async body
}
```

**`enum`** - Enum Declaration
```powerscript
enum EnumName {
    Value1,
    Value2,
    Value3
}
```

### 3. File Recognition ✅

**Supported Extensions:**
- `.ps` - PowerScript source files
- `.pscript` - Alternative extension

**Auto-Detection:**
- VS Code automatically applies PowerScript syntax when opening `.ps` files
- Language mode shows "PowerScript" in status bar

### 4. Comment Support ✅

**Single-line Comments:**
```powerscript
// This is a single-line comment
let x: number = 5; // inline comment
```

**Multi-line Comments:**
```powerscript
/*
 * This is a
 * multi-line comment
 */
function test(): void {
    /* inline block comment */
}
```

**Keyboard Shortcuts:**
- Toggle comment: `Cmd+/` (Mac) or `Ctrl+/` (Windows/Linux)
- Block comment: `Cmd+Shift+A` (Mac) or `Ctrl+Shift+A` (Windows/Linux)

### 5. Bracket Matching ✅

**Auto-completion:**
- Type `{` → Auto-completes `}`
- Type `[` → Auto-completes `]`
- Type `(` → Auto-completes `)`
- Type `"` → Auto-completes `"`
- Type `'` → Auto-completes `'`

**Auto-surrounding:**
- Select text and type `{` → Wraps in `{}`
- Select text and type `"` → Wraps in `""`

---

## 🎯 Usage Tips

### Snippet Workflow

1. **Type snippet prefix** (e.g., `func`)
2. **Press Tab** to expand
3. **Tab through placeholders** to fill in values
4. **Press Enter** when done

### Example: Create a Class

```
1. Type: class [Tab]
2. Fill in: Person
3. Tab to param: name
4. Tab to type: string
5. Tab to method: greet
6. Tab to return type: string
7. Done!
```

Result:
```powerscript
class Person {
    constructor(name: string) {
        // constructor body
    }
    
    greet(): string {
        // method body
    }
}
```

### Keyboard Shortcuts

| Action | Mac | Windows/Linux |
|--------|-----|---------------|
| Toggle comment | `Cmd+/` | `Ctrl+/` |
| Block comment | `Cmd+Shift+A` | `Ctrl+Shift+A` |
| Format document | `Cmd+Shift+F` | `Ctrl+Shift+F` |
| Command palette | `Cmd+Shift+P` | `Ctrl+Shift+P` |

---

## 🔧 Recommended Settings

Add to your VS Code `settings.json`:

```json
{
  "[powerscript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode",
    "editor.formatOnSave": true,
    "editor.tabSize": 4,
    "editor.insertSpaces": true
  },
  
  "editor.bracketPairColorization.enabled": true,
  "editor.autoClosingBrackets": "always",
  "editor.autoClosingQuotes": "always",
  
  "editor.quickSuggestions": {
    "other": true,
    "comments": false,
    "strings": false
  },
  
  "files.associations": {
    "*.ps": "powerscript",
    "*.pscript": "powerscript"
  }
}
```

---

## 🚀 Workflow Integration

### Compile on Save

Create `.vscode/tasks.json`:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "compile-powerscript",
      "type": "shell",
      "command": "tps-compile ${file}",
      "group": {
        "kind": "build",
        "isDefault": true
      },
      "presentation": {
        "reveal": "always",
        "panel": "new"
      }
    }
  ]
}
```

**Usage:**
Press `Cmd+Shift+B` (Mac) or `Ctrl+Shift+B` (Windows/Linux) to compile current file.

### Run PowerScript Files

Add to `tasks.json`:

```json
{
  "label": "run-powerscript",
  "type": "shell",
  "command": "tps-run ${file}",
  "group": "test",
  "presentation": {
    "reveal": "always",
    "panel": "new"
  }
}
```

---

## 🎨 Theme Compatibility

The extension works with all VS Code themes:

**Recommended Themes:**
- Dark+ (default dark)
- Light+ (default light)
- Monokai
- Dracula
- One Dark Pro
- Material Theme

---

## 🐛 Troubleshooting

### Extension Not Loading

**Symptom:** No PowerScript in Extensions panel

**Solutions:**
1. Reload VS Code: `Cmd/Ctrl+Shift+P` → "Reload Window"
2. Check installation: View → Extensions → Search "PowerScript"
3. Reinstall from VSIX

### No Syntax Highlighting

**Symptom:** `.ps` files show as plain text

**Solutions:**
1. Check language mode (bottom right) - should show "PowerScript"
2. Manually set language: `Cmd/Ctrl+K M` → type "powerscript"
3. Check file association in settings
4. Reload window

### Snippets Not Working

**Symptom:** Typing `func` doesn't show snippet

**Solutions:**
1. Check suggestions enabled: Settings → Editor: Quick Suggestions
2. Press `Cmd+Space` (Mac) or `Ctrl+Space` (Windows/Linux) manually
3. Type snippet prefix and press `Tab` instead of `Enter`

---

## 📚 Coming Soon 🔄

Future extension features:

- **LSP Integration** - Real-time error checking
- **IntelliSense** - Smart code completion
- **Go to Definition** - Jump to symbol definitions
- **Find References** - Find all symbol usages
- **Rename Refactoring** - Rename across files
- **Debugging Support** - Step-through debugging

---

## 🆘 Getting Help

**Issues with Extension?**
- Check [Troubleshooting](troubleshooting.md)
- Report issue: [GitHub Issues](https://github.com/SaleemLww/PowerScript-EITPS/issues)
- Ask community: [GitHub Discussions](https://github.com/SaleemLww/PowerScript-EITPS/discussions)

---

**Extension installed? Start coding with [Quick Start](quickstart.md)! 🚀**
