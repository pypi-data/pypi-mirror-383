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

import ast
from typing import List, Dict, Any, Optional, Union
from .ast_nodes import *
from .lexer import Token


class TranspilerError(Exception):
    """Exception raised during transpilation"""
    
    def __init__(self, message: str, node: Optional[ASTNode] = None):
        self.message = message
        self.node = node
        location_info = ""
        if node and node.location:
            location_info = f" at line {node.location.line}, column {node.location.column}"
        super().__init__(f"{message}{location_info}")


class Transpiler(ASTVisitor):
    """Transpiles PowerScript AST to Python AST and code"""
    
    def __init__(self):
        self.python_ast_nodes: List[ast.AST] = []
        self.current_class: Optional[str] = None
        self.imports: Dict[str, List[str]] = {}
        self.type_imports: List[str] = []
        self.runtime_checks_enabled = False
        self.strict_typing = True
        self.type_map = {
            'number': 'float',
            'string': 'str',
            'boolean': 'bool'
        }
    
    def transpile(self, powerscript_nodes: List[ASTNode]) -> ast.Module:
        """Transpile PowerScript AST to Python AST Module"""
        self.python_ast_nodes = []
        self.imports = {}
        self.type_imports = []
        
        # Process all nodes
        for node in powerscript_nodes:
            python_node = node.accept(self)
            if python_node:
                if isinstance(python_node, list):
                    self.python_ast_nodes.extend(python_node)
                else:
                    # Wrap expressions in ast.Expr for statement context
                    if isinstance(python_node, (ast.Call, ast.Name, ast.Constant, 
                                               ast.BinOp, ast.UnaryOp, ast.Compare,
                                               ast.BoolOp, ast.Attribute, ast.Subscript)):
                        python_node = ast.Expr(value=python_node)
                    self.python_ast_nodes.append(python_node)
        
        # Add necessary imports at the beginning
        import_nodes = self._generate_imports()
        all_nodes = import_nodes + self.python_ast_nodes
        
        # Create Python module
        module = ast.Module(body=all_nodes, type_ignores=[])
        
        # Fix missing locations
        ast.fix_missing_locations(module)
        
        return module
    
    def transpile_to_code(self, powerscript_nodes: List[ASTNode]) -> str:
        """Transpile PowerScript AST to Python source code"""
        module = self.transpile(powerscript_nodes)
        return ast.unparse(module)
    
    def _generate_imports(self) -> List[ast.AST]:
        """Generate necessary import statements"""
        imports = []
        
        # Add PowerScript built-ins import
        builtins_import = ast.ImportFrom(
            module='powerscript.runtime.builtins',
            names=[ast.alias(name='*', asname=None)],
            level=0
        )
        imports.append(builtins_import)
        
        # Add typing imports if needed
        if self.type_imports:
            typing_import = ast.ImportFrom(
                module='typing',
                names=[ast.alias(name=name, asname=None) for name in set(self.type_imports)],
                level=0
            )
            imports.append(typing_import)
        
        # Add asyncio if async functions are used
        if 'asyncio' in self.imports:
            asyncio_import = ast.Import(names=[ast.alias(name='asyncio', asname=None)])
            imports.append(asyncio_import)
        
        # Add runtime validation imports if needed
        if self.runtime_checks_enabled:
            beartype_import = ast.ImportFrom(
                module='beartype',
                names=[ast.alias(name='beartype', asname=None)],
                level=0
            )
            imports.append(beartype_import)
        
        return imports
    
    def visit_class(self, node: ClassNode) -> ast.ClassDef:
        """Visit class node"""
        self.current_class = node.name
        
        # Base classes
        bases = [ast.Name(id=base, ctx=ast.Load()) for base in node.base_classes]
        
        # Generic support
        if node.generic_params:
            self.type_imports.extend(['Generic', 'TypeVar'])
            # Add Generic as base class
            bases.append(ast.Name(id='Generic', ctx=ast.Load()))
            
            # Create TypeVar definitions
            for param in node.generic_params:
                type_var = ast.Assign(
                    targets=[ast.Name(id=param, ctx=ast.Store())],
                    value=ast.Call(
                        func=ast.Name(id='TypeVar', ctx=ast.Load()),
                        args=[ast.Constant(value=param)],
                        keywords=[]
                    )
                )
                self.python_ast_nodes.append(type_var)
        
        # Class body
        body = []
        
        # Add constructor if present
        if node.constructor:
            constructor_method = node.constructor.accept(self)
            body.append(constructor_method)
        
        # Add methods
        for method in node.methods:
            method_def = method.accept(self)
            body.append(method_def)
        
        # Add fields as class variables or in __init__
        for field in node.fields:
            if field.initializer and field.is_const:
                # Class constant
                field_assign = ast.Assign(
                    targets=[ast.Name(id=field.name, ctx=ast.Store())],
                    value=field.initializer.accept(self)
                )
                body.append(field_assign)
        
        # If no body, add pass
        if not body:
            body.append(ast.Pass())
        
        class_def = ast.ClassDef(
            name=node.name,
            bases=bases,
            keywords=[],
            decorator_list=self._get_class_decorators(node),
            body=body
        )
        
        self.current_class = None
        return class_def
    
    def visit_enum(self, node: EnumNode) -> ast.ClassDef:
        """Visit enum node - convert to class with constants"""
        body = []
        
        for i, value in enumerate(node.values):
            assign = ast.Assign(
                targets=[ast.Name(id=value, ctx=ast.Store())],
                value=ast.Constant(value=i)
            )
            body.append(assign)
        
        if not body:
            body.append(ast.Pass())
        
        return ast.ClassDef(
            name=node.name,
            bases=[],
            keywords=[],
            decorator_list=[],
            body=body
        )
    
    def visit_function(self, node: FunctionNode) -> ast.FunctionDef:
        """Visit function node"""
        # Handle constructor specially
        if node.is_constructor:
            return self._create_constructor(node)
        
        # Function arguments
        args = []
        defaults = []
        
        # Add self parameter for methods
        if self.current_class:
            args.append(ast.arg(arg='self', annotation=None))
        
        # Add parameters
        for param in node.parameters:
            arg_node = param.accept(self)
            args.append(arg_node)
            
            if param.default_value:
                defaults.append(param.default_value.accept(self))
        
        # Function body
        body = []
        if node.body:
            for stmt in node.body.statements:
                stmt_node = stmt.accept(self)
                if stmt_node:
                    if isinstance(stmt_node, list):
                        body.extend(stmt_node)
                    else:
                        body.append(stmt_node)
        
        if not body:
            body.append(ast.Pass())
        
        # Create function
        func_class = ast.AsyncFunctionDef if node.is_async else ast.FunctionDef
        
        func_def = func_class(
            name=node.name,
            args=ast.arguments(
                posonlyargs=[],
                args=args,
                vararg=None,
                kwonlyargs=[],
                kw_defaults=[],
                kwarg=None,
                defaults=defaults
            ),
            body=body,
            decorator_list=self._get_function_decorators(node),
            returns=self._get_type_annotation(node.return_type) if node.return_type else None
        )
        
        return func_def
    
    def _create_constructor(self, node: FunctionNode) -> ast.FunctionDef:
        """Create Python __init__ method from PowerScript constructor"""
        # Arguments
        args = [ast.arg(arg='self', annotation=None)]
        defaults = []
        
        for param in node.parameters:
            arg_node = ast.arg(
                arg=param.name,
                annotation=self._get_type_annotation(param.param_type) if param.param_type else None
            )
            args.append(arg_node)
            
            if param.default_value:
                defaults.append(param.default_value.accept(self))
        
        # Body
        body = []
        
        # Add parameter assignments to self
        for param in node.parameters:
            assignment = ast.Assign(
                targets=[ast.Attribute(
                    value=ast.Name(id='self', ctx=ast.Load()),
                    attr=param.name,
                    ctx=ast.Store()
                )],
                value=ast.Name(id=param.name, ctx=ast.Load())
            )
            body.append(assignment)
        
        # Add constructor body
        if node.body:
            for stmt in node.body.statements:
                stmt_node = stmt.accept(self)
                if stmt_node:
                    if isinstance(stmt_node, list):
                        body.extend(stmt_node)
                    else:
                        body.append(stmt_node)
        
        if not body:
            body.append(ast.Pass())
        
        return ast.FunctionDef(
            name='__init__',
            args=ast.arguments(
                posonlyargs=[],
                args=args,
                vararg=None,
                kwonlyargs=[],
                kw_defaults=[],
                kwarg=None,
                defaults=defaults
            ),
            body=body,
            decorator_list=self._get_function_decorators(node),
            returns=None
        )
    
    def visit_parameter(self, node: ParameterNode) -> ast.arg:
        """Visit parameter node"""
        annotation = None
        if node.param_type:
            if isinstance(node.param_type, str):
                # Handle legacy string-based type annotations
                annotation = self._get_type_annotation(node.param_type)
            else:
                # Handle ExpressionNode-based type annotations (union types, etc.)
                annotation = node.param_type.accept(self)
        
        return ast.arg(
            arg=node.name,
            annotation=annotation
        )
    
    def visit_variable(self, node: VariableNode) -> ast.Assign:
        """Visit variable node"""
        target = ast.Name(id=node.name, ctx=ast.Store())
        
        if node.initializer:
            value = node.initializer.accept(self)
        else:
            value = ast.Constant(value=None)
        
        return ast.Assign(targets=[target], value=value)
    
    def visit_identifier(self, node: IdentifierNode) -> ast.Name:
        """Visit identifier node"""
        name = self.type_map.get(node.name, node.name)
        return ast.Name(id=name, ctx=ast.Load())
    
    def visit_literal(self, node: LiteralNode) -> ast.Constant:
        """Visit literal node"""
        value = node.value
        
        # Handle different number formats
        if isinstance(value, str) and value.replace('.', '').replace('-', '').replace('+', '').replace('e', '').replace('E', '').isdigit() == False:
            # Check for special number formats
            if value.startswith('0x') or value.startswith('0X'):
                # Hexadecimal
                try:
                    value = int(value, 16)
                except ValueError:
                    value = float.fromhex(value)
            elif value.startswith('0b') or value.startswith('0B'):
                # Binary
                try:
                    value = int(value, 2)
                except ValueError:
                    # Handle binary floats (custom implementation)
                    pass
            elif value.startswith('0o') or value.startswith('0O'):
                # Octal
                try:
                    value = int(value, 8)
                except ValueError:
                    # Handle octal floats (custom implementation)
                    pass
            elif 'e' in value.lower():
                # Scientific notation
                try:
                    value = float(value)
                except ValueError:
                    pass
        
        return ast.Constant(value=value)
    
    def visit_array_literal(self, node: ArrayLiteralNode) -> ast.List:
        """Visit array literal node"""
        elements = [elem.accept(self) for elem in node.elements]
        return ast.List(elts=elements, ctx=ast.Load())
    
    def visit_object_literal(self, node: ObjectLiteralNode) -> ast.Dict:
        """Visit object literal node"""
        keys = []
        values = []
        for key_node, value_node in node.properties:
            # If key is an identifier, convert it to a string literal
            # This handles JavaScript-style object literals like {name: "John"}
            if isinstance(key_node, IdentifierNode):
                key_ast = ast.Constant(value=key_node.name)
            else:
                key_ast = key_node.accept(self)
            keys.append(key_ast)
            values.append(value_node.accept(self))
        return ast.Dict(keys=keys, values=values)
    
    def visit_set_literal(self, node: SetLiteralNode) -> ast.Set:
        """Visit set literal node"""
        elements = [elem.accept(self) for elem in node.elements]
        return ast.Set(elts=elements)
    
    def visit_f_string(self, node: FStringNode) -> ast.JoinedStr:
        """Visit f-string node and convert to Python f-string"""
        import re
        
        # Parse the f-string content to create values list
        values = []
        
        if node.value.startswith('f"'):
            content = node.value[2:-1]  # Remove f" and "
        else:  # f'...'
            content = node.value[2:-1]  # Remove f' and '
        
        # Split content by {expr} patterns
        expr_pattern = r'\{([^}]+)\}'
        last_end = 0
        
        for match in re.finditer(expr_pattern, content):
            # Add text before the expression
            if match.start() > last_end:
                text = content[last_end:match.start()]
                if text:
                    values.append(ast.Constant(value=text))
            
            # Add the expression
            expr_idx = 0
            if expr_idx < len(node.expressions):
                formatted_value = ast.FormattedValue(
                    value=node.expressions[expr_idx].accept(self),
                    conversion=-1,  # No conversion
                    format_spec=None
                )
                values.append(formatted_value)
                expr_idx += 1
            
            last_end = match.end()
        
        # Add remaining text
        if last_end < len(content):
            remaining = content[last_end:]
            if remaining:
                values.append(ast.Constant(value=remaining))
        
        return ast.JoinedStr(values=values)
    
    def visit_call(self, node: CallNode) -> ast.Call:
        """Visit call node"""
        func = node.callee.accept(self)
        args = [arg.accept(self) for arg in node.arguments]
        
        # Special handling for console.log -> print
        if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name) and func.value.id == 'console' and func.attr == 'log':
            return ast.Call(func=ast.Name(id='print', ctx=ast.Load()), args=args, keywords=[])
        
        # Map PowerScript method names to Python equivalents
        method_mapping = {
            'push': 'append',
            # Add more mappings as needed
        }
        if isinstance(func, ast.Attribute) and func.attr in method_mapping:
            func = ast.Attribute(value=func.value, attr=method_mapping[func.attr], ctx=ast.Load())
        
        # Special handling for array methods
        if isinstance(func, ast.Attribute) and func.attr == 'filter':
            # data.filter(lambda) -> filter(lambda, data)
            return ast.Call(func=ast.Name(id='filter', ctx=ast.Load()), args=[args[0], func.value], keywords=[])
        elif isinstance(func, ast.Attribute) and func.attr == 'map':
            # data.map(lambda) -> map(lambda, data)
            return ast.Call(func=ast.Name(id='map', ctx=ast.Load()), args=[args[0], func.value], keywords=[])
        elif isinstance(func, ast.Attribute) and func.attr == 'reduce':
            # Assume reduce is imported or available
            self.type_imports.append('functools')
            reduce_call = ast.Call(
                func=ast.Attribute(value=ast.Name(id='functools', ctx=ast.Load()), attr='reduce', ctx=ast.Load()),
                args=[args[0], func.value] + args[1:],  # lambda, data, initial
                keywords=[]
            )
            return reduce_call
        
        return ast.Call(func=func, args=args, keywords=[])
    
    def visit_expression_statement(self, node: ExpressionStatementNode) -> ast.Expr:
        """Visit expression statement"""
        return ast.Expr(value=node.expression.accept(self))
    
    def visit_binary_op(self, node: BinaryOpNode) -> Union[ast.BinOp, ast.Compare, ast.BoolOp, ast.Attribute, ast.Subscript]:
        """Visit binary operation node"""
        left = node.left.accept(self)
        right = node.right.accept(self)
        
        # Handle member access
        if node.operator == '.':
            # Special case for .length -> len()
            if isinstance(right, ast.Name) and right.id == 'length':
                return ast.Call(func=ast.Name(id='len', ctx=ast.Load()), args=[left], keywords=[])
            return ast.Attribute(value=left, attr=right.id, ctx=ast.Load())
        
        # Handle array indexing
        if node.operator == '[]':
            return ast.Subscript(value=left, slice=right, ctx=ast.Load())
        
        # Handle comparison operators
        if node.operator in ['==', '!=', '<', '<=', '>', '>=']:
            op_map = {
                '==': ast.Eq(),
                '!=': ast.NotEq(),
                '<': ast.Lt(),
                '<=': ast.LtE(),
                '>': ast.Gt(),
                '>=': ast.GtE()
            }
            return ast.Compare(left=left, ops=[op_map[node.operator]], comparators=[right])
        
        # Handle logical operators
        if node.operator == '&&':
            return ast.BoolOp(op=ast.And(), values=[left, right])
        elif node.operator == '||':
            return ast.BoolOp(op=ast.Or(), values=[left, right])
        
        # Handle arithmetic operators
        op_map = {
            '+': ast.Add(),
            '-': ast.Sub(),
            '*': ast.Mult(),
            '/': ast.Div(),
            '%': ast.Mod(),
            '**': ast.Pow(),
            '&': ast.BitAnd(),
            '|': ast.BitOr(),
            '^': ast.BitXor(),
            '<<': ast.LShift(),
            '>>': ast.RShift()
        }
        
        if node.operator in op_map:
            return ast.BinOp(left=left, op=op_map[node.operator], right=right)
        
        raise TranspilerError(f"Unsupported binary operator: {node.operator}", node)
    
    def visit_unary_op(self, node: UnaryOpNode) -> ast.UnaryOp:
        """Visit unary operation node"""
        operand = node.operand.accept(self)
        
        op_map = {
            '-': ast.USub(),
            '+': ast.UAdd(),
            '!': ast.Not(),
            '~': ast.Invert()
        }
        
        if node.operator in op_map:
            return ast.UnaryOp(op=op_map[node.operator], operand=operand)
        
        raise TranspilerError(f"Unsupported unary operator: {node.operator}", node)
    
    def visit_await(self, node: AwaitNode) -> ast.Await:
        """Visit await expression node"""
        expression = node.expression.accept(self)
        return ast.Await(value=expression)
    
    def visit_assignment(self, node: AssignmentNode) -> Union[ast.Assign, ast.AugAssign]:
        """Visit assignment node"""
        target = node.target.accept(self)
        value = node.value.accept(self)
        
        # Handle compound assignments
        if hasattr(node, 'operator') and node.operator != "=":
            # Map compound operators to AST operators
            op_map = {
                "+=": ast.Add(),
                "-=": ast.Sub(),
                "*=": ast.Mult(),
                "/=": ast.Div(),
                "%=": ast.Mod(),
                "**=": ast.Pow(),
            }
            
            if node.operator in op_map:
                # Set target context for reading (for augmented assignment)
                if isinstance(target, ast.Name):
                    target.ctx = ast.Store()
                elif isinstance(target, ast.Attribute):
                    target.ctx = ast.Store()
                elif isinstance(target, ast.Subscript):
                    target.ctx = ast.Store()
                
                return ast.AugAssign(target=target, op=op_map[node.operator], value=value)
        
        # Regular assignment
        # Ensure target has Store context
        if isinstance(target, ast.Name):
            target.ctx = ast.Store()
        elif isinstance(target, ast.Attribute):
            target.ctx = ast.Store()
        elif isinstance(target, ast.Subscript):
            target.ctx = ast.Store()
        
        return ast.Assign(targets=[target], value=value)
    
    def visit_block(self, node: BlockNode) -> List[ast.AST]:
        """Visit block node"""
        statements = []
        for stmt in node.statements:
            stmt_node = stmt.accept(self)
            if stmt_node:
                if isinstance(stmt_node, list):
                    statements.extend(stmt_node)
                else:
                    statements.append(stmt_node)
        return statements
    
    def visit_return(self, node: ReturnNode) -> ast.Return:
        """Visit return node"""
        value = node.value.accept(self) if node.value else None
        return ast.Return(value=value)
    
    def visit_if(self, node: IfNode) -> ast.If:
        """Visit if node"""
        test = node.condition.accept(self)
        body = node.then_block.accept(self)
        orelse = node.else_block.accept(self) if node.else_block else []
        
        return ast.If(test=test, body=body, orelse=orelse)
    
    def visit_while(self, node: WhileNode) -> ast.While:
        """Visit while node"""
        test = node.condition.accept(self)
        body = node.body.accept(self)
        
        return ast.While(test=test, body=body, orelse=[])
    
    def visit_for(self, node: ForNode) -> ast.For:
        """Visit for node"""
        target = ast.Name(id=node.variable, ctx=ast.Store())
        iter_expr = node.iterable.accept(self)
        body = node.body.accept(self)
        
        return ast.For(target=target, iter=iter_expr, body=body, orelse=[])
    
    def visit_switch(self, node: SwitchNode) -> List[ast.AST]:
        """Visit switch node - transpile to if-elif chain"""
        switch_expr = node.expression.accept(self)
        
        # Create a temporary variable to store the switch expression value
        temp_var = f"_switch_expr_{id(node)}"
        assign_stmt = ast.Assign(
            targets=[ast.Name(id=temp_var, ctx=ast.Store())],
            value=switch_expr
        )
        
        statements = [assign_stmt]
        
        # Build if-elif chain
        if_node = None
        current_node = None
        
        for case in node.cases:
            # Create condition: temp_var == case_value1 or temp_var == case_value2 ...
            conditions = []
            for case_value in case.values:
                compare = ast.Compare(
                    left=ast.Name(id=temp_var, ctx=ast.Load()),
                    ops=[ast.Eq()],
                    comparators=[case_value.accept(self)]
                )
                conditions.append(compare)
            
            # Combine conditions with OR
            if len(conditions) == 1:
                condition = conditions[0]
            else:
                condition = ast.BoolOp(op=ast.Or(), values=conditions)
            
            # Get case body, filter out break statements (not needed in if/elif)
            case_statements = case.body.accept(self)
            case_body = [stmt for stmt in case_statements if not isinstance(stmt, ast.Break)]
            
            if if_node is None:
                # First case becomes if
                if_node = ast.If(test=condition, body=case_body, orelse=[])
                current_node = if_node
            else:
                # Subsequent cases become elif
                elif_node = ast.If(test=condition, body=case_body, orelse=[])
                current_node.orelse = [elif_node]
                current_node = elif_node
        
        # Add default case if present
        if node.default_case:
            default_statements = node.default_case.body.accept(self)
            default_body = [stmt for stmt in default_statements if not isinstance(stmt, ast.Break)]
            if current_node:
                current_node.orelse = default_body
            else:
                # Only default case
                statements.extend(default_body)
                return statements
        
        if if_node:
            statements.append(if_node)
        
        return statements
    
    def visit_case(self, node: CaseNode) -> List[ast.AST]:
        """Visit case node - handled by visit_switch"""
        return node.body.accept(self)
    
    def visit_break(self, node: BreakNode) -> ast.Break:
        """Visit break node"""
        return ast.Break()
    
    def visit_continue(self, node: ContinueNode) -> ast.Continue:
        """Visit continue node"""
        return ast.Continue()
    
    def visit_template_literal(self, node: TemplateLiteralNode) -> ast.JoinedStr:
        """Visit template literal node and convert to Python f-string"""
        import re
        
        # Parse the template literal content to create values list
        values = []
        
        content = node.value[1:-1]  # Remove backticks
        
        # Split content by ${expr} patterns
        expr_pattern = r'\$\{([^}]+)\}'
        last_end = 0
        expr_idx = 0
        
        for match in re.finditer(expr_pattern, content):
            # Add text before the expression
            if match.start() > last_end:
                text = content[last_end:match.start()]
                if text:
                    values.append(ast.Constant(value=text))
            
            # Add the expression
            if expr_idx < len(node.expressions):
                formatted_value = ast.FormattedValue(
                    value=node.expressions[expr_idx].accept(self),
                    conversion=-1,  # No conversion
                    format_spec=None
                )
                values.append(formatted_value)
                expr_idx += 1
            
            last_end = match.end()
        
        # Add remaining text
        if last_end < len(content):
            remaining = content[last_end:]
            if remaining:
                values.append(ast.Constant(value=remaining))
        
        return ast.JoinedStr(values=values)
    
    def visit_import(self, node: ImportNode) -> Union[ast.Import, ast.ImportFrom]:
        """Visit import node"""
        if node.is_default_import:
            # Default import: import defaultName from "module" -> from module import defaultName
            alias = ast.alias(name=node.specifiers[0].imported_name, asname=node.specifiers[0].local_name)
            return ast.ImportFrom(module=node.module_name, names=[alias], level=0)
        elif node.specifiers and node.specifiers[0].imported_name == "*":
            # Namespace import: import * as name from "module" -> import module as name
            alias = ast.alias(name=node.module_name, asname=node.specifiers[0].local_name)
            return ast.Import(names=[alias])
        else:
            # Named imports: import { name1, name2 } from "module" -> from module import name1, name2
            aliases = []
            for spec in node.specifiers:
                alias = ast.alias(name=spec.imported_name, asname=spec.local_name if spec.local_name != spec.imported_name else None)
                aliases.append(alias)
            return ast.ImportFrom(module=node.module_name, names=aliases, level=0)
    
    def visit_export(self, node: ExportNode) -> List[ast.AST]:
        """Visit export node - In Python, we'll just generate the declaration"""
        statements = []
        
        if node.declaration:
            # Export a declaration - just generate the declaration itself
            decl_stmt = node.declaration.accept(self)
            if isinstance(decl_stmt, list):
                statements.extend(decl_stmt)
            else:
                statements.append(decl_stmt)
        
        elif node.specifiers:
            # Named exports: export { name1, name2 } - create __all__ list
            export_names = [spec.exported_name for spec in node.specifiers]
            all_stmt = ast.Assign(
                targets=[ast.Name(id='__all__', ctx=ast.Store())],
                value=ast.List(elts=[ast.Constant(value=name) for name in export_names], ctx=ast.Load())
            )
            statements.append(all_stmt)
        
        return statements
    
    def visit_destructuring(self, node: DestructuringNode) -> List[ast.AST]:
        """Visit destructuring node - convert to multiple assignments"""
        statements = []
        
        if isinstance(node.pattern, ArrayPattern):
            # Array destructuring: [a, b] = arr -> a, b = arr
            targets = []
            for i, element in enumerate(node.pattern.elements):
                if element:  # Skip holes (None elements)
                    targets.append(ast.Name(id=element, ctx=ast.Store()))
            
            if targets:
                # Create tuple assignment
                target_tuple = ast.Tuple(elts=targets, ctx=ast.Store())
                value = node.value.accept(self)
                assign = ast.Assign(targets=[target_tuple], value=value)
                statements.append(assign)
        
        elif isinstance(node.pattern, ObjectPattern):
            # Object destructuring: {x, y} = obj -> x = obj['x']; y = obj['y']
            obj_value = node.value.accept(self)
            
            # Create temporary variable to avoid multiple evaluations
            temp_var = f"_temp_obj_{id(node)}"
            temp_assign = ast.Assign(
                targets=[ast.Name(id=temp_var, ctx=ast.Store())],
                value=obj_value
            )
            statements.append(temp_assign)
            
            for prop in node.pattern.properties:
                # Create assignment: var_name = temp_var['key']
                key_access = ast.Subscript(
                    value=ast.Name(id=temp_var, ctx=ast.Load()),
                    slice=ast.Constant(value=prop.key),
                    ctx=ast.Load()
                )
                assign = ast.Assign(
                    targets=[ast.Name(id=prop.value, ctx=ast.Store())],
                    value=key_access
                )
                statements.append(assign)
        
        return statements
    
    def visit_spread(self, node: SpreadNode) -> ast.Starred:
        """Visit spread node - convert to Python starred expression"""
        return ast.Starred(value=node.expression.accept(self), ctx=ast.Load())
    
    def visit_try(self, node: TryNode) -> ast.Try:
        """Visit try node"""
        # Try body
        body = []
        for stmt in node.try_block.statements:
            stmt_node = stmt.accept(self)
            if stmt_node:
                if isinstance(stmt_node, list):
                    body.extend(stmt_node)
                else:
                    body.append(stmt_node)
        
        # Catch handlers
        handlers = []
        for catch_clause in node.catch_clauses:
            handler = self._create_exception_handler(catch_clause)
            handlers.append(handler)
        
        # Finally block
        finalbody = []
        if node.finally_block:
            for stmt in node.finally_block.statements:
                stmt_node = stmt.accept(self)
                if stmt_node:
                    if isinstance(stmt_node, list):
                        finalbody.extend(stmt_node)
                    else:
                        finalbody.append(stmt_node)
        
        return ast.Try(body=body, handlers=handlers, orelse=[], finalbody=finalbody)
    
    def visit_catch(self, node: CatchNode) -> ast.ExceptHandler:
        """Visit catch node - this is handled by visit_try"""
        return self._create_exception_handler(node)
    
    def visit_throw(self, node: ThrowNode) -> ast.Raise:
        """Visit throw node"""
        exc = node.expression.accept(self)
        return ast.Raise(exc=exc, cause=None)
    
    def _create_exception_handler(self, catch_node: CatchNode) -> ast.ExceptHandler:
        """Create Python exception handler from catch node"""
        # Exception type
        exception_type = ast.Name(id='Exception', ctx=ast.Load())
        if catch_node.exception_type:
            # Map PowerScript exception types to Python
            type_map = {
                'Error': 'Exception',
                'TypeError': 'TypeError', 
                'ValueError': 'ValueError',
                'RuntimeError': 'RuntimeError'
            }
            python_type = type_map.get(catch_node.exception_type, catch_node.exception_type)
            exception_type = ast.Name(id=python_type, ctx=ast.Load())
        
        # Exception name binding
        name = catch_node.exception_name
        
        # Handler body
        body = []
        for stmt in catch_node.body.statements:
            stmt_node = stmt.accept(self)
            if stmt_node:
                if isinstance(stmt_node, list):
                    body.extend(stmt_node)
                else:
                    body.append(stmt_node)
        
        if not body:
            body.append(ast.Pass())
        
        return ast.ExceptHandler(type=exception_type, name=name, body=body)
    
    def _get_type_annotation(self, type_annotation) -> Optional[ast.AST]:
        """Convert PowerScript type annotation to Python AST"""
        if not type_annotation or not self.strict_typing:
            return None
        
        # Convert AST node to string if needed
        if hasattr(type_annotation, 'name'):  # IdentifierNode
            type_str = type_annotation.name
        elif isinstance(type_annotation, str):
            type_str = type_annotation
        else:
            return None
        
        # Handle basic types
        type_map = {
            'string': 'str',
            'number': 'float',
            'integer': 'int', 
            'boolean': 'bool',
            'void': 'None'
        }
        
        if type_str in type_map:
            return ast.Name(id=type_map[type_str], ctx=ast.Load())
        
        # Handle generic types
        if '<' in type_str and '>' in type_str:
            self.type_imports.append('List')
            # Simple handling for List<T>
            base_type = type_str.split('<')[0]
            inner_type = type_str.split('<')[1].split('>')[0]
            
            if base_type.lower() == 'array' or base_type.lower() == 'list':
                return ast.Subscript(
                    value=ast.Name(id='List', ctx=ast.Load()),
                    slice=self._get_type_annotation(inner_type),
                    ctx=ast.Load()
                )
        
        # Handle optional types
        if type_str.endswith('?'):
            self.type_imports.append('Optional')
            base_type = type_str[:-1]
            return ast.Subscript(
                value=ast.Name(id='Optional', ctx=ast.Load()),
                slice=self._get_type_annotation(base_type),
                ctx=ast.Load()
            )
        
        # Default to the type name as is
        return ast.Name(id=type_str, ctx=ast.Load())
    
    def _get_class_decorators(self, node: ClassNode) -> List[ast.AST]:
        """Get decorators for class"""
        decorators = []
        
        if self.runtime_checks_enabled:
            decorators.append(ast.Name(id='beartype', ctx=ast.Load()))
        
        return decorators
    
    def _get_function_decorators(self, node: FunctionNode) -> List[ast.AST]:
        """Get decorators for function"""
        decorators = []
        
        # Add access modifier decorators
        if node.access_modifier == AccessModifier.PRIVATE:
            # Use name mangling for private methods
            pass  # Python handles this with __ prefix
        elif node.access_modifier == AccessModifier.PROTECTED:
            # Use single underscore convention
            pass
        
        # Only add beartype if there are type annotations to check
        if self.runtime_checks_enabled and not node.is_constructor:
            has_type_annotations = (
                node.return_type is not None or
                any(param.param_type is not None for param in node.parameters)
            )
            if has_type_annotations:
                decorators.append(ast.Name(id='beartype', ctx=ast.Load()))
        
        return decorators
    
    def visit_lambda(self, node: LambdaNode) -> ast.Lambda:
        """Visit lambda node"""
        args = []
        for param in node.parameters:
            args.append(ast.arg(arg=param.name, annotation=None))
        
        arguments = ast.arguments(
            posonlyargs=[],
            args=args,
            vararg=None,
            kwonlyargs=[],
            kw_defaults=[],
            kwarg=None,
            defaults=[]
        )
        
        body = node.body.accept(self)
        return ast.Lambda(args=arguments, body=body)
    
    def visit_with(self, node: WithNode) -> ast.With:
        """Visit with statement node"""
        context_expr = node.context_expr.accept(self)
        optional_vars = None
        if node.optional_vars:
            optional_vars = node.optional_vars.accept(self)
        
        with_item = ast.withitem(context_expr=context_expr, optional_vars=optional_vars)
        
        body = []
        for stmt in node.body.statements:
            stmt_node = stmt.accept(self)
            if isinstance(stmt_node, list):
                body.extend(stmt_node)
            else:
                body.append(stmt_node)
        
        return ast.With(items=[with_item], body=body)
    
    def visit_yield(self, node: YieldNode) -> Union[ast.Yield, ast.YieldFrom]:
        """Visit yield node"""
        value = None
        if node.value:
            value = node.value.accept(self)
            
        if node.is_yield_from:
            return ast.YieldFrom(value=value)
        else:
            return ast.Yield(value=value)
    
    def visit_comprehension(self, node: ComprehensionNode) -> Union[ast.ListComp, ast.DictComp, ast.SetComp]:
        """Visit comprehension node"""
        target = ast.Name(id=node.target.name, ctx=ast.Store())
        iter_expr = node.iterable.accept(self)
        
        ifs = []
        for condition in node.conditions:
            ifs.append(condition.accept(self))
        
        comprehension = ast.comprehension(target=target, iter=iter_expr, ifs=ifs, is_async=0)
        
        if node.comp_type == "list":
            elt = node.expr.accept(self)
            return ast.ListComp(elt=elt, generators=[comprehension])
        elif node.comp_type == "set":
            elt = node.expr.accept(self)
            return ast.SetComp(elt=elt, generators=[comprehension])
        elif node.comp_type == "dict":
            # For dict comprehensions, expr should contain key:value
            # This is a simplified implementation
            key = node.expr.accept(self)  # Should be the key part
            value = node.expr.accept(self)  # Should be the value part
            return ast.DictComp(key=key, value=value, generators=[comprehension])
        
        # Default to list comprehension
        elt = node.expr.accept(self)
        return ast.ListComp(elt=elt, generators=[comprehension])
    
    def visit_slice(self, node: SliceNode) -> ast.Subscript:
        """Visit slice node"""
        value = node.object_expr.accept(self)
        
        lower = None
        upper = None
        step = None
        
        if node.lower:
            lower = node.lower.accept(self)
        if node.upper:
            upper = node.upper.accept(self)
        if node.step:
            step = node.step.accept(self)
        
        slice_obj = ast.Slice(lower=lower, upper=upper, step=step)
        return ast.Subscript(value=value, slice=slice_obj, ctx=ast.Load())
    
    def visit_ellipsis(self, node: EllipsisNode) -> ast.Constant:
        """Visit ellipsis node"""
        return ast.Constant(value=...)
    
    def visit_union_type(self, node: UnionTypeNode) -> ast.Subscript:
        """Visit union type node (A | B becomes Union[A, B])"""
        # Import Union from typing
        self.type_imports.append('Union')
        
        # Create Union[...] subscript
        union_name = ast.Name(id='Union', ctx=ast.Load())
        
        # Convert types to AST nodes
        type_elts = []
        for type_node in node.types:
            if isinstance(type_node, IdentifierNode):
                name = self.type_map.get(type_node.name, type_node.name)
                type_elts.append(ast.Name(id=name, ctx=ast.Load()))
            else:
                type_elts.append(type_node.accept(self))
        
        slice_value = ast.Tuple(elts=type_elts, ctx=ast.Load())
        return ast.Subscript(value=union_name, slice=slice_value, ctx=ast.Load())
    
    def visit_intersection_type(self, node: IntersectionTypeNode) -> ast.Subscript:
        """Visit intersection type node (A & B)"""
        # For now, treat as Union since Python doesn't have intersection types natively
        # In practice, this would require a custom type system or Protocol
        return self.visit_union_type(UnionTypeNode(node.types, node.location))
    
    def visit_literal_type(self, node: LiteralTypeNode) -> ast.Subscript:
        """Visit literal type node (Literal["hello"])"""
        # Import Literal from typing
        self.type_imports.append('Literal')
        
        literal_name = ast.Name(id='Literal', ctx=ast.Load())
        value = ast.Constant(value=node.value)
        
        return ast.Subscript(value=literal_name, slice=value, ctx=ast.Load())
    
    def visit_optional_type(self, node: OptionalTypeNode) -> ast.Subscript:
        """Visit optional type node (T? becomes Union[T, None])"""
        self.type_imports.append('Union')
        
        union_name = ast.Name(id='Union', ctx=ast.Load())
        type_arg = node.type_expr.accept(self)
        none_type = ast.Constant(value=None)
        
        slice_value = ast.Tuple(elts=[type_arg, none_type], ctx=ast.Load())
        return ast.Subscript(value=union_name, slice=slice_value, ctx=ast.Load())
    
    def visit_generic_type(self, node: GenericTypeNode) -> ast.Subscript:
        """Visit generic type node (Array<T> becomes List<T>)"""
        # Map PowerScript types to Python types
        type_mapping = {
            'Array': 'List',
            'Dict': 'Dict',
            'Set': 'Set',
        }
        
        base_name = type_mapping.get(node.base_type, node.base_type)
        if base_name in ['List', 'Dict', 'Set']:
            self.type_imports.append(base_name)
        
        base_ast = ast.Name(id=base_name, ctx=ast.Load())
        
        # Convert type args
        type_elts = [arg.accept(self) for arg in node.type_args]
        
        if len(type_elts) == 1:
            slice_value = type_elts[0]
        else:
            slice_value = ast.Tuple(elts=type_elts, ctx=ast.Load())
        
        return ast.Subscript(value=base_ast, slice=slice_value, ctx=ast.Load())
    
    def visit_object_type(self, node: ObjectTypeNode) -> ast.Subscript:
        """Visit object type node ({name: string} becomes Dict[str, Any])"""
        self.type_imports.extend(['Dict', 'Any'])
        
        dict_name = ast.Name(id='Dict', ctx=ast.Load())
        str_type = ast.Name(id='str', ctx=ast.Load())
        any_type = ast.Name(id='Any', ctx=ast.Load())
        
        slice_value = ast.Tuple(elts=[str_type, any_type], ctx=ast.Load())
        return ast.Subscript(value=dict_name, slice=slice_value, ctx=ast.Load())
    
    def visit_generic_constraint(self, node: GenericConstraintNode) -> ast.Name:
        """Visit generic constraint node (T extends U)"""
        # For now, just return the type parameter name
        # Full constraint checking would require a type checker
        return ast.Name(id=node.type_param, ctx=ast.Load())
    
    def visit_type_alias(self, node: TypeAliasNode) -> ast.Assign:
        """Visit type alias node (type MyType = string | number)"""
        # Create assignment: MyType = Union[str, int]
        target = ast.Name(id=node.name, ctx=ast.Store())
        value = node.type_expr.accept(self)
        
        return ast.Assign(targets=[target], value=value)


def transpile_file(powerscript_source: str, filename: str = "") -> str:
    """Convenience function to transpile PowerScript source to Python"""
    from .lexer import Lexer
    from .parser import Parser
    
    # Lex and parse
    lexer = Lexer(powerscript_source, filename)
    lexer.tokenize()
    
    parser = Parser(lexer)
    ast_nodes = parser.parse()
    
    # Transpile
    transpiler = Transpiler()
    return transpiler.transpile_to_code(ast_nodes)