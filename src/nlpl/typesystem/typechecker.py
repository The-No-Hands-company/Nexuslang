"""
Type checker for the NLPL language.
This module provides type checking functionality for NLPL programs.
"""

from typing import Dict, List, Optional, Set, Union, Any, Tuple
from ..parser.ast import (
    Program, VariableDeclaration, FunctionDefinition, Parameter,
    IfStatement, WhileLoop, ForLoop, MemoryAllocation, MemoryDeallocation,
    ClassDefinition, PropertyDeclaration, MethodDefinition,
    ConcurrentExecution, TryCatch, BinaryOperation, UnaryOperation,
    Literal, Identifier, FunctionCall, RepeatNTimesLoop,
    ReturnStatement, Block, ConcurrentBlock, TryCatchBlock,
    InterfaceDefinition, AbstractClassDefinition, TraitDefinition,
    TypeAliasDefinition, AbstractMethodDefinition,
    TypeParameter, TypeConstraint, TypeGuard,
    PrintStatement,  # Add print statement
    TypeCastExpression,  # Add type cast
    # Low-level constructs
    StructDefinition, UnionDefinition, ObjectInstantiation, MemberAssignment,
    SizeofExpression, AddressOfExpression, DereferenceExpression
)
from ..typesystem.types import (
    Type, PrimitiveType, ListType, DictionaryType, ClassType, 
    FunctionType, UnionType, AnyType, 
    INTEGER_TYPE, FLOAT_TYPE, STRING_TYPE, BOOLEAN_TYPE, NULL_TYPE, ANY_TYPE,
    get_type_by_name, infer_type, GenericType, GenericParameter
)
from ..typesystem.type_inference import TypeInferenceEngine
from ..typesystem.generic_types import GenericTypeRegistry, GenericTypeContext
from ..typesystem.generics_system import (
    GenericContext, GenericTypeInference, Monomorphizer,
    TypeConstraint as GenericConstraint, TypeParameterInfo
)

class TypeCheckError(Exception):
    """Exception raised for type checking errors."""
    pass

class TypeEnvironment:
    """Environment for type checking, containing variable and function types."""
    
    def __init__(self, parent: Optional['TypeEnvironment'] = None):
        self.parent = parent
        self.variables: Dict[str, Type] = {}
        self.functions: Dict[str, FunctionType] = {}
        self.return_type: Optional[Type] = None
        
        # Generic support
        self.generic_context: Optional[GenericContext] = None
        self.type_parameters: Dict[str, TypeParameterInfo] = {}
    
    def enter_generic_scope(self, type_params: List[TypeParameterInfo]) -> None:
        """Enter a new generic scope with type parameters."""
        self.generic_context = GenericContext(parent=self.generic_context)
        for param in type_params:
            self.generic_context.add_type_parameter(param)
            self.type_parameters[param.name] = param
    
    def exit_generic_scope(self) -> None:
        """Exit the current generic scope."""
        if self.generic_context and self.generic_context.parent:
            self.generic_context = self.generic_context.parent
        else:
            self.generic_context = None
    
    def is_type_parameter(self, name: str) -> bool:
        """Check if a name is a type parameter."""
        return name in self.type_parameters
    
    def resolve_type(self, type_: Type) -> Type:
        """Resolve a type by applying generic substitutions."""
        if self.generic_context:
            return self.generic_context.resolve_type(type_)
        return type_
    
    def define_variable(self, name: str, type_: Type) -> None:
        """Define a variable with a type in the current scope."""
        self.variables[name] = type_
    
    def define_function(self, name: str, type_: FunctionType) -> None:
        """Define a function with a type in the current scope."""
        self.functions[name] = type_
    
    def get_variable_type(self, name: str) -> Type:
        """Get the type of a variable from the environment."""
        if name in self.variables:
            return self.variables[name]
        
        if self.parent:
            return self.parent.get_variable_type(name)
        
        raise TypeCheckError(f"Undefined variable: {name}")
    
    def get_function_type(self, name: str) -> FunctionType:
        """Get the type of a function from the environment."""
        if name in self.functions:
            return self.functions[name]
        
        if self.parent:
            return self.parent.get_function_type(name)
        
        raise TypeCheckError(f"Undefined function: {name}")
    
    def set_return_type(self, type_: Type) -> None:
        """Set the expected return type for the current function scope."""
        self.return_type = type_
    
    def get_return_type(self) -> Optional[Type]:
        """Get the expected return type for the current function scope."""
        if self.return_type:
            return self.return_type
        
        if self.parent:
            return self.parent.get_return_type()
        
        return None

