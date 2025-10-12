#!/bin/bash

# MIT License
#
# Copyright (c) 2025 Saleem Ahmad (Elite India Org Team)
# Email: team@eliteindia.org
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# PowerScript VS Code Extension Test Script
# This script demonstrates the extension installation and testing process

echo "🚀 PowerScript VS Code Extension - Phase 6 Implementation"
echo "=========================================================="

# Check if VS Code is installed
if ! command -v code &> /dev/null; then
    echo "❌ VS Code is not installed or not in PATH"
    exit 1
fi

echo "✅ VS Code found"

# Navigate to extension directory
cd "$(dirname "$0")"

echo "📦 Packaging extension..."
if vsce package; then
    echo "✅ Extension packaged successfully"
else
    echo "❌ Failed to package extension"
    exit 1
fi

echo "🔧 Installing extension..."
if code --install-extension powerscript-1.0.0.vsix; then
    echo "✅ Extension installed successfully"
else
    echo "❌ Failed to install extension"
    exit 1
fi

echo "🧪 Opening test files..."
code ../ps_tests/test_simple.ps
code ../ps_tests/extension_demo.ps

echo ""
echo "🎉 PowerScript VS Code Extension is ready!"
echo ""
echo "Features available:"
echo "- ✅ Syntax highlighting for .ps files"
echo "- ✅ Code snippets (try typing 'class', 'function', etc.)"
echo "- ✅ Basic diagnostics and error detection"
echo "- ✅ Compile and run commands in context menu"
echo "- ✅ Keyboard shortcuts (Ctrl+Shift+B to compile, Ctrl+Shift+R to run)"
echo ""
echo "Test the extension by:"
echo "1. Opening a .ps file"
echo "2. Trying code snippets"
echo "3. Right-clicking for compile/run options"
echo "4. Using keyboard shortcuts"
echo ""
echo "Extension files located at: $(pwd)"
echo "Test files opened in VS Code"