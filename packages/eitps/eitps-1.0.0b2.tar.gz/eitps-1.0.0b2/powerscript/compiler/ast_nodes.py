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

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Union, Tuple
from dataclasses import dataclass
from enum import Enum


class NodeType(Enum):
    """AST Node types"""
    CLASS = "class"
    ENUM = "enum"
    FUNCTION = "function"
    CONSTRUCTOR = "constructor"
    VARIABLE = "variable"
    EXPRESSION = "expression"
    BLOCK = "block"
    PARAMETER = "parameter"
    IDENTIFIER = "identifier"
    LITERAL = "literal"
    ARRAY_LITERAL = "array_literal"
    OBJECT_LITERAL = "object_literal"
    SET_LITERAL = "set_literal"
    CALL = "call"
    ASSIGNMENT = "assignment"
    BINARY_OP = "binary_op"
    UNARY_OP = "unary_op"
    AWAIT = "await"
    RETURN = "return"
    IF = "if"
    WHILE = "while"
    FOR = "for"
    TRY = "try"
    CATCH = "catch"
    FINALLY = "finally"
    THROW = "throw"
    LAMBDA = "lambda"
    WITH = "with"
    YIELD = "yield"
    COMPREHENSION = "comprehension"
    GENERATOR = "generator"
    SLICE = "slice"
    ELLIPSIS = "ellipsis"
    F_STRING = "f_string"
    SWITCH = "switch"
    CASE = "case"
    BREAK = "break"
    CONTINUE = "continue"
    TEMPLATE_LITERAL = "template_literal"
    IMPORT = "import"
    EXPORT = "export"
    DESTRUCTURING = "destructuring"
    SPREAD = "spread"
    UNION_TYPE = "union_type"
    INTERSECTION_TYPE = "intersection_type"
    LITERAL_TYPE = "literal_type"
    GENERIC_CONSTRAINT = "generic_constraint"
    TYPE_ALIAS = "type_alias"
    GENERIC_TYPE = "generic_type"
    OBJECT_TYPE = "object_type"
    OPTIONAL_TYPE = "optional_type"


class AccessModifier(Enum):
    """Access modifier types"""
    PUBLIC = "public"
    PRIVATE = "private"
    PROTECTED = "protected"


@dataclass
class SourceLocation:
    """Source code location information"""
    line: int
    column: int
    filename: str = ""


class ASTNode(ABC):
    """Base class for all AST nodes"""
    
    def __init__(self, node_type: NodeType, location: Optional[SourceLocation] = None):
        self.node_type = node_type
        self.location = location
        self.parent: Optional['ASTNode'] = None
        self.children: List['ASTNode'] = []
    
    @abstractmethod
    def accept(self, visitor):
        """Accept a visitor for the visitor pattern"""
        pass
    
    def add_child(self, child: 'ASTNode'):
        """Add a child node"""
        child.parent = self
        self.children.append(child)
    
    def get_children(self) -> List['ASTNode']:
        """Get all child nodes"""
        return self.children.copy()


class ClassNode(ASTNode):
    """AST node for class declarations"""
    
    def __init__(self, name: str, base_classes: List[str] = None, 
                 generic_params: List[str] = None, location: Optional[SourceLocation] = None):
        super().__init__(NodeType.CLASS, location)
        self.name = name
        self.base_classes = base_classes or []
        self.generic_params = generic_params or []
        self.constructor: Optional['FunctionNode'] = None
        self.methods: List['FunctionNode'] = []
        self.fields: List['VariableNode'] = []
    
    def accept(self, visitor):
        return visitor.visit_class(self)


class EnumNode(ASTNode):
    """AST node for enum declarations"""
    
    def __init__(self, name: str, values: List[str], location: Optional[SourceLocation] = None):
        super().__init__(NodeType.ENUM, location)
        self.name = name
        self.values = values
    
    def accept(self, visitor):
        return visitor.visit_enum(self)


