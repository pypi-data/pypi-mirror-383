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

PowerScript (TPS) Auto-Compiler
Automatically compiles .ps files when imported or when files change
"""

import os
import sys
import glob
import time
from pathlib import Path
from typing import List, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from .compiler.lexer import Lexer
from .compiler.parser import Parser
from .compiler.transpiler import Transpiler


class PSFileHandler(FileSystemEventHandler):
    """Handles .ps file changes for auto-compilation"""
    
    def __init__(self, auto_compiler):
        self.auto_compiler = auto_compiler
        self.last_modified = {}
    
    def on_modified(self, event):
        if event.is_directory:
            return
        
        if event.src_path.endswith('.ps'):
            # Debounce: only compile if file hasn't been modified in last 1 second
            current_time = time.time()
            if (event.src_path not in self.last_modified or 
                current_time - self.last_modified[event.src_path] > 1):
                
                self.last_modified[event.src_path] = current_time
                print(f"🔄 Auto-compiling {event.src_path}...")
                try:
                    self.auto_compiler.compile_file(event.src_path)
                    print(f"✅ Successfully compiled {event.src_path}")
                except Exception as e:
                    print(f"❌ Compilation error in {event.src_path}: {e}")


class TPSAutoCompiler:
    """Automatically compiles PowerScript (TPS) files"""
    
    def __init__(self, watch: bool = True, output_dir: str = "build"):
        self.watch = watch
        self.output_dir = output_dir
        self.observer = None
        self.transpiler = Transpiler()
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
    
    def compile_file(self, ps_file: str) -> Optional[str]:
        """Compile a single .ps file to Python"""
        try:
            with open(ps_file, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            # Lex and parse the source code
            lexer = Lexer(source_code, ps_file)
            lexer.tokenize()
            
            parser = Parser(lexer)
            ast_nodes = parser.parse()
            
            # Transpile to Python source
            python_code = self.transpiler.transpile_to_code(ast_nodes)
            
            # Write output
            ps_path = Path(ps_file)
            py_filename = ps_path.stem + '.py'
            output_path = os.path.join(self.output_dir, py_filename)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(python_code)
            
            return output_path
            
        except Exception as e:
            raise Exception(f"Failed to compile {ps_file}: {str(e)}")
    
    def find_ps_files(self, directory: str = ".") -> List[str]:
        """Find all .ps files in directory"""
        return glob.glob(os.path.join(directory, "**/*.ps"), recursive=True)
    
    def compile_all(self, directory: str = ".") -> List[str]:
        """Compile all .ps files in directory"""
        ps_files = self.find_ps_files(directory)
        compiled_files = []
        errors = []
        
        for ps_file in ps_files:
            try:
                output_file = self.compile_file(ps_file)
                compiled_files.append(output_file)
                print(f"✅ Compiled: {ps_file} -> {output_file}")
            except Exception as e:
                errors.append(f"❌ {ps_file}: {e}")
        
        if errors:
            for error in errors:
                print(error, file=sys.stderr)
            raise Exception(f"Failed to compile {len(errors)} files")
        
        return compiled_files
    
    def start_watching(self, directory: str = "."):
        """Start watching for file changes"""
        if not self.watch:
            return
        
        print(f"👀 Watching for .ps file changes in {directory}...")
        
        event_handler = PSFileHandler(self)
        self.observer = Observer()
        self.observer.schedule(event_handler, directory, recursive=True)
        self.observer.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop_watching()
    
    def stop_watching(self):
        """Stop watching for file changes"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            print("⏹️  Stopped watching for file changes")


def auto_compile_project(directory: str = ".", output_dir: str = "build", watch: bool = False):
    """
    Auto-compile all PowerScript (.ps) files in a project
    
    Args:
        directory: Directory to search for .ps files
        output_dir: Output directory for compiled Python files
        watch: Whether to watch for file changes
    """
    compiler = TPSAutoCompiler(watch=watch, output_dir=output_dir)
    
    # Compile all existing files
    try:
        compiled_files = compiler.compile_all(directory)
        print(f"🎉 Successfully compiled {len(compiled_files)} PowerScript files!")
        
        if watch:
            compiler.start_watching(directory)
        
        return compiled_files
        
    except Exception as e:
        print(f"❌ Auto-compilation failed: {e}", file=sys.stderr)
        raise


def setup_auto_compile():
    """
    Set up automatic compilation for PowerScript files in the current project
    Call this in your main Python script to enable auto-compilation
    """
    # Check if we're in a project with .ps files
    ps_files = glob.glob("**/*.ps", recursive=True)
    
    if ps_files:
        print(f"🔍 Found {len(ps_files)} PowerScript files. Setting up auto-compilation...")
        try:
            auto_compile_project(watch=False)  # Compile once, don't watch
        except Exception as e:
            print(f"⚠️  Auto-compilation setup failed: {e}", file=sys.stderr)
    
    return len(ps_files)


# Auto-setup when module is imported
if __name__ != '__main__':
    # Automatically compile .ps files when this module is imported
    try:
        ps_count = setup_auto_compile()
        if ps_count > 0:
            print(f"✨ PowerScript auto-compilation ready! {ps_count} files processed.")
    except:
        pass  # Silent fail for imports