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

import asyncio
from typing import Dict, List, Optional, Any
from pygls.server import LanguageServer
from pygls.lsp import types
from lsprotocol.types import (
    TEXT_DOCUMENT_DID_OPEN,
    TEXT_DOCUMENT_DID_CHANGE,
    TEXT_DOCUMENT_DID_SAVE,
    TEXT_DOCUMENT_COMPLETION,
    TEXT_DOCUMENT_HOVER,
    TEXT_DOCUMENT_DEFINITION,
    INITIALIZE,
)

from ..compiler import Lexer, Parser, Transpiler
from ..typechecker import TypeChecker
from .handlers import CompletionHandler, DiagnosticsHandler, HoverHandler


class PowerScriptLanguageServer:
    """PowerScript Language Server Protocol implementation"""
    
    def __init__(self):
        self.server = LanguageServer("powerscript-lsp", "0.1.0")
        self.documents: Dict[str, str] = {}
        self.ast_cache: Dict[str, List] = {}
        
        # Initialize handlers
        self.completion_handler = CompletionHandler(self)
        self.diagnostics_handler = DiagnosticsHandler(self)
        self.hover_handler = HoverHandler(self)
        
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup LSP message handlers"""
        
        @self.server.feature(INITIALIZE)
        async def initialize(params):
            return types.InitializeResult(
                capabilities=types.ServerCapabilities(
                    text_document_sync=types.TextDocumentSyncOptions(
                        open_close=True,
                        change=types.TextDocumentSyncKind.Full,
                        save=True,
                    ),
                    completion_provider=types.CompletionOptions(
                        trigger_characters=['.', ':', '<']
                    ),
                    hover_provider=True,
                    definition_provider=True,
                    diagnostic_provider=types.DiagnosticOptions(
                        inter_file_dependencies=True,
                        workspace_diagnostics=True,
                    ),
                )
            )
        
        @self.server.feature(TEXT_DOCUMENT_DID_OPEN)
        async def did_open(params: types.DidOpenTextDocumentParams):
            uri = params.text_document.uri
            text = params.text_document.text
            self.documents[uri] = text
            await self._update_ast(uri, text)
            await self.diagnostics_handler.publish_diagnostics(uri)
        
        @self.server.feature(TEXT_DOCUMENT_DID_CHANGE)
        async def did_change(params: types.DidChangeTextDocumentParams):
            uri = params.text_document.uri
            changes = params.content_changes
            
            # Apply changes (assuming full document sync)
            if changes and len(changes) > 0:
                text = changes[0].text
                self.documents[uri] = text
                await self._update_ast(uri, text)
                await self.diagnostics_handler.publish_diagnostics(uri)
        
        @self.server.feature(TEXT_DOCUMENT_DID_SAVE)
        async def did_save(params: types.DidSaveTextDocumentParams):
            uri = params.text_document.uri
            if uri in self.documents:
                await self.diagnostics_handler.publish_diagnostics(uri)
        
        @self.server.feature(TEXT_DOCUMENT_COMPLETION)
        async def completion(params: types.CompletionParams):
            return await self.completion_handler.provide_completions(params)
        
        @self.server.feature(TEXT_DOCUMENT_HOVER)
        async def hover(params: types.HoverParams):
            return await self.hover_handler.provide_hover(params)
        
        @self.server.feature(TEXT_DOCUMENT_DEFINITION)
        async def definition(params: types.DefinitionParams):
            # TODO: Implement go-to-definition
            return None
    
    async def _update_ast(self, uri: str, text: str):
        """Update AST cache for document"""
        try:
            lexer = Lexer(text, uri)
            lexer.tokenize()
            
            parser = Parser(lexer)
            ast_nodes = parser.parse()
            
            self.ast_cache[uri] = ast_nodes
        except Exception as e:
            # Store error for diagnostics
            self.ast_cache[uri] = []
    
    def get_ast(self, uri: str) -> List:
        """Get cached AST for document"""
        return self.ast_cache.get(uri, [])
    
    def get_document_text(self, uri: str) -> Optional[str]:
        """Get document text"""
        return self.documents.get(uri)
    
    def start_server(self, host: str = "localhost", port: int = 8080):
        """Start the LSP server"""
        print(f"Starting PowerScript LSP server on {host}:{port}")
        self.server.start_tcp(host, port)
    
    def start_stdio(self):
        """Start server using stdio"""
        print("Starting PowerScript LSP server on stdio")
        self.server.start_io()


def main():
    """Main entry point for LSP server"""
    import sys
    
    server = PowerScriptLanguageServer()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--tcp":
        server.start_server()
    else:
        server.start_stdio()


if __name__ == "__main__":
    main()