class FunctionNode(ASTNode):
    """AST node for function declarations"""
    
    def __init__(self, name: str, parameters: List['ParameterNode'] = None,
                 return_type: Optional[str] = None, is_async: bool = False,
                 access_modifier: AccessModifier = AccessModifier.PUBLIC,
                 is_constructor: bool = False, is_generator: bool = False,
                 location: Optional[SourceLocation] = None):
        super().__init__(NodeType.CONSTRUCTOR if is_constructor else NodeType.FUNCTION, location)
        self.name = name
        self.parameters = parameters or []
        self.return_type = return_type
        self.is_async = is_async
        self.access_modifier = access_modifier
        self.is_constructor = is_constructor
        self.is_generator = is_generator
        self.body: Optional['BlockNode'] = None
        self.generic_params: List[str] = []
    
    def accept(self, visitor):
        return visitor.visit_function(self)


class ParameterNode(ASTNode):
    """AST node for function parameters"""
    
    def __init__(self, name: str, param_type: Optional['ExpressionNode'] = None,
                 default_value: Optional['ExpressionNode'] = None,
                 location: Optional[SourceLocation] = None):
        super().__init__(NodeType.PARAMETER, location)
        self.name = name
        self.param_type = param_type
        self.default_value = default_value
    
    def accept(self, visitor):
        return visitor.visit_parameter(self)


class VariableNode(ASTNode):
    """AST node for variable declarations"""
    
    def __init__(self, name: str, var_type: Optional['ExpressionNode'] = None,
                 initializer: Optional['ExpressionNode'] = None,
                 is_const: bool = False, access_modifier: AccessModifier = AccessModifier.PUBLIC,
                 location: Optional[SourceLocation] = None):
        super().__init__(NodeType.VARIABLE, location)
        self.name = name
        self.var_type = var_type
        self.initializer = initializer
        self.is_const = is_const
        self.access_modifier = access_modifier
    
    def accept(self, visitor):
        return visitor.visit_variable(self)


class ExpressionNode(ASTNode):
    """Base class for expression nodes"""
    
    def __init__(self, node_type: NodeType = NodeType.EXPRESSION, location: Optional[SourceLocation] = None):
        super().__init__(node_type, location)


class ExpressionStatementNode(ASTNode):
    """AST node for expression statements"""
    
    def __init__(self, expression: ExpressionNode, location: Optional[SourceLocation] = None):
        super().__init__(NodeType.EXPRESSION, location)  # Using EXPRESSION for now
        self.expression = expression
    
    def accept(self, visitor):
        return visitor.visit_expression_statement(self)


class IdentifierNode(ExpressionNode):
    """AST node for identifiers"""
    
    def __init__(self, name: str, location: Optional[SourceLocation] = None):
        super().__init__(NodeType.IDENTIFIER, location)
        self.name = name
    
    def accept(self, visitor):
        return visitor.visit_identifier(self)


class LiteralNode(ExpressionNode):
    """AST node for literal values"""
    
    def __init__(self, value: Any, literal_type: str, location: Optional[SourceLocation] = None):
        super().__init__(NodeType.LITERAL, location)
        self.value = value
        self.literal_type = literal_type  # "string", "number", "boolean", "null"
    
    def accept(self, visitor):
        return visitor.visit_literal(self)


class ArrayLiteralNode(ExpressionNode):
    """AST node for array literals [1, 2, 3]"""
    
    def __init__(self, elements: List[ExpressionNode], location: Optional[SourceLocation] = None):
        super().__init__(NodeType.ARRAY_LITERAL, location)
        self.elements = elements
    
    def accept(self, visitor):
        return visitor.visit_array_literal(self)


class ObjectLiteralNode(ExpressionNode):
    """AST node for object literals {key: value, ...}"""
    
    def __init__(self, properties: List[Tuple[ExpressionNode, ExpressionNode]], 
                 location: Optional[SourceLocation] = None):
        super().__init__(NodeType.OBJECT_LITERAL, location)
        self.properties = properties  # List of (key, value) pairs
    
    def accept(self, visitor):
        return visitor.visit_object_literal(self)


class SetLiteralNode(ExpressionNode):
    """AST node for set literals {1, 2, 3}"""
    
    def __init__(self, elements: List[ExpressionNode], location: Optional[SourceLocation] = None):
        super().__init__(NodeType.SET_LITERAL, location)
        self.elements = elements
    
    def accept(self, visitor):
        return visitor.visit_set_literal(self)


