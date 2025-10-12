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

from typing import List, Dict, Set, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
from ..compiler.ast_nodes import *


class TypeErrorSeverity(Enum):
    """Severity levels for type errors"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class TypeCheckError:
    """Represents a type checking error"""
    message: str
    node: Optional[ASTNode]
    severity: TypeErrorSeverity
    line: int = 0
    column: int = 0
    
    def __post_init__(self):
        if self.node and self.node.location:
            self.line = self.node.location.line
            self.column = self.node.location.column


@dataclass
class TypeCheckResult:
    """Result of type checking"""
    errors: List[TypeCheckError]
    warnings: List[TypeCheckError]
    success: bool
    
    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0
    
    @property
    def has_warnings(self) -> bool:
        return len(self.warnings) > 0


class TypeEnvironment:
    """Type environment for variable and function types"""
    
    def __init__(self, parent: Optional['TypeEnvironment'] = None):
        self.parent = parent
        self.variables: Dict[str, str] = {}
        self.functions: Dict[str, Dict[str, Any]] = {}
        self.classes: Dict[str, Dict[str, Any]] = {}
    
    def define_variable(self, name: str, var_type: str):
        """Define a variable type"""
        self.variables[name] = var_type
    
    def get_variable_type(self, name: str) -> Optional[str]:
        """Get variable type"""
        if name in self.variables:
            return self.variables[name]
        if self.parent:
            return self.parent.get_variable_type(name)
        return None
    
    def define_function(self, name: str, params: List[str], return_type: str):
        """Define a function signature"""
        self.functions[name] = {
            'params': params,
            'return_type': return_type
        }
    
    def get_function_signature(self, name: str) -> Optional[Dict[str, Any]]:
        """Get function signature"""
        if name in self.functions:
            return self.functions[name]
        if self.parent:
            return self.parent.get_function_signature(name)
        return None
    
    def define_class(self, name: str, class_info: Dict[str, Any]):
        """Define a class"""
        self.classes[name] = class_info
    
    def get_class_info(self, name: str) -> Optional[Dict[str, Any]]:
        """Get class information"""
        if name in self.classes:
            return self.classes[name]
        if self.parent:
            return self.parent.get_class_info(name)
        return None
    
    def create_child(self) -> 'TypeEnvironment':
        """Create a child environment"""
        return TypeEnvironment(self)


class TypeChecker(ASTVisitor):
    """PowerScript type checker"""
    
    def __init__(self, strict_mode: bool = True):
        self.strict_mode = strict_mode
        self.errors: List[TypeCheckError] = []
        self.warnings: List[TypeCheckError] = []
        self.environment = TypeEnvironment()
        self.current_function_return_type: Optional[str] = None
        self.current_class: Optional[str] = None
        
        # Built-in types
        self._init_builtin_types()
    
    def _init_builtin_types(self):
        """Initialize built-in types"""
        builtins = {
            'print': {'params': ['any'], 'return_type': 'void'},
            'len': {'params': ['any'], 'return_type': 'number'},
            'str': {'params': ['any'], 'return_type': 'string'},
            'int': {'params': ['any'], 'return_type': 'number'},
            'float': {'params': ['any'], 'return_type': 'number'},
            'bool': {'params': ['any'], 'return_type': 'boolean'},
        }
        
        for name, signature in builtins.items():
            self.environment.define_function(name, signature['params'], signature['return_type'])
    
    def check(self, nodes: List[ASTNode]) -> TypeCheckResult:
        """Perform type checking on AST nodes"""
        self.errors = []
        self.warnings = []
        
        # First pass: collect class and function declarations
        for node in nodes:
            if isinstance(node, ClassNode):
                self._collect_class_declaration(node)
            elif isinstance(node, FunctionNode):
                self._collect_function_declaration(node)
        
        # Second pass: type check
        for node in nodes:
            node.accept(self)
        
        return TypeCheckResult(
            errors=[e for e in self.errors + self.warnings if e.severity == TypeErrorSeverity.ERROR],
            warnings=[w for w in self.errors + self.warnings if w.severity == TypeErrorSeverity.WARNING],
            success=not any(e.severity == TypeErrorSeverity.ERROR for e in self.errors + self.warnings)
        )
    
    def _collect_class_declaration(self, node: ClassNode):
        """Collect class declaration for later reference"""
        class_info = {
            'name': node.name,
            'base_classes': node.base_classes,
            'generic_params': node.generic_params,
            'methods': {},
            'fields': {}
        }
        
        # Collect methods
        if node.constructor:
            class_info['methods']['__init__'] = {
                'params': [p.param_type or 'any' for p in node.constructor.parameters],
                'return_type': 'void'
            }
        
        for method in node.methods:
            class_info['methods'][method.name] = {
                'params': [p.param_type or 'any' for p in method.parameters],
                'return_type': method.return_type or 'any'
            }
        
        # Collect fields
        for field in node.fields:
            class_info['fields'][field.name] = field.var_type or 'any'
        
        self.environment.define_class(node.name, class_info)
    
    def _collect_function_declaration(self, node: FunctionNode):
        """Collect function declaration for later reference"""
        param_types = [p.param_type or 'any' for p in node.parameters]
        return_type = node.return_type or 'any'
        self.environment.define_function(node.name, param_types, return_type)
    
    def visit_class(self, node: ClassNode):
        """Type check class declaration"""
        self.current_class = node.name
        
        # Check base classes exist
        for base_class in node.base_classes:
            if not self.environment.get_class_info(base_class):
                self._add_error(f"Unknown base class '{base_class}'", node)
        
        # Type check constructor
        if node.constructor:
            node.constructor.accept(self)
        
        # Type check methods
        for method in node.methods:
            method.accept(self)
        
        # Type check fields
        for field in node.fields:
            field.accept(self)
        
        self.current_class = None
        return None
    
    def visit_function(self, node: FunctionNode):
        """Type check function declaration"""
        # Create new scope
        old_env = self.environment
        self.environment = self.environment.create_child()
        
        # Set current function return type
        old_return_type = self.current_function_return_type
        self.current_function_return_type = node.return_type
        
        # Add self parameter for methods
        if self.current_class and not node.is_constructor:
            self.environment.define_variable('self', self.current_class)
        
        # Add parameters to environment
        for param in node.parameters:
            param_type = param.param_type or 'any'
            self.environment.define_variable(param.name, param_type)
            
            # Check default value type matches parameter type
            if param.default_value and param.param_type:
                default_type = self._infer_expression_type(param.default_value)
                if not self._is_assignable(default_type, param_type):
                    self._add_error(
                        f"Default value type '{default_type}' not assignable to parameter type '{param_type}'",
                        param.default_value
                    )
        
        # Type check body
        if node.body:
            node.body.accept(self)
        
        # Restore environment and return type
        self.environment = old_env
        self.current_function_return_type = old_return_type
        
        return None
    
    def visit_parameter(self, node: ParameterNode):
        """Type check parameter"""
        if node.default_value:
            node.default_value.accept(self)
        return None
    
    def visit_variable(self, node: VariableNode):
        """Type check variable declaration"""
        # Infer type from initializer if not specified
        if node.initializer:
            initializer_type = self._infer_expression_type(node.initializer)
            
            if node.var_type:
                # Check if initializer type is assignable to declared type
                if not self._is_assignable(initializer_type, node.var_type):
                    self._add_error(
                        f"Cannot assign '{initializer_type}' to variable of type '{node.var_type}'",
                        node.initializer
                    )
            else:
                # Use inferred type
                node.var_type = initializer_type
            
            node.initializer.accept(self)
        
        # Add to environment
        var_type = node.var_type or 'any'
        self.environment.define_variable(node.name, var_type)
        
        return None
    
    def visit_identifier(self, node: IdentifierNode):
        """Type check identifier"""
        var_type = self.environment.get_variable_type(node.name)
        if var_type is None and self.strict_mode:
            self._add_error(f"Undefined variable '{node.name}'", node)
        return var_type or 'any'
    
    def visit_literal(self, node: LiteralNode):
        """Type check literal"""
        return node.literal_type
    
    def visit_call(self, node: CallNode):
        """Type check function call"""
        # Type check arguments
        arg_types = []
        for arg in node.arguments:
            arg.accept(self)
            arg_types.append(self._infer_expression_type(arg))
        
        # Check if function exists and types match
        if isinstance(node.callee, IdentifierNode):
            func_name = node.callee.name
            signature = self.environment.get_function_signature(func_name)
            
            if signature:
                expected_params = signature['params']
                
                # Check argument count
                if len(arg_types) != len(expected_params):
                    self._add_error(
                        f"Function '{func_name}' expects {len(expected_params)} arguments, got {len(arg_types)}",
                        node
                    )
                
                # Check argument types
                for i, (arg_type, expected_type) in enumerate(zip(arg_types, expected_params)):
                    if not self._is_assignable(arg_type, expected_type):
                        self._add_error(
                            f"Argument {i+1} type '{arg_type}' not assignable to parameter type '{expected_type}'",
                            node.arguments[i]
                        )
                
                return signature['return_type']
            elif self.strict_mode:
                self._add_error(f"Unknown function '{func_name}'", node.callee)
        
        return 'any'
    
    def visit_binary_op(self, node: BinaryOpNode):
        """Type check binary operation"""
        node.left.accept(self)
        node.right.accept(self)
        
        left_type = self._infer_expression_type(node.left)
        right_type = self._infer_expression_type(node.right)
        
        # Type checking rules for operators
        if node.operator in ['+', '-', '*', '/', '%', '**']:
            if left_type in ['number', 'int', 'float'] and right_type in ['number', 'int', 'float']:
                return 'number'
            elif node.operator == '+' and (left_type == 'string' or right_type == 'string'):
                return 'string'
            else:
                self._add_error(f"Cannot apply operator '{node.operator}' to '{left_type}' and '{right_type}'", node)
                return 'any'
        
        elif node.operator in ['==', '!=', '<', '<=', '>', '>=']:
            return 'boolean'
        
        elif node.operator in ['&&', '||']:
            return 'boolean'
        
        elif node.operator == '.':
            # Member access
            if isinstance(node.right, IdentifierNode):
                class_info = self.environment.get_class_info(left_type)
                if class_info:
                    member_name = node.right.name
                    if member_name in class_info['fields']:
                        return class_info['fields'][member_name]
                    elif member_name in class_info['methods']:
                        return 'function'
                    else:
                        self._add_error(f"Class '{left_type}' has no member '{member_name}'", node)
            return 'any'
        
        return 'any'
    
    def visit_unary_op(self, node: UnaryOpNode):
        """Type check unary operation"""
        node.operand.accept(self)
        operand_type = self._infer_expression_type(node.operand)
        
        if node.operator == '!':
            return 'boolean'
        elif node.operator in ['+', '-']:
            if operand_type in ['number', 'int', 'float']:
                return operand_type
            else:
                self._add_error(f"Cannot apply unary '{node.operator}' to '{operand_type}'", node)
                return 'any'
        
        return operand_type
    
    def visit_assignment(self, node: AssignmentNode):
        """Type check assignment"""
        node.value.accept(self)
        value_type = self._infer_expression_type(node.value)
        
        if isinstance(node.target, IdentifierNode):
            var_type = self.environment.get_variable_type(node.target.name)
            if var_type and not self._is_assignable(value_type, var_type):
                self._add_error(
                    f"Cannot assign '{value_type}' to variable of type '{var_type}'",
                    node
                )
        
        return None
    
    def visit_block(self, node: BlockNode):
        """Type check block"""
        for stmt in node.statements:
            stmt.accept(self)
        return None
    
    def visit_return(self, node: ReturnNode):
        """Type check return statement"""
        if node.value:
            node.value.accept(self)
            return_type = self._infer_expression_type(node.value)
        else:
            return_type = 'void'
        
        # Check return type matches function signature
        if self.current_function_return_type:
            if not self._is_assignable(return_type, self.current_function_return_type):
                self._add_error(
                    f"Return type '{return_type}' not assignable to function return type '{self.current_function_return_type}'",
                    node
                )
        
        return None
    
    def visit_if(self, node: IfNode):
        """Type check if statement"""
        node.condition.accept(self)
        condition_type = self._infer_expression_type(node.condition)
        
        if condition_type != 'boolean' and self.strict_mode:
            self._add_warning(f"Condition should be boolean, got '{condition_type}'", node.condition)
        
        node.then_block.accept(self)
        if node.else_block:
            node.else_block.accept(self)
        
        return None
    
    def visit_while(self, node: WhileNode):
        """Type check while loop"""
        node.condition.accept(self)
        condition_type = self._infer_expression_type(node.condition)
        
        if condition_type != 'boolean' and self.strict_mode:
            self._add_warning(f"Condition should be boolean, got '{condition_type}'", node.condition)
        
        node.body.accept(self)
        return None
    
    def visit_for(self, node: ForNode):
        """Type check for loop"""
        # Create new scope for loop variable
        old_env = self.environment
        self.environment = self.environment.create_child()
        
        node.iterable.accept(self)
        iterable_type = self._infer_expression_type(node.iterable)
        
        # Infer loop variable type
        if iterable_type.startswith('list<') or iterable_type.startswith('Array<'):
            # Extract element type
            element_type = iterable_type[iterable_type.index('<')+1:iterable_type.rindex('>')]
        else:
            element_type = 'any'
        
        self.environment.define_variable(node.variable, element_type)
        node.body.accept(self)
        
        # Restore environment
        self.environment = old_env
        return None
    
    def _infer_expression_type(self, expr: ExpressionNode) -> str:
        """Infer the type of an expression"""
        if isinstance(expr, LiteralNode):
            return expr.literal_type
        elif isinstance(expr, IdentifierNode):
            return self.environment.get_variable_type(expr.name) or 'any'
        elif isinstance(expr, CallNode):
            if isinstance(expr.callee, IdentifierNode):
                signature = self.environment.get_function_signature(expr.callee.name)
                if signature:
                    return signature['return_type']
            return 'any'
        elif isinstance(expr, BinaryOpNode):
            left_type = self._infer_expression_type(expr.left)
            right_type = self._infer_expression_type(expr.right)
            
            if expr.operator in ['+', '-', '*', '/', '%']:
                if left_type == 'string' or right_type == 'string':
                    return 'string'
                return 'number'
            elif expr.operator in ['==', '!=', '<', '<=', '>', '>=', '&&', '||']:
                return 'boolean'
            elif expr.operator == '.':
                # Member access
                if isinstance(expr.right, IdentifierNode):
                    class_info = self.environment.get_class_info(left_type)
                    if class_info:
                        member_name = expr.right.name
                        if member_name in class_info['fields']:
                            return class_info['fields'][member_name]
                        elif member_name in class_info['methods']:
                            return 'function'
                return 'any'
        elif isinstance(expr, UnaryOpNode):
            if expr.operator == '!':
                return 'boolean'
            return self._infer_expression_type(expr.operand)
        
        return 'any'
    
    def _is_assignable(self, from_type: str, to_type: str) -> bool:
        """Check if one type is assignable to another"""
        if from_type == to_type or to_type == 'any' or from_type == 'any':
            return True
        
        # Number type compatibility
        if to_type in ['number', 'float'] and from_type in ['int', 'integer']:
            return True
        
        # String conversions
        if to_type == 'string':
            return True  # Most types can be converted to string
        
        return False
    
    def _add_error(self, message: str, node: Optional[ASTNode] = None):
        """Add a type checking error"""
        self.errors.append(TypeCheckError(message, node, TypeErrorSeverity.ERROR))
    
    def _add_warning(self, message: str, node: Optional[ASTNode] = None):
        """Add a type checking warning"""
        self.warnings.append(TypeCheckError(message, node, TypeErrorSeverity.WARNING))
    
    def visit_try(self, node):
        """Visit try statement"""
        # Type check try block
        node.try_block.accept(self)
        
        # Type check catch clauses
        for catch_clause in node.catch_clauses:
            catch_clause.accept(self)
        
        # Type check finally block
        if node.finally_block:
            node.finally_block.accept(self)
        
        return None
    
    def visit_catch(self, node):
        """Visit catch clause"""
        # Add exception variable to environment if present
        old_env = self.environment
        self.environment = TypeEnvironment(old_env)
        
        if node.exception_name:
            exception_type = node.exception_type or 'Error'
            self.environment.define_variable(node.exception_name, exception_type)
        
        # Type check catch body
        node.body.accept(self)
        
        # Restore environment
        self.environment = old_env
        return None
    
    def visit_throw(self, node):
        """Visit throw statement"""
        # Type check the thrown expression
        expr_type = self._infer_expression_type(node.expression)
        
        # Should be an Error type or string
        if expr_type not in ['Error', 'string', 'any']:
            self._add_warning(f"Thrown expression should be Error type, got '{expr_type}'", node)
        
        return None