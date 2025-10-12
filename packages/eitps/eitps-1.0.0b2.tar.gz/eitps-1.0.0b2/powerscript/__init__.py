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

"""
PowerScript (TPS) - A fully structured development language that transpiles to Python.

This package provides:
- Lexer and Parser for PowerScript syntax
- AST to Python transpilation
- Static and runtime type checking
- CLI tools for development workflow
- Auto-compilation for .ps files
- LSP server for IDE support
- VS Code extension integration

Usage:
    # Auto-compile all .ps files in your project
    import tps
    tps.setup_auto_compile()
    
    # Or use CLI commands
    tps compile src/
    tps-run main.ps
    ps main.ps  # Quick run
"""

__version__ = "1.0.0b1"
__author__ = "PowerScript Team (Elite India Org)"
__package_name__ = "tps"

from .compiler import Lexer, Parser, Transpiler
from .runtime import RuntimeValidator, AccessModifiers
from .typechecker import TypeChecker, StaticAnalyzer
from .cli import CLI

# Auto-compilation features
try:
    from .auto_compile import (
        TPSAutoCompiler, 
        auto_compile_project, 
        setup_auto_compile
    )
    __all__ = [
        "Lexer", "Parser", "Transpiler",
        "RuntimeValidator", "AccessModifiers", 
        "TypeChecker", "StaticAnalyzer", "CLI",
        "TPSAutoCompiler", "auto_compile_project", "setup_auto_compile"
    ]
except ImportError:
    # Fallback if watchdog is not available
    __all__ = [
        "Lexer", "Parser", "Transpiler",
        "RuntimeValidator", "AccessModifiers",
        "TypeChecker", "StaticAnalyzer", "CLI"
    ]