class FStringNode(ExpressionNode):
    """AST node for f-string literals f"Hello {name}!" """
    
    def __init__(self, value: str, expressions: List[ExpressionNode] = None, location: Optional[SourceLocation] = None):
        super().__init__(NodeType.F_STRING, location)
        self.value = value  # Original f-string with placeholders
        self.expressions = expressions or []  # Parsed expressions from {expr}
    
    def accept(self, visitor):
        return visitor.visit_f_string(self)


class CallNode(ExpressionNode):
    """AST node for function calls"""
    
    def __init__(self, callee: ExpressionNode, arguments: List[ExpressionNode] = None,
                 location: Optional[SourceLocation] = None):
        super().__init__(NodeType.CALL, location)
        self.callee = callee
        self.arguments = arguments or []
    
    def accept(self, visitor):
        return visitor.visit_call(self)


class BinaryOpNode(ExpressionNode):
    """AST node for binary operations"""
    
    def __init__(self, left: ExpressionNode, operator: str, right: ExpressionNode,
                 location: Optional[SourceLocation] = None):
        super().__init__(NodeType.BINARY_OP, location)
        self.left = left
        self.operator = operator
        self.right = right
    
    def accept(self, visitor):
        return visitor.visit_binary_op(self)


class UnaryOpNode(ExpressionNode):
    """AST node for unary operations"""
    
    def __init__(self, operator: str, operand: ExpressionNode,
                 location: Optional[SourceLocation] = None):
        super().__init__(NodeType.UNARY_OP, location)
        self.operator = operator
        self.operand = operand
    
    def accept(self, visitor):
        return visitor.visit_unary_op(self)


class AwaitNode(ExpressionNode):
    """AST node for await expressions"""
    
    def __init__(self, expression: ExpressionNode, location: Optional[SourceLocation] = None):
        super().__init__(NodeType.AWAIT, location)
        self.expression = expression
    
    def accept(self, visitor):
        return visitor.visit_await(self)


class AssignmentNode(ExpressionNode):
    """AST node for assignments"""
    
    def __init__(self, target: ExpressionNode, value: ExpressionNode,
                 location: Optional[SourceLocation] = None, operator: str = "="):
        super().__init__(NodeType.ASSIGNMENT, location)
        self.target = target
        self.value = value
        self.operator = operator
    
    def accept(self, visitor):
        return visitor.visit_assignment(self)


class BlockNode(ASTNode):
    """AST node for code blocks"""
    
    def __init__(self, statements: List[ASTNode] = None, location: Optional[SourceLocation] = None):
        super().__init__(NodeType.BLOCK, location)
        self.statements = statements or []
    
    def accept(self, visitor):
        return visitor.visit_block(self)


class ReturnNode(ASTNode):
    """AST node for return statements"""
    
    def __init__(self, value: Optional[ExpressionNode] = None, location: Optional[SourceLocation] = None):
        super().__init__(NodeType.RETURN, location)
        self.value = value
    
    def accept(self, visitor):
        return visitor.visit_return(self)


class IfNode(ASTNode):
    """AST node for if statements"""
    
    def __init__(self, condition: ExpressionNode, then_block: BlockNode,
                 else_block: Optional[BlockNode] = None, location: Optional[SourceLocation] = None):
        super().__init__(NodeType.IF, location)
        self.condition = condition
        self.then_block = then_block
        self.else_block = else_block
    
    def accept(self, visitor):
        return visitor.visit_if(self)


class WhileNode(ASTNode):
    """AST node for while loops"""
    
    def __init__(self, condition: ExpressionNode, body: BlockNode,
                 location: Optional[SourceLocation] = None):
        super().__init__(NodeType.WHILE, location)
        self.condition = condition
        self.body = body
    
    def accept(self, visitor):
        return visitor.visit_while(self)


