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

import re
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional, Iterator, Dict, Pattern
from .ast_nodes import SourceLocation


class TokenType(Enum):
    """Token types for PowerScript"""
    # Literals
    IDENTIFIER = auto()
    STRING = auto()
    F_STRING = auto()
    TEMPLATE_LITERAL = auto()
    NUMBER = auto()
    BOOLEAN = auto()
    NULL = auto()
    
    # Keywords
    CLASS = auto()
    CONSTRUCTOR = auto()
    FUNCTION = auto()
    ASYNC = auto()
    AWAIT = auto()
    LET = auto()
    CONST = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    FOR = auto()
    IN = auto()
    RETURN = auto()
    BREAK = auto()
    CONTINUE = auto()
    SWITCH = auto()
    CASE = auto()
    TRY = auto()
    CATCH = auto()
    FINALLY = auto()
    THROW = auto()
    IMPORT = auto()
    FROM = auto()
    EXPORT = auto()
    DEFAULT = auto()
    AS = auto()
    
    # New language features
    LAMBDA = auto()
    WITH = auto()
    YIELD = auto()
    YIELD_FROM = auto()
    GENERATOR = auto()
    COMPREHENSION = auto()
    ELLIPSIS = auto()
    
    # Access modifiers
    PUBLIC = auto()
    PRIVATE = auto()
    PROTECTED = auto()
    
    # Types
    TYPE = auto()
    INTERFACE = auto()
    ENUM = auto()
    EXTENDS = auto()
    KEYOF = auto()
    TYPEOF = auto()
    INFER = auto()
    UNION = auto()
    INTERSECTION = auto()
    
    # Operators
    PLUS = auto()           # +
    MINUS = auto()          # -
    MULTIPLY = auto()       # *
    DIVIDE = auto()         # /
    MODULO = auto()         # %
    POWER = auto()          # **
    
    # Assignment
    ASSIGN = auto()         # =
    PLUS_ASSIGN = auto()    # +=
    MINUS_ASSIGN = auto()   # -=
    MULTIPLY_ASSIGN = auto() # *=
    DIVIDE_ASSIGN = auto()  # /=
    MODULO_ASSIGN = auto()  # %=
    POWER_ASSIGN = auto()   # **=
    
    # Comparison
    EQUAL = auto()          # ==
    NOT_EQUAL = auto()      # !=
    LESS_THAN = auto()      # <
    LESS_EQUAL = auto()     # <=
    GREATER_THAN = auto()   # >
    GREATER_EQUAL = auto()  # >=
    
    # Logical
    AND = auto()            # &&
    OR = auto()             # ||
    NOT = auto()            # !
    
    # Bitwise
    BIT_AND = auto()        # &
    BIT_OR = auto()         # |
    BIT_XOR = auto()        # ^
    BIT_NOT = auto()        # ~
    LEFT_SHIFT = auto()     # <<
    RIGHT_SHIFT = auto()    # >>
    
    # Punctuation
    LEFT_PAREN = auto()     # (
    RIGHT_PAREN = auto()    # )
    LEFT_BRACE = auto()     # {
    RIGHT_BRACE = auto()    # }
    LEFT_BRACKET = auto()   # [
    RIGHT_BRACKET = auto()  # ]
    SEMICOLON = auto()      # ;
    COMMA = auto()          # ,
    DOT = auto()            # .
    COLON = auto()          # :
    QUESTION = auto()       # ?
    ARROW = auto()          # =>
    
    # Special
    OPTIONAL_CHAIN = auto()    # ?.
    NULL_COALESCE = auto()     # ??
    SPREAD = auto()            # ...
    
    # Generics
    LESS_GENERIC = auto()      # < (in generic context)
    GREATER_GENERIC = auto()   # > (in generic context)
    
    # Comments and whitespace
    COMMENT = auto()
    WHITESPACE = auto()
    NEWLINE = auto()
    
    # Special tokens
    EOF = auto()
    UNKNOWN = auto()


@dataclass
class Token:
    """Represents a token in PowerScript source code"""
    type: TokenType
    value: str
    location: SourceLocation
    raw_value: str = ""  # Original text including quotes for strings


class LexerError(Exception):
    """Exception raised during lexical analysis"""
    
    def __init__(self, message: str, location: SourceLocation):
        self.message = message
        self.location = location
        super().__init__(f"{message} at line {location.line}, column {location.column}")


