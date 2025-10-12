"""
MIT License

Copyright (c) 2025 Saleem Ahmad (Elite India Org Team)
Email: team@eliteindia.org

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
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional


class ProjectCreator:
    """Creates new PowerScript projects"""
    
    def __init__(self):
        self.templates = {
            'basic': self._create_basic_project,
            'ai': self._create_ai_project,
            'web': self._create_web_project,
            'cli': self._create_cli_project
        }
    
    def create_project(self, name: str, template: str = 'basic', init_git: bool = True) -> bool:
        """Create a new PowerScript project"""
        if template not in self.templates:
            print(f"Unknown template: {template}")
            return False
        
        project_path = Path(name)
        
        if project_path.exists():
            print(f"Directory '{name}' already exists")
            return False
        
        try:
            # Create project directory
            project_path.mkdir(parents=True)
            
            # Create project structure using template
            self.templates[template](project_path, name)
            
            # Initialize git repository
            if init_git:
                self._init_git(project_path)
            
            print(f"✓ Created PowerScript project '{name}' using '{template}' template")
            print(f"  cd {name}")
            print(f"  powerscript compile src/ -o build/")
            print(f"  powerscript run src/main.ps")
            
            return True
            
        except Exception as e:
            print(f"Failed to create project: {e}")
            # Clean up on failure
            if project_path.exists():
                shutil.rmtree(project_path)
            return False
    
    def _create_basic_project(self, project_path: Path, name: str):
        """Create basic project structure"""
        # Create directories
        (project_path / 'src').mkdir()
        (project_path / 'tests').mkdir()
        (project_path / 'build').mkdir()
        (project_path / 'docs').mkdir()
        
        # Create powerscript.toml
        toml_content = f"""[project]
name = "{name}"
version = "0.1.0"
main = "src/main.ps"
description = "A PowerScript project"

[compiler]
output_dir = "build"
strict_typing = true
runtime_checks = true
target_python_version = "3.8"
generate_stubs = true

[runtime]
async_enabled = true
access_modifiers = true
type_validation = "strict"
"""
        with open(project_path / 'powerscript.toml', 'w') as f:
            f.write(toml_content)
        
        # Create main.ps
        main_content = '''// PowerScript Main File
import { print } from "builtins";

class Greeting {
    private message: string;
    
    constructor(message: string) {
        this.message = message;
    }
    
    public function greet(): void {
        print("Hello from PowerScript!");
        print(this.message);
    }
}

async function main(): void {
    let greeter: Greeting = new Greeting("Welcome to your new project!");
    greeter.greet();
}

main();
'''
        with open(project_path / 'src' / 'main.ps', 'w') as f:
            f.write(main_content)
        
        # Create README.md
        readme_content = f"""# {name}

A PowerScript project.

## Getting Started

### Compile and Run

```bash
# Compile PowerScript to Python
powerscript compile src/ -o build/

# Run the compiled Python
python build/main.py

# Or run directly
powerscript run src/main.ps
```

### Watch Mode

```bash
# Automatically recompile on changes
powerscript compile src/ -o build/ --watch
```

### Type Checking

```bash
# Check types
powerscript check src/
```

## Project Structure

```
{name}/
├── src/           # PowerScript source files
├── tests/         # Test files
├── build/         # Compiled Python files
├── docs/          # Documentation
└── powerscript.toml  # Project configuration
```
"""
        with open(project_path / 'README.md', 'w') as f:
            f.write(readme_content)
        
        # Create .gitignore
        gitignore_content = """# Build outputs
build/
*.py
*.pyc
__pycache__/
*.pyo
*.pyd
.Python

# PowerScript cache
.powerscript/

# IDEs
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Runtime
.env
"""
        with open(project_path / '.gitignore', 'w') as f:
            f.write(gitignore_content)
    
    def _create_ai_project(self, project_path: Path, name: str):
        """Create AI project structure"""
        # Start with basic structure
        self._create_basic_project(project_path, name)
        
        # Add AI-specific directories
        (project_path / 'data').mkdir()
        (project_path / 'models').mkdir()
        (project_path / 'notebooks').mkdir()
        
        # Create AI-specific main.ps
        ai_main_content = '''// PowerScript AI Project
import { print } from "builtins";

class DataProcessor {
    private data: Array<number>;
    
    constructor(data: Array<number>) {
        this.data = data;
    }
    
    public async function process(): Array<number> {
        // AI data processing logic here
        print("Processing AI data...");
        return this.data.map(x => x * 2);
    }
}

class MLModel {
    private weights: Array<Array<number>>;
    
    constructor() {
        this.weights = [];
    }
    
    public async function train(data: Array<Array<number>>): void {
        print("Training ML model...");
        // Training logic here
    }
    
    public async function predict(input: Array<number>): Array<number> {
        print("Making predictions...");
        // Prediction logic here
        return input;
    }
}

async function main(): void {
    let processor: DataProcessor = new DataProcessor([1, 2, 3, 4, 5]);
    let processedData: Array<number> = await processor.process();
    
    let model: MLModel = new MLModel();
    await model.train([processedData]);
    
    let predictions: Array<number> = await model.predict([1, 2, 3]);
    print("Predictions:", predictions);
}

main();
'''
        with open(project_path / 'src' / 'main.ps', 'w') as f:
            f.write(ai_main_content)
        
        # Create requirements.txt for Python dependencies
        requirements_content = """numpy>=1.21.0