class ForNode(ASTNode):
    """AST node for for loops"""
    
    def __init__(self, variable: str, iterable: ExpressionNode, body: BlockNode,
                 location: Optional[SourceLocation] = None):
        super().__init__(NodeType.FOR, location)
        self.variable = variable
        self.iterable = iterable
        self.body = body
    
    def accept(self, visitor):
        return visitor.visit_for(self)


class SwitchNode(ASTNode):
    """AST node for switch statements"""
    
    def __init__(self, expression: ExpressionNode, cases: List['CaseNode'], 
                 default_case: Optional['CaseNode'] = None, location: Optional[SourceLocation] = None):
        super().__init__(NodeType.SWITCH, location)
        self.expression = expression
        self.cases = cases
        self.default_case = default_case
    
    def accept(self, visitor):
        return visitor.visit_switch(self)


class CaseNode(ASTNode):
    """AST node for case clauses in switch statements"""
    
    def __init__(self, values: List[ExpressionNode], body: BlockNode, 
                 is_default: bool = False, location: Optional[SourceLocation] = None):
        super().__init__(NodeType.CASE, location)
        self.values = values  # For case 1, 2, 3: multiple values
        self.body = body
        self.is_default = is_default  # True for default case
    
    def accept(self, visitor):
        return visitor.visit_case(self)


class BreakNode(ASTNode):
    """AST node for break statements"""
    
    def __init__(self, location: Optional[SourceLocation] = None):
        super().__init__(NodeType.BREAK, location)
    
    def accept(self, visitor):
        return visitor.visit_break(self)


class ContinueNode(ASTNode):
    """AST node for continue statements"""
    
    def __init__(self, location: Optional[SourceLocation] = None):
        super().__init__(NodeType.CONTINUE, location)
    
    def accept(self, visitor):
        return visitor.visit_continue(self)


class TemplateLiteralNode(ExpressionNode):
    """AST node for template literals `Hello ${name}!`"""
    
    def __init__(self, value: str, expressions: List[ExpressionNode] = None, location: Optional[SourceLocation] = None):
        super().__init__(NodeType.TEMPLATE_LITERAL, location)
        self.value = value  # Original template with placeholders
        self.expressions = expressions or []  # Parsed expressions from ${expr}
    
    def accept(self, visitor):
        return visitor.visit_template_literal(self)


class ImportNode(ASTNode):
    """AST node for import statements"""
    
    def __init__(self, module_name: str, specifiers: List['ImportSpecifier'] = None, 
                 is_default_import: bool = False, location: Optional[SourceLocation] = None):
        super().__init__(NodeType.IMPORT, location)
        self.module_name = module_name
        self.specifiers = specifiers or []  # Named imports: { name1, name2 }
        self.is_default_import = is_default_import  # import defaultName from "module"
    
    def accept(self, visitor):
        return visitor.visit_import(self)


class ImportSpecifier:
    """Import specifier for named imports"""
    
    def __init__(self, imported_name: str, local_name: Optional[str] = None):
        self.imported_name = imported_name  # Original name in module
        self.local_name = local_name or imported_name  # Local alias


class ExportNode(ASTNode):
    """AST node for export statements"""
    
    def __init__(self, declaration: Optional[ASTNode] = None, specifiers: List['ExportSpecifier'] = None,
                 is_default: bool = False, location: Optional[SourceLocation] = None):
        super().__init__(NodeType.EXPORT, location)
        self.declaration = declaration  # export class/function/etc
        self.specifiers = specifiers or []  # export { name1, name2 }
        self.is_default = is_default  # export default
    
    def accept(self, visitor):
        return visitor.visit_export(self)


class ExportSpecifier:
    """Export specifier for named exports"""
    
    def __init__(self, local_name: str, exported_name: Optional[str] = None):
        self.local_name = local_name  # Local name
        self.exported_name = exported_name or local_name  # Exported alias


class DestructuringNode(ASTNode):
    """AST node for destructuring assignment: let {x, y} = obj or let [a, b] = arr"""
    
    def __init__(self, pattern: 'DestructuringPattern', value: ExpressionNode, 
                 location: Optional[SourceLocation] = None):
        super().__init__(NodeType.DESTRUCTURING, location)
        self.pattern = pattern  # Array or object pattern
        self.value = value      # Expression being destructured
    
    def accept(self, visitor):
        return visitor.visit_destructuring(self)


