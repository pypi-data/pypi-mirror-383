# PowerScript VS Code Extension

A comprehensive VS Code extension that provides full IDE support for the PowerScript programming language - a modern, typed language that transpiles to Python.

## Features

### 🎨 Syntax Highlighting
- Complete TextMate grammar support for PowerScript syntax
- Highlighting for keywords, types, strings, comments, and operators
- Support for modern language features like F-strings, template literals, and arrow functions
- Syntax support for classes, interfaces, enums, and decorators

### 📝 Code Snippets
Ready-to-use code templates for faster development:
- `class` - Class definition with constructor
- `constructor` - Constructor method
- `function` - Function definition with types
- `arrow` - Arrow function (single and multi-line)
- `async` - Async function
- `if` - If statement
- `for` - For loop (standard and for-in)
- `while` - While loop
- `try` - Try-catch-finally block
- `switch` - Switch statement
- `import` - Import statement
- `fstring` - F-string template
- `template` - Template literal

### 🔧 Language Server Protocol (LSP)
- **Auto-completion**: IntelliSense for keywords, types, and user-defined symbols
- **Hover information**: Documentation and type information on hover
- **Diagnostics**: Real-time syntax and type error detection
- **Error highlighting**: Inline error messages and warnings
- **Type checking**: Static type validation

### ⚡ Commands
- `PowerScript: Compile File` - Compile current PowerScript file to Python
- `PowerScript: Run File` - Compile and run current PowerScript file  
- `PowerScript: Create Project` - Create new PowerScript project with templates

### 🎯 Current PowerScript Features Supported

