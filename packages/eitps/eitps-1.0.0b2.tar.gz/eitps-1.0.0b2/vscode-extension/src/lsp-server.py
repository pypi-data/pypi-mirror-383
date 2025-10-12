#!/usr/bin/env python3
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
PowerScript Language Server Protocol implementation
Provides IntelliSense, hover information, diagnostics, and go-to-definition for PowerScript files
"""

import json
import sys
import re
from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import urlparse, unquote

class PowerScriptLSP:
    def __init__(self):
        self.workspace_folders = []
        self.documents = {}
        self.symbols = {}
        self.is_debug = '--debug' in sys.argv
        
    def log(self, message: str):
        if self.is_debug:
            print(f"[DEBUG] {message}", file=sys.stderr)
    
    def send_response(self, id: Any, result: Any = None, error: Any = None):
        """Send JSON-RPC response"""
        response = {"jsonrpc": "2.0", "id": id}
        if error:
            response["error"] = error
        else:
            response["result"] = result
        
        message = json.dumps(response)
        content_length = len(message.encode('utf-8'))
        
        print(f"Content-Length: {content_length}\r\n\r\n{message}", end='', flush=True)
    
    def send_notification(self, method: str, params: Any = None):
        """Send JSON-RPC notification"""
        notification = {"jsonrpc": "2.0", "method": method}
        if params:
            notification["params"] = params
        
        message = json.dumps(notification)
        content_length = len(message.encode('utf-8'))
        
        print(f"Content-Length: {content_length}\r\n\r\n{message}", end='', flush=True)
    
    def parse_powerscript(self, content: str) -> Dict[str, List[Dict]]:
        """Parse PowerScript content and extract symbols"""
        symbols = {
            'classes': [],
            'functions': [],
            'variables': [],
            'imports': []
        }
        
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Parse class definitions
            class_match = re.match(r'class\s+(\w+)(?:\s*:\s*(\w+))?\s*{', line)
            if class_match:
                class_name = class_match.group(1)
                base_class = class_match.group(2)
                symbols['classes'].append({
                    'name': class_name,
                    'line': i,
                    'base': base_class,
                    'type': 'class'
                })
            
            # Parse function definitions
            func_match = re.match(r'(?:async\s+)?function\s+(\w+)\s*\([^)]*\)(?:\s*:\s*(\w+))?\s*{', line)
            if func_match:
                func_name = func_match.group(1)
                return_type = func_match.group(2)
                symbols['functions'].append({
                    'name': func_name,
                    'line': i,
                    'return_type': return_type,
                    'type': 'function'
                })
            
            # Parse arrow functions
            arrow_match = re.match(r'(?:let|const)\s+(\w+)\s*=\s*\([^)]*\)\s*=>', line)
            if arrow_match:
                func_name = arrow_match.group(1)
                symbols['functions'].append({
                    'name': func_name,
                    'line': i,
                    'type': 'arrow_function'
                })
            
            # Parse variable declarations
            var_match = re.match(r'(?:let|const|var)\s+(\w+)(?:\s*:\s*(\w+))?\s*=', line)
            if var_match:
                var_name = var_match.group(1)
                var_type = var_match.group(2)
                symbols['variables'].append({
                    'name': var_name,
                    'line': i,
                    'type': var_type or 'any'
                })
            
            # Parse imports
            import_match = re.match(r'import\s+(?:{([^}]+)}|\*\s+as\s+(\w+)|(\w+))\s+from\s+["\']([^"\']+)["\']', line)
            if import_match:
                if import_match.group(1):  # Named imports
                    imports = [name.strip() for name in import_match.group(1).split(',')]
                elif import_match.group(2):  # Namespace import
                    imports = [import_match.group(2)]
                else:  # Default import
                    imports = [import_match.group(3)]
                
                module = import_match.group(4)
                symbols['imports'].append({
                    'names': imports,
                    'module': module,
                    'line': i
                })
        
        return symbols
    
    def get_completions(self, uri: str, line: int, character: int) -> List[Dict]:
        """Provide auto-completion suggestions"""
        if uri not in self.documents:
            return []
        
        content = self.documents[uri]
        symbols = self.parse_powerscript(content)
        
        completions = []
        
        # Add built-in keywords
        keywords = [
            'class', 'function', 'async', 'await', 'let', 'const', 'var',
            'if', 'else', 'for', 'while', 'do', 'switch', 'case', 'default',
            'try', 'catch', 'finally', 'throw', 'return', 'break', 'continue',
            'import', 'export', 'from', 'as', 'null', 'undefined', 'true', 'false'
        ]
        
        for keyword in keywords:
            completions.append({
                'label': keyword,
                'kind': 14,  # Keyword
                'detail': f'PowerScript keyword: {keyword}',
                'insertText': keyword
            })
        
        # Add types
        types = ['string', 'number', 'boolean', 'object', 'array', 'function', 'Hello']
        for type_name in types:
            completions.append({
                'label': type_name,
                'kind': 25,  # TypeParameter
                'detail': f'PowerScript type: {type_name}',
                'insertText': type_name
            })
        
        # Add user-defined symbols
        for class_info in symbols['classes']:
            completions.append({
                'label': class_info['name'],
                'kind': 7,  # Class
                'detail': f"Class {class_info['name']}",
                'insertText': class_info['name']
            })
        
        for func_info in symbols['functions']:
            completions.append({
                'label': func_info['name'],
                'kind': 3,  # Function
                'detail': f"Function {func_info['name']}",
                'insertText': func_info['name']
            })
        
        for var_info in symbols['variables']:
            completions.append({
                'label': var_info['name'],
                'kind': 6,  # Variable
                'detail': f"Variable {var_info['name']}: {var_info['type']}",
                'insertText': var_info['name']
            })
        
        return completions
    
    def get_hover_info(self, uri: str, line: int, character: int) -> Optional[Dict]:
        """Provide hover information"""
        if uri not in self.documents:
            return None
        
        content = self.documents[uri]
        lines = content.split('\n')
        
        if line >= len(lines):
            return None
        
        current_line = lines[line]
        symbols = self.parse_powerscript(content)
        
        # Find word at position
        if character >= len(current_line):
            return None
        
        start = character
        end = character
        
        while start > 0 and current_line[start - 1].isalnum():
            start -= 1
        while end < len(current_line) and current_line[end].isalnum():
            end += 1
        
        word = current_line[start:end]
        if not word:
            return None
        
        # Check if word is a known symbol
        for class_info in symbols['classes']:
            if class_info['name'] == word:
                return {
                    'contents': {
                        'kind': 'markdown',
                        'value': f"**Class** `{word}`\n\nPowerScript class definition"
                    }
                }
        
        for func_info in symbols['functions']:
            if func_info['name'] == word:
                return_type = func_info.get('return_type', 'void')
                return {
                    'contents': {
                        'kind': 'markdown',
                        'value': f"**Function** `{word}(): {return_type}`\n\nPowerScript function"
                    }
                }
        
        for var_info in symbols['variables']:
            if var_info['name'] == word:
                return {
                    'contents': {
                        'kind': 'markdown',
                        'value': f"**Variable** `{word}: {var_info['type']}`\n\nPowerScript variable"
                    }
                }
        
        # Check for built-in types/keywords
        if word in ['string', 'number', 'boolean', 'Hello']:
            return {
                'contents': {
                    'kind': 'markdown',
                    'value': f"**Type** `{word}`\n\nPowerScript built-in type"
                }
            }
        
        return None
    
    def get_diagnostics(self, uri: str) -> List[Dict]:
        """Provide diagnostic information"""
        if uri not in self.documents:
            return []
        
        content = self.documents[uri]
        lines = content.split('\n')
        diagnostics = []
        
        for i, line in enumerate(lines):
            # Check for syntax errors
            if 'class ' in line and '{' not in line and (i + 1 >= len(lines) or '{' not in lines[i + 1]):
                diagnostics.append({
                    'range': {
                        'start': {'line': i, 'character': 0},
                        'end': {'line': i, 'character': len(line)}
                    },
                    'severity': 1,  # Error
                    'message': 'Class declaration should be followed by opening brace',
                    'source': 'powerscript'
                })
            
            # Check for undefined types
            type_match = re.search(r':\s*(\w+)', line)
            if type_match:
                type_name = type_match.group(1)
                if type_name not in ['string', 'number', 'boolean', 'Hello', 'void', 'any']:
                    start_pos = type_match.start(1)
                    end_pos = type_match.end(1)
                    diagnostics.append({
                        'range': {
                            'start': {'line': i, 'character': start_pos},
                            'end': {'line': i, 'character': end_pos}
                        },
                        'severity': 2,  # Warning
                        'message': f'Unknown type: {type_name}',
                        'source': 'powerscript'
                    })
        
        return diagnostics
    
    def uri_to_path(self, uri: str) -> str:
        """Convert URI to file path"""
        parsed = urlparse(uri)
        return unquote(parsed.path)
    
    def handle_request(self, request: Dict):
        """Handle JSON-RPC request"""
        method = request.get('method')
        params = request.get('params', {})
        id = request.get('id')
        
        self.log(f"Handling request: {method}")
        
        if method == 'initialize':
            capabilities = {
                'textDocumentSync': 1,  # Full sync
                'completionProvider': {
                    'triggerCharacters': ['.', ':']
                },
                'hoverProvider': True,
                'definitionProvider': True,
                'diagnosticProvider': True
            }
            self.send_response(id, {'capabilities': capabilities})
        
        elif method == 'initialized':
            self.log("Language server initialized")
        
        elif method == 'textDocument/didOpen':
            uri = params['textDocument']['uri']
            content = params['textDocument']['text']
            self.documents[uri] = content
            
            # Send diagnostics
            diagnostics = self.get_diagnostics(uri)
            self.send_notification('textDocument/publishDiagnostics', {
                'uri': uri,
                'diagnostics': diagnostics
            })
        
        elif method == 'textDocument/didChange':
            uri = params['textDocument']['uri']
            changes = params['contentChanges']
            if changes:
                self.documents[uri] = changes[0]['text']
                
                # Send updated diagnostics
                diagnostics = self.get_diagnostics(uri)
                self.send_notification('textDocument/publishDiagnostics', {
                    'uri': uri,
                    'diagnostics': diagnostics
                })
        
        elif method == 'textDocument/completion':
            uri = params['textDocument']['uri']
            position = params['position']
            completions = self.get_completions(uri, position['line'], position['character'])
            self.send_response(id, {'items': completions})
        
        elif method == 'textDocument/hover':
            uri = params['textDocument']['uri']
            position = params['position']
            hover = self.get_hover_info(uri, position['line'], position['character'])
            self.send_response(id, hover)
        
        elif method == 'shutdown':
            self.send_response(id, None)
        
        elif method == 'exit':
            sys.exit(0)
        
        else:
            self.log(f"Unhandled method: {method}")
            if id is not None:
                self.send_response(id, None, {'code': -32601, 'message': 'Method not found'})

def main():
    lsp = PowerScriptLSP()
    lsp.log("PowerScript LSP Server starting...")
    
    while True:
        try:
            # Read Content-Length header
            header = sys.stdin.readline().strip()
            if not header.startswith('Content-Length:'):
                continue
            
            content_length = int(header.split(':')[1].strip())
            
            # Read empty line
            sys.stdin.readline()
            
            # Read message content
            content = sys.stdin.read(content_length)
            if not content:
                break
            
            request = json.loads(content)
            lsp.handle_request(request)
            
        except EOFError:
            break
        except Exception as e:
            lsp.log(f"Error: {e}")
            continue

if __name__ == '__main__':
    main()