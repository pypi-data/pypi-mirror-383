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
from .lexer import Lexer, Token, TokenType
from .ast_nodes import *


class ParseError(Exception):
    """Exception raised during parsing"""
    
    def __init__(self, message: str, token: Token):
        self.message = message
        self.token = token
        super().__init__(f"{message} at line {token.location.line}, column {token.location.column}")


class Parser:
    """PowerScript recursive descent parser"""
    
    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.tokens = lexer.get_tokens()
        self.current = 0
    
    def parse(self) -> List[ASTNode]:
        """Parse tokens into AST"""
        statements = []
        
        while not self._is_at_end():
            stmt = self._declaration()
            if stmt:
                statements.append(stmt)
        
        return statements
    
    def _declaration(self) -> Optional[ASTNode]:
        """Parse top-level declarations"""
        try:
            if self._match(TokenType.IMPORT):
                return self._import_declaration()
            elif self._match(TokenType.EXPORT):
                return self._export_declaration()
            elif self._match(TokenType.CLASS):
                return self._class_declaration()
            elif self._match(TokenType.ENUM):
                return self._enum_declaration()
            elif self._match(TokenType.FUNCTION):
                return self._function_declaration()
            elif self._match(TokenType.ASYNC):
                if self._check(TokenType.FUNCTION):
                    return self._function_declaration(is_async=True)
                else:
                    self._error("Expected 'function' after 'async'")
            elif self._match(TokenType.LET, TokenType.CONST):
                return self._variable_declaration()
            elif self._match(TokenType.TYPE):
                return self._type_alias_declaration()
            else:
                return self._statement()
        except ParseError as e:
            self._synchronize()
            raise e
    
    def _class_declaration(self) -> ClassNode:
        """Parse class declaration"""
        name_token = self._consume(TokenType.IDENTIFIER, "Expected class name")
        name = name_token.value
        
        # Generic parameters
        generic_params = []
        if self._check(TokenType.LESS_THAN):
            generic_params = self._generic_parameters()
        
        # Base classes
        base_classes = []
        if self._match(TokenType.COLON) or self._match(TokenType.EXTENDS):  # Using : or extends for inheritance
            base_classes.append(self._consume(TokenType.IDENTIFIER, "Expected base class name").value)
            while self._match(TokenType.COMMA):
                base_classes.append(self._consume(TokenType.IDENTIFIER, "Expected base class name").value)
        
        self._consume(TokenType.LEFT_BRACE, "Expected '{' after class declaration")
        
        class_node = ClassNode(name, base_classes, generic_params, name_token.location)
        
        # Parse class body
        while not self._check(TokenType.RIGHT_BRACE) and not self._is_at_end():
            access_modifier = AccessModifier.PUBLIC
            
            # Check for access modifiers
            if self._match(TokenType.PRIVATE):
                access_modifier = AccessModifier.PRIVATE
            elif self._match(TokenType.PROTECTED):
                access_modifier = AccessModifier.PROTECTED
            elif self._match(TokenType.PUBLIC):
                access_modifier = AccessModifier.PUBLIC
            
            if self._check(TokenType.CONSTRUCTOR):
                constructor = self._constructor_declaration(access_modifier)
                class_node.constructor = constructor
            elif self._check(TokenType.FUNCTION) or self._check(TokenType.ASYNC):
                method = self._method_declaration(access_modifier)
                class_node.methods.append(method)
            elif self._check(TokenType.LET) or self._check(TokenType.CONST):
                field = self._field_declaration(access_modifier)
                class_node.fields.append(field)
            else:
                self._error("Expected constructor, method, or field declaration")
        
        self._consume(TokenType.RIGHT_BRACE, "Expected '}' after class body")
        return class_node
    
    def _enum_declaration(self) -> EnumNode:
        """Parse enum declaration"""
        name_token = self._consume(TokenType.IDENTIFIER, "Expected enum name")
        name = name_token.value
        
        self._consume(TokenType.LEFT_BRACE, "Expected '{' after enum name")
        
        values = []
        while not self._check(TokenType.RIGHT_BRACE) and not self._is_at_end():
            value_token = self._consume(TokenType.IDENTIFIER, "Expected enum value")
            values.append(value_token.value)
            if not self._match(TokenType.COMMA):
                break
        
        self._consume(TokenType.RIGHT_BRACE, "Expected '}' after enum values")
        return EnumNode(name, values, name_token.location)
    
    def _constructor_declaration(self, access_modifier: AccessModifier) -> FunctionNode:
        """Parse constructor declaration"""
        self._consume(TokenType.CONSTRUCTOR, "Expected 'constructor'")
        
        parameters = self._parameters()
        
        self._consume(TokenType.LEFT_BRACE, "Expected '{' after constructor parameters")
        body = self._block()
        
        constructor = FunctionNode("__init__", parameters, None, False, access_modifier, True, False, self._previous().location)
        constructor.body = body
        return constructor
    
    def _method_declaration(self, access_modifier: AccessModifier) -> FunctionNode:
        """Parse method declaration"""
        is_async = self._match(TokenType.ASYNC)
        self._consume(TokenType.FUNCTION, "Expected 'function'")
        
        name_token = self._consume(TokenType.IDENTIFIER, "Expected method name")
        name = name_token.value
        
        # Generic parameters
        generic_params = []
        if self._check(TokenType.LESS_THAN):
            generic_params = self._generic_parameters()
        
        parameters = self._parameters()
        
        # Return type
        return_type = None
        if self._match(TokenType.COLON):
            return_type = self._type_expression()
        
        self._consume(TokenType.LEFT_BRACE, "Expected '{' after method signature")
        body = self._block()
        
        method = FunctionNode(name, parameters, return_type, is_async, access_modifier, False, False, name_token.location)
        method.generic_params = generic_params
        method.body = body
        return method
    
    def _field_declaration(self, access_modifier: AccessModifier) -> VariableNode:
        """Parse field declaration"""
        is_const = self._match(TokenType.CONST)
        if not is_const:
            self._consume(TokenType.LET, "Expected 'let' or 'const'")
        
        name_token = self._consume(TokenType.IDENTIFIER, "Expected field name")
        name = name_token.value
        
        # Type annotation
        field_type = None
        if self._match(TokenType.COLON):
            field_type = self._type_annotation()
        
        # Initializer
        initializer = None
        if self._match(TokenType.ASSIGN):
            initializer = self._expression()
        
        self._consume(TokenType.SEMICOLON, "Expected ';' after field declaration")
        
        return VariableNode(name, field_type, initializer, is_const, access_modifier, name_token.location)
    
    def _function_declaration(self, is_async: bool = False) -> FunctionNode:
        """Parse function declaration"""
        # Note: 'function' token has already been consumed by _declaration()
        # unless this is an async function
        if is_async:
            self._consume(TokenType.FUNCTION, "Expected 'function' after 'async'")
        
        # Check for generator function (function*)
        is_generator = self._match(TokenType.MULTIPLY)
        
        name_token = self._consume(TokenType.IDENTIFIER, "Expected function name")
        name = name_token.value
        
        # Generic parameters
        generic_params = []
        if self._check(TokenType.LESS_THAN):
            generic_params = self._generic_parameters()
        
        parameters = self._parameters()
        
        # Return type
        return_type = None
        if self._match(TokenType.COLON):
            return_type = self._type_expression()
        
        self._consume(TokenType.LEFT_BRACE, "Expected '{' after function signature")
        body = self._block()
        
        function = FunctionNode(name, parameters, return_type, is_async, AccessModifier.PUBLIC, False, is_generator, name_token.location)
        function.generic_params = generic_params
        function.body = body
        return function
    
    def _variable_declaration(self) -> VariableNode:
        """Parse variable declaration"""
        is_const = self._previous().type == TokenType.CONST
        
        name_token = self._consume(TokenType.IDENTIFIER, "Expected variable name")
        name = name_token.value
        
        # Type annotation
        var_type = None
        if self._match(TokenType.COLON):
            var_type = self._type_expression()
        
        # Initializer
        initializer = None
        if self._match(TokenType.ASSIGN):
            initializer = self._expression()
        elif is_const:
            self._error("Const variables must be initialized")
        
        self._consume(TokenType.SEMICOLON, "Expected ';' after variable declaration")
        
        return VariableNode(name, var_type, initializer, is_const, AccessModifier.PUBLIC, name_token.location)
    
    def _import_declaration(self) -> ImportNode:
        """Parse import declaration: 
        - import defaultName from "module"
        - import { name1, name2 } from "module"  
        - import * as name from "module"
        """
        location = self._previous().location
        
        specifiers = []
        is_default_import = False
        module_name = ""
        
        if self._match(TokenType.MULTIPLY):
            # Namespace import: import * as name from "module"
            self._consume(TokenType.AS, "Expected 'as' after '*'")
            namespace_name = self._consume(TokenType.IDENTIFIER, "Expected namespace name after 'as'").value
            specifiers.append(ImportSpecifier("*", namespace_name))
            self._consume(TokenType.FROM, "Expected 'from' after namespace import")
            module_name = self._consume(TokenType.STRING, "Expected module name").value[1:-1]  # Remove quotes
        
        elif self._match(TokenType.LEFT_BRACE):
            # Named imports: import { name1, name2 } from "module"
            while not self._check(TokenType.RIGHT_BRACE) and not self._is_at_end():
                imported_name = self._consume(TokenType.IDENTIFIER, "Expected import name").value
                local_name = imported_name
                
                if self._match(TokenType.AS):
                    local_name = self._consume(TokenType.IDENTIFIER, "Expected local name after 'as'").value
                
                specifiers.append(ImportSpecifier(imported_name, local_name))
                
                if not self._match(TokenType.COMMA):
                    break
            
            self._consume(TokenType.RIGHT_BRACE, "Expected '}' after import specifiers")
            self._consume(TokenType.FROM, "Expected 'from' after import specifiers")
            module_name = self._consume(TokenType.STRING, "Expected module name").value[1:-1]  # Remove quotes
        
        elif self._check(TokenType.IDENTIFIER):
            # Default import: import defaultName from "module"
            default_name = self._consume(TokenType.IDENTIFIER, "Expected default import name").value
            specifiers.append(ImportSpecifier("default", default_name))
            is_default_import = True
            self._consume(TokenType.FROM, "Expected 'from' after default import")
            module_name = self._consume(TokenType.STRING, "Expected module name").value[1:-1]  # Remove quotes
        
        else:
            self._error("Expected import specifier or default import name")
        
        self._consume(TokenType.SEMICOLON, "Expected ';' after import declaration")
        return ImportNode(module_name, specifiers, is_default_import, location)
    
    def _export_declaration(self) -> ExportNode:
        """Parse export declaration:
        - export { name1, name2 }
        - export default expression
        - export class/function/variable
        """
        location = self._previous().location
        
        if self._match(TokenType.DEFAULT):
            # Export default
            if self._match(TokenType.CLASS):
                declaration = self._class_declaration()
            elif self._match(TokenType.FUNCTION):
                declaration = self._function_declaration()
            else:
                # Export default expression
                expr = self._expression()
                self._consume(TokenType.SEMICOLON, "Expected ';' after export default expression")
                declaration = expr
            
            return ExportNode(declaration=declaration, is_default=True, location=location)
        
        elif self._match(TokenType.LEFT_BRACE):
            # Named exports: export { name1, name2 }
            specifiers = []
            
            while not self._check(TokenType.RIGHT_BRACE) and not self._is_at_end():
                local_name = self._consume(TokenType.IDENTIFIER, "Expected export name").value
                exported_name = local_name
                
                if self._match(TokenType.AS):
                    exported_name = self._consume(TokenType.IDENTIFIER, "Expected exported name after 'as'").value
                
                specifiers.append(ExportSpecifier(local_name, exported_name))
                
                if not self._match(TokenType.COMMA):
                    break
            
            self._consume(TokenType.RIGHT_BRACE, "Expected '}' after export specifiers")
            self._consume(TokenType.SEMICOLON, "Expected ';' after export declaration")
            
            return ExportNode(specifiers=specifiers, location=location)
        
        else:
            # Export declaration: export class/function/variable
            if self._match(TokenType.CLASS):
                declaration = self._class_declaration()
            elif self._match(TokenType.FUNCTION):
                declaration = self._function_declaration()
            elif self._match(TokenType.LET, TokenType.CONST):
                declaration = self._variable_declaration()
            else:
                self._error("Expected exportable declaration after 'export'")
            
            return ExportNode(declaration=declaration, location=location)
    
    def _parameters(self) -> List[ParameterNode]:
        """Parse function parameters"""
        self._consume(TokenType.LEFT_PAREN, "Expected '(' before parameters")
        
        parameters = []
        if not self._check(TokenType.RIGHT_PAREN):
            parameters.append(self._parameter())
            while self._match(TokenType.COMMA):
                parameters.append(self._parameter())
        
        self._consume(TokenType.RIGHT_PAREN, "Expected ')' after parameters")
        return parameters
    
    def _parameter(self) -> ParameterNode:
        """Parse single parameter"""
        name_token = self._consume(TokenType.IDENTIFIER, "Expected parameter name")
        name = name_token.value
        
        # Type annotation
        param_type = None
        if self._match(TokenType.COLON):
            param_type = self._type_expression()
        
        # Default value
        default_value = None
        if self._match(TokenType.ASSIGN):
            default_value = self._expression()
        
        return ParameterNode(name, param_type, default_value, name_token.location)
    
    def _generic_parameters(self) -> List[str]:
        """Parse generic type parameters"""
        self._consume(TokenType.LESS_THAN, "Expected '<' for generic parameters")
        
        params = []
        params.append(self._consume(TokenType.IDENTIFIER, "Expected generic parameter name").value)
        
        while self._match(TokenType.COMMA):
            params.append(self._consume(TokenType.IDENTIFIER, "Expected generic parameter name").value)
        
        self._consume(TokenType.GREATER_THAN, "Expected '>' after generic parameters")
        return params
    
    def _type_annotation(self) -> str:
        """Parse type annotation"""
        type_name = self._consume(TokenType.IDENTIFIER, "Expected type name").value
        
        # Handle generic types like Array<T>
        if self._match(TokenType.LESS_THAN):
            type_name += "<"
            type_name += self._type_annotation()
            while self._match(TokenType.COMMA):
                type_name += ", " + self._type_annotation()
            self._consume(TokenType.GREATER_THAN, "Expected '>' after generic type parameters")
            type_name += ">"
        
        # Handle array types
        while self._match(TokenType.LEFT_BRACKET):
            self._consume(TokenType.RIGHT_BRACKET, "Expected ']' after '['")
            type_name += "[]"
        
        # Handle optional types
        if self._match(TokenType.QUESTION):
            type_name += "?"
        
        return type_name
    
    def _type_alias_declaration(self) -> TypeAliasNode:
        """Parse type alias declaration: type MyType = string | number"""
        location = self._previous().location
        
        name_token = self._consume(TokenType.IDENTIFIER, "Expected type alias name")
        name = name_token.value
        
        self._consume(TokenType.ASSIGN, "Expected '=' after type alias name")
        
        type_expr = self._type_expression()
        
        self._consume(TokenType.SEMICOLON, "Expected ';' after type alias")
        
        return TypeAliasNode(name, type_expr, location)
    
    def _type_expression(self) -> ExpressionNode:
        """Parse type expression (with union, intersection, etc.)"""
        return self._union_type()
    
    def _union_type(self) -> ExpressionNode:
        """Parse union type: A | B | C"""
        expr = self._intersection_type()
        
        types = [expr]
        while self._match(TokenType.BIT_OR):  # Using | for union types
            types.append(self._intersection_type())
        
        if len(types) == 1:
            return types[0]
        else:
            return UnionTypeNode(types, expr.location)
    
    def _intersection_type(self) -> ExpressionNode:
        """Parse intersection type: A & B & C"""
        expr = self._primary_type()
        
        types = [expr]
        while self._match(TokenType.BIT_AND):  # Using & for intersection types
            types.append(self._primary_type())
        
        if len(types) == 1:
            return types[0]
        else:
            return IntersectionTypeNode(types, expr.location)
    
    def _primary_type(self) -> ExpressionNode:
        """Parse primary type expression"""
        if self._match(TokenType.IDENTIFIER):
            type_expr = IdentifierNode(self._previous().value, self._previous().location)
            # Check for generic type
            if self._check(TokenType.LESS_THAN):
                self._advance()  # consume <
                type_args = []
                type_args.append(self._type_expression())
                while self._match(TokenType.COMMA):
                    type_args.append(self._type_expression())
                self._consume(TokenType.GREATER_THAN, "Expected '>' after type arguments")
                type_expr = GenericTypeNode(self._previous().value, type_args, self._previous().location)
            # Check for optional
            if self._match(TokenType.QUESTION):
                type_expr = OptionalTypeNode(type_expr, self._previous().location)
            return type_expr
        
        if self._match(TokenType.LEFT_BRACE):
            properties = {}
            while not self._check(TokenType.RIGHT_BRACE) and not self._is_at_end():
                key_token = self._consume(TokenType.IDENTIFIER, "Expected property name")
                self._consume(TokenType.COLON, "Expected ':' after property name")
                prop_type = self._type_expression()
                properties[key_token.value] = prop_type
                if not self._match(TokenType.COMMA):
                    break
            self._consume(TokenType.RIGHT_BRACE, "Expected '}' after object type")
            return ObjectTypeNode(properties, self._previous().location)
        
        if self._match(TokenType.STRING, TokenType.NUMBER, TokenType.BOOLEAN, TokenType.NULL):
            value = self._previous().value
            if self._previous().type == TokenType.BOOLEAN:
                value = value == "true"
            elif self._previous().type == TokenType.NUMBER:
                value = float(value) if '.' in value else int(value)
            elif self._previous().type == TokenType.NULL:
                value = None
            else:
                # Remove quotes from string
                value = value[1:-1]
            return LiteralTypeNode(value, self._previous().location)
        
        if self._match(TokenType.LEFT_PAREN):
            expr = self._type_expression()
            self._consume(TokenType.RIGHT_PAREN, "Expected ')' after type expression")
            return expr
        
        raise self._error("Expected type expression")
    
    def _statement(self) -> ASTNode:
        """Parse statement"""
        if self._match(TokenType.IF):
            return self._if_statement()
        elif self._match(TokenType.WHILE):
            return self._while_statement()
        elif self._match(TokenType.FOR):
            return self._for_statement()
        elif self._match(TokenType.SWITCH):
            return self._switch_statement()
        elif self._match(TokenType.TRY):
            return self._try_statement()
        elif self._match(TokenType.THROW):
            return self._throw_statement()
        elif self._match(TokenType.RETURN):
            return self._return_statement()
        elif self._match(TokenType.BREAK):
            return self._break_statement()
        elif self._match(TokenType.CONTINUE):
            return self._continue_statement()
        elif self._match(TokenType.WITH):
            return self._with_statement()
        elif self._match(TokenType.YIELD):
            return self._yield_statement()
        elif self._match(TokenType.LEFT_BRACE):
            return BlockNode(self._block().statements, self._previous().location)
        else:
            return self._expression_statement()
    
    def _if_statement(self) -> IfNode:
        """Parse if statement"""
        self._consume(TokenType.LEFT_PAREN, "Expected '(' after 'if'")
        condition = self._expression()
        self._consume(TokenType.RIGHT_PAREN, "Expected ')' after if condition")
        
        then_block = self._statement_as_block()
        
        else_block = None
        if self._match(TokenType.ELSE):
            else_block = self._statement_as_block()
        
        return IfNode(condition, then_block, else_block, condition.location)
    
    def _while_statement(self) -> WhileNode:
        """Parse while statement"""
        self._consume(TokenType.LEFT_PAREN, "Expected '(' after 'while'")
        condition = self._expression()
        self._consume(TokenType.RIGHT_PAREN, "Expected ')' after while condition")
        
        body = self._statement_as_block()
        return WhileNode(condition, body, condition.location)
    
    def _for_statement(self) -> ForNode:
        """Parse for statement"""
        self._consume(TokenType.LEFT_PAREN, "Expected '(' after 'for'")
        
        variable = self._consume(TokenType.IDENTIFIER, "Expected variable name in for loop").value
        self._consume(TokenType.IN, "Expected 'in' in for loop")
        iterable = self._expression()
        
        self._consume(TokenType.RIGHT_PAREN, "Expected ')' after for clause")
        
        body = self._statement_as_block()
        return ForNode(variable, iterable, body, iterable.location)
    
    def _switch_statement(self) -> SwitchNode:
        """Parse switch statement: switch (expr) { case value: ... default: ... }"""
        location = self._previous().location
        
        self._consume(TokenType.LEFT_PAREN, "Expected '(' after 'switch'")
        expression = self._expression()
        self._consume(TokenType.RIGHT_PAREN, "Expected ')' after switch expression")
        
        self._consume(TokenType.LEFT_BRACE, "Expected '{' before switch body")
        
        cases = []
        default_case = None
        
        while not self._check(TokenType.RIGHT_BRACE) and not self._is_at_end():
            if self._match(TokenType.CASE):
                case_node = self._case_clause()
                cases.append(case_node)
            elif self._match(TokenType.DEFAULT):
                if default_case is not None:
                    self._error("Multiple default cases in switch statement")
                self._consume(TokenType.COLON, "Expected ':' after 'default'")
                statements = []
                while not self._check(TokenType.CASE) and not self._check(TokenType.DEFAULT) and not self._check(TokenType.RIGHT_BRACE) and not self._is_at_end():
                    statements.append(self._statement())
                default_case = CaseNode([], BlockNode(statements, self._previous().location), is_default=True, location=self._previous().location)
            else:
                self._error("Expected 'case' or 'default' in switch statement")
        
        self._consume(TokenType.RIGHT_BRACE, "Expected '}' after switch body")
        return SwitchNode(expression, cases, default_case, location)
    
    def _case_clause(self) -> CaseNode:
        """Parse case clause: case value1, value2: statements"""
        location = self._previous().location
        
        values = [self._expression()]
        while self._match(TokenType.COMMA):
            values.append(self._expression())
        
        self._consume(TokenType.COLON, "Expected ':' after case values")
        
        statements = []
        while not self._check(TokenType.CASE) and not self._check(TokenType.DEFAULT) and not self._check(TokenType.RIGHT_BRACE) and not self._is_at_end():
            statements.append(self._statement())
        
        return CaseNode(values, BlockNode(statements, location), is_default=False, location=location)
    
    def _return_statement(self) -> ReturnNode:
        """Parse return statement"""
        location = self._previous().location
        
        value = None
        if not self._check(TokenType.SEMICOLON) and not self._is_at_end():
            value = self._expression()
        
        self._consume(TokenType.SEMICOLON, "Expected ';' after return value")
        return ReturnNode(value, location)
    
    def _break_statement(self) -> BreakNode:
        """Parse break statement"""
        location = self._previous().location
        self._consume(TokenType.SEMICOLON, "Expected ';' after break")
        return BreakNode(location)
    
    def _continue_statement(self) -> ContinueNode:
        """Parse continue statement"""
        location = self._previous().location
        self._consume(TokenType.SEMICOLON, "Expected ';' after continue")
        return ContinueNode(location)
    
    def _try_statement(self) -> TryNode:
        """Parse try-catch-finally statement"""
        location = self._previous().location
        
        # Parse try block
        self._consume(TokenType.LEFT_BRACE, "Expected '{' after 'try'")
        try_block = self._block()
        
        # Parse catch clauses
        catch_clauses = []
        while self._match(TokenType.CATCH):
            catch_clauses.append(self._catch_clause())
        
        # Parse optional finally block
        finally_block = None
        if self._match(TokenType.FINALLY):
            self._consume(TokenType.LEFT_BRACE, "Expected '{' after 'finally'")
            finally_block = self._block()
        
        # Must have at least catch or finally
        if not catch_clauses and not finally_block:
            self._error("Try statement must have at least one catch or finally clause")
        
        return TryNode(try_block, catch_clauses, finally_block, location)
    
    def _catch_clause(self) -> CatchNode:
        """Parse catch clause"""
        location = self._previous().location
        
        # Parse optional exception parameter
        exception_name = None
        exception_type = None
        
        if self._match(TokenType.LEFT_PAREN):
            if self._match(TokenType.IDENTIFIER):
                exception_name = self._previous().value
                
                # Optional type annotation
                if self._match(TokenType.COLON):
                    exception_type = self._parse_type()
            
            self._consume(TokenType.RIGHT_PAREN, "Expected ')' after catch parameter")
        
        # Parse catch body
        self._consume(TokenType.LEFT_BRACE, "Expected '{' after catch clause")
        body = self._block()
        
        return CatchNode(exception_name, exception_type, body, location)
    
    def _throw_statement(self) -> ThrowNode:
        """Parse throw statement"""
        location = self._previous().location
        
        expression = self._expression()
        self._consume(TokenType.SEMICOLON, "Expected ';' after throw expression")
        
        return ThrowNode(expression, location)
    
    def _statement_as_block(self) -> BlockNode:
        """Convert statement to block if needed"""
        if self._check(TokenType.LEFT_BRACE):
            self._advance()
            return self._block()
        else:
            stmt = self._statement()
            return BlockNode([stmt], stmt.location)
    
    def _block(self) -> BlockNode:
        """Parse block statement (assumes { already consumed)"""
        statements = []
        location = self._previous().location
        
        while not self._check(TokenType.RIGHT_BRACE) and not self._is_at_end():
            stmt = self._declaration()
            if stmt:
                statements.append(stmt)
        
        self._consume(TokenType.RIGHT_BRACE, "Expected '}' after block")
        return BlockNode(statements, location)
    
    def _expression_statement(self) -> ExpressionStatementNode:
        """Parse expression statement"""
        expr = self._expression()
        self._consume(TokenType.SEMICOLON, "Expected ';' after expression")
        return ExpressionStatementNode(expr, expr.location)
    
    def _expression(self) -> ExpressionNode:
        """Parse expression"""
        return self._assignment()
    
    def _assignment(self) -> ExpressionNode:
        """Parse assignment expression"""
        expr = self._arrow_function()
        
        if self._match(TokenType.ASSIGN, TokenType.PLUS_ASSIGN, TokenType.MINUS_ASSIGN,
                      TokenType.MULTIPLY_ASSIGN, TokenType.DIVIDE_ASSIGN, 
                      TokenType.MODULO_ASSIGN, TokenType.POWER_ASSIGN):
            operator = self._previous()
            value = self._assignment()
            
            if isinstance(expr, IdentifierNode):
                return AssignmentNode(expr, value, operator.location, operator.value)
            
            self._error("Invalid assignment target")
        
        return expr
    
    def _arrow_function(self) -> ExpressionNode:
        """Parse arrow function: (x, y) => x + y or x => x * 2 or () => { block }"""
        # Check for arrow function patterns
        if self._check(TokenType.IDENTIFIER):
            # Look ahead for arrow: x => ...
            if self.current + 1 < len(self.tokens) and self.tokens[self.current + 1].type == TokenType.ARROW:
                # Single parameter arrow function
                param_name = self._advance().value
                self._consume(TokenType.ARROW, "Expected '=>'")
                
                # Check if body is a block or expression
                if self._check(TokenType.LEFT_BRACE):
                    # Block body: x => { statements }
                    body_block = self._block()
                    param = ParameterNode(param_name, None, None, self._previous().location)
                    return LambdaNode([param], body_block, self._previous().location)
                else:
                    # Expression body: x => expression
                    body = self._assignment()
                    param = ParameterNode(param_name, None, None, self._previous().location)
                    return LambdaNode([param], body, self._previous().location)
        
        elif self._check(TokenType.LEFT_PAREN):
            # Look ahead for potential arrow function: (params) => ...
            saved_pos = self.current
            try:
                self._advance()  # consume '('
                
                # Try to parse parameter list
                params = []
                if not self._check(TokenType.RIGHT_PAREN):
                    param_name = self._consume(TokenType.IDENTIFIER, "Expected parameter name").value
                    param_type = None
                    # Support type annotations: (x: number) => ...
                    if self._match(TokenType.COLON):
                        param_type = self._type_expression()
                    params.append(ParameterNode(param_name, param_type, None, self._previous().location))
                    
                    while self._match(TokenType.COMMA):
                        param_name = self._consume(TokenType.IDENTIFIER, "Expected parameter name").value
                        param_type = None
                        # Support type annotations
                        if self._match(TokenType.COLON):
                            param_type = self._type_expression()
                        params.append(ParameterNode(param_name, param_type, None, self._previous().location))
                
                self._consume(TokenType.RIGHT_PAREN, "Expected ')' after parameters")
                
                if self._match(TokenType.ARROW):
                    # This is an arrow function
                    # Check if body is a block or expression
                    if self._check(TokenType.LEFT_BRACE):
                        # Block body: () => { statements }
                        body_block = self._block()
                        return LambdaNode(params, body_block, self._previous().location)
                    else:
                        # Expression body: () => expression
                        body = self._assignment()
                        return LambdaNode(params, body, self._previous().location)
                
            except ParseError:
                pass
            
            # Reset position if not an arrow function
            self.current = saved_pos
        
        return self._or()
    
    def _or(self) -> ExpressionNode:
        """Parse logical OR expression"""
        expr = self._and()
        
        while self._match(TokenType.OR):
            operator = self._previous()
            right = self._and()
            expr = BinaryOpNode(expr, operator.value, right, operator.location)
        
        return expr
    
    def _and(self) -> ExpressionNode:
        """Parse logical AND expression"""
        expr = self._bitwise_or()
        
        while self._match(TokenType.AND):
            operator = self._previous()
            right = self._bitwise_or()
            expr = BinaryOpNode(expr, operator.value, right, operator.location)
        
        return expr
    
    def _bitwise_or(self) -> ExpressionNode:
        """Parse bitwise OR expression"""
        expr = self._bitwise_xor()
        
        while self._match(TokenType.BIT_OR):
            operator = self._previous()
            right = self._bitwise_xor()
            expr = BinaryOpNode(expr, operator.value, right, operator.location)
        
        return expr
    
    def _bitwise_xor(self) -> ExpressionNode:
        """Parse bitwise XOR expression"""
        expr = self._bitwise_and()
        
        while self._match(TokenType.BIT_XOR):
            operator = self._previous()
            right = self._bitwise_and()
            expr = BinaryOpNode(expr, operator.value, right, operator.location)
        
        return expr
    
    def _bitwise_and(self) -> ExpressionNode:
        """Parse bitwise AND expression"""
        expr = self._equality()
        
        while self._match(TokenType.BIT_AND):
            operator = self._previous()
            right = self._equality()
            expr = BinaryOpNode(expr, operator.value, right, operator.location)
        
        return expr
    
    def _equality(self) -> ExpressionNode:
        """Parse equality expression"""
        expr = self._comparison()
        
        while self._match(TokenType.EQUAL, TokenType.NOT_EQUAL):
            operator = self._previous()
            right = self._comparison()
            expr = BinaryOpNode(expr, operator.value, right, operator.location)
        
        return expr
    
    def _comparison(self) -> ExpressionNode:
        """Parse comparison expression"""
        expr = self._shift()
        
        while self._match(TokenType.GREATER_THAN, TokenType.GREATER_EQUAL, 
                          TokenType.LESS_THAN, TokenType.LESS_EQUAL):
            operator = self._previous()
            right = self._shift()
            expr = BinaryOpNode(expr, operator.value, right, operator.location)
        
        return expr
    
    def _shift(self) -> ExpressionNode:
        """Parse shift expression (<< >>)"""
        expr = self._term()
        
        while self._match(TokenType.LEFT_SHIFT, TokenType.RIGHT_SHIFT):
            operator = self._previous()
            right = self._term()
            expr = BinaryOpNode(expr, operator.value, right, operator.location)
        
        return expr
    
    def _term(self) -> ExpressionNode:
        """Parse term expression (+ -)"""
        expr = self._factor()
        
        while self._match(TokenType.MINUS, TokenType.PLUS):
            operator = self._previous()
            right = self._factor()
            expr = BinaryOpNode(expr, operator.value, right, operator.location)
        
        return expr
    
    def _factor(self) -> ExpressionNode:
        """Parse factor expression (* / %)"""
        expr = self._unary()
        
        while self._match(TokenType.DIVIDE, TokenType.MULTIPLY, TokenType.MODULO):
            operator = self._previous()
            right = self._unary()
            expr = BinaryOpNode(expr, operator.value, right, operator.location)
        
        return expr
    
    def _unary(self) -> ExpressionNode:
        """Parse unary expression"""
        if self._match(TokenType.AWAIT):
            operator = self._previous()
            right = self._unary()
            return AwaitNode(right, operator.location)
        
        if self._match(TokenType.NOT, TokenType.MINUS, TokenType.PLUS, TokenType.BIT_NOT):
            operator = self._previous()
            right = self._unary()
            return UnaryOpNode(operator.value, right, operator.location)
        
        return self._call()
    
    def _call(self) -> ExpressionNode:
        """Parse function call expression"""
        expr = self._primary()
        
        while True:
            if self._match(TokenType.LEFT_PAREN):
                expr = self._finish_call(expr)
            elif self._match(TokenType.DOT):
                name = self._consume(TokenType.IDENTIFIER, "Expected property name after '.'")
                expr = BinaryOpNode(expr, ".", IdentifierNode(name.value, name.location), name.location)
            elif self._match(TokenType.LEFT_BRACKET):
                index = self._expression()
                self._consume(TokenType.RIGHT_BRACKET, "Expected ']' after index")
                expr = BinaryOpNode(expr, "[]", index, expr.location)
            else:
                break
        
        return expr
    
    def _finish_call(self, callee: ExpressionNode) -> CallNode:
        """Finish parsing function call"""
        arguments = []
        
        if not self._check(TokenType.RIGHT_PAREN):
            arguments.append(self._expression())
            while self._match(TokenType.COMMA):
                if len(arguments) >= 255:
                    self._error("Can't have more than 255 arguments")
                arguments.append(self._expression())
        
        paren = self._consume(TokenType.RIGHT_PAREN, "Expected ')' after arguments")
        return CallNode(callee, arguments, paren.location)
    
    def _primary(self) -> ExpressionNode:
        """Parse primary expression"""
        if self._match(TokenType.LAMBDA):
            return self._lambda_expression()
        
        if self._match(TokenType.ELLIPSIS):
            return EllipsisNode(self._previous().location)
        
        if self._match(TokenType.BOOLEAN):
            value = self._previous().value == "true"
            return LiteralNode(value, "boolean", self._previous().location)
        
        if self._match(TokenType.NULL):
            return LiteralNode(None, "null", self._previous().location)
        
        if self._match(TokenType.NUMBER):
            value = self._previous().value
            location = self._previous().location
            
            # Handle different number formats
            try:
                if value.startswith('0x') or value.startswith('0X'):
                    # Hexadecimal
                    parsed_value = int(value, 16)
                elif value.startswith('0b') or value.startswith('0B'):
                    # Binary
                    parsed_value = int(value, 2)
                elif value.startswith('0o') or value.startswith('0O'):
                    # Octal
                    parsed_value = int(value, 8)
                elif 'e' in value.lower() or 'E' in value:
                    # Scientific notation
                    parsed_value = float(value)
                elif '.' in value:
                    # Regular float
                    parsed_value = float(value)
                else:
                    # Regular integer
                    parsed_value = int(value)
                    
                return LiteralNode(parsed_value, "number", location)
            except ValueError:
                # If conversion fails, keep as string and let transpiler handle it
                return LiteralNode(value, "number", location)
        
        if self._match(TokenType.STRING):
            value = self._previous().value
            # Remove quotes
            value = value[1:-1]
            return LiteralNode(value, "string", self._previous().location)
        
        if self._match(TokenType.F_STRING):
            return self._f_string()
        
        if self._match(TokenType.TEMPLATE_LITERAL):
            return self._template_literal()
        
        if self._match(TokenType.IDENTIFIER):
            return IdentifierNode(self._previous().value, self._previous().location)
        
        if self._match(TokenType.LEFT_PAREN):
            expr = self._expression()
            self._consume(TokenType.RIGHT_PAREN, "Expected ')' after expression")
            return expr
        
        if self._match(TokenType.LEFT_BRACKET):
            return self._array_or_list_comprehension()
        
        if self._match(TokenType.LEFT_BRACE):
            return self._object_or_comprehension()
        
        raise self._error("Expected expression")
    
    def _lambda_expression(self) -> LambdaNode:
        """Parse lambda expression: lambda x, y: x + y"""
        location = self._previous().location
        
        # Parse parameters
        parameters = []
        if not self._check(TokenType.COLON):
            if self._match(TokenType.IDENTIFIER):
                param_name = self._previous().value
                parameters.append(ParameterNode(param_name, "any", location=self._previous().location))
                
                while self._match(TokenType.COMMA):
                    self._consume(TokenType.IDENTIFIER, "Expected parameter name")
                    param_name = self._previous().value
                    parameters.append(ParameterNode(param_name, "any", location=self._previous().location))
        
        self._consume(TokenType.COLON, "Expected ':' after lambda parameters")
        body = self._expression()
        
        return LambdaNode(parameters, body, location)
    
    def _with_statement(self) -> WithNode:
        """Parse with statement: with expr as var { body }"""
        location = self._previous().location
        context_expr = self._expression()
        
        optional_vars = None
        if self._match(TokenType.AS):
            var_token = self._consume(TokenType.IDENTIFIER, "Expected variable name after 'as'")
            optional_vars = IdentifierNode(var_token.value, var_token.location)
        
        self._consume(TokenType.LEFT_BRACE, "Expected '{' after with expression")
        body = self._block()
        
        return WithNode(context_expr, optional_vars, body, location)
    
    def _yield_statement(self) -> YieldNode:
        """Parse yield statement: yield value; or yield from iterable;"""
        location = self._previous().location
        value = None
        is_yield_from = False
        
        # Check for 'yield from'
        if self._match(TokenType.FROM):
            is_yield_from = True
            value = self._expression()
        elif not self._check(TokenType.SEMICOLON):
            value = self._expression()
        
        self._consume(TokenType.SEMICOLON, "Expected ';' after yield statement")
        return YieldNode(value, is_yield_from, location)
    
    def _yield_expression(self) -> YieldNode:
        """Parse yield expression: yield value or yield from iterable (without semicolon)"""
        location = self._peek().location  # Use peek since we haven't consumed YIELD yet
        value = None
        is_yield_from = False
        
        # Check for 'yield from'
        if self._match(TokenType.FROM):
            is_yield_from = True
            value = self._expression()
        elif not self._check(TokenType.SEMICOLON) and not self._check(TokenType.RIGHT_PAREN) and not self._check(TokenType.RIGHT_BRACE) and not self._is_at_end():
            value = self._expression()
        
        return YieldNode(value, is_yield_from, location)
    
    def _array_or_list_comprehension(self) -> Union[ArrayLiteralNode, ComprehensionNode]:
        """Parse array literal or list comprehension: [1, 2, 3] or [x for x in list]"""
        location = self._previous().location
        
        # Empty array
        if self._match(TokenType.RIGHT_BRACKET):
            return ArrayLiteralNode([], location)
        
        # Parse first expression
        expr = self._expression()
        
        # Check if this is a comprehension (look for 'for' keyword)
        if self._match(TokenType.FOR):
            # This is a list comprehension: [expr for x in iterable]
            target_token = self._consume(TokenType.IDENTIFIER, "Expected variable name in comprehension")
            target = IdentifierNode(target_token.value, target_token.location)
            
            self._consume(TokenType.IN, "Expected 'in' after comprehension variable")
            iterable = self._expression()
            
            # Optional conditions
            conditions = []
            while self._match(TokenType.IF):
                conditions.append(self._expression())
            
            self._consume(TokenType.RIGHT_BRACKET, "Expected ']' after list comprehension")
            return ComprehensionNode(expr, target, iterable, conditions, "list", location)
        else:
            # This is an array literal: [1, 2, 3]
            elements = [expr]
            while self._match(TokenType.COMMA):
                if self._check(TokenType.RIGHT_BRACKET):  # Trailing comma
                    break
                elements.append(self._expression())
            
            self._consume(TokenType.RIGHT_BRACKET, "Expected ']' after array elements")
            return ArrayLiteralNode(elements, location)
    
    def _object_or_comprehension(self) -> Union[ObjectLiteralNode, ComprehensionNode]:
        """Parse object literal, set comprehension, or dict comprehension"""
        location = self._previous().location
        
        # Empty object/set
        if self._match(TokenType.RIGHT_BRACE):
            return ObjectLiteralNode([], location)
        
        # Parse first expression or key:value pair
        first_expr = self._expression()
        
        # Check for dict comprehension: {key: value for x in iterable}
        if self._match(TokenType.COLON):
            value_expr = self._expression()
            
            if self._match(TokenType.FOR):
                # Dict comprehension: {key: value for x in iterable}
                target_token = self._consume(TokenType.IDENTIFIER, "Expected variable name in comprehension")
                target = IdentifierNode(target_token.value, target_token.location)
                
                self._consume(TokenType.IN, "Expected 'in' after comprehension variable")
                iterable = self._expression()
                
                conditions = []
                while self._match(TokenType.IF):
                    conditions.append(self._expression())
                
                self._consume(TokenType.RIGHT_BRACE, "Expected '}' after dict comprehension")
                # For dict comprehension, we need to store both key and value
                # For now, create a simple key-value pair structure
                return ComprehensionNode(first_expr, target, iterable, conditions, "dict", location)
            else:
                # Regular object literal: {key: value, ...}
                properties = [(first_expr, value_expr)]
                while self._match(TokenType.COMMA):
                    if self._check(TokenType.RIGHT_BRACE):  # Trailing comma
                        break
                    key = self._expression()
                    self._consume(TokenType.COLON, "Expected ':' after object key")
                    value = self._expression()
                    properties.append((key, value))
                
                self._consume(TokenType.RIGHT_BRACE, "Expected '}' after object literal")
                return ObjectLiteralNode(properties, location)
        
        # Check for set comprehension: {expr for x in iterable}
        elif self._match(TokenType.FOR):
            # Set comprehension: {expr for x in iterable}
            target_token = self._consume(TokenType.IDENTIFIER, "Expected variable name in comprehension")
            target = IdentifierNode(target_token.value, target_token.location)
            
            self._consume(TokenType.IN, "Expected 'in' after comprehension variable")
            iterable = self._expression()
            
            conditions = []
            while self._match(TokenType.IF):
                conditions.append(self._expression())
            
            self._consume(TokenType.RIGHT_BRACE, "Expected '}' after set comprehension")
            return ComprehensionNode(first_expr, target, iterable, conditions, "set", location)
        else:
            # Set literal: {1, 2, 3}
            elements = [first_expr]
            while self._match(TokenType.COMMA):
                if self._check(TokenType.RIGHT_BRACE):  # Trailing comma
                    break
                elements.append(self._expression())
            
            self._consume(TokenType.RIGHT_BRACE, "Expected '}' after set literal")
            return SetLiteralNode(elements, location)
    
    def _comprehension_expression(self) -> ComprehensionNode:
        """Parse list/dict/set comprehensions: [expr for x in iterable if condition]"""
        # This method is now replaced by _array_or_list_comprehension and _object_or_comprehension
        location = self._peek().location
        
        # Parse the expression
        expr = self._expression()
        
        self._consume(TokenType.FOR, "Expected 'for' in comprehension")
        self._consume(TokenType.IDENTIFIER, "Expected target variable")
        target = IdentifierNode(self._previous().value, self._previous().location)
        
        self._consume(TokenType.IN, "Expected 'in' after comprehension target")
        iterable = self._expression()
        
        conditions = []
        while self._match(TokenType.IF):
            conditions.append(self._expression())
        
        return ComprehensionNode(expr, target, iterable, conditions, "list", location)
    
    def _slice_expression(self, object_expr: ExpressionNode) -> SliceNode:
        """Parse slice expression: obj[start:end:step]"""
        location = self._peek().location
        
        lower = None
        upper = None
        step = None
        
        # Parse lower bound
        if not self._check(TokenType.COLON):
            lower = self._expression()
        
        if self._match(TokenType.COLON):
            # Parse upper bound
            if not self._check(TokenType.COLON) and not self._check(TokenType.RIGHT_BRACKET):
                upper = self._expression()
            
            # Parse step
            if self._match(TokenType.COLON):
                if not self._check(TokenType.RIGHT_BRACKET):
                    step = self._expression()
        
        return SliceNode(object_expr, lower, upper, step, location)
    
    def _f_string(self) -> FStringNode:
        """Parse f-string with expression interpolation: f"Hello {name}!" """
        import re
        
        location = self._previous().location
        value = self._previous().value
        # Remove f" or f' and closing quote
        if value.startswith('f"'):
            content = value[2:-1]
        else:  # f'...'
            content = value[2:-1]
        
        expressions = []
        
        # Simple regex to find {expr} patterns
        # This is a basic implementation - a full implementation would need proper parsing
        expr_pattern = r'\{([^}]+)\}'
        matches = list(re.finditer(expr_pattern, content))
        
        for match in matches:
            expr_str = match.group(1)
            # Create a mini-parser for the expression
            try:
                # Parse the expression string as PowerScript code
                from .lexer import Lexer
                lexer = Lexer()
                expr_tokens = lexer.tokenize(expr_str)
                # Create a sub-parser for the expression
                sub_parser = Parser(expr_tokens)
                sub_parser.current = 0
                expr_ast = sub_parser._expression()
                expressions.append(expr_ast)
            except Exception:
                # If parsing fails, treat as identifier
                expressions.append(IdentifierNode(expr_str, location))
        
        return FStringNode(value, expressions, location)

    def _template_literal(self) -> TemplateLiteralNode:
        """Parse template literal with expression interpolation: `Hello ${name}!`"""
        import re
        
        location = self._previous().location
        value = self._previous().value
        # Remove backticks
        content = value[1:-1]
        
        expressions = []
        
        # Find ${expr} patterns
        expr_pattern = r'\$\{([^}]+)\}'
        matches = list(re.finditer(expr_pattern, content))
        
        for match in matches:
            expr_str = match.group(1)
            # Create a mini-parser for the expression
            try:
                # Parse the expression string as PowerScript code
                from .lexer import Lexer
                lexer = Lexer()
                expr_tokens = lexer.tokenize(expr_str)
                # Create a sub-parser for the expression
                sub_parser = Parser(expr_tokens)
                sub_parser.current = 0
                expr_ast = sub_parser._expression()
                expressions.append(expr_ast)
            except Exception:
                # If parsing fails, treat as identifier
                expressions.append(IdentifierNode(expr_str, location))
        
        return TemplateLiteralNode(value, expressions, location)

    # Helper methods
    def _match(self, *types: TokenType) -> bool:
        """Check if current token matches any of the given types"""
        for token_type in types:
            if self._check(token_type):
                self._advance()
                return True
        return False
    
    def _check(self, token_type: TokenType) -> bool:
        """Check if current token is of given type"""
        if self._is_at_end():
            return False
        return self._peek().type == token_type
    
    def _advance(self) -> Token:
        """Consume and return current token"""
        if not self._is_at_end():
            self.current += 1
        return self._previous()
    
    def _is_at_end(self) -> bool:
        """Check if we're at end of tokens"""
        return self._peek().type == TokenType.EOF
    
    def _peek(self) -> Token:
        """Return current token without consuming"""
        return self.tokens[self.current]
    
    def _previous(self) -> Token:
        """Return previous token"""
        return self.tokens[self.current - 1]
    
    def _consume(self, token_type: TokenType, message: str) -> Token:
        """Consume token of expected type or raise error"""
        if self._check(token_type):
            return self._advance()
        
        current_token = self._peek()
        raise ParseError(f"{message}. Got {current_token.type.name}", current_token)
    
    def _error(self, message: str) -> ParseError:
        """Create parse error"""
        return ParseError(message, self._peek())
    
    def _synchronize(self):
        """Synchronize after parse error"""
        self._advance()
        
        while not self._is_at_end():
            if self._previous().type == TokenType.SEMICOLON:
                return
            
            if self._peek().type in [TokenType.CLASS, TokenType.FUNCTION, TokenType.LET, 
                                   TokenType.CONST, TokenType.FOR, TokenType.IF, 
                                   TokenType.WHILE, TokenType.RETURN]:
                return
            
            self._advance()