"""
Interpreter for NLPL.
Executes AST nodes and manages program state.
"""

import os
import struct
from typing import Any, Dict, List, Optional

from nlpl.errors import NLPLNameError, NLPLRuntimeError, NLPLTypeError, get_close_matches
from nlpl.parser.ast import (
    Program, VariableDeclaration, FunctionDefinition, Parameter,
    IfStatement, WhileLoop, ForLoop, MemoryAllocation, MemoryDeallocation,
    ClassDefinition, PropertyDeclaration, MethodDefinition,
    ObjectInstantiation,
    ConcurrentExecution, TryCatch, BinaryOperation, UnaryOperation,
    Literal, Identifier, FunctionCall, RepeatNTimesLoop,
    ReturnStatement, BreakStatement, ContinueStatement, Block, ConcurrentBlock, TryCatchBlock,
    # Module-related AST nodes
    ImportStatement, SelectiveImport, ModuleAccess, PrivateDeclaration
)
from nlpl.runtime import Runtime
# Don't import ModuleLoader here to avoid circular imports
# from nlpl.modules.module_loader import ModuleLoader
from nlpl.runtime.structures import StructDefinition, UnionDefinition, StructureInstance
from nlpl.typesystem.generics_system import TypeParameterInfo, TypeConstraint, GenericTypeInference



# Control flow exceptions for break/continue
class BreakException(Exception):
    """Raised when a break statement is encountered."""
    pass


class ContinueException(Exception):
    """Raised when a continue statement is encountered."""
    pass


class ReturnException(Exception):
    """Raised when a return statement is encountered."""
    def __init__(self, value=None):
        self.value = value


