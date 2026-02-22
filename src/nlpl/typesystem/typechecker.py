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
    Literal, Identifier, FunctionCall, RepeatNTimesLoop, RepeatWhileLoop,
    ReturnStatement, Block, ConcurrentBlock, TryCatchBlock,
    InterfaceDefinition, AbstractClassDefinition, TraitDefinition,
    TypeAliasDefinition, AbstractMethodDefinition,
    TypeParameter, TypeConstraint, TypeGuard,
    PrintStatement,  # Add print statement
    TypeCastExpression,  # Add type cast
    RaiseStatement,  # Add raise statement
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

class TypeRegistry(dict):
    """Registry for user-defined types (classes, interfaces, traits, aliases).

    Extends ``dict`` so callers can use the standard ``reg[name]``,
    ``name in reg``, and ``reg[name] = t`` patterns while also providing
    the domain-specific helpers expected by TypeChecker.
    """

    def __init__(self) -> None:
        super().__init__()
        # Map interface name -> frozenset of required method names.
        self._interfaces: Dict[str, Set[str]] = {}

    # ------------------------------------------------------------------
    # Helpers used by TypeChecker
    # ------------------------------------------------------------------

    def create_class_type(
        self,
        name: str,
        properties: Dict[str, Any],
        methods: Dict[str, Any],
        parent_classes: Optional[List[str]] = None,
    ) -> "ClassType":
        """Create a ClassType, register it, and return it."""
        class_type = ClassType(name, properties, methods, parent_classes)
        self[name] = class_type
        return class_type

    def register_interface(self, name: str, required_methods: List[str]) -> None:
        """Record which methods an interface mandates."""
        self._interfaces[name] = set(required_methods)

    def check_interface_implementation(
        self, class_name: str, interface_name: str
    ) -> List[str]:
        """Return the list of methods required by *interface_name* that
        *class_name* has not yet implemented.  Returns ``[]`` when the
        interface is unknown (forward reference) or fully satisfied.
        """
        required = self._interfaces.get(interface_name, set())
        if not required:
            return []
        class_type = self.get(class_name)
        implemented: Set[str] = set()
        if class_type is not None and hasattr(class_type, "methods"):
            implemented = set(class_type.methods.keys())
        return sorted(required - implemented)