pandas>=1.3.0
scikit-learn>=1.0.0
torch>=1.9.0
matplotlib>=3.4.0
jupyter>=1.0.0
beartype>=0.10.0
"""
        with open(project_path / 'requirements.txt', 'w') as f:
            f.write(requirements_content)
    
    def _create_web_project(self, project_path: Path, name: str):
        """Create web project structure"""
        # Start with basic structure
        self._create_basic_project(project_path, name)
        
        # Add web-specific directories
        (project_path / 'static').mkdir()
        (project_path / 'templates').mkdir()
        (project_path / 'api').mkdir()
        
        # Create web-specific main.ps
        web_main_content = '''// PowerScript Web Project
import { print } from "builtins";

class WebServer {
    private port: number;
    private routes: Map<string, Function>;
    
    constructor(port: number = 8000) {
        this.port = port;
        this.routes = new Map();
    }
    
    public function route(path: string, handler: Function): void {
        this.routes.set(path, handler);
    }
    
    public async function start(): void {
        print(`Starting web server on port ${this.port}...`);
        // Web server logic here
    }
}

class APIHandler {
    public async function handleRequest(request: any): any {
        // API request handling logic
        return { message: "Hello from PowerScript API!" };
    }
}

async function main(): void {
    let server: WebServer = new WebServer(8000);
    let apiHandler: APIHandler = new APIHandler();
    
    server.route("/api/hello", apiHandler.handleRequest);
    
    await server.start();
}

main();
'''
        with open(project_path / 'src' / 'main.ps', 'w') as f:
            f.write(web_main_content)
        
        # Create requirements.txt
        requirements_content = """flask>=2.0.0
fastapi>=0.70.0
uvicorn>=0.15.0
pydantic>=1.8.0
beartype>=0.10.0
"""
        with open(project_path / 'requirements.txt', 'w') as f:
            f.write(requirements_content)
    
    def _create_cli_project(self, project_path: Path, name: str):
        """Create CLI project structure"""
        # Start with basic structure
        self._create_basic_project(project_path, name)
        
        # Create CLI-specific main.ps
        cli_main_content = '''// PowerScript CLI Project
import { print } from "builtins";

class CLIApp {
    private name: string;
    private version: string;
    
    constructor(name: string, version: string = "1.0.0") {
        this.name = name;
        this.version = version;
    }
    
    public function parseArgs(args: Array<string>): Map<string, any> {
        let parsed: Map<string, any> = new Map();
        
        for (let i: number = 0; i < args.length; i++) {
            let arg: string = args[i];
            if (arg.startsWith("--")) {
                let key: string = arg.substring(2);
                let value: string = i + 1 < args.length ? args[i + 1] : "true";
                parsed.set(key, value);
                i++;
            }
        }
        
        return parsed;
    }
    
    public async function run(args: Array<string>): void {
        let parsedArgs: Map<string, any> = this.parseArgs(args);
        
        if (parsedArgs.has("help")) {
            this.showHelp();
            return;
        }
        
        if (parsedArgs.has("version")) {
            print(`${this.name} v${this.version}`);
            return;
        }
        
        print(`Running ${this.name}...`);
        // CLI logic here
    }
    
    private function showHelp(): void {
        print(`${this.name} v${this.version}`);
        print("");
        print("Usage: powerscript run src/main.ps [options]");
        print("");
        print("Options:");
        print("  --help     Show this help message");
        print("  --version  Show version information");
    }
}

async function main(): void {
    let app: CLIApp = new CLIApp("PowerScript CLI App");
    
    // Get command line arguments (simulated)
    let args: Array<string> = ["--help"];
    
    await app.run(args);
}

main();
'''
        with open(project_path / 'src' / 'main.ps', 'w') as f:
            f.write(cli_main_content)
        
        # Create requirements.txt
        requirements_content = """click>=8.0.0
typer>=0.4.0
rich>=10.0.0
beartype>=0.10.0
"""
        with open(project_path / 'requirements.txt', 'w') as f:
            f.write(requirements_content)
    
    def _init_git(self, project_path: Path):
        """Initialize git repository"""
        try:
            subprocess.run(['git', 'init'], cwd=project_path, check=True, capture_output=True)
            subprocess.run(['git', 'add', '.'], cwd=project_path, check=True, capture_output=True)
            subprocess.run(['git', 'commit', '-m', 'Initial commit'], cwd=project_path, check=True, capture_output=True)
        except subprocess.CalledProcessError:
            print("Warning: Could not initialize git repository")
        except FileNotFoundError:
            print("Warning: Git not found, skipping repository initialization")