class DestructuringPattern:
    """Base class for destructuring patterns"""
    pass


class ArrayPattern(DestructuringPattern):
    """Array destructuring pattern: [a, b, ...rest]"""
    
    def __init__(self, elements: List[Optional[str]], rest: Optional[str] = None):
        self.elements = elements  # Variable names, None for holes
        self.rest = rest         # Rest parameter name


class ObjectPattern(DestructuringPattern):
    """Object destructuring pattern: {x, y: newName, ...rest}"""
    
    def __init__(self, properties: List['ObjectPatternProperty'], rest: Optional[str] = None):
        self.properties = properties
        self.rest = rest


class ObjectPatternProperty:
    """Property in object destructuring pattern"""
    
    def __init__(self, key: str, value: Optional[str] = None):
        self.key = key      # Property key
        self.value = value or key  # Local variable name


class SpreadNode(ExpressionNode):
    """AST node for spread operator: ...array"""
    
    def __init__(self, expression: ExpressionNode, location: Optional[SourceLocation] = None):
        super().__init__(NodeType.SPREAD, location)
        self.expression = expression
    
    def accept(self, visitor):
        return visitor.visit_spread(self)


class TryNode(ASTNode):
    """Try-catch-finally statement node"""
    
    def __init__(self, try_block: BlockNode, catch_clauses: List['CatchNode'] = None, 
                 finally_block: Optional[BlockNode] = None, location: Optional[SourceLocation] = None):
        super().__init__(NodeType.TRY, location)
        self.try_block = try_block
        self.catch_clauses = catch_clauses or []
        self.finally_block = finally_block
    
    def accept(self, visitor):
        return visitor.visit_try(self)


class CatchNode(ASTNode):
    """Catch clause node"""
    
    def __init__(self, exception_name: Optional[str], exception_type: Optional[str], 
                 body: BlockNode, location: Optional[SourceLocation] = None):
        super().__init__(NodeType.CATCH, location)
        self.exception_name = exception_name  # Variable name to bind exception to
        self.exception_type = exception_type  # Optional type filter
        self.body = body
    
    def accept(self, visitor):
        return visitor.visit_catch(self)


class ThrowNode(ASTNode):
    """Throw statement node"""
    
    def __init__(self, expression: ExpressionNode, location: Optional[SourceLocation] = None):
        super().__init__(NodeType.THROW, location)
        self.expression = expression
    
    def accept(self, visitor):
        return visitor.visit_throw(self)


class LambdaNode(ExpressionNode):
    """Lambda expression node"""
    
    def __init__(self, parameters: List[ParameterNode], body: ExpressionNode, 
                 location: Optional[SourceLocation] = None):
        super().__init__(NodeType.LAMBDA, location)
        self.parameters = parameters or []
        self.body = body
    
    def accept(self, visitor):
        return visitor.visit_lambda(self)


class WithNode(ASTNode):
    """Context manager (with statement) node"""
    
    def __init__(self, context_expr: ExpressionNode, optional_vars: Optional[IdentifierNode],
                 body: BlockNode, location: Optional[SourceLocation] = None):
        super().__init__(NodeType.WITH, location)
        self.context_expr = context_expr
        self.optional_vars = optional_vars
        self.body = body
    
    def accept(self, visitor):
        return visitor.visit_with(self)


class YieldNode(ExpressionNode):
    """Yield expression node for generators"""
    
    def __init__(self, value: Optional[ExpressionNode] = None, 
                 is_yield_from: bool = False,
                 location: Optional[SourceLocation] = None):
        super().__init__(NodeType.YIELD, location)
        self.value = value
        self.is_yield_from = is_yield_from
    
    def accept(self, visitor):
        return visitor.visit_yield(self)


class ComprehensionNode(ExpressionNode):
    """List/Dict/Set comprehension node"""
    
    def __init__(self, expr: ExpressionNode, target: IdentifierNode, 
                 iterable: ExpressionNode, conditions: List[ExpressionNode] = None,
                 comp_type: str = "list", location: Optional[SourceLocation] = None):
        super().__init__(NodeType.COMPREHENSION, location)
        self.expr = expr
        self.target = target
        self.iterable = iterable
        self.conditions = conditions or []
        self.comp_type = comp_type  # "list", "dict", "set"
    
    def accept(self, visitor):
        return visitor.visit_comprehension(self)