class TypeChecker:
    """Type checker for NLPL programs."""
    
    def __init__(self):
        self.env = TypeEnvironment()
        self.errors: List[str] = []
        # Use the type inference engine for improved inference
        self.type_inference = TypeInferenceEngine()
        self.type_inference_engine = self.type_inference  # Alias for pattern matching
        # Use the user-defined type registry
        self.type_registry = TypeRegistry()
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
        elif isinstance(statement, RepeatWhileLoop):
            return self.check_repeat_while_loop(statement, env)
        elif isinstance(statement, ReturnStatement):
            return self.check_return_statement(statement, env)
        elif statement.__class__.__name__ == 'BreakStatement':
            # Break statements are valid in loop contexts
            return ANY_TYPE
        elif statement.__class__.__name__ == 'ContinueStatement':
            # Continue statements are valid in loop contexts
            return ANY_TYPE
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
        elif statement.__class__.__name__ == 'ImportStatement':
            # Import statements bring modules into scope
            # Register the module name (or alias if provided) as a variable
            if hasattr(statement, 'module_name'):
                # Use alias if provided, otherwise extract last part of module name
                if hasattr(statement, 'alias') and statement.alias:
                    module_name = statement.alias
                else:
                    # Extract the last part of dotted names (e.g., "test_modules.math_utils" -> "math_utils")
                    module_name = statement.module_name
                    if '.' in module_name:
                        module_name = module_name.split('.')[-1]
                env.define_variable(module_name, ANY_TYPE)
            return ANY_TYPE
        elif statement.__class__.__name__ == 'SelectiveImport':
            # Selective imports bring specific names into scope
            # Register each imported name as a variable
            if hasattr(statement, 'imported_names'):
                for name in statement.imported_names:
                    env.define_variable(name, ANY_TYPE)
            return ANY_TYPE
        elif statement.__class__.__name__ == 'ModuleAccess':
            # Module access expressions (module.member) are valid
            return ANY_TYPE
        elif isinstance(statement, StructDefinition):
            return ANY_TYPE  # Struct definitions are valid, return ANY for now
        elif isinstance(statement, UnionDefinition):
            return ANY_TYPE  # Union definitions are valid, return ANY for now  
        elif isinstance(statement, ObjectInstantiation):
            return ANY_TYPE  # Object instantiation valid, return ANY for now
        elif isinstance(statement, MemberAssignment):
            return ANY_TYPE  # Member assignment valid, return ANY for now
        elif statement.__class__.__name__ == 'IndexAssignment':
            # Handle index assignment: set array[index] to value
            # Check that the target (IndexExpression) is valid
            if hasattr(statement, 'target'):
                self.check_expression(statement.target, env)
            # Check that the value is valid
            if hasattr(statement, 'value'):
                return self.check_expression(statement.value, env)
            return ANY_TYPE
        elif isinstance(statement, SizeofExpression):
            return INTEGER_TYPE  # sizeof returns integer
        elif isinstance(statement, AddressOfExpression):
            return ANY_TYPE  # Address-of returns pointer type (simplified)
        elif isinstance(statement, DereferenceExpression):
            return ANY_TYPE  # Dereference returns the pointed-to type (simplified)
        elif isinstance(statement, TypeCastExpression):
            return self.check_type_cast(statement, env)
        elif statement.__class__.__name__ == 'LambdaExpression':
            # Handle lambda expressions
            return self.check_lambda_expression(statement, env)
        elif statement.__class__.__name__ == 'ListExpression':
            # Handle list literals: [1, 2, 3]
            return self.check_list_expression(statement, env)
        elif statement.__class__.__name__ == 'DictExpression':
            # Handle dict literals: {"key": "value"}
            return self.check_dict_expression(statement, env)
        elif statement.__class__.__name__ == 'ListComprehension':
            # Handle list comprehensions: [x for x in range(10)]
            return self.check_list_comprehension(statement, env)
        elif statement.__class__.__name__ == 'DictComprehension':
            # Handle dict comprehensions: {k: v for k, v in items}
            return self.check_dict_comprehension(statement, env)
        elif statement.__class__.__name__ == 'MemberAccess':
            # Handle member access: object.property or object.method()
            return self.check_member_access(statement, env)
        elif statement.__class__.__name__ == 'IndexExpression':
            # Handle index expressions: array[index] or dict[key]
            return self.check_index_expression(statement, env)
        elif statement.__class__.__name__ == 'GenericTypeInstantiation':
            # Handle generic type instantiation: create list, create list of Integer
            return self.check_generic_type_instantiation(statement, env)
        elif statement.__class__.__name__ == 'ExternFunctionDeclaration':
            # Handle extern function declarations (FFI)
            # Register the extern function so it can be type-checked when called
            if hasattr(statement, 'name'):
                # Create a function type for the extern function
                param_types = []
                if hasattr(statement, 'parameters'):
                    for param in statement.parameters:
                        param_type = get_type_by_name(param.type_annotation) if hasattr(param, 'type_annotation') else ANY_TYPE
                        param_types.append(param_type)
                
                return_type = get_type_by_name(statement.return_type) if hasattr(statement, 'return_type') else ANY_TYPE
                func_type = FunctionType(param_types, return_type)
                
                # Mark as variadic if specified (allows variable number of arguments)
                if hasattr(statement, 'variadic') and statement.variadic:
                    func_type.variadic = True
                
                env.define_function(statement.name, func_type)
            return ANY_TYPE
        elif statement.__class__.__name__ == 'ExternVariableDeclaration':
            # Handle extern variable declarations (FFI)
            if hasattr(statement, 'name') and hasattr(statement, 'type_annotation'):
                var_type = get_type_by_name(statement.type_annotation)
                env.define_variable(statement.name, var_type)
            return ANY_TYPE
        elif statement.__class__.__name__ == 'ExternTypeDeclaration':
            # Handle extern type declarations (FFI)
            # These define type aliases for FFI types, just accept them
            return ANY_TYPE
        elif statement.__class__.__name__ == 'InlineAssembly':
            # Handle inline assembly blocks
            # Assembly can read/write variables, but we can't statically type check it
            # Just verify that input/output operands exist in scope
            if hasattr(statement, 'inputs'):
                # inputs is a list of (constraint, expr) tuples
                for constraint, expr in statement.inputs:
                    # Check that input expressions are valid
                    self.check_expression(expr, env)
            
            if hasattr(statement, 'outputs'):
                # outputs is a list of (constraint, var) tuples
                for constraint, var in statement.outputs:
                    # Outputs should be identifiers (variables)
                    # They can be assigned to, so we don't need to check if they exist yet
                    pass
            
            # Assembly return type is typically Integer (return value in register)
            return INTEGER_TYPE
        elif statement.__class__.__name__ == 'MatchExpression':
            # Handle pattern matching expressions with enhanced type inference
            # Check the match expression type
            match_expr_type = self.check_expression(statement.expression, env)
            
            # Check each case
            result_types = []
            for case in statement.cases:
                # Create a new scope for pattern bindings
                case_env = TypeEnvironment(parent=env)
                
                # Infer types for pattern bindings using TypeInferenceEngine
                pattern = case.pattern
                
                # Use type inference to get precise pattern binding types
                if hasattr(self, 'type_inference_engine'):
                    # Use the inference engine if available
                    bindings = self.type_inference_engine.infer_pattern_binding_type(pattern, match_expr_type)
                    for var_name, var_type in bindings.items():
                        case_env.define_variable(var_name, var_type)
                else:
                    # Fall back to basic inference
                    if hasattr(pattern, 'name'):  # IdentifierPattern
                        case_env.define_variable(pattern.name, match_expr_type)
                    elif hasattr(pattern, 'binding'):  # OptionPattern, ResultPattern
                        if pattern.binding:
                            # For Option<T>/Result<T,E>, unwrap the type
                            inner_type = ANY_TYPE
                            if hasattr(match_expr_type, 'type_parameters') and match_expr_type.type_parameters:
                                inner_type = match_expr_type.type_parameters[0]
                            case_env.define_variable(pattern.binding, inner_type)
                    elif hasattr(pattern, 'bindings'):  # VariantPattern
                        for binding in pattern.bindings:
                            case_env.define_variable(binding, ANY_TYPE)
                
                # Check guard if present
                if case.guard:
                    guard_type = self.check_expression(case.guard, case_env)
                    if guard_type != BOOLEAN_TYPE and guard_type != ANY_TYPE:
                        self.errors.append(
                            f"Line {getattr(case, 'line_number', '?')}: Guard condition must be boolean, "
                            f"got {guard_type}"
                        )
                
                # Check case body and collect return type
                body_type = ANY_TYPE
                for stmt in case.body:
                    body_type = self.check_statement(stmt, case_env)
                result_types.append(body_type)
            
            # Match expression type is the union of all case body types
            # If all types are the same, use that; otherwise try to unify or use ANY_TYPE
            if result_types:
                if all(t == result_types[0] for t in result_types):
                    return result_types[0]
                # Try to unify types using type inference engine
                if hasattr(self, 'type_inference_engine'):
                    unified_type = result_types[0]
                    for rt in result_types[1:]:
                        unified = self.type_inference_engine.unify_types(unified_type, rt)
                        if unified:
                            unified_type = unified
                        else:
                            return ANY_TYPE  # Can't unify - use ANY
                    return unified_type
            return ANY_TYPE
        elif isinstance(statement, RaiseStatement):
            # Raise statements don't return a value, but we check the message type
            if statement.message:
                message_type = self.check_statement(statement.message, env)
                # Message should be a string, but we're lenient
                if message_type != STRING_TYPE and message_type != ANY_TYPE:
                    self.errors.append(
                        f"Line {getattr(statement, 'line_number', '?')}: Raise message should be String, got {message_type}"
                    )
            return ANY_TYPE  # Raise statements don't produce a value
        elif hasattr(statement, 'node_type') and getattr(statement, 'node_type', None) == 'conditional_compilation_block':
            # Conditional compilation block - type-check both branches
            branch_env = env.create_child_scope() if hasattr(env, 'create_child_scope') else env
            for stmt in (statement.body or []):
                self.check_statement(stmt, branch_env)
            if statement.else_body:
                for stmt in statement.else_body:
                    self.check_statement(stmt, branch_env)
            return ANY_TYPE
        else:
            raise TypeCheckError(f"Unsupported statement type: {statement.__class__.__name__}")
            return ANY_TYPE
    
    def check_expression(self, expression: Any, env: TypeEnvironment) -> Type:
        """Check the type of an expression. Alias for check_statement for compatibility."""
        return self.check_statement(expression, env)
    
    def check_variable_declaration(self, declaration: VariableDeclaration, env: TypeEnvironment) -> Type:
        """Check the type of a variable declaration with bidirectional inference."""
        # If there's a type annotation, use bidirectional inference
        if declaration.type_annotation:
            declared_type = get_type_by_name(declaration.type_annotation)
            
            # Use bidirectional inference: expected type guides value type inference
            value_type = self.type_inference.infer_with_expected_type(
                declaration.value, declared_type, env.variables
            )
            
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
        
        # If there's no type annotation, infer without expected type
        value_type = self.check_expression(declaration.value, env)
        inferred_type = self.type_inference.infer_variable_declaration(declaration, env.variables)
        if inferred_type != value_type and inferred_type != ANY_TYPE:
            # If inference came up with a more specific type, use it
            value_type = inferred_type
        
        # If value is a function reference, get its type
        if hasattr(declaration.value, '__class__') and declaration.value.__class__.__name__ == 'Identifier':
            try:
                func_type = env.get_function_type(declaration.value.name)
                value_type = func_type
            except TypeCheckError:
                pass  # Not a function, use inferred type
        
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
                    # New format: dict mapping parameter name to list of trait names
                    if isinstance(definition.type_constraints, dict):
                        trait_names = definition.type_constraints.get(param_name, [])
                        for trait_name in trait_names:
                            # For now, store trait names directly
                            # Validation will happen at instantiation time
                            constraints.append(trait_name)
                    # Old format: list of constraint objects (for backward compatibility)
                    elif isinstance(definition.type_constraints, list):
                        for constraint in definition.type_constraints:
                            if hasattr(constraint, 'type_parameter') and constraint.type_parameter == param_name:
                                # Convert AST constraint to type system constraint
                                constraint_type = get_type_by_name(constraint.constraint_type)
                                constraints.append(constraint_type)
                
                # Store parameter info with constraints
                if constraints:
                    # For now, we'll just track that constraints exist
                    # Full validation happens during type checking
                    pass
                
                type_param_info.append({
                    'name': param_name,
                    'constraints': constraints
                })
            
            # Note: We don't enter a generic scope here anymore
            # Just track that this is a generic function
        
        # Create a new environment for the function scope
        function_env = TypeEnvironment(env)
        if is_generic:
            function_env.generic_context = env.generic_context
            function_env.type_parameters = env.type_parameters
        
        # Process parameters
        param_types = []
        min_params = 0  # Count of required parameters (without defaults)
        has_defaults = False
        has_variadic = False
        variadic_index = -1
        
        for i, param in enumerate(definition.parameters):
            param_type = ANY_TYPE
            
            # Check if this is a variadic parameter
            is_variadic_param = hasattr(param, 'is_variadic') and param.is_variadic
            if is_variadic_param:
                has_variadic = True
                variadic_index = i
            
            if param.type_annotation:
                # Check if this is a type parameter
                if env.is_type_parameter(param.type_annotation):
                    param_type = GenericParameter(param.type_annotation)
                else:
                    param_type = get_type_by_name(param.type_annotation)
                
                # Wrap variadic parameter type in ListType
                if is_variadic_param:
                    param_type = ListType(param_type)
            elif is_variadic_param:
                # Variadic parameter with no type annotation defaults to List of Any
                param_type = ListType(ANY_TYPE)
            
            param_types.append(param_type)
            function_env.define_variable(param.name, param_type)
            
            # Track if parameter has a default value
            if hasattr(param, 'default_value') and param.default_value is not None:
                has_defaults = True
            elif not is_variadic_param:
                # If no default and not variadic, this parameter is required
                if not has_defaults and not has_variadic:
                    min_params += 1
        
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
        
        # Create function type with default parameter info
        function_type = FunctionType(param_types, return_type)
        function_type.has_defaults = has_defaults
        function_type.min_params = min_params
        function_type.variadic = has_variadic
        function_type.variadic_index = variadic_index
        
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
        
        # Allow ANY_TYPE (unknown) and FunctionType (likely a method call whose
        # return type could not be statically resolved) to pass through without
        # an error. Only hard-fail on concrete non-boolean types.
        if (not isinstance(condition_type, (AnyType, FunctionType))
                and not condition_type.is_compatible_with(BOOLEAN_TYPE)):
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
        
        # Allow ANY_TYPE (unknown) and FunctionType (likely a method call whose
        # return type could not be statically resolved) to pass through without
        # an error. Only hard-fail on concrete non-boolean types.
        if (not isinstance(condition_type, (AnyType, FunctionType))
                and not condition_type.is_compatible_with(BOOLEAN_TYPE)):
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
    
    def check_repeat_while_loop(self, loop: RepeatWhileLoop, env: TypeEnvironment) -> Type:
        """Check a repeat-while loop (natural language while loop)."""
        # Check the condition
        condition_type = self.check_statement(loop.condition, env)
        
        # Condition should be boolean-compatible (any type can be truthy/falsy)
        # No strict type checking needed for conditions in NLPL
        
        # Check the body
        loop_env = TypeEnvironment(env)
        result_type = NULL_TYPE
        for stmt in loop.body:
            result_type = self.check_statement(stmt, loop_env)
        
        # Check else body if present
        if loop.else_body:
            for stmt in loop.else_body:
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
        """Check a function call with bidirectional type inference."""
        # Handle module.function calls (function name contains a dot)
        if isinstance(call.name, str) and '.' in call.name:
            # Module member access - type check arguments but return ANY_TYPE
            # since we don't track module member types yet
            arg_types = [self.check_statement(arg, env) for arg in call.arguments]
            return ANY_TYPE
        
        try:
            # Get the function type
            function_type = env.get_function_type(call.name)
            
            # Count total arguments (positional + named)
            total_args = len(call.arguments)
            if hasattr(call, 'named_arguments') and call.named_arguments:
                # Defensive: ensure named_arguments is actually a dict/list, not an int
                if isinstance(call.named_arguments, (dict, list)):
                    total_args += len(call.named_arguments)
            
            # Check argument count (skip for variadic functions)
            has_variadic = getattr(function_type, 'variadic', False)
            if not has_variadic:
                # Count required parameters (those without defaults)
                required_params = len(function_type.param_types)
                if hasattr(function_type, 'has_defaults') and function_type.has_defaults:
                    # If function has defaults, allow fewer arguments
                    required_params = function_type.min_params if hasattr(function_type, 'min_params') else 0
                
                # Allow arguments between min and max
                max_params = len(function_type.param_types)
                if total_args < required_params or total_args > max_params:
                    if required_params == max_params:
                        self.errors.append(
                            f"Type error: Function '{call.name}' expects {required_params} arguments, got {total_args}"
                        )
                    else:
                        self.errors.append(
                            f"Type error: Function '{call.name}' expects {required_params}-{max_params} arguments, got {total_args}"
                        )
                    return function_type.return_type
            else:
                # Variadic function - check we have at least min_params
                min_required = function_type.min_params if hasattr(function_type, 'min_params') else 0
                variadic_index = function_type.variadic_index if hasattr(function_type, 'variadic_index') else len(function_type.param_types) - 1
                
                # Need at least enough args for non-variadic parameters
                if total_args < min_required:
                    self.errors.append(
                        f"Type error: Function '{call.name}' expects at least {min_required} arguments, got {total_args}"
                    )
                    return function_type.return_type
            
            # Type check positional arguments
            arg_types = self.type_inference.infer_argument_types_from_function(
                function_type, call.arguments, env.variables
            )
            
            # Type check named arguments (just ensure expressions are valid, not param matching)
            # Note: We can't match named args to param types here because FunctionType
            # doesn't include parameter names, only types
            if hasattr(call, 'named_arguments') and call.named_arguments:
                for param_name, arg_expr in call.named_arguments.items():
                    # Just check that the expression is valid
                    self.check_statement(arg_expr, env)
            
            # Only check positional argument types against parameter types
            # Named arguments will be validated at runtime
            # For variadic functions, stop type checking before the variadic parameter
            if has_variadic and hasattr(function_type, 'variadic_index'):
                # Only check non-variadic parameters
                check_count = min(len(call.arguments), function_type.variadic_index)
                positional_param_types = function_type.param_types[:check_count]
                arg_types_to_check = arg_types[:check_count]
            else:
                positional_param_types = function_type.param_types[:len(call.arguments)]
                arg_types_to_check = arg_types
            
            for i, (arg_type, param_type) in enumerate(zip(arg_types_to_check, positional_param_types)):
                if param_type != ANY_TYPE and not arg_type.is_compatible_with(param_type):
                    self.errors.append(
                        f"Type error: Function '{call.name}' argument {i+1} expects type '{self._type_name(param_type)}', got '{self._type_name(arg_type)}'"
                    )
            
            return function_type.return_type
        except TypeCheckError:
            # If the function is not defined, assume it's a runtime-registered function (stdlib)
            # Check arguments without expected types to ensure they're valid expressions
            arg_types = [self.check_statement(arg, env) for arg in call.arguments]
            # Also check named arguments
            if hasattr(call, 'named_arguments') and call.named_arguments:
                for param_name, arg_expr in call.named_arguments.items():
                    self.check_statement(arg_expr, env)
            # Return ANY_TYPE to allow runtime resolution
            # NOTE: The function MUST exist at runtime or it will fail there
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
        comparison_ops = ['==', '!=', '<', '>', '<=', '>=', 
                         'equals', 'equal to', 'is equal to', 
                         'not equal to', 'is not equal to', 
                         'greater than', 'is greater than', 
                         'less than', 'is less than',
                         'greater than or equal to', 'is greater than or equal to', 
                         'less than or equal to', 'is less than or equal to']
        if op in comparison_ops:
            # For equality operators, any types can be compared
            if op in ['==', '!=', 'equals', 'equal to', 'is equal to', 'not equal to', 'is not equal to']:
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
        
        # Bitwise operators (require integers)
        bitwise_ops = ['bitwise and', 'bitwise or', 'bitwise xor', '&', '|', '^', '<<', '>>', 'shift left', 'shift right']
        if op in bitwise_ops:
            if not left_type.is_compatible_with(INTEGER_TYPE):
                self.errors.append(
                    f"Type error: Left operand of '{op}' must be an integer, got '{self._type_name(left_type)}'"
                )
            
            if not right_type.is_compatible_with(INTEGER_TYPE):
                self.errors.append(
                    f"Type error: Right operand of '{op}' must be an integer, got '{self._type_name(right_type)}'"
                )
            
            return INTEGER_TYPE
        
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
        
        elif op in ['~', 'bitwise not']:
            if not operand_type.is_compatible_with(INTEGER_TYPE):
                self.errors.append(
                    f"Type error: Operand of '{op}' must be an integer, got '{self._type_name(operand_type)}'"
                )
            
            return INTEGER_TYPE
        
        else:
            self.errors.append(f"Unsupported unary operator: {op}")
            return ANY_TYPE
    
    def check_literal(self, literal: Literal, env: TypeEnvironment) -> Type:
        """Check a literal value."""
        return infer_type(literal.value)
    
    def check_identifier(self, identifier: Identifier, env: TypeEnvironment) -> Type:
        """Check an identifier (variable or function reference)."""
        try:
            # First try to get it as a variable
            return env.get_variable_type(identifier.name)
        except TypeCheckError:
            # If not a variable, try to get it as a function
            try:
                return env.get_function_type(identifier.name)
            except TypeCheckError as e:
                self.errors.append(str(e))
                return ANY_TYPE
    
    def check_list_expression(self, list_expr, env: TypeEnvironment) -> Type:
        """Check a list literal: [1, 2, 3]."""
        from ..typesystem.types import ListType
        
        if not list_expr.elements:
            # Empty list - return generic List type
            return ListType(ANY_TYPE)
        
        # Check all elements and infer common type
        element_types = [self.check_statement(elem, env) for elem in list_expr.elements]
        
        # Find common type (simplified - use first element's type)
        common_type = element_types[0]
        for elem_type in element_types[1:]:
            if not elem_type.is_compatible_with(common_type):
                # Types don't match - use ANY_TYPE
                common_type = ANY_TYPE
                break
        
        return ListType(common_type)
    
    def check_dict_expression(self, dict_expr, env: TypeEnvironment) -> Type:
        """Check a dictionary literal: {"key": "value"}."""
        from ..typesystem.types import DictionaryType
        
        if not dict_expr.entries:
            # Empty dict - return generic Dict type
            return DictionaryType(ANY_TYPE, ANY_TYPE)
        
        # Check all key-value pairs
        key_types = []
        value_types = []
        for key_expr, value_expr in dict_expr.entries:
            key_types.append(self.check_statement(key_expr, env))
            value_types.append(self.check_statement(value_expr, env))
        
        # Find common key and value types
        common_key_type = key_types[0]
        common_value_type = value_types[0]
        
        for key_type in key_types[1:]:
            if not key_type.is_compatible_with(common_key_type):
                common_key_type = ANY_TYPE
                break
        
        for value_type in value_types[1:]:
            if not value_type.is_compatible_with(common_value_type):
                common_value_type = ANY_TYPE
                break
        
        return DictionaryType(common_key_type, common_value_type)
    
    def check_list_comprehension(self, comp_expr, env: TypeEnvironment) -> Type:
        """Check a list comprehension: [x for x in range(10)]."""
        from ..typesystem.types import ListType
        
        # Create new scope for comprehension variable
        comp_env = TypeEnvironment(env)
        
        # Check iterable type
        iterable_type = self.check_statement(comp_expr.iterable, env)
        
        # Define loop variable in comprehension scope
        # For now, use ANY_TYPE for the loop variable
        comp_env.define_variable(comp_expr.target.name, ANY_TYPE)
        
        # Check condition if present
        if comp_expr.condition:
            self.check_statement(comp_expr.condition, comp_env)
        
        # Check element expression
        element_type = self.check_statement(comp_expr.element, comp_env)
        
        return ListType(element_type)
    
    def check_dict_comprehension(self, comp_expr, env: TypeEnvironment) -> Type:
        """Check a dict comprehension: {k: v for k, v in items}."""
        from ..typesystem.types import DictionaryType
        
        # Create new scope for comprehension variable
        comp_env = TypeEnvironment(env)
        
        # Check iterable type
        iterable_type = self.check_statement(comp_expr.iterable, env)
        
        # Define loop variable in comprehension scope
        comp_env.define_variable(comp_expr.target.name, ANY_TYPE)
        
        # Check condition if present
        if comp_expr.condition:
            self.check_statement(comp_expr.condition, comp_env)
        
        # Check key and value expressions
        key_type = self.check_statement(comp_expr.key, comp_env)
        value_type = self.check_statement(comp_expr.value, comp_env)
        
        return DictionaryType(key_type, value_type)

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
    
    def check_lambda_expression(self, lambda_expr, env: TypeEnvironment) -> FunctionType:
        """
        Check a lambda expression and infer its type.
        
        Uses type inference to determine parameter and return types.
        Supports bidirectional type inference when expected type is available.
        """
        # Use type inference to get the lambda's function type
        # The type inference engine handles bidirectional inference
        lambda_type = self.type_inference.infer_lambda_types(
            lambda_expr, 
            None,  # No expected type (context-free checking)
            env.variables
        )
        
        return lambda_type
    
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
        """
        Check a member access expression: object.member
        
        Uses type inference engine for proper type propagation through
        member access chains (e.g., obj.method().property.another_method()).
        """
        # Use type inference engine for comprehensive member access handling
        inferred_type = self.type_inference.infer_member_access_type(expr, env.variables)
        
        # If inference succeeded, return the inferred type
        if inferred_type != ANY_TYPE:
            # When this is a method call (has arguments) and inference returned
            # FunctionType, we should return the function's return type, not the
            # FunctionType itself. This handles native dict/list method calls such
            # as d.has("key"), d.size(), d.get("k") used directly in if-conditions.
            if isinstance(inferred_type, FunctionType) and getattr(expr, 'is_method_call', False):
                rt = getattr(inferred_type, 'return_type', None)
                return rt if rt is not None else ANY_TYPE
            return inferred_type
        
        # Fallback: Check the object expression directly
        obj_type = self.check_statement(expr.object_expr, env)
        
        # If object type is a class type, check if member exists
        if isinstance(obj_type, ClassType):
            member_name = expr.member_name
            
            # Check properties
            if member_name in obj_type.properties:
                return obj_type.properties[member_name]
            
            # Check methods
            if member_name in obj_type.methods:
                method_type = obj_type.methods[member_name]
                
                # If this is a method call, return the return type
                if hasattr(expr, 'is_method_call') and expr.is_method_call:
                    if isinstance(method_type, FunctionType):
                        return method_type.return_type
                return method_type
            
            # Member not found - return ANY for error recovery
            self.errors.append(
                f"Member '{member_name}' not found in class '{obj_type.name}'"
            )
            return ANY_TYPE
        
        # For other types, return ANY_TYPE
        return ANY_TYPE
    
    def check_index_expression(self, expr: Any, env: TypeEnvironment) -> Type:
        """
        Check an index expression: array[index] or dict[key]
        
        Validates that:
        - The indexed object is a collection type (list, dict, string)
        - The index type matches the expected type (integer for lists, key type for dicts)
        """
        # Use type inference engine for proper index type checking
        inferred_type = self.type_inference.infer_index_expression_type(expr, env.variables)
        
        # Check the array/collection type
        array_type = self.check_statement(expr.array_expr, env)
        
        # Check the index type
        index_type = self.check_statement(expr.index_expr, env)
        
        # Validate based on collection type
        if isinstance(array_type, ListType):
            # List indexing requires integer index
            if not index_type.is_compatible_with(INTEGER_TYPE) and index_type != ANY_TYPE:
                self.errors.append(
                    f"List index must be Integer, got {index_type}"
                )
            return array_type.element_type
        
        elif isinstance(array_type, DictionaryType):
            # Dictionary access requires key type
            if not index_type.is_compatible_with(array_type.key_type) and index_type != ANY_TYPE:
                self.errors.append(
                    f"Dictionary key must be {array_type.key_type}, got {index_type}"
                )
            return array_type.value_type
        
        elif array_type == STRING_TYPE:
            # String indexing requires integer index, returns string (character)
            if not index_type.is_compatible_with(INTEGER_TYPE) and index_type != ANY_TYPE:
                self.errors.append(
                    f"String index must be Integer, got {index_type}"
                )
            return STRING_TYPE
        
        elif array_type != ANY_TYPE:
            # Type error - trying to index non-indexable type
            self.errors.append(
                f"Cannot index into type {array_type}"
            )
        
        return inferred_type

    def check_generic_type_instantiation(self, expr: Any, env: TypeEnvironment) -> Type:
        """
        Check a generic type instantiation: create list, create list of Integer
        
        Returns the appropriate generic type based on the instantiation:
        - create list of Integer -> ListType(INTEGER_TYPE)
        - create dict of String to Integer -> DictionaryType(STRING_TYPE, INTEGER_TYPE)
        - create list (no type args) -> ListType(ANY_TYPE) with type inference
        """
        from nlpl.typesystem.types import ListType, DictionaryType, SetType, TupleType
        
        generic_name = expr.generic_name.lower()
        
        # Handle list types
        if generic_name == "list":
            if expr.type_args and len(expr.type_args) > 0:
                # Explicit type: create list of Integer
                element_type = get_type_by_name(expr.type_args[0])
                return ListType(element_type)
            else:
                # Type inference: create list (will infer from usage)
                # Check if there's an initial value to infer from
                if expr.initial_value:
                    # Infer element type from initial value
                    init_type = self.check_statement(expr.initial_value, env)
                    if isinstance(init_type, ListType):
                        return init_type  # Already a list with inferred type
                    else:
                        return ListType(init_type)  # Single element
                return ListType(ANY_TYPE)  # Will infer later
        
        # Handle dict/dictionary/map types
        elif generic_name in ("dict", "dictionary", "map"):
            if expr.type_args and len(expr.type_args) >= 2:
                # Explicit types: create dict of String to Integer
                key_type = get_type_by_name(expr.type_args[0])
                value_type = get_type_by_name(expr.type_args[1])
                return DictionaryType(key_type, value_type)
            else:
                # Type inference: create dict
                if expr.initial_value:
                    init_type = self.check_statement(expr.initial_value, env)
                    if isinstance(init_type, DictionaryType):
                        return init_type
                return DictionaryType(ANY_TYPE, ANY_TYPE)
        
        # Handle set types
        elif generic_name == "set":
            if expr.type_args and len(expr.type_args) > 0:
                element_type = get_type_by_name(expr.type_args[0])
                return SetType(element_type)
            else:
                if expr.initial_value:
                    init_type = self.check_statement(expr.initial_value, env)
                    if isinstance(init_type, SetType):
                        return init_type
                    else:
                        return SetType(init_type)
                return SetType(ANY_TYPE)
        
        # Handle tuple types
        elif generic_name == "tuple":
            if expr.type_args and len(expr.type_args) > 0:
                element_types = [get_type_by_name(t) for t in expr.type_args]
                return TupleType(element_types)
            else:
                if expr.initial_value:
                    # Infer from initial values
                    init_type = self.check_statement(expr.initial_value, env)
                    if isinstance(init_type, TupleType):
                        return init_type
                return TupleType([ANY_TYPE])
        
        # Handle queue and stack (simplified as List)
        elif generic_name in ("queue", "stack"):
            if expr.type_args and len(expr.type_args) > 0:
                element_type = get_type_by_name(expr.type_args[0])
                return ListType(element_type)
            else:
                return ListType(ANY_TYPE)
        
        # Unknown generic type
        else:
            self.errors.append(f"Unknown generic type: {generic_name}")
            return ANY_TYPE

    def check_generic_constraints(self, type_params: list, type_args: list, 
                                   constraints: dict, context: str = "") -> bool:
        """
        Check if type arguments satisfy generic type parameter constraints.
        
        Args:
            type_params: List of type parameter names (e.g., ['T', 'R'])
            type_args: List of concrete types being substituted
            constraints: Dict mapping parameter name to list of trait names
            context: Context string for error messages (e.g., "function sum")
            
        Returns:
            True if all constraints are satisfied, False otherwise
        """
        from nlpl.typesystem.types import TraitType, COMPARABLE_TRAIT, EQUATABLE_TRAIT, PRINTABLE_TRAIT
        from nlpl.typesystem.generic_types import GenericTypeConstraint
        
        if len(type_params) != len(type_args):
            self.errors.append(
                f"Type error in {context}: Expected {len(type_params)} type arguments, got {len(type_args)}"
            )
            return False
        
        # Map of predefined traits
        TRAIT_MAP = {
            'Comparable': COMPARABLE_TRAIT,
            'Equatable': EQUATABLE_TRAIT,
            'Printable': PRINTABLE_TRAIT,
            # Add more traits as they're defined
        }
        
        all_satisfied = True
        
        for param_name, type_arg in zip(type_params, type_args):
            # Check if this parameter has constraints
            if param_name not in constraints:
                continue
            
            trait_names = constraints[param_name]
            
            for trait_name in trait_names:
                # Get the trait type
                trait = TRAIT_MAP.get(trait_name)
                
                if trait is None:
                    self.errors.append(
                        f"Type error in {context}: Unknown trait '{trait_name}'"
                    )
                    all_satisfied = False
                    continue
                
                # Check if the type argument implements the trait
                if not trait.is_implemented_by(type_arg):
                    self.errors.append(
                        f"Type error in {context}: Type '{self._type_name(type_arg)}' does not implement trait '{trait_name}'"
                    )
                    all_satisfied = False
        
        return all_satisfied
    
    def validate_generic_function_call(self, func_name: str, func_def, type_args: list) -> bool:
        """
        Validate that a generic function call satisfies trait bounds.
        
        Args:
            func_name: Name of the function being called
            func_def: FunctionDefinition AST node
            type_args: List of concrete type arguments
            
        Returns:
            True if valid, False otherwise
        """
        if not hasattr(func_def, 'type_parameters') or not func_def.type_parameters:
            return True  # Not a generic function
        
        # Get constraints from function definition
        constraints = {}
        if hasattr(func_def, 'type_constraints') and isinstance(func_def.type_constraints, dict):
            constraints = func_def.type_constraints
        
        return self.check_generic_constraints(
            func_def.type_parameters,
            type_args,
            constraints,
            context=f"function '{func_name}'"
        )
 