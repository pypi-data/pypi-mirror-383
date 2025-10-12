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

from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class PowerScriptDiagnostic:
    """PowerScript-specific diagnostic information"""
    line: int
    column: int
    message: str
    severity: str  # "error", "warning", "info"
    code: Optional[str] = None
    source: str = "powerscript"


@dataclass
class PowerScriptSymbol:
    """Symbol information for LSP"""
    name: str
    kind: str  # "class", "function", "variable", "method"
    type_info: Optional[str] = None
    line: int = 0
    column: int = 0
    doc_string: Optional[str] = None


class PowerScriptLSPProtocol:
    """PowerScript-specific LSP protocol extensions"""
    
    @staticmethod
    def create_completion_item(symbol: PowerScriptSymbol) -> Dict[str, Any]:
        """Create LSP completion item from PowerScript symbol"""
        kind_map = {
            "class": 7,      # CompletionItemKind.Class
            "function": 3,   # CompletionItemKind.Function
            "method": 2,     # CompletionItemKind.Method
            "variable": 6,   # CompletionItemKind.Variable
            "keyword": 14,   # CompletionItemKind.Keyword
            "type": 25,      # CompletionItemKind.TypeParameter
        }
        
        return {
            "label": symbol.name,
            "kind": kind_map.get(symbol.kind, 1),
            "detail": symbol.type_info or "",
            "documentation": symbol.doc_string or "",
            "insertText": symbol.name,
        }
    
    @staticmethod
    def create_hover_content(symbol: PowerScriptSymbol) -> Dict[str, Any]:
        """Create LSP hover content from PowerScript symbol"""
        content = f"```powerscript\n{symbol.name}"
        if symbol.type_info:
            content += f": {symbol.type_info}"
        content += "\n```"
        
        if symbol.doc_string:
            content += f"\n\n{symbol.doc_string}"
        
        return {
            "kind": "markdown",
            "value": content
        }
    
    @staticmethod
    def create_diagnostic(diag: PowerScriptDiagnostic) -> Dict[str, Any]:
        """Create LSP diagnostic from PowerScript diagnostic"""
        severity_map = {
            "error": 1,    # DiagnosticSeverity.Error
            "warning": 2,  # DiagnosticSeverity.Warning
            "info": 3,     # DiagnosticSeverity.Information
            "hint": 4,     # DiagnosticSeverity.Hint
        }
        
        return {
            "range": {
                "start": {"line": diag.line - 1, "character": diag.column},
                "end": {"line": diag.line - 1, "character": diag.column + 100}
            },
            "message": diag.message,
            "severity": severity_map.get(diag.severity, 1),
            "source": diag.source,
            "code": diag.code
        }