class SliceNode(ExpressionNode):
    """Slice expression node (obj[start:end:step])"""
    
    def __init__(self, object_expr: ExpressionNode, lower: Optional[ExpressionNode] = None,
                 upper: Optional[ExpressionNode] = None, step: Optional[ExpressionNode] = None,
                 location: Optional[SourceLocation] = None):
        super().__init__(NodeType.SLICE, location)
        self.object_expr = object_expr
        self.lower = lower
        self.upper = upper
        self.step = step
    
    def accept(self, visitor):
        return visitor.visit_slice(self)


class EllipsisNode(ExpressionNode):
    """Ellipsis (...) node"""
    
    def __init__(self, location: Optional[SourceLocation] = None):
        super().__init__(NodeType.ELLIPSIS, location)
    
    def accept(self, visitor):
        return visitor.visit_ellipsis(self)


class UnionTypeNode(ExpressionNode):
    """Union type node (A | B)"""
    
    def __init__(self, types: List[ExpressionNode], location: Optional[SourceLocation] = None):
        super().__init__(NodeType.UNION_TYPE, location)
        self.types = types
    
    def accept(self, visitor):
        return visitor.visit_union_type(self)


class IntersectionTypeNode(ExpressionNode):
    """Intersection type node (A & B)"""
    
    def __init__(self, types: List[ExpressionNode], location: Optional[SourceLocation] = None):
        super().__init__(NodeType.INTERSECTION_TYPE, location)
        self.types = types
    
    def accept(self, visitor):
        return visitor.visit_intersection_type(self)


class LiteralTypeNode(ExpressionNode):
    """Literal type node (e.g., "hello" | 42 | true)"""
    
    def __init__(self, value: Any, location: Optional[SourceLocation] = None):
        super().__init__(NodeType.LITERAL_TYPE, location)
        self.value = value
    
    def accept(self, visitor):
        return visitor.visit_literal_type(self)


class GenericConstraintNode(ExpressionNode):
    """Generic constraint node (T extends U)"""
    
    def __init__(self, type_param: str, constraint: ExpressionNode, 
                 location: Optional[SourceLocation] = None):
        super().__init__(NodeType.GENERIC_CONSTRAINT, location)
        self.type_param = type_param
        self.constraint = constraint
    
    def accept(self, visitor):
        return visitor.visit_generic_constraint(self)


class TypeAliasNode(ASTNode):
    """Type alias node (type MyType = string | number)"""
    
    def __init__(self, name: str, type_expr: ExpressionNode, 
                 location: Optional[SourceLocation] = None):
        super().__init__(NodeType.TYPE_ALIAS, location)
        self.name = name
        self.type_expr = type_expr
    
    def accept(self, visitor):
        return visitor.visit_type_alias(self)


class GenericTypeNode(ExpressionNode):
    """Generic type node (e.g., Array<T>, Dict<K,V>)"""
    
    def __init__(self, base_type: str, type_args: List[ExpressionNode], 
                 location: Optional[SourceLocation] = None):
        super().__init__(NodeType.GENERIC_TYPE, location)
        self.base_type = base_type
        self.type_args = type_args
    
    def accept(self, visitor):
        return visitor.visit_generic_type(self)


class ObjectTypeNode(ExpressionNode):
    """Object type node (e.g., {name: string, age: number})"""
    
    def __init__(self, properties: Dict[str, ExpressionNode], 
                 location: Optional[SourceLocation] = None):
        super().__init__(NodeType.OBJECT_TYPE, location)
        self.properties = properties
    
    def accept(self, visitor):
        return visitor.visit_object_type(self)


class OptionalTypeNode(ExpressionNode):
    """Optional type node (e.g., T?)"""
    
    def __init__(self, type_expr: ExpressionNode, 
                 location: Optional[SourceLocation] = None):
        super().__init__(NodeType.OPTIONAL_TYPE, location)
        self.type_expr = type_expr
    
    def accept(self, visitor):
        return visitor.visit_optional_type(self)


