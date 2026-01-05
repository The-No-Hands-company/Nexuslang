"""
Type inference for the NLPL language.
This module provides advanced type inference functionality.
"""

from typing import Dict, List, Optional, Set, Union, Any, Tuple
from ..parser.ast import (
    Program, VariableDeclaration, FunctionDefinition, Parameter,
    BinaryOperation, UnaryOperation, Literal, Identifier, FunctionCall,
    Expression, ClassDefinition, MethodDefinition, ReturnStatement
)
from ..typesystem.types import (
    Type, PrimitiveType, ListType, DictionaryType, ClassType, 
    FunctionType, UnionType, AnyType, GenericType, GenericParameter,
    INTEGER_TYPE, FLOAT_TYPE, STRING_TYPE, BOOLEAN_TYPE, NULL_TYPE, ANY_TYPE,
    get_type_by_name, infer_type
)


class TypeInferenceEngine:
    """Engine for inferring types in NLPL programs."""
    
    def __init__(self):
        self.type_constraints: Dict[str, Type] = {}
        self.type_variables: Dict[str, Type] = {}
        self.next_type_var = 0
        self.function_return_types: Dict[str, Type] = {}
        self.variable_types: Dict[str, Type] = {}
    
    def fresh_type_variable(self) -> str:
        """Generate a fresh type variable name."""
        var_name = f"T{self.next_type_var}"
        self.next_type_var += 1
        return var_name
    
    def reset(self):
        """Reset the inference engine state."""
        self.type_constraints.clear()
        self.type_variables.clear()
        self.function_return_types.clear()
        self.variable_types.clear()
        self.next_type_var = 0
    
    def infer_expression_type(self, expr: Expression, env: Dict[str, Type]) -> Type:
        """Infer the type of an expression based on context."""
        if isinstance(expr, Literal):
            return infer_type(expr.value)
        
        if isinstance(expr, Identifier):
            if expr.name in env:
                return env[expr.name]
            if expr.name in self.variable_types:
                return self.variable_types[expr.name]
            return ANY_TYPE  # Unresolved identifier
        
        if isinstance(expr, BinaryOperation):
            left_type = self.infer_expression_type(expr.left, env)
            right_type = self.infer_expression_type(expr.right, env)
            
            # Infer type based on operation
            if expr.operator in ('plus', 'minus', 'times', 'divided by', 'modulo', '+', '-', '*', '/', '%'):
                # If both are integers, result is integer
                if left_type == INTEGER_TYPE and right_type == INTEGER_TYPE:
                    if expr.operator in ('divided by', '/'):
                        return FLOAT_TYPE  # Division always returns float
                    return INTEGER_TYPE
                # If either is float, result is float
                elif left_type in (INTEGER_TYPE, FLOAT_TYPE) and right_type in (INTEGER_TYPE, FLOAT_TYPE):
                    return FLOAT_TYPE
                # String concatenation
                elif expr.operator in ('plus', '+') and (left_type == STRING_TYPE or right_type == STRING_TYPE):
                    return STRING_TYPE
                
            elif expr.operator in ('to the power of', 'power', '**'):
                # Power operations
                if left_type in (INTEGER_TYPE, FLOAT_TYPE) and right_type in (INTEGER_TYPE, FLOAT_TYPE):
                    return FLOAT_TYPE  # Power usually returns float
                
            elif expr.operator in ('equals', 'is equal to', 'not equal to', 'is not equal to', 
                                    'greater than', 'is greater than', 'less than', 'is less than',
                                    'greater than or equal to', 'is greater than or equal to',
                                    'less than or equal to', 'is less than or equal to',
                                    '==', '!=', '<', '>', '<=', '>='):
                return BOOLEAN_TYPE
                
            elif expr.operator in ('and', 'or'):
                if left_type == BOOLEAN_TYPE and right_type == BOOLEAN_TYPE:
                    return BOOLEAN_TYPE
            
            return ANY_TYPE  # Default for unresolved operations
        
        if isinstance(expr, UnaryOperation):
            operand_type = self.infer_expression_type(expr.operand, env)
            
            if expr.operator == '-' and operand_type in (INTEGER_TYPE, FLOAT_TYPE):
                return operand_type
                
            elif expr.operator == 'not' and operand_type == BOOLEAN_TYPE:
                return BOOLEAN_TYPE
                
            return ANY_TYPE  # Default for unresolved operations
        
        if isinstance(expr, FunctionCall):
            # For function calls, check if we know the return type
            if expr.name in env and isinstance(env[expr.name], FunctionType):
                return env[expr.name].return_type
            if expr.name in self.function_return_types:
                return self.function_return_types[expr.name]
            return ANY_TYPE  # Unresolved function
        
        # Handle list literals
        if hasattr(expr, 'node_type') and expr.node_type == 'list_literal':
            if hasattr(expr, 'elements') and expr.elements:
                # Infer element type from first element
                element_type = self.infer_expression_type(expr.elements[0], env)
                return ListType(element_type)
            return ListType(ANY_TYPE)
        
        # Handle dictionary literals
        if hasattr(expr, 'node_type') and expr.node_type == 'dictionary_literal':
            if hasattr(expr, 'keys') and expr.keys:
                key_type = self.infer_expression_type(expr.keys[0], env)
                value_type = self.infer_expression_type(expr.values[0], env)
                return DictionaryType(key_type, value_type)
            return DictionaryType(ANY_TYPE, ANY_TYPE)
        
        return ANY_TYPE  # Default for unresolved expressions
    
    def infer_with_expected_type(self, expr: Expression, expected: Optional[Type], env: Dict[str, Type]) -> Type:
        """
        Infer expression type with expected type hint (bidirectional inference).
        
        This enables context-sensitive type inference where the expected type
        influences how we infer the expression's type.
        
        Args:
            expr: Expression to infer type for
            expected: Expected type from context (e.g., from variable annotation)
            env: Type environment
            
        Returns:
            Inferred type
        """
        if expected is None:
            # No expected type, fall back to regular inference
            return self.infer_expression_type(expr, env)
        
        # Handle list literals with expected element type
        if hasattr(expr, 'node_type') and expr.node_type == 'list_literal':
            if isinstance(expected, ListType):
                element_type = expected.element_type
                # Check all elements are compatible with expected element type
                if hasattr(expr, 'elements'):
                    for elem in expr.elements:
                        elem_type = self.infer_with_expected_type(elem, element_type, env)
                        if not elem_type.is_compatible_with(element_type):
                            # Type mismatch - fall back to regular inference
                            return self.infer_expression_type(expr, env)
                return expected
        
        # Handle dictionary literals with expected key/value types
        if hasattr(expr, 'node_type') and expr.node_type == 'dictionary_literal':
            if isinstance(expected, DictionaryType):
                key_type = expected.key_type
                value_type = expected.value_type
                # Check all entries are compatible
                if hasattr(expr, 'keys') and hasattr(expr, 'values'):
                    for k, v in zip(expr.keys, expr.values):
                        k_type = self.infer_with_expected_type(k, key_type, env)
                        v_type = self.infer_with_expected_type(v, value_type, env)
                        if not (k_type.is_compatible_with(key_type) and v_type.is_compatible_with(value_type)):
                            return self.infer_expression_type(expr, env)
                return expected
        
        # Handle lambda expressions with expected function type
        if hasattr(expr, 'node_type') and expr.node_type == 'lambda_expression':
            if isinstance(expected, FunctionType):
                # Infer lambda types from expected function type
                return self.infer_lambda_types(expr, expected, env)
            else:
                # No expected function type, try to infer from lambda itself
                return self.infer_lambda_types(expr, None, env)
        
        # Handle LambdaExpression class directly
        if expr.__class__.__name__ == 'LambdaExpression':
            if isinstance(expected, FunctionType):
                return self.infer_lambda_types(expr, expected, env)
            else:
                return self.infer_lambda_types(expr, None, env)
        
        # Handle function calls with expected return type
        if isinstance(expr, FunctionCall):
            # Even if we expect a specific return type, we still need to infer the actual return type
            # But we can use the expected type to guide argument type inference
            inferred = self.infer_expression_type(expr, env)
            if inferred.is_compatible_with(expected):
                return expected
            return inferred
        
        # For other expressions, check if inferred type matches expected
        inferred = self.infer_expression_type(expr, env)
        if inferred.is_compatible_with(expected):
            return expected  # Use expected type for better precision
        
        return inferred  # Fall back to inferred type
    
    def infer_variable_declaration(self, declaration: VariableDeclaration, env: Dict[str, Type], generic_context: Optional['GenericTypeContext'] = None) -> Type:
        """Infer the type of a variable declaration."""
        # If there's an explicit type annotation, use it
        if declaration.type_annotation:
            type_ = get_type_by_name(declaration.type_annotation)
            
            # If we have a generic context, substitute any generic parameters
            if generic_context:
                type_ = generic_context.get_substituted_type(type_, {})
            
            # Use bidirectional inference with expected type
            if hasattr(declaration, 'value') and declaration.value:
                inferred = self.infer_with_expected_type(declaration.value, type_, env)
                return inferred
            
            return type_
        
        # Otherwise infer from the initial value
        if hasattr(declaration, 'value') and declaration.value:
            return self.infer_expression_type(declaration.value, env)
        
        return ANY_TYPE
    
    def infer_function_return_type(self, function: FunctionDefinition, env: Dict[str, Type]) -> Type:
        """Infer the return type of a function based on its body."""
        # If there's an explicit return type annotation, use it
        if function.return_type:
            return get_type_by_name(function.return_type)
        
        # Create a new environment with parameter types
        func_env = env.copy()
        
        # Create generic context if the function has type parameters
        generic_context = None
        if hasattr(function, 'type_parameters') and function.type_parameters:
            generic_context = self.create_generic_context(
                function.name,
                function.type_parameters,
                getattr(function, 'type_constraints', None)
            )
        
        # Process parameters
        for param in function.parameters:
            if param.type_annotation:
                param_type = get_type_by_name(param.type_annotation)
                if generic_context:
                    param_type = generic_context.get_substituted_type(param_type, {})
                func_env[param.name] = param_type
            else:
                # If parameter has no type annotation, use a type variable
                func_env[param.name] = ANY_TYPE
        
        # Infer types for variables in the function body
        self.infer_types_in_block(function.body, func_env, generic_context)
        
        # Analyze return statements to infer return type
        return_types = []
        for stmt in function.body:
            if hasattr(stmt, 'node_type') and stmt.node_type == 'return_statement':
                if stmt.value:
                    return_type = self.infer_expression_type(stmt.value, func_env)
                    return_types.append(return_type)
                else:
                    return_types.append(NULL_TYPE)
        
        if not return_types:
            # Function has no return statements, assume it returns null
            return NULL_TYPE
            
        # If there are multiple return statements, unify their types
        result_type = return_types[0]
        for rt in return_types[1:]:
            unified = self.unify_types(result_type, rt)
            if unified:
                result_type = unified
            else:
                # If types can't be unified, fallback to ANY
                return ANY_TYPE
                
        return result_type
    
    def infer_class_type(self, class_def: ClassDefinition, env: Dict[str, Type]) -> Type:
        """Infer the type of a class definition."""
        # Create generic context if the class has type parameters
        generic_context = None
        if hasattr(class_def, 'type_parameters') and class_def.type_parameters:
            generic_context = self.create_generic_context(
                class_def.name,
                class_def.type_parameters,
                getattr(class_def, 'type_constraints', None)
            )
        
        # Process properties
        properties = {}
        for prop in class_def.properties:
            if isinstance(prop, PropertyDeclaration):
                prop_type = ANY_TYPE
                if prop.type_annotation:
                    prop_type = get_type_by_name(prop.type_annotation)
                    if generic_context:
                        prop_type = generic_context.get_substituted_type(prop_type, {})
                properties[prop.name] = prop_type
        
        # Process methods
        methods = {}
        for method in class_def.methods:
            if isinstance(method, MethodDefinition):
                # Create a new environment for method scope
                method_env = env.copy()
                
                # Add 'this' parameter
                method_env['this'] = ClassType(class_def.name, properties, {}, None)
                
                # Process method parameters
                param_types = []
                for param in method.parameters:
                    param_type = ANY_TYPE
                    if param.type_annotation:
                        param_type = get_type_by_name(param.type_annotation)
                        if generic_context:
                            param_type = generic_context.get_substituted_type(param_type, {})
                    param_types.append(param_type)
                    method_env[param.name] = param_type
                
                # Infer return type
                return_type = ANY_TYPE
                if method.return_type:
                    return_type = get_type_by_name(method.return_type)
                    if generic_context:
                        return_type = generic_context.get_substituted_type(return_type, {})
                else:
                    return_type = self.infer_function_return_type(method, method_env)
                
                # Create method type
                method_type = FunctionType(param_types, return_type)
                methods[method.name] = method_type
        
        # Create class type
        class_type = ClassType(class_def.name, properties, methods, None)
        
        # If this is a generic class, wrap it in a GenericType
        if generic_context:
            class_type = GenericType(
                class_def.name,
                class_def.type_parameters,
                class_type
            )
        
        return class_type
    
    def unify_types(self, type1: Type, type2: Type) -> Optional[Type]:
        """Unify two types, returning a common supertype if possible."""
        if type1 == type2:
            return type1
        
        if type1 == ANY_TYPE or type2 == ANY_TYPE:
            return ANY_TYPE
        
        if isinstance(type1, UnionType) and isinstance(type2, UnionType):
            # Unify union types by taking the union of their types
            unified_types = set(type1.types + type2.types)
            return UnionType(list(unified_types))
        
        if isinstance(type1, UnionType):
            # If type2 is compatible with any of type1's types, return type1
            if any(type2.is_compatible_with(t) for t in type1.types):
                return type1
        
        if isinstance(type2, UnionType):
            # If type1 is compatible with any of type2's types, return type2
            if any(type1.is_compatible_with(t) for t in type2.types):
                return type2
        
        # If one type is compatible with the other, return the more general type
        if type1.is_compatible_with(type2):
            return type2
        if type2.is_compatible_with(type1):
            return type1
        
        return None  # Types cannot be unified
    
    def infer_types_in_block(self, statements: List[Any], initial_env: Dict[str, Type] = None, generic_context: Optional[GenericTypeContext] = None) -> Dict[str, Type]:
        """Infer types for variables in a block of statements."""
        env = initial_env or {}
        
        for stmt in statements:
            if isinstance(stmt, VariableDeclaration):
                inferred_type = self.infer_variable_declaration(stmt, env, generic_context)
                env[stmt.name] = inferred_type
        
        return env
    
    def infer_argument_types_from_function(self, function_type: FunctionType, arguments: List[Expression], env: Dict[str, Type]) -> List[Type]:
        """
        Infer argument types using bidirectional inference from function signature.
        
        This uses the function's parameter types to guide inference of argument expressions.
        Especially useful for lambdas and literals where type can be ambiguous.
        
        Args:
            function_type: The function type being called
            arguments: Argument expressions
            env: Type environment
            
        Returns:
            List of inferred argument types
        """
        inferred_types = []
        
        for i, arg in enumerate(arguments):
            # Get expected type from function signature
            expected_type = None
            if i < len(function_type.param_types):
                expected_type = function_type.param_types[i]
            
            # Use bidirectional inference with expected type
            arg_type = self.infer_with_expected_type(arg, expected_type, env)
            inferred_types.append(arg_type)
        
        return inferred_types
    
    def infer_from_return_context(self, expr: Expression, expected_return_type: Type, env: Dict[str, Type]) -> Type:
        """
        Infer expression type with expected return type context.
        
        This helps when the expression is in a return statement and we know
        what type the function should return.
        
        Args:
            expr: Expression being returned
            expected_return_type: Expected return type of the function
            env: Type environment
            
        Returns:
            Inferred type
        """
        return self.infer_with_expected_type(expr, expected_return_type, env)
    
    def infer_lambda_types(self, lambda_expr, expected_func_type: Optional[FunctionType], env: Dict[str, Type]) -> FunctionType:
        """
        Infer parameter and return types for a lambda expression.
        
        This is the core of lambda type inference, using bidirectional inference:
        - If expected_func_type is provided, use it to guide parameter type inference
        - If lambda has explicit types, use those
        - Infer return type from body with expected return type context
        
        Args:
            lambda_expr: LambdaExpression AST node
            expected_func_type: Expected function type from context (or None)
            env: Type environment
            
        Returns:
            Inferred FunctionType for the lambda
        """
        from ..parser.ast import Parameter
        
        # Extract lambda parameters
        params = lambda_expr.parameters if hasattr(lambda_expr, 'parameters') else []
        body = lambda_expr.body if hasattr(lambda_expr, 'body') else None
        explicit_return_type = lambda_expr.return_type if hasattr(lambda_expr, 'return_type') else None
        
        # Infer parameter types
        param_types = []
        lambda_env = env.copy()
        
        for i, param in enumerate(params):
            param_name = param.name if hasattr(param, 'name') else str(param)
            
            # Check if parameter has explicit type annotation
            if hasattr(param, 'type_annotation') and param.type_annotation:
                # Use explicit type
                param_type = get_type_by_name(param.type_annotation)
            elif expected_func_type and i < len(expected_func_type.param_types):
                # Use expected type from context (bidirectional inference!)
                param_type = expected_func_type.param_types[i]
            else:
                # No type information available - use ANY
                param_type = ANY_TYPE
            
            param_types.append(param_type)
            lambda_env[param_name] = param_type
        
        # Infer return type
        if explicit_return_type:
            # Use explicit return type annotation
            return_type = get_type_by_name(explicit_return_type)
        elif expected_func_type:
            # Use expected return type and infer body with it
            if body:
                if isinstance(body, list):
                    # Multi-statement body - infer from return statements
                    return_type = self._infer_lambda_body_type(body, expected_func_type.return_type, lambda_env)
                else:
                    # Single expression body
                    return_type = self.infer_with_expected_type(body, expected_func_type.return_type, lambda_env)
            else:
                return_type = expected_func_type.return_type
        else:
            # No expected return type - infer from body without context
            if body:
                if isinstance(body, list):
                    return_type = self._infer_lambda_body_type(body, None, lambda_env)
                else:
                    return_type = self.infer_expression_type(body, lambda_env)
            else:
                return_type = ANY_TYPE
        
        return FunctionType(param_types, return_type)
    
    def _infer_lambda_body_type(self, statements: List[Any], expected_return_type: Optional[Type], env: Dict[str, Type]) -> Type:
        """
        Infer return type from lambda body statements.
        
        Looks for return statements and infers their types.
        
        Args:
            statements: List of statements in lambda body
            expected_return_type: Expected return type (or None)
            env: Type environment
            
        Returns:
            Inferred return type
        """
        return_types = []
        
        for stmt in statements:
            # Check if this is a return statement
            if hasattr(stmt, 'node_type') and stmt.node_type == 'return_statement':
                if hasattr(stmt, 'value') and stmt.value:
                    if expected_return_type:
                        # Use expected type to guide inference
                        ret_type = self.infer_with_expected_type(stmt.value, expected_return_type, env)
                    else:
                        # Infer without context
                        ret_type = self.infer_expression_type(stmt.value, env)
                    return_types.append(ret_type)
                else:
                    return_types.append(NULL_TYPE)
        
        if not return_types:
            # No return statements - lambda returns NULL
            return NULL_TYPE if not expected_return_type else expected_return_type
        
        # Unify all return types
        result_type = return_types[0]
        for rt in return_types[1:]:
            unified = self.unify_types(result_type, rt)
            if unified:
                result_type = unified
            else:
                # Can't unify - use ANY
                return ANY_TYPE
        
        return result_type 