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

from typing import List, Optional, Dict, Any, Union
from .ast_nodes import *
from .lexer import TokenType


# Additional AST Nodes for Missing Features

class IfElseNode(ASTNode):
    """Enhanced if-else statement with multiple conditions"""
    
    def __init__(self, conditions: List[ExpressionNode], bodies: List[BlockNode], 
                 else_body: Optional[BlockNode] = None, location: Optional[SourceLocation] = None):
        super().__init__(NodeType.IF, location)
        self.conditions = conditions  # List for if/else-if conditions
        self.bodies = bodies         # Corresponding bodies
        self.else_body = else_body   # Optional else body
    
    def accept(self, visitor):
        return visitor.visit_if_else(self)


class SwitchNode(ASTNode):
    """Switch/case statement"""
    
    def __init__(self, expression: ExpressionNode, cases: List['CaseNode'], 
                 default_case: Optional['CaseNode'] = None, location: Optional[SourceLocation] = None):
        super().__init__(NodeType.SWITCH, location)
        self.expression = expression
        self.cases = cases
        self.default_case = default_case
    
    def accept(self, visitor):
        return visitor.visit_switch(self)


class CaseNode(ASTNode):
    """Case clause in switch statement"""
    
    def __init__(self, values: List[ExpressionNode], body: BlockNode, 
                 location: Optional[SourceLocation] = None):
        super().__init__(NodeType.CASE, location)
        self.values = values  # Multiple values for case
        self.body = body
    
    def accept(self, visitor):
        return visitor.visit_case(self)


class BreakNode(ASTNode):
    """Break statement"""
    
    def __init__(self, label: Optional[str] = None, location: Optional[SourceLocation] = None):
        super().__init__(NodeType.BREAK, location)
        self.label = label  # Optional label for labeled breaks
    
    def accept(self, visitor):
        return visitor.visit_break(self)


class ContinueNode(ASTNode):
    """Continue statement"""
    
    def __init__(self, label: Optional[str] = None, location: Optional[SourceLocation] = None):
        super().__init__(NodeType.CONTINUE, location)
        self.label = label  # Optional label for labeled continues
    
    def accept(self, visitor):
        return visitor.visit_continue(self)


class ArrayLiteralNode(ExpressionNode):
    """Array literal expression [1, 2, 3]"""
    
    def __init__(self, elements: List[ExpressionNode], location: Optional[SourceLocation] = None):
        super().__init__(NodeType.ARRAY_LITERAL, location)
        self.elements = elements
    
    def accept(self, visitor):
        return visitor.visit_array_literal(self)


class ObjectLiteralNode(ExpressionNode):
    """Object literal expression {key: value, ...}"""
    
    def __init__(self, properties: List['PropertyNode'], location: Optional[SourceLocation] = None):
        super().__init__(NodeType.OBJECT_LITERAL, location)
        self.properties = properties
    
    def accept(self, visitor):
        return visitor.visit_object_literal(self)


class PropertyNode(ASTNode):
    """Property in object literal"""
    
    def __init__(self, key: Union[str, ExpressionNode], value: ExpressionNode, 
                 is_computed: bool = False, location: Optional[SourceLocation] = None):
        super().__init__(NodeType.PROPERTY, location)
        self.key = key
        self.value = value
        self.is_computed = is_computed  # true for [expr]: value
    
    def accept(self, visitor):
        return visitor.visit_property(self)


class TemplateLiteralNode(ExpressionNode):
    """Template literal with interpolation `Hello ${name}!`"""
    
    def __init__(self, parts: List[Union[str, ExpressionNode]], location: Optional[SourceLocation] = None):
        super().__init__(NodeType.TEMPLATE_LITERAL, location)
        self.parts = parts  # Alternating strings and expressions
    
    def accept(self, visitor):
        return visitor.visit_template_literal(self)


class ImportNode(ASTNode):
    """Import statement"""
    
    def __init__(self, specifiers: List['ImportSpecifier'], source: str, 
                 is_type_only: bool = False, location: Optional[SourceLocation] = None):
        super().__init__(NodeType.IMPORT, location)
        self.specifiers = specifiers
        self.source = source
        self.is_type_only = is_type_only
    
    def accept(self, visitor):
        return visitor.visit_import(self)


class ImportSpecifier:
    """Import specifier (imported name and optional alias)"""
    
    def __init__(self, imported: str, local: Optional[str] = None, is_default: bool = False):
        self.imported = imported  # Name in source module
        self.local = local or imported  # Local name (alias)
        self.is_default = is_default  # Default import