# Visitor interface
class ASTVisitor(ABC):
    """Abstract base class for AST visitors"""
    
    @abstractmethod
    def visit_class(self, node: ClassNode): pass
    
    @abstractmethod  
    def visit_function(self, node: FunctionNode): pass
    
    @abstractmethod
    def visit_parameter(self, node: ParameterNode): pass
    
    @abstractmethod
    def visit_variable(self, node: VariableNode): pass
    
    @abstractmethod
    def visit_identifier(self, node: IdentifierNode): pass
    
    @abstractmethod
    def visit_literal(self, node: LiteralNode): pass
    
    @abstractmethod
    def visit_array_literal(self, node: ArrayLiteralNode): pass
    
    @abstractmethod
    def visit_object_literal(self, node: ObjectLiteralNode): pass
    
    @abstractmethod
    def visit_set_literal(self, node: SetLiteralNode): pass
    
    @abstractmethod
    def visit_call(self, node: CallNode): pass
    
    @abstractmethod
    def visit_binary_op(self, node: BinaryOpNode): pass
    
    @abstractmethod
    def visit_unary_op(self, node: UnaryOpNode): pass
    
    @abstractmethod
    def visit_await(self, node: AwaitNode): pass
    
    @abstractmethod
    def visit_assignment(self, node: AssignmentNode): pass
    
    @abstractmethod
    def visit_block(self, node: BlockNode): pass
    
    @abstractmethod
    def visit_return(self, node: ReturnNode): pass
    
    @abstractmethod
    def visit_if(self, node: IfNode): pass
    
    @abstractmethod
    def visit_while(self, node: WhileNode): pass
    
    @abstractmethod
    def visit_for(self, node: ForNode): pass
    
    @abstractmethod
    def visit_try(self, node: TryNode): pass
    
    @abstractmethod
    def visit_catch(self, node: CatchNode): pass
    
    @abstractmethod
    def visit_throw(self, node: ThrowNode): pass
    
    @abstractmethod
    def visit_lambda(self, node: LambdaNode): pass
    
    @abstractmethod
    def visit_with(self, node: WithNode): pass
    
    @abstractmethod
    def visit_yield(self, node: YieldNode): pass
    
    @abstractmethod
    def visit_comprehension(self, node: ComprehensionNode): pass
    
    @abstractmethod
    def visit_slice(self, node: SliceNode): pass
    
    @abstractmethod
    def visit_ellipsis(self, node: EllipsisNode): pass
    
    @abstractmethod
    def visit_switch(self, node: SwitchNode): pass
    
    @abstractmethod
    def visit_case(self, node: CaseNode): pass
    
    @abstractmethod
    def visit_break(self, node: BreakNode): pass
    
    @abstractmethod
    def visit_continue(self, node: ContinueNode): pass
    
    @abstractmethod
    def visit_template_literal(self, node: TemplateLiteralNode): pass
    
    @abstractmethod
    def visit_import(self, node: ImportNode): pass
    
    @abstractmethod
    def visit_export(self, node: ExportNode): pass
    
    @abstractmethod
    def visit_destructuring(self, node: DestructuringNode): pass
    
    @abstractmethod
    def visit_spread(self, node: SpreadNode): pass
    
    @abstractmethod
    def visit_union_type(self, node: UnionTypeNode): pass
    
    @abstractmethod
    def visit_intersection_type(self, node: IntersectionTypeNode): pass
    
    @abstractmethod
    def visit_literal_type(self, node: LiteralTypeNode): pass
    
    @abstractmethod
    def visit_generic_constraint(self, node: GenericConstraintNode): pass
    
    @abstractmethod
    def visit_type_alias(self, node: TypeAliasNode): pass
    
    @abstractmethod
    def visit_generic_type(self, node: GenericTypeNode): pass
    
    @abstractmethod
    def visit_object_type(self, node: ObjectTypeNode): pass
    
    @abstractmethod
    def visit_optional_type(self, node: OptionalTypeNode): pass