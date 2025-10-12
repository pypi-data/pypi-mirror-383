# PowerScript Quick Reference Guide

## Extension Commands

| Command | Shortcut | Description |
|---------|----------|-------------|
| PowerScript: Compile File | `Ctrl+Shift+B` / `Cmd+Shift+B` | Compile current file to Python |
| PowerScript: Run File | `Ctrl+Shift+R` / `Cmd+Shift+R` | Compile and run current file |
| PowerScript: Create Project | - | Create new project with templates |

## Code Snippets

Type these keywords and press `Tab` to expand:

| Trigger | Description |
|---------|-------------|
| `class` | Class definition with constructor |
| `constructor` | Constructor method |
| `function` | Function with parameters and return type |
| `arrow` | Arrow function |
| `async` | Async function |
| `if` | If statement |
| `for` | For loop |
| `while` | While loop |
| `try` | Try-catch-finally block |
| `switch` | Switch statement |
| `import` | Import statement |
| `fstring` | F-string template |
| `template` | Template literal |

## Common Patterns

### Variables
```powerscript
let name: string = "value";
const PI: number = 3.14159;
let isActive: boolean = true;
```

### Functions
```powerscript
// Regular function
function add(a: number, b: number): number {
    return a + b;
}

// Arrow function
const multiply = (a: number, b: number): number => a * b;

// Async function
async function fetchData(): Promise {
    return await someAsyncOperation();
}
```

### Arrays and Objects
```powerscript
// Arrays
let numbers: Array = [1, 2, 3, 4, 5];
numbers.append(6);
console.log(len(numbers));

// Objects (use bracket notation)
let person = {
    "name": "John",
    "age": 30
};
console.log(person["name"]);
```

### Control Flow
```powerscript
// If-else
if (condition) {
    // code
} else if (otherCondition) {
    // code
} else {
    // code
}

// For loop (declare variable before)
let i = 0;
for (i = 0; i < 10; i += 1) {
    console.log(i);
}

// For-in loop
for (item in array) {
    console.log(item);
}

// While loop
while (condition) {
    // code
}
```

### Strings
```powerscript
// F-strings
let name = "World";
let message = f"Hello, {name}!";

// Template literals
let text = `
    Multiline
    String
`;

// String methods
text.upper();
text.lower();
text.replace("old", "new");
```

### Error Handling
```powerscript
try {
    // risky code
} catch (error) {
    console.log("Error:", error);
} finally {
    // cleanup
}

// Throw error
throw "Error message";
```

### Enums
```powerscript
enum Status {
    Pending,
    Active,
    Completed
}

let current = Status.Active;
```

## Type Annotations

```powerscript
// Primitives
let name: string = "text";
let age: number = 25;
let active: boolean = true;

// Collections
let items: Array = [1, 2, 3];
let data: Dict = {"key": "value"};

// Functions
function process(input: string): number {
    return int(input);
}

// Async
async function fetch(): Promise {
    return await getData();
}
```

## Important Workarounds

### 1. Object Property Access
❌ **Don't use**: `obj.property`  
✅ **Use**: `obj["property"]`

### 2. Array Methods
❌ **Don't use**: `arr.push(item)`  
✅ **Use**: `arr.append(item)`

❌ **Don't use**: `arr.length`  
✅ **Use**: `len(arr)`

### 3. Type Conversion
Always use explicit conversion:
```powerscript
str(123)      // Number to string
int("123")    // String to integer
float("3.14") // String to float
bool(1)       // To boolean
```

### 4. String Concatenation
```powerscript
let num = 42;
let text = "Answer: " + str(num);  // ✅ Convert first
```

### 5. For Loop Variables
```powerscript
// Declare before loop
let i = 0;
for (i = 0; i < 10; i += 1) {
    console.log(i);
}
```

## CLI Commands

```bash
# Install PowerScript
pip install eitps

# Compile file
tps compile file.ps

# Run file
tps run file.ps

# Create project
tps create my-project

# Watch mode
tps compile --watch file.ps

# Type checking
tps check file.ps
```

## Configuration

Add to `.vscode/settings.json`:

```json
{
    "powerscript.enableLSP": true,
    "powerscript.enableDiagnostics": true,
    "powerscript.compilerPath": "tps",
    "powerscript.pythonPath": "python3"
}
```

## Common Errors

### Error: "Expected ';' after variable declaration"
**Cause**: Missing semicolon  
**Fix**: Add semicolon at end of statement

### Error: "Expected ')' after arguments"
**Cause**: Syntax error in function call  
**Fix**: Check parentheses and commas

### Error: "Expected expression"
**Cause**: Invalid syntax or unsupported feature  
**Fix**: Check syntax or use workaround

### Error: "Class declaration should be followed by opening brace"
**Cause**: Missing space or brace after class name  
**Fix**: Ensure proper class syntax

## Getting Help

- **Documentation**: Check README.md
- **Examples**: See test_suits/ folder
- **Issues**: GitHub Issues
- **Email**: team@eliteindia.org

## Feature Status

✅ **Working**: Variables, functions, arrays, objects, strings, control flow, error handling, enums, JSON, math  
🟡 **Partial**: Classes (basic), modules (basic)  
🔄 **In Development**: Class inheritance, interfaces, generics, decorators, spread operator, destructuring

---

**Version**: 1.0.0  
**Last Updated**: October 11, 2025