#### ✅ Fully Supported
- **Basic Syntax**: Variables (let/const), operators, expressions
- **Control Flow**: if/else, while loops, for loops, switch/case
- **Functions**: Regular functions, arrow functions, async/await
- **Data Types**: strings, numbers, booleans, arrays, objects/dictionaries
- **String Features**: F-strings, template literals, multiline strings
- **Error Handling**: try/catch/finally, throw, custom errors
- **Type System**: Type annotations, type inference, type checking
- **Enums**: Enum declarations and usage
- **Comments**: Single-line (//) and multi-line (/* */)
- **JSON**: JSON parsing and serialization
- **Math**: Mathematical operations and functions
- **Operators**: Arithmetic, comparison, logical, assignment

#### 🟡 Partially Supported
- **Classes**: Basic class syntax (full OOP in development)
- **Object Access**: Use bracket notation `obj["property"]` (dot notation coming soon)
- **Modules**: Basic import/export (advanced module system in development)

#### 🔄 In Development
- **Class Inheritance**: extends, super(), method overriding
- **Interfaces**: Interface declarations and implementations
- **Generics**: Generic types and constraints
- **Decorators**: Function and class decorators
- **Spread Operator**: Rest parameters (...args)
- **Destructuring**: Array and object destructuring
- **List Comprehensions**: Python-style comprehensions
- **Advanced Types**: Union types, intersection types, type guards

## Installation

### From VSIX Package
1. Download the `powerscript-1.0.0.vsix` file
2. Open VS Code
3. Go to Extensions view (`Ctrl+Shift+X`)
4. Click the "..." menu and select "Install from VSIX..."
5. Select the downloaded `.vsix` file

### From Command Line
```bash
code --install-extension powerscript-1.0.0.vsix
```

## Usage

### Basic Usage
1. Create or open a `.ps` file
2. The extension will automatically activate and provide syntax highlighting
3. Use snippets by typing trigger words (e.g., `class`, `function`) and pressing Tab
4. Right-click in editor for compile/run options

### Keyboard Shortcuts
- `Ctrl+Shift+B` / `Cmd+Shift+B` - Compile current file
- `Ctrl+Shift+R` / `Cmd+Shift+R` - Run current file

### Configuration
The extension supports the following settings:

```json
{
    "powerscript.enableLSP": true,
    "powerscript.enableDiagnostics": true,
    "powerscript.compilerPath": "powerscriptc",
    "powerscript.pythonPath": "python3"
}
```

## PowerScript Language Features

### ✅ Currently Working Features

#### Variables and Data Types
```powerscript
// Variables
let name: string = "PowerScript";
const version: number = 1.0;
let isReady: boolean = true;

// Arrays and Objects
let numbers: Array = [1, 2, 3, 4, 5];
let person = {
    "name": "John",
    "age": 30,
    "email": "john@example.com"
};

// Access with bracket notation
console.log(person["name"]);
numbers.append(6);
```

#### Functions
```powerscript
// Regular function
function add(a: number, b: number): number {
    return a + b;
}

// Arrow function
const multiply = (a: number, b: number): number => {
    return a * b;
};

// Single-expression arrow function
const square = (x: number): number => x * x;

// Async function
async function fetchData(url: string): Promise {
    let response = await fetch(url);
    return await response.json();
}
```

#### Control Flow
```powerscript
// If-else
if (age >= 18) {
    console.log("Adult");
} else if (age >= 13) {
    console.log("Teenager");
} else {
    console.log("Child");
}

// While loop
let i = 0;
while (i < 5) {
    console.log(i);
    i += 1;
}

// For loop
for (let j = 0; j < 10; j += 1) {
    console.log(j);
}

// For-in loop
for (item in array) {
    console.log(item);
}

// Switch case
switch (day) {
    case "Monday":
        console.log("Start of week");
        break;
    case "Friday":
        console.log("Almost weekend");
        break;
    default:
        console.log("Regular day");
}
```

#### String Features
```powerscript
let name = "PowerScript";
let version = "1.0";

// F-strings (Python-style)
let message = f"Welcome to {name} v{version}!";

// Template literals
let template = `
    Language: ${name}
    Version: ${version}
    Status: Ready
`;

// String methods
let text = "hello world";
console.log(text.upper());        // HELLO WORLD
console.log(text.capitalize());   // Hello world
console.log(text.replace("hello", "hi"));
```

#### Error Handling
```powerscript
try {
    let result = riskyOperation();
    console.log(result);
} catch (error) {
    console.log("Error:", error);
} finally {
    console.log("Cleanup");
}

// Throw errors
if (value < 0) {
    throw "Value cannot be negative";
}
```

#### Enums
```powerscript
enum Color {
    Red,
    Green,
    Blue
}

let favorite = Color.Blue;
console.log(favorite);  // Blue
```

#### JSON Operations
```powerscript
// Parse JSON
let jsonString = '{"name": "John", "age": 30}';
let data = JSON.parse(jsonString);

// Stringify JSON
let obj = {"name": "Alice", "age": 25};
let json = JSON.stringify(obj);
```

### 🔄 Features in Development

#### Classes (Basic Support)
```powerscript
// Basic class syntax works
class Person {
    constructor(name: string, age: number) {
        this.name = name;
        this.age = age;
    }
    
    greet(): string {
        return f"Hello, I'm {this.name}";
    }
}

// Note: Full OOP features coming soon
// - Inheritance (extends, super)
// - Private/protected members
// - Static methods
// - Getters/setters
```

#### Advanced Features Coming Soon
- **Spread Operator**: `...args` in function parameters
- **Destructuring**: `let {name, age} = person`
- **List Comprehensions**: `[x * 2 for x in numbers]`
- **Type Guards**: Advanced type checking
- **Decorators**: `@decorator` syntax
- **Interfaces**: Interface declarations
- **Generics**: Generic type parameters

## Requirements

- **VS Code**: Version 1.60.0 or higher
- **PowerScript Compiler**: Install via pip:
  ```bash
  pip install tps
  ```
- **Python**: Version 3.8 or higher for running compiled code

## Quick Start

1. **Install PowerScript**:
   ```bash
   pip install tps
   ```

2. **Install VS Code Extension**:
   - Download `powerscript-1.0.0.vsix`
   - Open VS Code
   - Go to Extensions (`Ctrl+Shift+X` / `Cmd+Shift+X`)
   - Click "..." menu → "Install from VSIX..."
   - Select the `.vsix` file

3. **Create Your First File**:
   ```powerscript
   // hello.ps
   console.log("Hello, PowerScript!");
   
   function greet(name: string): string {
       return f"Hello, {name}!";
   }
   
   console.log(greet("World"));
   ```

4. **Run It**:
   - Right-click in editor → "Run PowerScript File"
   - Or use command: `tps run hello.ps`

## Known Limitations & Workarounds

### Object Property Access
**Current**: Use bracket notation
```powerscript
let person = {"name": "John", "age": 30};
console.log(person["name"]);  // ✅ Works
```

**Coming Soon**: Dot notation
```powerscript
console.log(person.name);  // 🔄 In development
```

### Array Methods
**Current**: Use Python-style methods
```powerscript
let arr = [1, 2, 3];
arr.append(4);        // ✅ Works
console.log(len(arr)); // ✅ Works
```

### For Loop Declarations
**Current**: Declare variable before loop
```powerscript
let i = 0;
for (i = 0; i < 10; i += 1) {  // ✅ Works
    console.log(i);
}
```

**Coming Soon**: Inline declaration
```powerscript
for (let i = 0; i < 10; i += 1) {  // 🔄 In development
    console.log(i);
}
```

### Type Conversions
Always use explicit conversion functions:
```powerscript
let num = 42;
let text = "The answer is " + str(num);  // ✅ Works

let x = int("123");    // String to int
let y = float("3.14"); // String to float
let z = bool(1);       // To boolean
```

## Development

### Building from Source
1. Clone the repository
2. Install dependencies: `npm install`
3. Compile extension source: `npm run compile`
4. Package extension: `vsce package`
5. Install: `code --install-extension powerscript-1.0.0.vsix`

### Project Structure
```
vscode-extension/
├── src/
│   ├── extension.ts          # Main extension entry point
│   ├── lsp-server.py        # Language Server Protocol implementation
│   └── extension-simple.ts  # Simplified extension version
├── syntaxes/
│   └── powerscript.tmLanguage.json  # TextMate grammar
├── snippets/
│   └── powerscript.json     # Code snippets
├── language-configuration.json     # Language configuration
├── package.json             # Extension manifest
└── tsconfig.json           # Build configuration
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License

Copyright (c) 2025 Saleem Ahmad (Elite India Org Team)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

**Author**: Saleem Ahmad (Elite India Org Team)  
**Email**: team@eliteindia.org

## Support

For issues, feature requests, or questions:
- Create an issue on GitHub
- Check the PowerScript documentation
- Join the community discussions

## Changelog

### 1.0.0 (Current)
- ✅ Complete syntax highlighting for PowerScript
- ✅ 13 code snippets for common patterns
- ✅ Basic LSP support with auto-completion
- ✅ Compile and run commands
- ✅ Real-time diagnostics and error detection
- ✅ Support for F-strings and template literals
- ✅ Enum syntax highlighting
- ✅ Async/await support
- ✅ Arrow function syntax

### Known Issues
- Dot notation for object property access not yet supported (use bracket notation)
- Class inheritance features in development
- Some advanced type features pending

## Roadmap

### Version 1.1 (Planned)
- [ ] Enhanced LSP features
  - [ ] Go-to-definition
  - [ ] Find all references
  - [ ] Rename symbol
  - [ ] Document symbols outline
- [ ] Code formatting support
- [ ] Linting integration
- [ ] Quick fixes and refactoring

### Version 1.2 (Planned)
- [ ] Integrated debugging support
  - [ ] Breakpoints
  - [ ] Variable inspection
  - [ ] Call stack
  - [ ] Step-through debugging
- [ ] Project templates
- [ ] Test runner integration

### Version 2.0 (Future)
- [ ] Full class inheritance support
- [ ] Interface and generic type support
- [ ] Advanced module system
- [ ] Live share integration
- [ ] Performance profiling tools

## Test Coverage

PowerScript has comprehensive test coverage with:
- **15/15 core tests passing** (100%)
- **43 W3Schools Python tutorial tests** covering:
  - Basic syntax and data types
  - Control flow and functions
  - OOP concepts
  - Advanced topics (DSA, databases, ML, visualization)
- **11/43 W3C tests currently passing** (26%)
- Remaining tests document features in development