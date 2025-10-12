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
import sys
import json
import time
import subprocess
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from pathlib import Path
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    HAS_WATCHDOG = True
except ImportError:
    Observer = None
    FileSystemEventHandler = None
    HAS_WATCHDOG = False
from ..compiler import Lexer, Parser, Transpiler
from ..typechecker import TypeChecker
from .project_creator import ProjectCreator


class Command(ABC):
    """Base class for CLI commands"""
    
    @abstractmethod
    def execute(self, args) -> int:
        """Execute the command"""
        pass


class CompileCommand(Command):
    """Compile PowerScript files to Python"""
    
    def execute(self, args) -> int:
        """Execute compile command"""
        source_path = Path(args.source)
        output_path = Path(args.output)
        
        if not source_path.exists():
            print(f"Error: Source path '{source_path}' does not exist", file=sys.stderr)
            return 1
        
        # Create output directory
        output_path.mkdir(parents=True, exist_ok=True)
        
        if args.watch:
            return self._watch_compile(source_path, output_path, args)
        else:
            return self._compile_once(source_path, output_path, args)
    
    def _compile_once(self, source_path: Path, output_path: Path, args) -> int:
        """Compile files once"""
        try:
            if source_path.is_file():
                return self._compile_file(source_path, output_path, args)
            else:
                return self._compile_directory(source_path, output_path, args)
        except Exception as e:
            print(f"Compilation failed: {e}", file=sys.stderr)
            return 1
    
    def _compile_file(self, source_file: Path, output_path: Path, args) -> int:
        """Compile a single file"""
        if not source_file.suffix == '.ps':
            print(f"Warning: '{source_file}' is not a PowerScript file (.ps)")
            return 0
        
        print(f"Compiling {source_file}...")
        
        try:
            # Read source
            with open(source_file, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            # Compile
            from ..compiler.transpiler import transpile_file
            python_code = transpile_file(source_code, str(source_file))
            
            # Write output
            output_file = output_path / source_file.with_suffix('.py').name
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(python_code)
            
            # Generate stub file if requested
            if args.generate_stubs:
                stub_file = output_path / source_file.with_suffix('.pyi').name
                stub_content = self._generate_stub(source_code, str(source_file))
                with open(stub_file, 'w', encoding='utf-8') as f:
                    f.write(stub_content)
            
            print(f"✓ Compiled {source_file} -> {output_file}")
            return 0
            
        except Exception as e:
            print(f"✗ Failed to compile {source_file}: {e}", file=sys.stderr)
            return 1
    
    def _compile_directory(self, source_dir: Path, output_path: Path, args) -> int:
        """Compile all files in directory"""
        success_count = 0
        error_count = 0
        
        # Find all .ps files
        ps_files = list(source_dir.rglob('*.ps'))
        
        if not ps_files:
            print(f"No PowerScript files found in {source_dir}")
            return 0
        
        for ps_file in ps_files:
            # Maintain directory structure
            relative_path = ps_file.relative_to(source_dir)
            output_file_path = output_path / relative_path.parent
            output_file_path.mkdir(parents=True, exist_ok=True)
            
            result = self._compile_file(ps_file, output_file_path, args)
            if result == 0:
                success_count += 1
            else:
                error_count += 1
        
        print(f"\nCompilation complete: {success_count} files compiled, {error_count} errors")
        return 0 if error_count == 0 else 1
    
    def _watch_compile(self, source_path: Path, output_path: Path, args) -> int:
        """Watch for changes and recompile"""
        if not HAS_WATCHDOG:
            print("Error: watchdog package not installed. Cannot use watch mode.")
            print("Install with: pip install watchdog")
            return 1
            
        print(f"Watching {source_path} for changes...")
        
        class PowerScriptHandler(FileSystemEventHandler):
            def __init__(self, command):
                self.command = command
                self.last_compile = 0
            
            def on_modified(self, event):
                if event.is_directory:
                    return
                
                file_path = Path(event.src_path)
                if file_path.suffix == '.ps':
                    # Debounce rapid changes
                    current_time = time.time()
                    if current_time - self.last_compile < 0.5:
                        return
                    self.last_compile = current_time
                    
                    print(f"\nChange detected in {file_path}")
                    self.command._compile_file(file_path, output_path, args)
        
        handler = PowerScriptHandler(self)
        observer = Observer()
        observer.schedule(handler, str(source_path), recursive=True)
        observer.start()
        
        try:
            # Initial compilation
            self._compile_once(source_path, output_path, args)
            
            # Watch for changes
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
            print("\nWatching stopped")
        
        observer.join()
        return 0
    
    def _generate_stub(self, source_code: str, filename: str) -> str:
        """Generate .pyi stub file"""
        # Basic stub generation - could be enhanced
        try:
            lexer = Lexer(source_code, filename)
            lexer.tokenize()
            
            parser = Parser(lexer)
            ast_nodes = parser.parse()
            
            stub_lines = []
            stub_lines.append("# PowerScript stub file")
            stub_lines.append("from typing import Any, Optional, List, Dict")
            stub_lines.append("")
            
            for node in ast_nodes:
                if hasattr(node, 'name'):
                    if hasattr(node, 'methods'):  # Class
                        stub_lines.append(f"class {node.name}:")
                        if node.constructor:
                            params = ", ".join([f"{p.name}: Any" for p in node.constructor.parameters])
                            stub_lines.append(f"    def __init__(self, {params}): ...")
                        for method in node.methods:
                            params = ", ".join([f"{p.name}: Any" for p in method.parameters])
                            stub_lines.append(f"    def {method.name}(self, {params}): ...")
                        stub_lines.append("")
                    elif hasattr(node, 'parameters'):  # Function
                        params = ", ".join([f"{p.name}: Any" for p in node.parameters])
                        stub_lines.append(f"def {node.name}({params}): ...")
                        stub_lines.append("")
            
            return "\n".join(stub_lines)
        except:
            return "# Stub generation failed\n"


class RunCommand(Command):
    """Run PowerScript files directly"""
    
    def execute(self, args) -> int:
        """Execute run command"""
        source_file = Path(args.file)
        
        if not source_file.exists():
            print(f"Error: File '{source_file}' does not exist", file=sys.stderr)
            return 1
        
        if source_file.suffix != '.ps':
            print(f"Error: '{source_file}' is not a PowerScript file (.ps)", file=sys.stderr)
            return 1
        
        try:
            # Read source
            with open(source_file, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            # Check for cached compiled version
            cache_dir = Path.home() / '.powerscript' / 'cache'
            cache_dir.mkdir(parents=True, exist_ok=True)
            
            cache_file = cache_dir / f"{source_file.stem}_{hash(source_code) % 1000000}.py"
            
            if not args.no_cache and cache_file.exists():
                python_file = cache_file
                print(f"Using cached version: {cache_file}")
            else:
                # Compile to Python
                print(f"Compiling {source_file}...")
                from ..compiler.transpiler import transpile_file
                python_code = transpile_file(source_code, str(source_file))
                
                # Write to cache
                with open(cache_file, 'w', encoding='utf-8') as f:
                    f.write(python_code)
                python_file = cache_file
            
            # Run the Python file
            print(f"Running {source_file}...")
            cmd = [sys.executable, str(python_file)] + args.args
            import os
            env = os.environ.copy()
            env['PYTHONPATH'] = str(Path.cwd())
            result = subprocess.run(cmd, env=env)
            return result.returncode
            
        except Exception as e:
            print(f"Failed to run {source_file}: {e}", file=sys.stderr)
            return 1


class CreateCommand(Command):
    """Create a new PowerScript project"""
    
    def execute(self, args) -> int:
        """Execute create command"""
        try:
            creator = ProjectCreator()
            success = creator.create_project(
                args.name, 
                args.template,
                not args.no_git
            )
            return 0 if success else 1
        except Exception as e:
            print(f"Failed to create project: {e}", file=sys.stderr)
            return 1


class CheckCommand(Command):
    """Run type checker on PowerScript files"""
    
    def execute(self, args) -> int:
        """Execute check command"""
        source_path = Path(args.source)
        
        if not source_path.exists():
            print(f"Error: Source path '{source_path}' does not exist", file=sys.stderr)
            return 1
        
        try:
            if source_path.is_file():
                return self._check_file(source_path, args)
            else:
                return self._check_directory(source_path, args)
        except Exception as e:
            print(f"Type checking failed: {e}", file=sys.stderr)
            return 1
    
    def _check_file(self, source_file: Path, args) -> int:
        """Check a single file"""
        if source_file.suffix != '.ps':
            print(f"Warning: '{source_file}' is not a PowerScript file (.ps)")
            return 0
        
        try:
            # Read source
            with open(source_file, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            # Parse and check
            lexer = Lexer(source_code, str(source_file))
            lexer.tokenize()
            
            parser = Parser(lexer)
            ast_nodes = parser.parse()
            
            type_checker = TypeChecker(strict_mode=args.strict)
            result = type_checker.check(ast_nodes)
            
            if args.json:
                self._output_json(result, source_file)
            else:
                self._output_text(result, source_file)
            
            return 0 if result.success else 1
            
        except Exception as e:
            print(f"Failed to check {source_file}: {e}", file=sys.stderr)
            return 1
    
    def _check_directory(self, source_dir: Path, args) -> int:
        """Check all files in directory"""
        ps_files = list(source_dir.rglob('*.ps'))
        
        if not ps_files:
            print(f"No PowerScript files found in {source_dir}")
            return 0
        
        all_results = []
        error_count = 0
        
        for ps_file in ps_files:
            result = self._check_file(ps_file, args)
            if result != 0:
                error_count += 1
        
        print(f"\nType checking complete: {len(ps_files)} files checked, {error_count} with errors")
        return 0 if error_count == 0 else 1
    
    def _output_text(self, result, source_file: Path):
        """Output results in text format"""
        print(f"Checking {source_file}...")
        
        if result.errors:
            print("Errors:")
            for error in result.errors:
                print(f"  Line {error.line}: {error.message}")
        
        if result.warnings:
            print("Warnings:")
            for warning in result.warnings:
                print(f"  Line {warning.line}: {warning.message}")
        
        if result.success:
            print("✓ No type errors found")
        else:
            print(f"✗ Found {len(result.errors)} errors")
    
    def _output_json(self, result, source_file: Path):
        """Output results in JSON format"""
        output = {
            "file": str(source_file),
            "success": result.success,
            "errors": [
                {
                    "line": e.line,
                    "column": e.column,
                    "message": e.message,
                    "severity": e.severity.value
                }
                for e in result.errors
            ],
            "warnings": [
                {
                    "line": w.line,
                    "column": w.column,
                    "message": w.message,
                    "severity": w.severity.value
                }
                for w in result.warnings
            ]
        }
        print(json.dumps(output, indent=2))