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

from typing import List, Optional, Dict, Any
from lsprotocol.types import (
    CompletionItem, CompletionItemKind, CompletionParams,
    Hover, HoverParams, MarkupContent, MarkupKind,
    Diagnostic, DiagnosticSeverity, Position, Range
)

from ..compiler import Lexer, Parser
from ..compiler.ast_nodes import ClassNode, FunctionNode, VariableNode
from ..typechecker import TypeChecker


class CompletionHandler:
    """Handles auto-completion requests"""
    
    def __init__(self, server):
        self.server = server
    
    async def provide_completions(self, params: CompletionParams) -> List[CompletionItem]:
        """Provide completion items"""
        uri = params.text_document.uri
        position = params.position
        
        completions = []
        
        # Get document and AST
        text = self.server.get_document_text(uri)
        ast_nodes = self.server.get_ast(uri)
        
        if not text or not ast_nodes:
            return completions
        
        # Add keyword completions
        keywords = [
            "class", "function", "constructor", "let", "const",
            "if", "else", "while", "for", "return", "async", "await",
            "public", "private", "protected", "import", "export"
        ]
        
        for keyword in keywords:
            completions.append(CompletionItem(
                label=keyword,
                kind=CompletionItemKind.Keyword,
                detail=f"PowerScript keyword",
                insert_text=keyword
            ))
        
        # Add type completions
        types = ["string", "number", "boolean", "void", "any", "Array", "Promise"]
        for type_name in types:
            completions.append(CompletionItem(
                label=type_name,
                kind=CompletionItemKind.TypeParameter,
                detail=f"PowerScript type",
                insert_text=type_name
            ))
        
        # Add completions from AST
        for node in ast_nodes:
            if isinstance(node, ClassNode):
                completions.append(CompletionItem(
                    label=node.name,
                    kind=CompletionItemKind.Class,
                    detail=f"class {node.name}",
                    insert_text=node.name
                ))
                
                # Add methods from class
                for method in node.methods:
                    completions.append(CompletionItem(
                        label=method.name,
                        kind=CompletionItemKind.Method,
                        detail=f"method {method.name}()",
                        insert_text=f"{method.name}()"
                    ))
            
            elif isinstance(node, FunctionNode):
                completions.append(CompletionItem(
                    label=node.name,
                    kind=CompletionItemKind.Function,
                    detail=f"function {node.name}()",
                    insert_text=f"{node.name}()"
                ))
            
            elif isinstance(node, VariableNode):
                completions.append(CompletionItem(
                    label=node.name,
                    kind=CompletionItemKind.Variable,
                    detail=f"let {node.name}: {node.var_type or 'any'}",
                    insert_text=node.name
                ))
        
        return completions


class HoverHandler:
    """Handles hover information requests"""
    
    def __init__(self, server):
        self.server = server
    
    async def provide_hover(self, params: HoverParams) -> Optional[Hover]:
        """Provide hover information"""
        uri = params.text_document.uri
        position = params.position
        
        text = self.server.get_document_text(uri)
        ast_nodes = self.server.get_ast(uri)
        
        if not text or not ast_nodes:
            return None
        
        # Find symbol at position
        lines = text.split('\n')
        if position.line >= len(lines):
            return None
        
        line = lines[position.line]
        if position.character >= len(line):
            return None
        
        # Extract word at position
        start = position.character
        end = position.character
        
        # Find word boundaries
        while start > 0 and (line[start - 1].isalnum() or line[start - 1] == '_'):
            start -= 1
        while end < len(line) and (line[end].isalnum() or line[end] == '_'):
            end += 1
        
        if start == end:
            return None
        
        word = line[start:end]
        
        # Find matching symbol in AST
        for node in ast_nodes:
            hover_info = self._get_hover_for_node(node, word)
            if hover_info:
                return Hover(
                    contents=MarkupContent(
                        kind=MarkupKind.Markdown,
                        value=hover_info
                    ),
                    range=Range(
                        start=Position(line=position.line, character=start),
                        end=Position(line=position.line, character=end)
                    )
                )
        
        return None
    
    def _get_hover_for_node(self, node: Any, symbol: str) -> Optional[str]:
        """Get hover information for a node"""
        if isinstance(node, ClassNode) and node.name == symbol:
            methods_info = []
            if node.constructor:
                methods_info.append(f"- constructor({', '.join(p.name + ': ' + (p.param_type or 'any') for p in node.constructor.parameters)})")
            
            for method in node.methods:
                params = ', '.join(p.name + ': ' + (p.param_type or 'any') for p in method.parameters)
                return_type = method.return_type or 'void'
                methods_info.append(f"- {method.name}({params}): {return_type}")
            
            return f"```powerscript\nclass {node.name}\n```\n\n**Methods:**\n" + '\n'.join(methods_info)
        
        elif isinstance(node, FunctionNode) and node.name == symbol:
            params = ', '.join(p.name + ': ' + (p.param_type or 'any') for p in node.parameters)
            return_type = node.return_type or 'void'
            async_prefix = 'async ' if node.is_async else ''
            
            return f"```powerscript\n{async_prefix}function {node.name}({params}): {return_type}\n```"
        
        elif isinstance(node, VariableNode) and node.name == symbol:
            var_type = node.var_type or 'any'
            const_prefix = 'const' if node.is_const else 'let'
            
            return f"```powerscript\n{const_prefix} {node.name}: {var_type}\n```"
        
        # Check nested nodes
        if hasattr(node, 'methods'):
            for method in node.methods:
                hover_info = self._get_hover_for_node(method, symbol)
                if hover_info:
                    return hover_info
        
        return None


class DiagnosticsHandler:
    """Handles diagnostic (error/warning) reporting"""
    
    def __init__(self, server):
        self.server = server
    
    async def publish_diagnostics(self, uri: str):
        """Publish diagnostics for a document"""
        text = self.server.get_document_text(uri)
        if not text:
            return
        
        diagnostics = []
        
        try:
            # Run lexer
            lexer = Lexer(text, uri)
            lexer.tokenize()
            
            # Run parser
            parser = Parser(lexer)
            ast_nodes = parser.parse()
            
            # Run type checker
            type_checker = TypeChecker()
            result = type_checker.check(ast_nodes)
            
            # Convert errors to diagnostics
            for error in result.errors:
                diagnostics.append(Diagnostic(
                    range=Range(
                        start=Position(line=error.line - 1, character=0),
                        end=Position(line=error.line - 1, character=100)
                    ),
                    message=error.message,
                    severity=DiagnosticSeverity.Error,
                    source="powerscript"
                ))
            
            # Convert warnings to diagnostics
            for warning in result.warnings:
                diagnostics.append(Diagnostic(
                    range=Range(
                        start=Position(line=warning.line - 1, character=0),
                        end=Position(line=warning.line - 1, character=100)
                    ),
                    message=warning.message,
                    severity=DiagnosticSeverity.Warning,
                    source="powerscript"
                ))
        
        except Exception as e:
            # Syntax error
            diagnostics.append(Diagnostic(
                range=Range(
                    start=Position(line=0, character=0),
                    end=Position(line=0, character=100)
                ),
                message=f"Syntax error: {str(e)}",
                severity=DiagnosticSeverity.Error,
                source="powerscript"
            ))
        
        # Publish diagnostics
        await self.server.server.publish_diagnostics(uri, diagnostics)