class Interpreter:
    """Interprets and executes the AST."""
    def __init__(self, runtime):
        self.runtime = runtime
        self.global_scope = {}
        self.current_scope = [self.global_scope]
        self.functions = {}
        self.classes = {}
        self.module_loader = None  # Will be initialized lazily
        
    def create_function_wrapper(self, function_def):
        """Create a callable wrapper for a user-defined function."""
        def wrapper(*args):
            # Create a new scope
            self.enter_scope()
            
            # Use 'create list of values' pattern to satisfy the expectation that each argument is a pair (name, value)
            # Actually, `self.functions` stores `FunctionDefinition` nodes.
            # We need to map `args` to `function_def.parameters`.
            
            # Check parameter count
            if len(args) != len(function_def.parameters):
                 # Handle varargs if needed, otherwise strict check
                 if not function_def.variadic:
                    raise TypeError(f"{function_def.name} expects {len(function_def.parameters)} arguments, got {len(args)}")

            try:
                # Bind parameters
                for param, value in zip(function_def.parameters, args):
                    self.set_variable(param.name, value)
                
                # Execute body
                for statement in function_def.body:
                    self.execute(statement)
            except ReturnException as ret:
                return ret.value
            finally:
                self.exit_scope()
            return None
        return wrapper

    def _get_module_loader(self):
        """Lazy initialize the module loader to avoid circular imports"""
        if self.module_loader is None:
            # Import here to avoid circular imports
            from ..modules.module_loader import ModuleLoader
            self.module_loader = ModuleLoader(self.runtime, [os.getcwd()])
        return self.module_loader
        
    def interpret(self, ast_or_source):
        """Interpret the AST and execute the program.
        
        Args:
            ast_or_source: Either an AST Program node or a source code string
            
        Returns:
            The result of program execution
        """
        # Support both AST and source string for backward compatibility
        if isinstance(ast_or_source, str):
            from ..parser.lexer import Lexer
            from ..parser.parser import Parser
            
            lexer = Lexer(ast_or_source)
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            ast = parser.parse()
        else:
            ast = ast_or_source
            
        if isinstance(ast, Program):
            result = None
            for statement in ast.statements:
                result = self.execute(statement)
            return result
        else:
            return self.execute(ast)
            
    def execute(self, node):
        """Execute a node in the AST."""
        # Get node type from either node_type attribute or class name
        if hasattr(node, 'node_type'):
            node_type = node.node_type
        else:
            node_type = node.__class__.__name__
        
        # Dispatch to the appropriate method based on node type
        # Convert CamelCase to snake_case for method names
        import re
        method_name = f"execute_{re.sub(r'(?<!^)(?=[A-Z])', '_', node_type).lower()}"
        
        if hasattr(self, method_name):
            return getattr(self, method_name)(node)
        else:
            raise NotImplementedError(f"Execution of {node_type} nodes is not implemented (looked for method: {method_name})")
            
    def get_variable(self, name):
        """Get a variable from the current scope with enhanced error reporting."""
        # Search from innermost to outermost scope
        for scope in reversed(self.current_scope):
            if name in scope:
                return scope[name]
        
        # Check runtime constants (PI, E, TAU, etc.)
        if hasattr(self.runtime, 'constants') and name in self.runtime.constants:
            return self.runtime.constants[name]

        # Check self.functions (user defined functions)
        if name in self.functions:
            raise NameError("Function found but not returned by get_variable - caught in execute_identifier")
        
        # Variable not found - provide helpful error with suggestions
        available_names = []
        for scope in self.current_scope:
            available_names.extend(scope.keys())
        
        # Also include runtime functions and constants as potential suggestions
        if hasattr(self.runtime, 'functions'):
            available_names.extend(self.runtime.functions.keys())
        if hasattr(self.runtime, 'constants'):
            available_names.extend(self.runtime.constants.keys())
        
        raise NLPLNameError(
            name,
            available_names=available_names
        )
        
    def set_variable(self, name, value):
        """Set a variable in the current scope."""
        # Set in the innermost scope
        self.current_scope[-1][name] = value
        return value
        
    def enter_scope(self):
        """Enter a new scope."""
        self.current_scope.append({})
        
    def exit_scope(self):
        """Exit the current scope."""
        if len(self.current_scope) > 1:
            self.current_scope.pop()
            
    # Module-related execution methods
    
    def execute_import_statement(self, node):
        """Execute an import statement."""
        try:
            # Get the current module path for relative imports
            current_path = getattr(self.runtime, 'module_path', None)
            
            # Load the module
            module = self._get_module_loader().load_module(node.module_name, current_path)
            
            # Use the alias if provided, otherwise use the module name
            module_name = node.alias if node.alias else node.module_name
            
            # If the module name contains path separators, use the last part
            if '/' in module_name:
                module_name = module_name.split('/')[-1]
            if '\\' in module_name:
                module_name = module_name.split('\\')[-1]
                
            # If the module name has an extension, remove it
            if '.' in module_name:
                module_name = module_name.split('.')[0]
                
            # Add the module to the current scope
            self.set_variable(module_name, module)
            
            return None
        except (ImportError, CircularImportError) as e:
            raise NLPLRuntimeError(
                message=f"Import error: {str(e)}",
                line=getattr(node, 'line', None),
                column=getattr(node, 'column', None)
            )
            
    def execute_selective_import(self, node):
        """Execute a selective import statement."""
        try:
            # Get the current module path for relative imports
            current_path = getattr(self.runtime, 'module_path', None)
            
            # Load the module
            module = self._get_module_loader().load_module(node.module_name, current_path)
            
            # Import each specified name
            for name in node.imported_names:
                # Check if the name exists in the module
                if hasattr(module, name):
                    # Add the name to the current scope
                    self.set_variable(name, getattr(module, name))
                else:
                    # Get available attributes for suggestions
                    available = [attr for attr in dir(module) if not attr.startswith('_')]
                    suggestions = get_close_matches(name, available, n=3, cutoff=0.6)
                    raise NLPLNameError(
                        message=f"Module '{node.module_name}' has no attribute '{name}'",
                        name=name,
                        suggestions=suggestions,
                        line=getattr(node, 'line', None),
                        column=getattr(node, 'column', None)
                    )
                    
            return None
        except (ImportError, CircularImportError) as e:
            raise NLPLRuntimeError(
                message=f"Import error: {str(e)}",
                line=getattr(node, 'line', None),
                column=getattr(node, 'column', None)
            )
            
    def execute_module_access(self, node):
        """Execute a module access expression."""
        # Get the module
        try:
            module = self.get_variable(node.module_name)
        except NLPLNameError:
            # Re-raise the name error with module context
            raise
            
        # Get the member from the module
        if hasattr(module, node.member_name):
            return getattr(module, node.member_name)
        else:
            # Get available attributes for suggestions
            available = [attr for attr in dir(module) if not attr.startswith('_')]
            suggestions = get_close_matches(node.member_name, available, n=3, cutoff=0.6)
            raise NLPLNameError(
                message=f"Module '{node.module_name}' has no attribute '{node.member_name}'",
                name=node.member_name,
                suggestions=suggestions,
                line=getattr(node, 'line', None),
                column=getattr(node, 'column', None)
            )
            
    def execute_private_declaration(self, node):
        """Execute a private declaration."""
        # Execute the declaration normally
        # The privacy is enforced by the module system
        return self.execute(node.declaration)
            
    # Statement execution methods
    
    def execute_variable_declaration(self, node):
        """Execute a variable declaration."""
        value = None
        if node.value:
            value = self.execute(node.value)
        return self.set_variable(node.name, value)
    
    def execute_index_assignment(self, node):
        """Execute an index assignment: set array[index] to value."""
        # Execute the target to get the IndexExpression
        target = node.target
        
        # Get the container (array, dict, etc.)
        container = self.execute(target.array_expr)
        
        # Get the index
        index = self.execute(target.index_expr)
        
        # Get the value to assign
        value = self.execute(node.value)
        
        # Perform the assignment
        try:
            container[index] = value
            return value
        except (IndexError, KeyError, TypeError) as e:
            if isinstance(e, IndexError):
                raise NLPLRuntimeError(
                    message=f"Index {index} is out of range for assignment",
                    line=getattr(node, 'line', None),
                    column=getattr(node, 'column', None)
                )
            elif isinstance(e, TypeError):
                raise NLPLTypeError(
                    message=f"Cannot assign to index on type {type(container).__name__}",
                    expected="list or dict",
                    got=type(container).__name__,
                    line=getattr(node, 'line', None),
                    column=getattr(node, 'column', None)
                )
            else:
                raise NLPLRuntimeError(
                    message=f"Failed to assign to index {index}: {e}",
                    line=getattr(node, 'line', None),
                    column=getattr(node, 'column', None)
                )
        
    def execute_function_definition(self, node):
        """Execute a function definition."""
        self.functions[node.name] = node
        return node.name
    
    def execute_async_function_definition(self, node):
        """Execute an async function definition."""
        # Store async function similar to regular function
        # Mark it as async so we know to handle it differently when called
        self.functions[node.name] = node
        return node.name
    
    def execute_await_expression(self, node):
        """Execute an await expression."""
        import asyncio
        
        # Execute the expression (should be an async function call or coroutine)
        result = self.execute(node.expression)
        
        # If result is a coroutine, run it
        if asyncio.iscoroutine(result):
            # Get or create event loop
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                # No running loop, create one
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(result)
                loop.close()
            else:
                # Already in async context - this shouldn't happen in interpreter
                # but handle it gracefully
                result = asyncio.run(result)
        
        return result
        
    def execute_if_statement(self, node):
        """Execute an if statement."""
        condition = self.execute(node.condition)
        
        # Don't create new scope - if statements should access outer scope variables
        if condition:
            result = None
            for statement in node.then_block:
                result = self.execute(statement)
            return result
        elif node.else_block:
            result = None
            for statement in node.else_block:
                result = self.execute(statement)
            return result
            
    def execute_while_loop(self, node):
        """Execute a while loop."""
        result = None
        
        # Don't create new scope - while loops should access outer scope variables
        try:
            while self.execute(node.condition):
                try:
                    for statement in node.body:
                        result = self.execute(statement)
                except ContinueException:
                    # Continue to next iteration
                    continue
        except BreakException:
            # Break out of loop
            pass
            
        return result
        
    def execute_for_loop(self, node):
        """Execute a for loop."""
        result = None
        iterable = self.execute(node.iterable)
        
        # Don't create new scope - for loops should access outer scope variables like while loops
        try:
            for item in iterable:
                # Set the iterator variable in the current scope
                self.set_variable(node.iterator, item)
                
                try:
                    for statement in node.body:
                        result = self.execute(statement)
                except ContinueException:
                    # Continue to next iteration
                    continue
        except BreakException:
            # Break out of loop
            pass
            
        return result
        
    def execute_memory_allocation(self, node):
        """Execute memory allocation."""
        initial_value = None
        if node.initial_value:
            initial_value = self.execute(node.initial_value)
            
        # Simulate memory allocation using the runtime
        pointer = self.runtime.allocate_memory(node.var_type, initial_value)
        self.set_variable(node.identifier, pointer)
        
        return pointer
        
    def execute_memory_deallocation(self, node):
        """Execute memory deallocation."""
        pointer = self.get_variable(node.identifier)
        self.runtime.free_memory(pointer)
        return None
        
    def execute_class_definition(self, node):
        """Execute a class definition."""
        # Store the AST node. It contains generic_parameters if defined.
        self.classes[node.name] = node
        return node.name
    
    def execute_struct_definition(self, node):
        """Execute a struct definition.
        
        Registers the struct as a type that can be instantiated.
        Structs are like classes but with explicit memory layout control.
        """
        # Extract fields and their types
        fields = []
        for field in node.fields:
            # field is PropertyDeclaration
            type_name = field.type_annotation
            if not type_name:
                type_name = "Pointer" # Default to pointer size if unknown
            fields.append((field.name, type_name))
            
        # Create definition and store in classes map
        definition = StructDefinition(node.name, fields)
        self.classes[node.name] = definition
        return node.name
    
    def execute_sizeof_expression(self, node):
        """Execute sizeof expression."""
        # Clean attribute access: try 'target' first, then 'type_name'
        target = getattr(node, 'target', getattr(node, 'type_name', None))
        
        # Resolve Identifier to string name if possible
        target_name = None
        if hasattr(target, 'name'):
            target_name = target.name
        elif isinstance(target, str):
            target_name = target
            
        # 1. Look up Type Name (e.g., "Point", "Integer")
        if target_name:
            # Check user-defined types
            if target_name in self.classes:
                defn = self.classes[target_name]
                if hasattr(defn, 'size'):
                    return defn.size
            
            # Check primitive types
            from ..runtime.structures import PrimitiveType
            if target_name in ("Integer", "Int"): return 8
            if target_name in ("Float", "Double"): return 8
            if target_name in ("Boolean", "Bool"): return 1
            if target_name == "Byte": return 1
            if target_name == "Char": return 1
            
        # 2. Evaluate Expression (e.g., variable instance)
        try:
            val = self.execute(target)
            from ..runtime.structures import StructureInstance
            if isinstance(val, StructureInstance):
                return val.definition.size
        except:
            pass
            
        return 8  # Default pointer size.
    
    def execute_union_definition(self, node):
        """Execute a union definition.
        
        Registers the union as a type. All fields share the same memory location.
        """
        # Extract fields and their types
        fields = []
        for field in node.fields:
            type_name = field.type_annotation
            if not type_name:
                type_name = "Pointer"
            fields.append((field.name, type_name))
            
        # Create definition and store in classes map
        definition = UnionDefinition(node.name, fields)
        self.classes[node.name] = definition
        return node.name
    
    def execute_enum_definition(self, node):
        """Execute an enum definition.
        
        Creates an enum type with named constant values.
        The enum is accessible as a namespace with member values.
        
        Example:
            enum Color
                Red = 0
                Green = 1
                Blue = 2
            end
            
            # Access: Color.Red, Color.Green, Color.Blue
        """
        # Create an enum object that acts as a namespace
        enum_obj = {}
        
        # Add each member to the enum object
        for member in node.members:
            # Evaluate the member value
            if member.value:
                value = self.execute(member.value)
            else:
                value = 0  # Default value if not specified
            
            enum_obj[member.name] = value
        
        # Store the enum in the current scope
        self.set_variable(node.name, enum_obj)
        
        return node.name
        
    def execute_concurrent_execution(self, node):
        """Execute concurrent tasks."""
        return self.runtime.run_concurrently([
            lambda task=task: self.execute(task) for task in node.tasks
        ])
        
    def execute_try_catch(self, node):
        """Execute a try-catch block."""
        try:
            # Execute all statements in try block
            result = None
            for statement in node.try_block:
                result = self.execute(statement)
            return result
        except Exception as e:
            # Only execute catch block if an exception occurred
            self.enter_scope()
            
            # Store exception in the exception variable if specified
            if node.exception_var:
                self.set_variable(node.exception_var, str(e))
            else:
                self.set_variable("error", str(e))
            
            result = None
            for statement in node.catch_block:
                result = self.execute(statement)
                
            self.exit_scope()
            return result
            
    def execute_repeat_n_times_loop(self, node):
        """Execute a repeat-n-times loop."""
        result = None
        count = int(self.execute(node.count))
        
        for _ in range(count):
            self.enter_scope()
            
            for statement in node.body:
                result = self.execute(statement)
                
            self.exit_scope()
            
        return result
            
    # Expression execution methods
    
    def execute_binary_operation(self, node):
        """Execute a binary operation."""
        left = self.execute(node.left)
        right = self.execute(node.right)
        
        # Perform the operation based on the operator
        from ..parser.lexer import TokenType
        
        # Get the operator type from the token
        op_type = node.operator.type if hasattr(node.operator, 'type') else node.operator
        
        if op_type == TokenType.PLUS:
            return left + right
        elif op_type == TokenType.MINUS:
            return left - right
        elif op_type == TokenType.TIMES:
            return left * right
        elif op_type == TokenType.DIVIDED_BY:
            return left / right
        elif op_type == TokenType.MODULO:
            return left % right
        elif op_type == TokenType.POWER:
            return left ** right
        elif op_type == TokenType.FLOOR_DIVIDE:
            return left // right
        elif op_type == TokenType.CONCATENATE:
            # String concatenation - convert both operands to strings
            return str(left) + str(right)
        elif op_type == TokenType.EQUAL_TO:
            return left == right
        elif op_type == TokenType.NOT_EQUAL_TO:
            return left != right
        elif op_type == TokenType.LESS_THAN:
            return left < right
        elif op_type == TokenType.GREATER_THAN:
            return left > right
        elif op_type == TokenType.LESS_THAN_OR_EQUAL_TO:
            return left <= right
        elif op_type == TokenType.GREATER_THAN_OR_EQUAL_TO:
            return left >= right
        elif op_type == TokenType.AND:
            return left and right
        elif op_type == TokenType.OR:
            return left or right
        elif op_type == TokenType.BITWISE_AND:
            return left & right
        elif op_type == TokenType.BITWISE_OR:
            return left | right
        elif op_type == TokenType.BITWISE_XOR:
            return left ^ right
        elif op_type == TokenType.LEFT_SHIFT:
            return left << right
        elif op_type == TokenType.RIGHT_SHIFT:
            return left >> right
        elif op_type == TokenType.IN:
            return left in right
        else:
            raise NotImplementedError(f"Binary operator {node.operator} is not implemented")
            
    def execute_unary_operation(self, node):
        """Execute a unary operation."""
        operand = self.execute(node.operand)
        
        # Perform the operation based on the operator
        from ..parser.lexer import TokenType
        
        op_type = node.operator.type if hasattr(node.operator, 'type') else node.operator
        
        if op_type == TokenType.PLUS:
            return +operand
        elif op_type == TokenType.MINUS:
            return -operand
        elif op_type == TokenType.NOT:
            return not operand
        elif op_type == TokenType.BITWISE_NOT:
            return ~operand
        else:
            raise NotImplementedError(f"Unary operator {node.operator} is not implemented")
            
    def execute_literal(self, node):
        """Execute a literal."""
        return node.value
    
    def execute_fstring_expression(self, node):
        """Execute f-string with interpolation and format specifiers."""
        result_parts = []
        for part_tuple in node.parts:
            # Handle both old (2-tuple) and new (3-tuple) formats
            if len(part_tuple) == 2:
                is_literal, content = part_tuple
                format_spec = None
            elif len(part_tuple) == 3:
                is_literal, content, format_spec = part_tuple
            else:
                continue
            
            if is_literal:
                # Literal string part
                result_parts.append(str(content))
            else:
                # Expression - evaluate it
                value = self.execute(content)
                
                # Apply format specifier if present
                if format_spec:
                    formatted = self._apply_format_spec(value, format_spec)
                    result_parts.append(formatted)
                else:
                    # Convert to string
                    result_parts.append(str(value))
        return ''.join(result_parts)
    
    def _apply_format_spec(self, value, format_spec):
        """Apply Python-style format specifier to a value.
        
        Supports:
        - .Nf for floats (precision)
        - 0Nd for integers (zero-padding)
        - >N, <N, ^N for alignment
        """
        try:
            # Use Python's format specification mini-language
            return format(value, format_spec)
        except (ValueError, TypeError) as e:
            # Fallback to string conversion if format fails
            return str(value)
    
    def execute_list_expression(self, node):
        """Execute a list expression (array literal)."""
        # Evaluate all elements in the list
        return [self.execute(element) for element in node.elements]
    
    def execute_dict_expression(self, node):
        """Execute a dictionary expression (dict literal)."""
        # Evaluate all key-value pairs
        result = {}
        for key_expr, value_expr in node.entries:
            key = self.execute(key_expr)
            value = self.execute(value_expr)
            result[key] = value
        return result
    
    def execute_index_expression(self, node):
        """Execute an index expression (array access)."""
        # Evaluate the array and index
        array = self.execute(node.array_expr)
        index = self.execute(node.index_expr)
        
        # Return the element at the index
        try:
            return array[index]
        except IndexError as e:
            raise NLPLRuntimeError(
                message=f"Index {index} is out of range for array of length {len(array)}",
                line=getattr(node, 'line', None),
                column=getattr(node, 'column', None)
            )
        except KeyError as e:
            # For dictionaries, suggest similar keys
            if isinstance(array, dict):
                available_keys = [str(k) for k in array.keys()]
                raise NLPLNameError(
                    name=str(index),
                    available_names=available_keys,
                    line=getattr(node, 'line', None),
                    column=getattr(node, 'column', None),
                    source_line=getattr(node, 'source_line', None)
                )
            raise NLPLRuntimeError(
                message=f"Key '{index}' not found",
                line=getattr(node, 'line', None),
                column=getattr(node, 'column', None)
            )
        except TypeError as e:
            raise NLPLTypeError(
                message=f"Cannot use index on type {type(array).__name__}",
                expected="list, dict, or string",
                got=type(array).__name__,
                line=getattr(node, 'line', None),
                column=getattr(node, 'column', None)
            )
        
    def execute_identifier(self, node):
        """Execute an identifier (variable reference)."""
        try:
            return self.get_variable(node.name)
        except NameError:
            # Check if it's a function (first-class support)
            if node.name in self.functions:
                return self.create_function_wrapper(self.functions[node.name])
            
                
            # Check if it's a built-in function
            if node.name in self.runtime.functions:
                return self.runtime.functions[node.name]
                
            raise NameError(f"Variable or function '{node.name}' is not defined")
        
    def execute_function_call(self, node):
        """Execute a function call."""
        function_name = node.name
        args = [self.execute(arg) for arg in node.arguments]
        
        # Check for built-in functions in the runtime
        if function_name in self.runtime.functions:
            return self.runtime.functions[function_name](*args)
        
        # Check for user-defined functions
        if function_name in self.functions:
            function_def = self.functions[function_name]
            
            # Create a new scope for the function
            self.enter_scope()
            
            # Bind arguments to parameters
            for i, param in enumerate(function_def.parameters):
                if i < len(args):
                    self.set_variable(param.name, args[i])
                else:
                    # Use default value if provided, otherwise None
                    default_value = None
                    if hasattr(param, 'default_value') and param.default_value:
                        default_value = self.execute(param.default_value)
                    self.set_variable(param.name, default_value)
            
            # Execute the function body
            result = None
            for statement in function_def.body:
                result = self.execute(statement)
                if isinstance(statement, ReturnStatement):
                    break
            
            # Clean up the function scope
            self.exit_scope()
            
            return result
        
        raise NameError(f"Function '{function_name}' is not defined")
        
    def execute_return_statement(self, node):
        """Execute a return statement."""
        value = None
        if node.value:
            value = self.execute(node.value)
        raise ReturnException(value)
    
    def execute_break_statement(self, node):
        """Execute a break statement."""
        raise BreakException()
    
    def execute_continue_statement(self, node):
        """Execute a continue statement."""
        raise ContinueException()
        
    def execute_block(self, node):
        """Execute a block of statements."""
        result = None
        
        self.enter_scope()
        try:
            for statement in node.statements:
                result = self.execute(statement)
                if isinstance(statement, ReturnStatement):
                    break
        finally:
            self.exit_scope()
            
        return result
        
    def execute_concurrent_block(self, node):
        """Execute a block of statements concurrently."""
        futures = []
        
        for statement in node.statements:
            # Create a function that executes the statement in its own scope
            def execute_concurrent(stmt=statement):
                self.enter_scope()
                try:
                    return self.execute(stmt)
                finally:
                    self.exit_scope()
            
            # Submit the function to the runtime's executor
            future = self.runtime.run_concurrent(execute_concurrent)
            futures.append(future)
        
        # Wait for all futures to complete and return their results
        return self.runtime.wait_for_futures(futures)
        
    def execute_try_catch_block(self, node):
        """Execute a try-catch block."""
        try:
            return self.execute(node.try_block)
        except Exception as e:
            # Enter the catch block with the exception bound to the variable
            self.enter_scope()
            try:
                if node.exception_var:
                    self.current_scope[-1][node.exception_var] = str(e)
                return self.execute(node.catch_block)
            finally:
                self.exit_scope() 
    
    # Low-level pointer operation execution methods
    
    def execute_address_of_expression(self, node):
        """
        Execute address-of operation: get memory address of a variable.
        Returns a MemoryAddress object.
        """
        # Get the target (must be an identifier or indexable expression)
        if hasattr(node.target, 'name'):
            # Simple variable: address of x
            var_name = node.target.name
            value = self.get_variable(var_name)
            return self.runtime.memory_manager.get_address(var_name, value)
        else:
            # Expression - evaluate it first
            value = self.execute(node.target)
            # Generate a temporary name for the address
            temp_name = f"_temp_{id(value)}"
            return self.runtime.memory_manager.get_address(temp_name, value)
    
    def execute_dereference_expression(self, node):
        """
        Execute dereference operation: get value at pointer address.
        """
        # Evaluate the pointer expression
        pointer = self.execute(node.pointer)
        
        # Dereference the pointer
        from ..runtime.memory import MemoryAddress
        if not isinstance(pointer, MemoryAddress):
            raise NLPLTypeError(
                message=f"Cannot dereference non-pointer type",
                expected_type="Pointer",
                got_type=type(pointer).__name__,
                line=getattr(node, 'line', None),
                column=getattr(node, 'column', None)
            )
        
        return self.runtime.memory_manager.dereference(pointer)
    
    def execute_sizeof_expression(self, node):
        """
        Execute sizeof operation: get size of type or variable in bytes.
        """
        # Check if target is a type name (identifier) or a value
        if hasattr(node.target, 'name'):
            # Type name or variable name
            target_name = node.target.name
            # Check if it's a known type
            type_names = ["Integer", "Float", "String", "Boolean", "Pointer", "List", "Dictionary"]
            if target_name in type_names:
                return self.runtime.memory_manager.sizeof(target_name)
            # Check if it's a struct/union/class
            elif target_name in self.classes:
                # Calculate size based on fields (simplified: 8 bytes per field)
                struct_def = self.classes[target_name]
                if hasattr(struct_def, 'fields'):
                    return len(struct_def.fields) * 8
                else:
                    # Default size for classes without explicit fields
                    return 8
            else:
                # It's a variable - get its value and find size
                value = self.get_variable(target_name)
                return self.runtime.memory_manager.sizeof(value)
        else:
            # Expression - evaluate and get size
            value = self.execute(node.target)
            return self.runtime.memory_manager.sizeof(value)    
    def execute_offsetof_expression(self, node):
        """
        Execute offsetof operation: get byte offset of field in struct/union.
        
        Returns the memory offset of a field within a struct or union type.
        """
        struct_name = node.struct_type
        field_name = node.field_name
        
        # Get struct definition
        if struct_name not in self.classes:
            raise RuntimeError(f"Unknown struct/union type: {struct_name}")
        
        struct_def = self.classes[struct_name]
        
        # Calculate offset (simplified - assume 8 bytes per field)
        offset = 0
        for field in struct_def.fields:
            if field.name == field_name:
                return offset
            # Increment offset (simplified calculation)
            offset += 8  # Assume 8 bytes per field for now
        
        raise RuntimeError(f"Field '{field_name}' not found in {struct_name}")
    
    def execute_type_cast(self, node):
        """
        Execute type cast: (expression as TargetType).
        
        Converts an expression to the target type.
        """
        # Evaluate the expression
        value = self.execute(node.expression)
        target_type = node.target_type
        
        # Handle pointer casts specially
        if "Pointer" in str(target_type):
            # For pointer casts, create a MemoryAddress if value is an integer
            from ..runtime.memory import MemoryAddress
            if isinstance(value, int):
                # Cast integer to pointer (memory-mapped I/O, hardware registers)
                return MemoryAddress(value)
            elif isinstance(value, MemoryAddress):
                # Already a pointer, return as-is
                return value
            else:
                # For other types, treat as reinterpret_cast
                return value
        
        # Type conversions
        if "Integer" in str(target_type):
            return int(value)
        elif "Float" in str(target_type):
            return float(value)
        elif "String" in str(target_type):
            return str(value)
        elif "Boolean" in str(target_type):
            return bool(value)
        else:
            # For struct/class types, return as-is (structural typing)
            return value
    
    def execute_object_instantiation(self, node):
        """
        Execute object instantiation: new ClassName or new StructName.
        
        Creates a new instance of a class or struct with initialized fields.
        """
        class_name = node.class_name
        
        # Handle built-in types
        if class_name == "List":
            return []
        elif class_name == "Dictionary":
            return {}
        elif "Array of" in class_name:
            # Parse array size and element type: "Array of 10 Point"
            parts = class_name.split()
            if len(parts) >= 3:
                try:
                    size = int(parts[2])
                    # Check if there's an element type (e.g., "Array of 10 Point")
                    if len(parts) >= 4:
                        element_type = parts[3]
                        # If element type is a struct/class, initialize with instances
                        if element_type in self.classes:
                            return [self.execute(ObjectInstantiation(element_type, [], None)) for _ in range(size)]
                    # Otherwise, return list with None elements
                    return [None] * size
                except ValueError:
                    pass
            return []
        
        # Look up the class definition
        class_def = self.classes.get(class_name)
        if not class_def:
            from ..exceptions import NLPLNameError
            raise NLPLNameError(f"Undefined class, struct, or union: '{class_name}'", 
                               line_number=node.line_number,
                               available_names=list(self.classes.keys()))
            
        # Handle Generics: Check if this is a generic class instantiation
        # Node has type_arguments: Box<Integer> -> type_arguments=['Integer']
        type_args_map = {}
        if hasattr(node, 'type_arguments') and node.type_arguments:
            from ..exceptions import NLPLTypeError
            if not hasattr(class_def, 'generic_parameters') or not class_def.generic_parameters:
                raise NLPLTypeError(f"Class '{class_name}' is not generic but was given type arguments",
                                    line=getattr(node, 'line', None),
                                    column=getattr(node, 'column', None))
            
            if len(node.type_arguments) != len(class_def.generic_parameters):
                raise NLPLTypeError(f"Class '{class_name}' expects {len(class_def.generic_parameters)} type arguments, got {len(node.type_arguments)}",
                                    line=getattr(node, 'line', None),
                                    column=getattr(node, 'column', None))
            
            # Map parameters T to arguments Integer
            # class_def.generic_parameters is a list of TypeParameter nodes
            # node.type_arguments is a list of type names or Type nodes (depending on parser)
            
            for param, arg in zip(class_def.generic_parameters, node.type_arguments):
                # Param is a TypeParameter node, use param.name (e.g., "T")
                param_name = param.name
                
                # Arg could be different depending on parser version. 
                # Assuming simple strings for now based on current test.
                # If complex type, it might be a node.
                arg_name = arg
                type_args_map[param_name] = arg_name

        # Handle Structs and Unions
        from ..runtime.structures import StructDefinition, UnionDefinition, StructureInstance
        if isinstance(class_def, (StructDefinition, UnionDefinition)):
            instance = StructureInstance(class_def)
            return instance

        # Regular Class Instantiation
        # Create a new object instance
        instance = self.runtime.create_object(class_name, type_arguments=type_args_map)
        
        # Initialize class properties
        if hasattr(class_def, 'properties'):
            for prop in class_def.properties:
                instance.set_property(prop.name, None)
        
        # Store methods
        if hasattr(class_def, 'methods'):
            for method in class_def.methods:
                instance.add_method(method.name, method)
                
        return instance
    
    def execute_member_access(self, node):
        """
        Execute member access: object.field or object.method().
        
        Accesses a field or calls a method on an object.
        """
        # Evaluate the object expression
        obj = self.execute(node.object_expr)
        member_name = node.member_name
        
        # Handle Struct/Union member access
        from ..runtime.structures import StructureInstance
        if isinstance(obj, StructureInstance):
            return obj.get_field(member_name)
            
        # Handle dict-based objects (our classes)
        if isinstance(obj, dict):
            if node.is_method_call:
                # Method call
                method_key = f"__method_{member_name}__"
                if method_key in obj:
                    # Execute the method with the instance as context
                    method_def = obj[method_key]
                    
                    # Enter new scope for method execution
                    self.enter_scope()
                    
                    try:
                        # Bind instance to 'self'
                        self.set_variable("self", obj)

                        # Bind instance fields to scope (implicit self)
                        # Fields are accessible directly as variables within the method
                        for key, value in obj.items():
                            if not key.startswith("__"):  # Skip internal keys
                                self.set_variable(key, value)
                        
                        # Bind method parameters
                        if hasattr(method_def, 'parameters') and method_def.parameters:
                            # Evaluate arguments
                            args = [self.execute(arg) for arg in node.arguments] if hasattr(node, 'arguments') and node.arguments else []
                            
                            # Bind parameters to arguments
                            for i, param in enumerate(method_def.parameters):
                                if i < len(args):
                                    self.set_variable(param.name, args[i])
                                elif hasattr(param, 'default_value') and param.default_value:
                                    self.set_variable(param.name, self.execute(param.default_value))
                                else:
                                    self.set_variable(param.name, None)
                        
                        # Execute method body
                        result = None
                        if hasattr(method_def, 'body'):
                            from ..parser.ast import ReturnStatement
                            for statement in method_def.body:
                                result = self.execute(statement)
                                # Check if this was a return statement
                                if isinstance(statement, ReturnStatement):
                                    break
                        
                        # Update instance fields from scope (fields may have been modified)
                        for key in obj.keys():
                            if not key.startswith("__"):
                                try:
                                    obj[key] = self.get_variable(key)
                                except:
                                    pass  # Field not modified
                        
                        return result
                    finally:
                        self.exit_scope()
                else:
                    raise RuntimeError(f"Unknown method: {member_name}")
            else:
                # Property/field access
                if member_name in obj:
                    return obj[member_name]
                else:
                    raise RuntimeError(f"Unknown field: {member_name}")
        
        # Handle regular Python objects
        elif hasattr(obj, member_name):
            attr = getattr(obj, member_name)
            if node.is_method_call:
                # Evaluate arguments
                args = [self.execute(arg) for arg in node.arguments]
                return attr(*args)
            else:
                return attr
        else:
            raise RuntimeError(f"Object has no member: {member_name}")
    
    def execute_member_assignment(self, node):
        """
        Execute member assignment: set object.field to value.
        
        Assigns a value to a struct/class field.
        """
        # Get the member access target
        member_access = node.target
        
        # Evaluate the object
        target_obj = self.execute(member_access.object_expr)
        member_name = member_access.member_name
        
        # Evaluate the value to assign
        value = self.execute(node.value)
        
        # Handle Struct/Union member assignment
        from ..runtime.structures import StructureInstance
        if isinstance(target_obj, StructureInstance):
             target_obj.set_field(member_name, value)
             return value

        # Handle regular object assignment
        if isinstance(target_obj, dict):
            target_obj[member_name] = value
            return value
            
        if hasattr(target_obj, 'set_property'):
            target_obj.set_property(member_name, value)
            return value
            
        if hasattr(target_obj, member_name):
            setattr(target_obj, member_name, value)
            return value
            
        raise RuntimeError(f"Cannot assign to member '{member_name}' on object of type {type(target_obj)}")
    
    def execute_generic_type_instantiation(self, node):
        """
        Execute generic type instantiation.
        Syntax: create list of Integer, create dict of String to Integer
        
        Creates typed collections using the GenericTypeRegistry.
        """
        generic_name = node.generic_name.lower()
        type_args = node.type_args
        
        # For now, create basic Python collections with type hints
        # In the future, this will integrate with the GenericTypeRegistry for type checking
        
        if generic_name == "list":
            # Create a list with optional initial value
            if node.initial_value:
                initial = self.execute(node.initial_value)
                if isinstance(initial, list):
                    return initial.copy()
                else:
                    return [initial]
            else:
                return []
        
        elif generic_name in ("dict", "dictionary"):
            # Create a dictionary
            if node.initial_value:
                initial = self.execute(node.initial_value)
                if isinstance(initial, dict):
                    return initial.copy()
                else:
                    raise TypeError("Dictionary initial value must be a dictionary")
            else:
                return {}
        
        else:
            raise NotImplementedError(f"Generic type '{generic_name}' not yet implemented")

    def execute_TryExpression(self, node):
        """Execute ? operator for error propagation."""
        from ..stdlib.option_result import Result
        
        result = self.execute(node.expression)
        
        if not isinstance(result, Result):
            raise RuntimeError(f'? operator requires Result type, got {type(result).__name__}')
        
        if result.is_ok():
            return result.unwrap()
        else:
            self.return_value = result
            return None