class ExportNode(ASTNode):
    """Export statement"""
    
    def __init__(self, declaration: Optional[ASTNode] = None, specifiers: List['ExportSpecifier'] = None,
                 source: Optional[str] = None, is_default: bool = False, location: Optional[SourceLocation] = None):
        super().__init__(NodeType.EXPORT, location)
        self.declaration = declaration  # export class/function/etc
        self.specifiers = specifiers or []  # export { name1, name2 }
        self.source = source  # export { name } from "module"
        self.is_default = is_default  # export default
    
    def accept(self, visitor):
        return visitor.visit_export(self)


class ExportSpecifier:
    """Export specifier"""
    
    def __init__(self, local: str, exported: Optional[str] = None):
        self.local = local  # Local name
        self.exported = exported or local  # Exported name


class SpreadNode(ExpressionNode):
    """Spread operator ...expr"""
    
    def __init__(self, argument: ExpressionNode, location: Optional[SourceLocation] = None):
        super().__init__(NodeType.SPREAD, location)
        self.argument = argument
    
    def accept(self, visitor):
        return visitor.visit_spread(self)


class DestructuringNode(ASTNode):
    """Destructuring assignment"""
    
    def __init__(self, pattern: 'DestructuringPattern', value: ExpressionNode, 
                 location: Optional[SourceLocation] = None):
        super().__init__(NodeType.DESTRUCTURING, location)
        self.pattern = pattern
        self.value = value
    
    def accept(self, visitor):
        return visitor.visit_destructuring(self)


class DestructuringPattern:
    """Base class for destructuring patterns"""
    pass


class ArrayPattern(DestructuringPattern):
    """Array destructuring pattern [a, b, ...rest]"""
    
    def __init__(self, elements: List[Optional[Union[str, 'DestructuringPattern']]], 
                 rest: Optional[str] = None):
        self.elements = elements
        self.rest = rest


class ObjectPattern(DestructuringPattern):
    """Object destructuring pattern {a, b: c, ...rest}"""
    
    def __init__(self, properties: List['ObjectPatternProperty'], rest: Optional[str] = None):
        self.properties = properties
        self.rest = rest


class ObjectPatternProperty:
    """Property in object destructuring pattern"""
    
    def __init__(self, key: str, value: Union[str, DestructuringPattern], default: Optional[ExpressionNode] = None):
        self.key = key
        self.value = value
        self.default = default


# Update NodeType enum to include new node types
class NodeType(Enum):
    """Extended AST Node types with all missing features"""
    # Existing types
    CLASS = "class"
    FUNCTION = "function"
    CONSTRUCTOR = "constructor"
    VARIABLE = "variable"
    EXPRESSION = "expression"
    BLOCK = "block"
    PARAMETER = "parameter"
    IDENTIFIER = "identifier"
    LITERAL = "literal"
    CALL = "call"
    ASSIGNMENT = "assignment"
    BINARY_OP = "binary_op"
    UNARY_OP = "unary_op"
    RETURN = "return"
    IF = "if"
    WHILE = "while"
    FOR = "for"
    TRY = "try"
    CATCH = "catch"
    FINALLY = "finally"
    THROW = "throw"
    
    # New missing features
    SWITCH = "switch"
    CASE = "case"
    BREAK = "break"
    CONTINUE = "continue"
    ARRAY_LITERAL = "array_literal"
    OBJECT_LITERAL = "object_literal"
    PROPERTY = "property"
    TEMPLATE_LITERAL = "template_literal"
    IMPORT = "import"
    EXPORT = "export"
    SPREAD = "spread"
    DESTRUCTURING = "destructuring"


# Extended ASTVisitor interface
class ExtendedASTVisitor(ASTVisitor):
    """Extended visitor interface with all missing features"""
    
    # Existing visitor methods...
    
    # New visitor methods for missing features
    @abstractmethod
    def visit_if_else(self, node: IfElseNode): pass
    
    @abstractmethod
    def visit_switch(self, node: SwitchNode): pass
    
    @abstractmethod
    def visit_case(self, node: CaseNode): pass
    
    @abstractmethod
    def visit_break(self, node: BreakNode): pass
    
    @abstractmethod
    def visit_continue(self, node: ContinueNode): pass
    
    @abstractmethod
    def visit_array_literal(self, node: ArrayLiteralNode): pass
    
    @abstractmethod
    def visit_object_literal(self, node: ObjectLiteralNode): pass
    
    @abstractmethod
    def visit_property(self, node: PropertyNode): pass
    
    @abstractmethod
    def visit_template_literal(self, node: TemplateLiteralNode): pass
    
    @abstractmethod
    def visit_import(self, node: ImportNode): pass
    
    @abstractmethod
    def visit_export(self, node: ExportNode): pass
    
    @abstractmethod
    def visit_spread(self, node: SpreadNode): pass
    
    @abstractmethod
    def visit_destructuring(self, node: DestructuringNode): pass