class TypeChecker:
    """Type checker for NLPL programs."""
    
    def __init__(self):
        self.env = TypeEnvironment()
        self.errors: List[str] = []
        # Use the type inference engine for improved inference
        self.type_inference = TypeInferenceEngine()
        # Use the user-defined type registry
        self.type_registry = {}
        self.generic_registry = GenericTypeRegistry()
        self.current_class: Optional[str] = None
        self.current_trait: Optional[str] = None
        self.current_interface: Optional[str] = None
        self.abstract_methods: Dict[str, Set[str]] = {}
        self.trait_methods: Dict[str, Set[str]] = {}
        
        # Generic system components
        self.monomorphizer = Monomorphizer()
        self.generic_inference = GenericTypeInference()
        self.generic_functions: Dict[str, FunctionDefinition] = {}  # Track generic function templates
    
    def check_program(self, program: Program) -> List[str]:
        """Check the types in a program and return any errors."""
        self.errors = []
        
        for statement in program.statements:
            self.check_statement(statement, self.env)
        
        return self.errors
    
    def check_statement(self, statement: Any, env: TypeEnvironment) -> Type:
        """Check the type of a statement."""
        if isinstance(statement, VariableDeclaration):
            return self.check_variable_declaration(statement, env)
        elif isinstance(statement, FunctionDefinition):
            return self.check_function_definition(statement, env)
        elif isinstance(statement, ClassDefinition):
            return self.check_class_definition(statement, env)
        elif isinstance(statement, InterfaceDefinition):
            return self.check_interface_definition(statement, env)
        elif isinstance(statement, IfStatement):
            return self.check_if_statement(statement, env)
        elif isinstance(statement, WhileLoop):
            return self.check_while_loop(statement, env)
        elif isinstance(statement, ForLoop):
            return self.check_for_loop(statement, env)
        elif isinstance(statement, RepeatNTimesLoop):
            return self.check_repeat_n_times_loop(statement, env)
        elif isinstance(statement, ReturnStatement):
            return self.check_return_statement(statement, env)
        elif isinstance(statement, Block):
            return self.check_block(statement, env)
        elif isinstance(statement, ConcurrentBlock):
            return self.check_concurrent_block(statement, env)
        elif isinstance(statement, TryCatchBlock):
            return self.check_try_catch_block(statement, env)
        elif isinstance(statement, FunctionCall):
            return self.check_function_call(statement, env)
        elif isinstance(statement, BinaryOperation):
            return self.check_binary_operation(statement, env)
        elif isinstance(statement, UnaryOperation):
            return self.check_unary_operation(statement, env)
        elif isinstance(statement, Literal):
            return self.check_literal(statement, env)
        elif isinstance(statement, Identifier):
            return self.check_identifier(statement, env)
        elif isinstance(statement, AbstractClassDefinition):
            return self.check_abstract_class_definition(statement)
        elif isinstance(statement, TraitDefinition):
            return self.check_trait_definition(statement)
        elif isinstance(statement, TypeAliasDefinition):
            return self.check_type_alias_definition(statement)
        elif isinstance(statement, PrintStatement):
            return self.check_print_statement(statement, env)
        elif isinstance(statement, StructDefinition):
            return ANY_TYPE  # Struct definitions are valid, return ANY for now
        elif isinstance(statement, UnionDefinition):
            return ANY_TYPE  # Union definitions are valid, return ANY for now  
        elif isinstance(statement, ObjectInstantiation):
            return ANY_TYPE  # Object instantiation valid, return ANY for now
        elif isinstance(statement, MemberAssignment):
            return ANY_TYPE  # Member assignment valid, return ANY for now
        elif isinstance(statement, SizeofExpression):
            return INTEGER_TYPE  # sizeof returns integer
        elif isinstance(statement, AddressOfExpression):
            return ANY_TYPE  # Address-of returns pointer type (simplified)
        elif isinstance(statement, DereferenceExpression):
            return ANY_TYPE  # Dereference returns the pointed-to type (simplified)
        elif isinstance(statement, TypeCastExpression):
            return self.check_type_cast(statement, env)
        elif statement.__class__.__name__ == 'MemberAccess':
            # Handle member access: object.property or object.method()
            return self.check_member_access(statement, env)
        else:
            raise TypeCheckError(f"Unsupported statement type: {statement.__class__.__name__}")
            return ANY_TYPE
    
    def check_expression(self, expression: Any, env: TypeEnvironment) -> Type:
        """Check the type of an expression. Alias for check_statement for compatibility."""
        return self.check_statement(expression, env)
    
    def check_variable_declaration(self, declaration: VariableDeclaration, env: TypeEnvironment) -> Type:
        """Check the type of a variable declaration."""
        # Check the type of the value
        value_type = self.check_expression(declaration.value, env)
        
        # If there's a type annotation, check that it's compatible
        if declaration.type_annotation:
            declared_type = get_type_by_name(declaration.type_annotation)
            if not value_type.is_compatible_with(declared_type):
                self.errors.append(
                    f"Line {declaration.line_number}: Type error: Cannot assign value of type "
                    f"'{value_type}' to variable '{declaration.name}' of type '{declared_type}'"
                )
                # Define the variable with the declared type anyway (for error recovery)
                env.define_variable(declaration.name, declared_type)
                return declared_type
            
            # Define the variable with the declared type
            env.define_variable(declaration.name, declared_type)
            return declared_type
        
        # If there's no type annotation, use type inference for improved type information
        inferred_type = self.type_inference.infer_variable_declaration(declaration, env.variables)
        if inferred_type != value_type and inferred_type != ANY_TYPE:
            # If inference came up with a more specific type, use it
            value_type = inferred_type
        
        # Define the variable with the inferred type
        env.define_variable(declaration.name, value_type)
        return value_type
    
    def check_function_definition(self, definition: FunctionDefinition, env: TypeEnvironment) -> Type:
        """Check the type of a function definition (with generic support)."""
        # Check if this is a generic function
        is_generic = bool(definition.type_parameters)
        
        if is_generic:
            # Store generic function template for later instantiation
            self.generic_functions[definition.name] = definition
            
            # Build type parameter info
            type_param_info = []
            for param_name in definition.type_parameters:
                # Find constraints for this parameter
                constraints = []
                if hasattr(definition, 'type_constraints'):
                    for constraint in definition.type_constraints:
                        if constraint.type_parameter == param_name:
                            # Convert AST constraint to type system constraint
                            constraint_type = get_type_by_name(constraint.constraint_type)
                            constraints.append(
                                GenericConstraint(
                                    param_name,
                                    constraint_type,
                                    'comparable' if constraint.constraint_type == 'Comparable' else 'subtype'
                                )
                            )
                
                type_param_info.append(TypeParameterInfo(
                    name=param_name,
                    constraints=constraints,
                    variance='invariant'
                ))
            
            # Enter generic scope
            env.enter_generic_scope(type_param_info)
        
        # Create a new environment for the function scope
        function_env = TypeEnvironment(env)
        if is_generic:
            function_env.generic_context = env.generic_context
            function_env.type_parameters = env.type_parameters
        
        # Process parameters
        param_types = []
        for param in definition.parameters:
            param_type = ANY_TYPE
            if param.type_annotation:
                # Check if this is a type parameter
                if env.is_type_parameter(param.type_annotation):
                    param_type = GenericParameter(param.type_annotation)
                else:
                    param_type = get_type_by_name(param.type_annotation)
            param_types.append(param_type)
            function_env.define_variable(param.name, param_type)
        
        # Set return type
        return_type = ANY_TYPE
        if definition.return_type:
            # Check if return type is a type parameter
            if env.is_type_parameter(definition.return_type):
                return_type = GenericParameter(definition.return_type)
            else:
                return_type = get_type_by_name(definition.return_type)
        else:
            # Use type inference to determine return type if not specified
            inferred_return_type = self.type_inference.infer_function_return_type(definition, env.variables)
            if inferred_return_type != ANY_TYPE:
                return_type = inferred_return_type
        
        function_env.set_return_type(return_type)
        
        # Create function type
        function_type = FunctionType(param_types, return_type)
        
        # Define the function in the parent environment
        env.define_function(definition.name, function_type)
        
        # Check the function body
        for statement in definition.body:
            self.check_statement(statement, function_env)
        
        if is_generic:
            # Exit generic scope
            env.exit_generic_scope()
        
        return function_type
    
    def check_if_statement(self, statement: IfStatement, env: TypeEnvironment) -> Type:
        """Check an if statement."""
        # Check the condition
        condition_type = self.check_statement(statement.condition, env)
        
        if not condition_type.is_compatible_with(BOOLEAN_TYPE):
            self.errors.append(
                f"Type error: If condition must be a boolean, got '{condition_type}'"
            )
        
        # Check the then branch
        then_env = TypeEnvironment(env)
        then_type = NULL_TYPE
        for stmt in statement.then_block:
            then_type = self.check_statement(stmt, then_env)
        
        # Check the else branch if it exists
        else_type = NULL_TYPE
        if statement.else_block:
            else_env = TypeEnvironment(env)
            for stmt in statement.else_block:
                else_type = self.check_statement(stmt, else_env)
        
        # The type of an if statement is the union of the then and else branch types
        return UnionType([then_type, else_type])
    
    def check_while_loop(self, loop: WhileLoop, env: TypeEnvironment) -> Type:
        """Check a while loop."""
        # Check the condition
        condition_type = self.check_statement(loop.condition, env)
        
        if not condition_type.is_compatible_with(BOOLEAN_TYPE):
            self.errors.append(
                f"Type error: While condition must be a boolean, got '{condition_type}'"
            )
        
        # Check the body
        loop_env = TypeEnvironment(env)
        result_type = NULL_TYPE
        for stmt in loop.body:
            result_type = self.check_statement(stmt, loop_env)
        
        return result_type
    
    def check_for_loop(self, loop: ForLoop, env: TypeEnvironment) -> Type:
        """Check a for loop."""
        # Check the iterable
        iterable_type = self.check_statement(loop.iterable, env)
        
        # Create a new environment for the loop body
        loop_env = TypeEnvironment(env)
        
        # Infer the element type from the iterable type
        if isinstance(iterable_type, ListType):
            element_type = iterable_type.element_type
        else:
            element_type = ANY_TYPE
            self.errors.append(
                f"Type error: For loop iterable must be a list, got '{iterable_type}'"
            )
        
        # Define the iterator variable in the loop environment
        loop_env.define_variable(loop.iterator, element_type)
        
        # Check the loop body
        result_type = NULL_TYPE
        for stmt in loop.body:
            result_type = self.check_statement(stmt, loop_env)
        
        return result_type
    
    def check_repeat_n_times_loop(self, loop: RepeatNTimesLoop, env: TypeEnvironment) -> Type:
        """Check a repeat-n-times loop."""
        # Check the count
        count_type = self.check_statement(loop.count, env)
        
        if not count_type.is_compatible_with(INTEGER_TYPE):
            self.errors.append(
                f"Type error: Repeat count must be an integer, got '{count_type}'"
            )
        
        # Check the body
        loop_env = TypeEnvironment(env)
        result_type = NULL_TYPE
        for stmt in loop.body:
            result_type = self.check_statement(stmt, loop_env)
        
        return result_type
    
    def check_return_statement(self, statement: ReturnStatement, env: TypeEnvironment) -> Type:
        """Check a return statement."""
        if statement.value:
            value_type = self.check_statement(statement.value, env)
        else:
            value_type = NULL_TYPE
        
        # Check compatibility with the expected return type
        expected_return_type = env.get_return_type()
        if expected_return_type and not value_type.is_compatible_with(expected_return_type):
            self.errors.append(
                f"Type error: Return value of type '{value_type}' is not compatible with expected return type '{expected_return_type}'"
            )
        
        return value_type
    
    def check_block(self, block: Block, env: TypeEnvironment) -> Type:
        """Check a block of statements."""
        block_env = TypeEnvironment(env)
        result_type = NULL_TYPE
        
        for stmt in block.statements:
            result_type = self.check_statement(stmt, block_env)
        
        return result_type
    
    def check_concurrent_block(self, block: ConcurrentBlock, env: TypeEnvironment) -> Type:
        """Check a concurrent block of statements."""
        block_env = TypeEnvironment(env)
        result_types = []
        
        for stmt in block.statements:
            result_types.append(self.check_statement(stmt, block_env))
        
        # The type of a concurrent block is a list of the result types
        return ListType(UnionType(result_types))
    
    def check_try_catch_block(self, block: TryCatchBlock, env: TypeEnvironment) -> Type:
        """Check a try-catch block."""
        # Check the try block
        try_env = TypeEnvironment(env)
        try_type = self.check_block(block.try_block, try_env)
        
        # Check the catch block
        catch_env = TypeEnvironment(env)
        
        # Define the exception variable if it exists
        if block.exception_var:
            catch_env.define_variable(block.exception_var, STRING_TYPE)
        
        catch_type = self.check_block(block.catch_block, catch_env)
        
        # The type of a try-catch block is the union of the try and catch block types
        return UnionType([try_type, catch_type])
    
    def check_function_call(self, call: FunctionCall, env: TypeEnvironment) -> Type:
        """Check a function call."""
        # Check the arguments
        arg_types = [self.check_statement(arg, env) for arg in call.arguments]
        
        try:
            # Get the function type
            function_type = env.get_function_type(call.name)
            
            # Check argument count
            if len(arg_types) != len(function_type.param_types):
                self.errors.append(
                    f"Type error: Function '{call.name}' expects {len(function_type.param_types)} arguments, got {len(arg_types)}"
                )
                return function_type.return_type
            
            # Check argument types
            for i, (arg_type, param_type) in enumerate(zip(arg_types, function_type.param_types)):
                if not arg_type.is_compatible_with(param_type):
                    self.errors.append(
                        f"Type error: Function '{call.name}' argument {i+1} expects type '{self._type_name(param_type)}', got '{self._type_name(arg_type)}'"
                    )
            
            return function_type.return_type
        except TypeCheckError:
            # If the function is not defined, assume it's a built-in function
            # In a real implementation, we would check against a registry of built-in functions
            return ANY_TYPE
    
    def _type_name(self, type_: Type) -> str:
        """Get a human-readable name for a type."""
        if hasattr(type_, 'name'):
            return type_.name
        return type_.__class__.__name__

    
    def check_binary_operation(self, operation: BinaryOperation, env: TypeEnvironment) -> Type:
        """Check a binary operation."""
        left_type = self.check_statement(operation.left, env)
        right_type = self.check_statement(operation.right, env)
        
        # Get the operator (handle both Token objects and strings)
        if hasattr(operation.operator, 'lexeme'):
            op = operation.operator.lexeme
        else:
            op = str(operation.operator)
        
        # Arithmetic operators (both symbolic and natural language)
        arithmetic_ops = ['+', '-', '*', '/', '%', 'plus', 'minus', 'times', 'divided by', 'modulo', 'power', 'to the power of', '**']
        if op in arithmetic_ops:
            if op in ['+', 'plus'] and (left_type == STRING_TYPE or right_type == STRING_TYPE):
                # String concatenation
                return STRING_TYPE
            
            if not (left_type.is_compatible_with(INTEGER_TYPE) or left_type.is_compatible_with(FLOAT_TYPE)):
                self.errors.append(
                    f"Type error: Left operand of '{op}' must be a number, got '{self._type_name(left_type)}'"
                )
            
            if not (right_type.is_compatible_with(INTEGER_TYPE) or right_type.is_compatible_with(FLOAT_TYPE)):
                self.errors.append(
                    f"Type error: Right operand of '{op}' must be a number, got '{self._type_name(right_type)}'"
                )
            
            # Division and power always return float
            if op in ['/', 'divided by', 'power', 'to the power of', '**']:
                return FLOAT_TYPE
            
            # If either operand is a float, the result is a float
            if left_type == FLOAT_TYPE or right_type == FLOAT_TYPE:
                return FLOAT_TYPE
            
            return INTEGER_TYPE
        
        # Comparison operators (both symbolic and natural language)
        comparison_ops = ['==', '!=', '<', '>', '<=', '>=', 'equals', 'is equal to', 'not equal to', 
                         'is not equal to', 'greater than', 'is greater than', 'less than', 'is less than',
                         'greater than or equal to', 'is greater than or equal to', 
                         'less than or equal to', 'is less than or equal to']
        if op in comparison_ops:
            # For equality operators, any types can be compared
            if op in ['==', '!=', 'equals', 'is equal to', 'not equal to', 'is not equal to']:
                return BOOLEAN_TYPE
            
            # For other comparison operators, operands must be comparable
            if not (
                (left_type.is_compatible_with(INTEGER_TYPE) or left_type.is_compatible_with(FLOAT_TYPE)) and
                (right_type.is_compatible_with(INTEGER_TYPE) or right_type.is_compatible_with(FLOAT_TYPE))
            ):
                self.errors.append(
                    f"Type error: Operands of '{op}' must be numbers, got '{self._type_name(left_type)}' and '{self._type_name(right_type)}'"
                )
            
            return BOOLEAN_TYPE
        
        # Logical operators
        logical_ops = ['and', 'or']
        if op in logical_ops:
            if not left_type.is_compatible_with(BOOLEAN_TYPE):
                self.errors.append(
                    f"Type error: Left operand of '{op}' must be a boolean, got '{self._type_name(left_type)}'"
                )
            
            if not right_type.is_compatible_with(BOOLEAN_TYPE):
                self.errors.append(
                    f"Type error: Right operand of '{op}' must be a boolean, got '{self._type_name(right_type)}'"
                )
            
            return BOOLEAN_TYPE
        
        else:
            self.errors.append(f"Unsupported binary operator: {op}")
            return ANY_TYPE

    
    def check_unary_operation(self, operation: UnaryOperation, env: TypeEnvironment) -> Type:
        """Check a unary operation."""
        operand_type = self.check_statement(operation.operand, env)
        
        # Get the operator (handle both Token objects and strings)
        if hasattr(operation.operator, 'lexeme'):
            op = operation.operator.lexeme
        else:
            op = str(operation.operator)
        
        if op == '-':
            if not (operand_type.is_compatible_with(INTEGER_TYPE) or operand_type.is_compatible_with(FLOAT_TYPE)):
                self.errors.append(
                    f"Type error: Operand of unary '-' must be a number, got '{self._type_name(operand_type)}'"
                )
            
            return operand_type
        
        elif op == 'not':
            if not operand_type.is_compatible_with(BOOLEAN_TYPE):
                self.errors.append(
                    f"Type error: Operand of 'not' must be a boolean, got '{self._type_name(operand_type)}'"
                )
            
            return BOOLEAN_TYPE
        
        else:
            self.errors.append(f"Unsupported unary operator: {op}")
            return ANY_TYPE
    
    def check_literal(self, literal: Literal, env: TypeEnvironment) -> Type:
        """Check a literal value."""
        return infer_type(literal.value)
    
    def check_identifier(self, identifier: Identifier, env: TypeEnvironment) -> Type:
        """Check an identifier (variable reference)."""
        try:
            return env.get_variable_type(identifier.name)
        except TypeCheckError as e:
            self.errors.append(str(e))
            return ANY_TYPE

    def check_class_definition(self, definition: ClassDefinition, env: TypeEnvironment) -> Type:
        """Check the type of a class definition."""
        # Check if class is already defined in the type registry
        if definition.name in self.type_registry:
            class_type = self.type_registry[definition.name]
        else:
            # Extract properties and their types
            properties = {}
            for prop in definition.properties:
                if isinstance(prop, PropertyDeclaration):
                    prop_type = ANY_TYPE
                    if prop.type_annotation:
                        prop_type = get_type_by_name(prop.type_annotation)
                    properties[prop.name] = prop_type
            
            # Extract methods and their types
            methods = {}
            for method in definition.methods:
                if isinstance(method, MethodDefinition):
                    # Create a new environment for method scope
                    method_env = TypeEnvironment(env)
                    
                    # Process parameters
                    param_types = []
                    for param in method.parameters:
                        param_type = ANY_TYPE
                        if param.type_annotation:
                            param_type = get_type_by_name(param.type_annotation)
                        param_types.append(param_type)
                        method_env.define_variable(param.name, param_type)
                    
                    # Set return type
                    return_type = ANY_TYPE
                    if method.return_type:
                        return_type = get_type_by_name(method.return_type)
                    
                    method_env.set_return_type(return_type)
                    
                    # Create method type
                    method_type = FunctionType(param_types, return_type)
                    methods[method.name] = method_type
                    
                    # Check method body
                    for statement in method.body:
                        self.check_statement(statement, method_env)
            
            # Process inheritance
            parent_classes = None
            if hasattr(definition, 'parent_classes') and definition.parent_classes:
                parent_classes = definition.parent_classes
                
                # Check that parent classes exist
                for parent in parent_classes:
                    if parent not in self.type_registry:
                        self.errors.append(
                            f"Line {definition.line_number}: Type error: Parent class '{parent}' not defined"
                        )
            
            # Process interface implementations
            if hasattr(definition, 'implemented_interfaces') and definition.implemented_interfaces:
                for interface in definition.implemented_interfaces:
                    if interface not in self.type_registry:
                        self.errors.append(
                            f"Line {definition.line_number}: Type error: Interface '{interface}' not defined"
                        )
                    else:
                        # Check that all required methods are implemented
                        missing_methods = self.type_registry.check_interface_implementation(definition.name, interface)
                        if missing_methods:
                            methods_str = ", ".join(missing_methods)
                            self.errors.append(
                                f"Line {definition.line_number}: Type error: Class '{definition.name}' "
                                f"does not implement methods required by interface '{interface}': {methods_str}"
                            )
            
            # Create or retrieve class type
            class_type = self.type_registry.create_class_type(
                definition.name,
                properties,
                methods,
                parent_classes
            )
        
        # Define the class in the environment
        env.define_variable(definition.name, class_type)
        
        return class_type

    def check_interface_definition(self, definition: InterfaceDefinition, env: TypeEnvironment) -> Type:
        """Check the type of an interface definition."""
        # Register the interface in the type registry with required methods
        required_methods = []
        
        for method in definition.methods:
            if isinstance(method, MethodDefinition):
                required_methods.append(method.name)
        
        self.type_registry.register_interface(definition.name, required_methods)
        
        # Process methods and their types
        methods = {}
        for method in definition.methods:
            if isinstance(method, MethodDefinition):
                # Create a new environment for method scope
                method_env = TypeEnvironment(env)
                
                # Process parameters
                param_types = []
                for param in method.parameters:
                    param_type = ANY_TYPE
                    if param.type_annotation:
                        param_type = get_type_by_name(param.type_annotation)
                    param_types.append(param_type)
                    method_env.define_variable(param.name, param_type)
                
                # Set return type
                return_type = ANY_TYPE
                if method.return_type:
                    return_type = get_type_by_name(method.return_type)
                
                method_env.set_return_type(return_type)
                
                # Create method type
                method_type = FunctionType(param_types, return_type)
                methods[method.name] = method_type
        
        # Create interface type (as a special kind of class type)
        interface_type = ClassType(definition.name, {}, methods)
        
        # Define the interface in the environment
        env.define_variable(definition.name, interface_type)
        
        return interface_type

    def check_abstract_class_definition(self, definition: AbstractClassDefinition) -> Type:
        """Check the type of an abstract class definition."""
        # Create a new type context for the class
        self.current_class = definition.name
        
        # Register the class type
        class_type = ClassType(
            name=definition.name,
            properties={},
            methods={},
            parent_classes=definition.parent_classes,
            is_abstract=True
        )
        self.type_registry[definition.name] = class_type
        
        # Check type parameters
        if definition.type_parameters:
            generic_context = self.generic_registry.create_context(definition.name)
            for param in definition.type_parameters:
                generic_context.add_type_parameter(param)
        
        # Check properties
        for prop in definition.properties:
            self.check_property_definition(prop)
        
        # Check methods
        abstract_methods = set()
        for method in definition.methods:
            if isinstance(method, AbstractMethodDefinition):
                abstract_methods.add(method.name)
            self.check_method_definition(method)
        
        # Store abstract methods
        self.abstract_methods[definition.name] = abstract_methods
        
        # Check interface implementation
        for interface in definition.implemented_interfaces:
            self.check_interface_implementation(definition.name, interface)
        
        self.current_class = None
        
        return class_type

    def check_trait_definition(self, definition: TraitDefinition) -> Type:
        """Check the type of a trait definition."""
        # Create a new type context for the trait
        self.current_trait = definition.name
        
        # Register the trait type
        trait_type = ClassType(
            name=definition.name,
            properties={},
            methods={},
            parent_classes=[],
            is_trait=True
        )
        self.type_registry[definition.name] = trait_type
        
        # Check type parameters
        if definition.type_parameters:
            generic_context = self.generic_registry.create_context(definition.name)
            for param in definition.type_parameters:
                generic_context.add_type_parameter(param)
        
        # Check methods
        trait_methods = set()
        for method in definition.methods:
            if isinstance(method, AbstractMethodDefinition):
                trait_methods.add(method.name)
            self.check_method_definition(method)
        
        # Store trait methods
        self.trait_methods[definition.name] = trait_methods
        
        self.current_trait = None
        
        return trait_type

    def check_type_alias_definition(self, definition: TypeAliasDefinition) -> Type:
        """Check the type of a type alias definition."""
        # Resolve the target type
        target_type = self.resolve_type(definition.target_type)
        
        # Register the type alias
        self.type_registry[definition.name] = target_type
        
        return target_type

    def check_interface_implementation(self, class_name: str, interface_name: str) -> None:
        """Check if a class properly implements an interface."""
        if interface_name not in self.type_registry:
            raise TypeError(f"Interface {interface_name} not found")
        
        interface_type = self.type_registry[interface_name]
        class_type = self.type_registry[class_name]
        
        # Check if all interface methods are implemented
        for method_name, method_type in interface_type.methods.items():
            if method_name not in class_type.methods:
                raise TypeError(f"Class {class_name} does not implement method {method_name} from interface {interface_name}")
            
            # Check method signature compatibility
            class_method = class_type.methods[method_name]
            if not self.types_compatible(class_method, method_type):
                raise TypeError(f"Method {method_name} in class {class_name} is not compatible with interface {interface_name}")
    
    def check_abstract_method_implementation(self, class_name: str) -> None:
        """Check if all abstract methods are implemented."""
        if class_name not in self.abstract_methods:
            return
        
        class_type = self.type_registry[class_name]
        abstract_methods = self.abstract_methods[class_name]
        
        for method_name in abstract_methods:
            if method_name not in class_type.methods:
                raise TypeError(f"Class {class_name} does not implement abstract method {method_name}")
    
    def check_trait_method_implementation(self, class_name: str, trait_name: str) -> None:
        """Check if all trait methods are implemented."""
        if trait_name not in self.trait_methods:
            return
        
        class_type = self.type_registry[class_name]
        trait_methods = self.trait_methods[trait_name]
        
        for method_name in trait_methods:
            if method_name not in class_type.methods:
                raise TypeError(f"Class {class_name} does not implement trait method {method_name} from trait {trait_name}")
    
    def resolve_type(self, type_name: str) -> Type:
        """Resolve a type name to its actual type."""
        if type_name in self.type_registry:
            return self.type_registry[type_name]
        
        # Handle generic types
        if '<' in type_name and type_name.endswith('>'):
            base_name, param_str = type_name.split('<', 1)
            param_str = param_str[:-1]  # Remove the closing '>'
            
            if base_name in self.type_registry:
                base_type = self.type_registry[base_name]
                if isinstance(base_type, GenericType):
                    type_args = [self.resolve_type(arg.strip()) for arg in param_str.split(',')]
                    return self.generic_registry.instantiate_type(base_type, type_args)
        
        raise TypeError(f"Type {type_name} not found")
    
    def types_compatible(self, type1: Type, type2: Type) -> bool:
        """Check if two types are compatible."""
        # Handle generic types
        if isinstance(type1, GenericType) and isinstance(type2, GenericType):
            if type1.name != type2.name:
                return False
            
            # Check type parameter compatibility
            for param1, param2 in zip(type1.type_parameters, type2.type_parameters):
                if not self.types_compatible(param1, param2):
                    return False
            
            return self.types_compatible(type1.base_type, type2.base_type)
        
        # Handle class types
        if isinstance(type1, ClassType) and isinstance(type2, ClassType):
            # Check inheritance
            if type1.name in type2.parent_classes:
                return True
            
        # Default: use Type's is_compatible_with method
        return type1.is_compatible_with(type2)
    
    def check_print_statement(self, statement: PrintStatement, env: TypeEnvironment) -> Type:
        """Check a print statement. Print can handle any type."""
        # Type check the expression being printed
        if hasattr(statement, 'value') and statement.value:
            self.check_statement(statement.value, env)
        return ANY_TYPE
    
    def check_type_cast(self, expr: TypeCastExpression, env: TypeEnvironment) -> Type:
        """Check a type cast expression and return the target type."""
        # Check the expression being cast
        source_type = self.check_statement(expr.expression, env)
        
        # Convert target_type to Type object if it's a string
        if isinstance(expr.target_type, str):
            type_name = expr.target_type.lower()
            if type_name == "integer" or type_name == "int":
                return INTEGER_TYPE
            elif type_name == "float":
                return FLOAT_TYPE
            elif type_name == "string":
                return STRING_TYPE
            elif type_name == "boolean" or type_name == "bool":
                return BOOLEAN_TYPE
            else:
                # For other types, return ANY_TYPE
                return ANY_TYPE
        
        # Return target type if already a Type object
        return expr.target_type if isinstance(expr.target_type, Type) else ANY_TYPE
    
    def check_member_access(self, expr: Any, env: TypeEnvironment) -> Type:
        """Check a member access expression: object.member."""
        # Check the object expression
        obj_type = self.check_statement(expr.object_expr, env)
        
        # If object type is a class type, check if member exists
        if isinstance(obj_type, ClassType):
            member_name = expr.member_name
            
            # Check properties
            if member_name in obj_type.properties:
                return obj_type.properties[member_name]
            
            # Check methods
            if member_name in obj_type.methods:
                return obj_type.methods[member_name]
            
            # Member not found - type checking will fail
            # For now, return ANY_TYPE to allow execution to continue
            return ANY_TYPE
        
        # For other types, return ANY_TYPE
        return ANY_TYPE

        # If target_type is already a Type object, return it
        return expr.target_type if isinstance(expr.target_type, Type) else ANY_TYPE
 