class Lexer:
    """PowerScript lexical analyzer"""
    
    # Keywords mapping
    KEYWORDS: Dict[str, TokenType] = {
        'class': TokenType.CLASS,
        'enum': TokenType.ENUM,
        'constructor': TokenType.CONSTRUCTOR,
        'function': TokenType.FUNCTION,
        'async': TokenType.ASYNC,
        'await': TokenType.AWAIT,
        'let': TokenType.LET,
        'const': TokenType.CONST,
        'if': TokenType.IF,
        'else': TokenType.ELSE,
        'while': TokenType.WHILE,
        'for': TokenType.FOR,
        'in': TokenType.IN,
        'return': TokenType.RETURN,
        'break': TokenType.BREAK,
        'continue': TokenType.CONTINUE,
        'switch': TokenType.SWITCH,
        'case': TokenType.CASE,
        'try': TokenType.TRY,
        'catch': TokenType.CATCH,
        'finally': TokenType.FINALLY,
        'throw': TokenType.THROW,
        'import': TokenType.IMPORT,
        'from': TokenType.FROM,
        'export': TokenType.EXPORT,
        'default': TokenType.DEFAULT,
        'public': TokenType.PUBLIC,
        'private': TokenType.PRIVATE,
        'protected': TokenType.PROTECTED,
        'type': TokenType.TYPE,
        'interface': TokenType.INTERFACE,
        'enum': TokenType.ENUM,
        'true': TokenType.BOOLEAN,
        'false': TokenType.BOOLEAN,
        'null': TokenType.NULL,
        'lambda': TokenType.LAMBDA,
        'with': TokenType.WITH,
        'yield': TokenType.YIELD,
        'as': TokenType.AS,
        'extends': TokenType.EXTENDS,
        'keyof': TokenType.KEYOF,
        'typeof': TokenType.TYPEOF,
        'infer': TokenType.INFER,
    }
    
    # Token patterns (order matters!)
    TOKEN_PATTERNS: List[tuple[TokenType, Pattern[str]]] = [
        # Comments
        (TokenType.COMMENT, re.compile(r'//.*')),
        (TokenType.COMMENT, re.compile(r'/\*.*?\*/', re.DOTALL)),
        
        # Multi-character operators (must come before single-character ones)
        (TokenType.POWER_ASSIGN, re.compile(r'\*\*=')),   # Must come before **
        (TokenType.POWER, re.compile(r'\*\*')),
        (TokenType.PLUS_ASSIGN, re.compile(r'\+=')),
        (TokenType.MINUS_ASSIGN, re.compile(r'-=')),
        (TokenType.MULTIPLY_ASSIGN, re.compile(r'\*=')),
        (TokenType.DIVIDE_ASSIGN, re.compile(r'/=')),
        (TokenType.MODULO_ASSIGN, re.compile(r'%=')),
        (TokenType.EQUAL, re.compile(r'==')),
        (TokenType.NOT_EQUAL, re.compile(r'!=')),
        (TokenType.LESS_EQUAL, re.compile(r'<=')),
        (TokenType.GREATER_EQUAL, re.compile(r'>=')),
        (TokenType.AND, re.compile(r'&&')),
        (TokenType.OR, re.compile(r'\|\|')),
        (TokenType.LEFT_SHIFT, re.compile(r'<<')),
        (TokenType.RIGHT_SHIFT, re.compile(r'>>')),
        (TokenType.ARROW, re.compile(r'=>')),
        (TokenType.OPTIONAL_CHAIN, re.compile(r'\?\.')),
        (TokenType.NULL_COALESCE, re.compile(r'\?\?')),
        (TokenType.SPREAD, re.compile(r'\.\.\.')),
        (TokenType.ELLIPSIS, re.compile(r'\.\.\.')),
        
        # String literals
        (TokenType.F_STRING, re.compile(r'f"(?:[^"\\]|\\.)*"')),  # F-string with double quotes
        (TokenType.F_STRING, re.compile(r"f'(?:[^'\\]|\\.)*'")),  # F-string with single quotes
        (TokenType.TEMPLATE_LITERAL, re.compile(r'`(?:[^`\\]|\\.)*`')),  # Template literals
        (TokenType.STRING, re.compile(r'"(?:[^"\\]|\\.)*"')),
        (TokenType.STRING, re.compile(r"'(?:[^'\\]|\\.)*'")),
        
        # Number literals (order matters - most specific first)
        (TokenType.NUMBER, re.compile(r'0[bB][01]+(?:\.[01]+)?(?:[eE][+-]?\d+)?')),  # Binary
        (TokenType.NUMBER, re.compile(r'0[oO][0-7]+(?:\.[0-7]+)?(?:[eE][+-]?\d+)?')),  # Octal
        (TokenType.NUMBER, re.compile(r'0[xX][0-9a-fA-F]+(?:\.[0-9a-fA-F]+)?(?:[eE][+-]?\d+)?')),  # Hex
        (TokenType.NUMBER, re.compile(r'\d+\.\d+(?:[eE][+-]?\d+)?')),  # Float with optional scientific
        (TokenType.NUMBER, re.compile(r'\d+\.(?:[eE][+-]?\d+)?')),     # Float ending with dot
        (TokenType.NUMBER, re.compile(r'\.\d+(?:[eE][+-]?\d+)?')),     # Float starting with dot
        (TokenType.NUMBER, re.compile(r'\d+[eE][+-]?\d+')),            # Scientific notation
        (TokenType.NUMBER, re.compile(r'\d+')),                       # Integer
        
        # Identifiers (must come after keywords check)
        (TokenType.IDENTIFIER, re.compile(r'[a-zA-Z_][a-zA-Z0-9_]*')),
        
        # Single-character operators and punctuation
        (TokenType.PLUS, re.compile(r'\+')),
        (TokenType.MINUS, re.compile(r'-')),
        (TokenType.MULTIPLY, re.compile(r'\*')),
        (TokenType.DIVIDE, re.compile(r'/')),
        (TokenType.MODULO, re.compile(r'%')),
        (TokenType.ASSIGN, re.compile(r'=')),
        (TokenType.LESS_THAN, re.compile(r'<')),
        (TokenType.GREATER_THAN, re.compile(r'>')),
        (TokenType.NOT, re.compile(r'!')),
        (TokenType.BIT_AND, re.compile(r'&')),
        (TokenType.BIT_OR, re.compile(r'\|')),
        (TokenType.BIT_XOR, re.compile(r'\^')),
        (TokenType.BIT_NOT, re.compile(r'~')),
        (TokenType.LEFT_PAREN, re.compile(r'\(')),
        (TokenType.RIGHT_PAREN, re.compile(r'\)')),
        (TokenType.LEFT_BRACE, re.compile(r'\{')),
        (TokenType.RIGHT_BRACE, re.compile(r'\}')),
        (TokenType.LEFT_BRACKET, re.compile(r'\[')),
        (TokenType.RIGHT_BRACKET, re.compile(r'\]')),
        (TokenType.SEMICOLON, re.compile(r';')),
        (TokenType.COMMA, re.compile(r',')),
        (TokenType.DOT, re.compile(r'\.')),
        (TokenType.COLON, re.compile(r':')),
        (TokenType.QUESTION, re.compile(r'\?')),
        
        # Whitespace and newlines
        (TokenType.NEWLINE, re.compile(r'\n')),
        (TokenType.WHITESPACE, re.compile(r'[ \t\r]+')),
    ]
    
    def __init__(self, source: str, filename: str = ""):
        self.source = source
        self.filename = filename
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
        self.current_token_index = 0
    
    def tokenize(self) -> List[Token]:
        """Tokenize the entire source code"""
        self.tokens = []
        self.position = 0
        self.line = 1
        self.column = 1
        
        while self.position < len(self.source):
            # Skip whitespace (but track position)
            if self._match_whitespace():
                continue
                
            # Try to match each token pattern
            token = self._next_token()
            if token:
                # Skip comments in the token stream (but preserve them for LSP)
                if token.type != TokenType.COMMENT:
                    self.tokens.append(token)
            else:
                # Unknown character
                location = SourceLocation(self.line, self.column, self.filename)
                char = self.source[self.position] if self.position < len(self.source) else 'EOF'
                raise LexerError(f"Unexpected character: '{char}'", location)
        
        # Add EOF token
        eof_location = SourceLocation(self.line, self.column, self.filename)
        self.tokens.append(Token(TokenType.EOF, "", eof_location))
        
        return self.tokens
    
    def _next_token(self) -> Optional[Token]:
        """Get the next token from the source"""
        if self.position >= len(self.source):
            return None
        
        location = SourceLocation(self.line, self.column, self.filename)
        
        # Try each token pattern
        for token_type, pattern in self.TOKEN_PATTERNS:
            match = pattern.match(self.source, self.position)
            if match:
                value = match.group(0)
                
                # Handle identifiers that might be keywords
                if token_type == TokenType.IDENTIFIER and value in self.KEYWORDS:
                    token_type = self.KEYWORDS[value]
                
                # Create token
                token = Token(token_type, value, location, value)
                
                # Update position
                self._advance_position(value)
                
                return token
        
        return None
    
    def _match_whitespace(self) -> bool:
        """Match and skip whitespace, updating position"""
        if self.position >= len(self.source):
            return False
        
        char = self.source[self.position]
        if char in ' \t\r':
            self.column += 1
            self.position += 1
            return True
        elif char == '\n':
            self.line += 1
            self.column = 1
            self.position += 1
            return True
        
        return False
    
    def _advance_position(self, text: str):
        """Advance position and update line/column counters"""
        for char in text:
            if char == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            self.position += 1
    
    def get_tokens(self) -> List[Token]:
        """Get all tokens (must call tokenize first)"""
        return self.tokens
    
    def peek(self, offset: int = 0) -> Token:
        """Peek at token at current position + offset"""
        index = self.current_token_index + offset
        if index >= len(self.tokens):
            return self.tokens[-1]  # EOF token
        return self.tokens[index]
    
    def advance(self) -> Token:
        """Advance to next token and return current"""
        token = self.peek()
        if self.current_token_index < len(self.tokens) - 1:
            self.current_token_index += 1
        return token
    
    def is_at_end(self) -> bool:
        """Check if we're at the end of tokens"""
        return self.current_token_index >= len(self.tokens) - 1 or self.peek().type == TokenType.EOF
    
    def reset(self):
        """Reset token position to beginning"""
        self.current_token_index = 0