# ⚡ Quick Start Guide

Get started with PowerScript in 5 minutes!

## 🎯 Your First Program

### Step 1: Install TPS

```bash
pip install tps
```

### Step 2: Create a File

Create `hello.ps`:

```powerscript
function main(): void {
    console.log("Hello, PowerScript!");
}
```

### Step 3: Compile and Run

```bash
# Compile to Python
tps-compile hello.ps

# Run the output
python hello.py
```

**Output:**
```
Hello, PowerScript!
```

🎉 **Congratulations!** You just ran your first PowerScript program!

## 🚀 5-Minute Tutorial

### Variables and Types

```powerscript
function main(): void {
    // Type declarations ✅
    let name: string = "PowerScript";
    let version: number = 1.0;
    let isAwesome: boolean = true;
    
    // Type inference ✅
    let auto = "Automatically typed!";
    
    console.log(name);
    console.log("Version: " + version);
}
```

### Functions

```powerscript
// Function with types ✅
function greet(name: string): string {
    return "Hello, " + name + "!";
}

function add(a: number, b: number): number {
    return a + b;
}

function main(): void {
    console.log(greet("World"));
    console.log("2 + 3 = " + add(2, 3));
}
```

### Arrays

```powerscript
function main(): void {
    // Typed arrays ✅
    let numbers: number[] = [1, 2, 3, 4, 5];
    let names: string[] = ["Alice", "Bob", "Charlie"];
    
    // Array operations ✅
    console.log(numbers[0]);        // 1
    console.log(names.length);       // 3
    
    // Iteration ✅
    for (let i = 0; i < numbers.length; i++) {
        console.log(numbers[i]);
    }
}
```

### Classes

```powerscript
// Class with constructor ✅
class Person {
    constructor(public name: string, public age: number) {}
    
    greet(): string {
        return "Hi, I'm " + this.name;
    }
}

function main(): void {
    let person = new Person("Alice", 30);
    console.log(person.greet());
    console.log(person.age);
}
```

### Control Flow

```powerscript
function main(): void {
    // If-else ✅
    let score: number = 85;
    
    if (score >= 90) {
        console.log("Grade: A");
    } else if (score >= 80) {
        console.log("Grade: B");
    } else {
        console.log("Grade: C");
    }
    
    // While loop ✅
    let count: number = 0;
    while (count < 3) {
        console.log("Count: " + count);
        count++;
    }
    
    // For loop ✅
    for (let i = 0; i < 5; i++) {
        console.log("i = " + i);
    }
}
```

## 💼 Practical Examples

### Example 1: Calculator

```powerscript
class Calculator {
    add(a: number, b: number): number {
        return a + b;
    }
    
    subtract(a: number, b: number): number {
        return a - b;
    }
    
    multiply(a: number, b: number): number {
        return a * b;
    }
    
    divide(a: number, b: number): number {
        if (b == 0) {
            console.log("Error: Division by zero");
            return 0;
        }
        return a / b;
    }
}

function main(): void {
    let calc = new Calculator();
    
    console.log("10 + 5 = " + calc.add(10, 5));
    console.log("10 - 5 = " + calc.subtract(10, 5));
    console.log("10 * 5 = " + calc.multiply(10, 5));
    console.log("10 / 5 = " + calc.divide(10, 5));
}
```

### Example 2: Todo List

```powerscript
class TodoItem {
    constructor(
        public id: number,
        public title: string,
        public completed: boolean
    ) {}
}

class TodoList {
    private items: TodoItem[] = [];
    private nextId: number = 1;
    
    add(title: string): void {
        let item = new TodoItem(this.nextId, title, false);
        this.items.push(item);
        this.nextId++;
        console.log("Added: " + title);
    }
    
    complete(id: number): void {
        for (let i = 0; i < this.items.length; i++) {
            if (this.items[i].id == id) {
                this.items[i].completed = true;
                console.log("Completed: " + this.items[i].title);
                return;
            }
        }
    }
    
    listAll(): void {
        console.log("Todo List:");
        for (let i = 0; i < this.items.length; i++) {
            let status = this.items[i].completed ? "✓" : " ";
            console.log("[" + status + "] " + this.items[i].title);
        }
    }
}

function main(): void {
    let todos = new TodoList();
    
    todos.add("Learn PowerScript");
    todos.add("Build a project");
    todos.add("Share with friends");
    
    todos.complete(1);
    todos.listAll();
}
```

## 🛠️ CLI Commands

### Compile Only

```bash
tps-compile myfile.ps
# Generates: myfile.py
```

### Compile and Run

```bash
tps-run myfile.ps
# Compiles and executes immediately
```

### Type Check

```bash
tps-check myfile.ps
# Validates types without compiling
```

### Create New Project

```bash
tps-create my-project
cd my-project
# Creates project structure with examples
```

## 🎨 VS Code Integration

### Useful Snippets

Type these and press Tab:

- `func` → Function declaration
- `class` → Class with constructor
- `if` → If-else statement
- `for` → For loop
- `while` → While loop
- `import` → Import statement

## 🔍 Common Patterns

### Error Handling

```powerscript
function divide(a: number, b: number): number {
    if (b == 0) {
        console.log("Error: Cannot divide by zero");
        return 0;
    }
    return a / b;
}
```

### Array Processing

```powerscript
function sumArray(numbers: number[]): number {
    let total: number = 0;
    for (let i = 0; i < numbers.length; i++) {
        total = total + numbers[i];
    }
    return total;
}

function main(): void {
    let nums: number[] = [1, 2, 3, 4, 5];
    console.log("Sum: " + sumArray(nums));  // Sum: 15
}
```

## 🎓 Next Steps

Now that you know the basics:

1. **[CLI Reference](cli_reference.md)** - Master command-line tools
2. **[VS Code Extension](vscode_extension.md)** - Setup your IDE
3. **[FAQ](faq.md)** - Common questions answered

## 💡 Tips for Success

- ✅ **Always declare types** - Catch errors early
- ✅ **Use meaningful names** - Code is read more than written
- ✅ **Start small** - Master basics before advanced features
- ✅ **Practice daily** - Consistency builds skill

---

**Ready for more? Continue to [CLI Reference](cli_reference.md)! 🚀**
