"""
Interpreter for NLPL.
Executes AST nodes and manages program state.
"""

import os
import re
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
    ImportStatement, SelectiveImport, ModuleAccess, PrivateDeclaration,
    # FFI-related AST nodes
    ExternFunctionDeclaration, ExternVariableDeclaration, ExternTypeDeclaration,
    # Inline assembly AST node
    InlineAssembly,
    # Struct/Union AST nodes
    StructDefinition as ASTStructDefinition, 
    UnionDefinition as ASTUnionDefinition,
    StructField,
    # Pattern matching AST nodes
    MatchExpression, MatchCase,
    LiteralPattern, IdentifierPattern, WildcardPattern,
    OptionPattern, ResultPattern, VariantPattern,
    # Smart pointer / ownership AST nodes
    RcCreation, DowngradeExpression, UpgradeExpression,
    MoveExpression, BorrowExpression, DropBorrowStatement,
    # Allocator hints and parallel execution
    AllocatorHint, ParallelForLoop,
    # Lifetime-annotated borrow expressions
    BorrowExpressionWithLifetime,
)
import concurrent.futures as _cf
from nlpl.runtime import Runtime
# Import CircularImportError for module loading
from nlpl.modules.module_loader import CircularImportError
# Don't import ModuleLoader here to avoid circular imports
# from nlpl.modules.module_loader import ModuleLoader
from nlpl.runtime.structures import (
    StructDefinition as RuntimeStructDefinition,
    UnionDefinition as RuntimeUnionDefinition,
    StructureInstance
)
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


class NLPLUserException(Exception):
    """Exception raised by NLPL 'raise' statements."""
    def __init__(self, exception_type, message, line=None, column=None):
        self.exception_type = exception_type
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"{exception_type}: {message}" if message else exception_type)


def _camel_to_snake(name: str) -> str:
    """Convert CamelCase to snake_case for dispatch table building."""
    return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()


class Interpreter:
    """Interprets and executes the AST."""

    # Class-level dispatch cache: maps node_type string -> bound method.
    # Built lazily on first Interpreter instantiation and shared across instances
    # (methods are looked up on self at call time via getattr, then cached per-instance).
    # This eliminates the per-call regex + hasattr + getattr chain in execute().
    _DISPATCH_TABLE: Dict[str, str] = {}  # node_type -> method_name (str)

    def __init__(self, runtime, enable_type_checking=False, source=None):
        self.runtime = runtime
        self.source = source  # Store full source for error context
        self.global_scope = {}
        self.current_scope = [self.global_scope]
        self.functions = {}
        self.classes = {}
        self.macros = {}  # Registry for macro definitions
        self.last_exception = None  # To support re-raising
        self.module_loader = None  # Will be initialized lazily

        # Ownership / borrow tracking
        # Structure: { var_name: {"immutable_count": int, "is_mutable": bool} }
        self._borrow_tracker: dict = {}
        
        # Type system components (lazy initialization)
        self.enable_type_checking = enable_type_checking
        self.type_checker = None
        self.type_inference = None
        if enable_type_checking:
            from ..typesystem.typechecker import TypeChecker
            from ..typesystem.type_inference import TypeInferenceEngine
            self.type_checker = TypeChecker()
            self.type_inference = TypeInferenceEngine()
        
        # Debugger integration (optional)
        self.debugger = None
        self.current_file = None
        self.current_line = None

        # Per-instance dispatch cache: node_type -> bound method (avoids repeated getattr).
        # Built lazily on first call to execute() so that subclasses that override
        # execute_* methods are also picked up correctly.
        self._dispatch_cache: Dict[str, Any] = {}

        # Build the class-level string dispatch table once (shared, maps type name -> method name)
        if not Interpreter._DISPATCH_TABLE:
            Interpreter._build_dispatch_table()
    
    @staticmethod
    def _build_dispatch_table():
        """Build the class-level node_type -> method_name mapping.

        Iterates over Interpreter's own execute_* methods once at class-init time
        and stores the camelCase node-type key alongside the method name string.
        This avoids the per-dispatch regex overhead at runtime.
        """
        table = {}
        for attr in dir(Interpreter):
            if not attr.startswith("execute_"):
                continue
            snake = attr[len("execute_"):]  # e.g. "binary_operation"
            # Derive CamelCase key (e.g. "BinaryOperation")
            camel = "".join(w.title() for w in snake.split("_"))
            table[camel] = attr
            # Also store the snake_case key directly for nodes that use
            # node_type in snake_case (rare, but keep backward compat)
            table[snake] = attr
        Interpreter._DISPATCH_TABLE = table

    def sync_runtime_functions_to_type_checker(self):
        """
        Sync runtime-registered functions to the type checker.
        
        This is critical for stdlib functions registered after interpreter initialization.
        Without this, the type checker won't know about graphics functions, math functions, etc.
        """
        if not self.enable_type_checking or not self.type_checker:
            return
        
        from ..typesystem.types import FunctionType, ANY_TYPE
        
        # Register all runtime functions with the type checker
        for func_name in self.runtime.functions.keys():
            if func_name not in self.type_checker.env.functions:
                # Create a permissive function type (accepts any args, returns any)
                # This allows type checking to pass while still catching undefined functions
                # We use a large param list to support functions with many arguments
                func_type = FunctionType(
                    param_types=[ANY_TYPE] * 20,  # Support up to 20 args
                    return_type=ANY_TYPE
                )
                # Mark it as variadic so argument count checking is skipped
                func_type.variadic = True
                self.type_checker.env.define_function(func_name, func_type)
        
    def create_function_wrapper(self, function_def):
        """Create a callable wrapper for a user-defined function.
        
        Supports both positional and keyword arguments, including:
        - Named/keyword parameters
        - Default values
        - Variadic parameters (*args)
        - Keyword-only parameters (after * separator)
        """
        def wrapper(*args, **kwargs):
            # Use _resolve_function_arguments to handle all parameter types
            resolved_args = self._resolve_function_arguments(
                function_def,
                list(args),
                kwargs,
                function_def.name
            )
            
            # Create a new scope
            self.enter_scope()

            try:
                # Bind parameters
                for param, value in zip(function_def.parameters, resolved_args):
                    self.set_variable(param.name, value)
                
                # Execute body
                result = None
                for statement in function_def.body:
                    result = self.execute(statement)
            except ReturnException as ret:
                return ret.value
            finally:
                self.exit_scope()
            return result
        return wrapper

    def _get_module_loader(self):
        """Lazy initialize the module loader to avoid circular imports"""
        if self.module_loader is None:
            # Import here to avoid circular imports
            from ..modules.module_loader import ModuleLoader
            search_paths = [os.getcwd()]
            # If the runtime knows the current file, add its directory to search
            # paths so bare-name imports like 'import utils' resolve from the
            # script's directory in addition to cwd.
            file_path = getattr(self.runtime, 'module_path', None)
            if file_path:
                file_dir = os.path.dirname(os.path.abspath(file_path))
                if file_dir not in search_paths:
                    search_paths.insert(0, file_dir)
            self.module_loader = ModuleLoader(self.runtime, search_paths)
        return self.module_loader
        
    def interpret(self, ast_or_source, optimization_level=0):
        """Interpret the AST and execute the program.

        Args:
            ast_or_source: Either an AST Program node or a source code string
            optimization_level: AST optimization level (0=none, 1=basic, 2=standard, 3=aggressive)

        Returns:
            The result of program execution
        """
        # Support both AST and source string for backward compatibility
        if isinstance(ast_or_source, str):
            from ..parser.lexer import Lexer
            from ..parser.parser import Parser

            lexer = Lexer(ast_or_source)
            tokens = lexer.tokenize()
            parser = Parser(tokens, source=ast_or_source)
            ast = parser.parse()
        else:
            ast = ast_or_source

        # Apply AST-level optimizations when level > 0
        if optimization_level > 0 and isinstance(ast, Program):
            from ..optimizer import create_optimization_pipeline, OptimizationLevel
            _level_map = {
                1: OptimizationLevel.O1,
                2: OptimizationLevel.O2,
                3: OptimizationLevel.O3,
            }
            opt_level = _level_map.get(optimization_level, OptimizationLevel.O1)
            pipeline = create_optimization_pipeline(opt_level)
            ast = pipeline.run(ast)

        # Run type checking if enabled
        if self.enable_type_checking and isinstance(ast, Program):
            # CRITICAL: Sync runtime functions to type checker first
            # This ensures stdlib functions (graphics, math, etc.) are known to the type system
            self.sync_runtime_functions_to_type_checker()
            
            errors = self.type_checker.check_program(ast)
            if errors:
                error_msg = "\n".join(errors)
                raise NLPLTypeError(
                    f"Type checking failed:\n{error_msg}",
                    error_type_key="type_mismatch",
                    full_source=self.source,
                )
            
        try:
            if isinstance(ast, Program):
                result = None
                for statement in ast.statements:
                    result = self.execute(statement)
                return result
            else:
                return self.execute(ast)
        except Exception as e:
            # Debugger hook: trace exception
            if self.debugger:
                self.debugger.trace_exception(e)
            raise
            
    def execute(self, node):
        """Execute a node in the AST."""
        # Debugger hook: trace execution if debugger attached
        if self.debugger and hasattr(node, 'line'):
            file = getattr(node, 'file', self.current_file or '<unknown>')
            line = getattr(node, 'line', self.current_line or 0)
            self.current_file = file
            self.current_line = line
            self.debugger.trace_line(file, line)

        # Get node type key (prefer node_type attr; fall back to class name)
        if hasattr(node, 'node_type'):
            node_type = node.node_type
        else:
            node_type = node.__class__.__name__

        # Fast path: check per-instance cache first (bound method lookup is O(1))
        handler = self._dispatch_cache.get(node_type)
        if handler is None:
            # Look up method name in the class-level table
            method_name = Interpreter._DISPATCH_TABLE.get(node_type)
            if method_name is None:
                # Fall back to on-the-fly camel->snake conversion (handles
                # subclasses or newly added node types not yet in the table)
                method_name = "execute_" + _camel_to_snake(node_type)
            if hasattr(self, method_name):
                handler = getattr(self, method_name)
                self._dispatch_cache[node_type] = handler
            else:
                raise NotImplementedError(
                    f"Execution of {node_type} nodes is not implemented "
                    f"(looked for method: {method_name})"
                )

        return handler(node)
            
    def get_variable_or_none(self, name):
        """
        Cheap speculative variable lookup — returns None on miss instead of raising.

        Use this for hot-path checks (e.g. 'is this name a callable variable?')
        where the absence of the name is expected and normal.  This avoids the
        expensive NLPLNameError construction (difflib.get_close_matches over all
        known names) that get_variable() incurs on every miss.
        """
        for scope in reversed(self.current_scope):
            if name in scope:
                return scope[name]
        if hasattr(self.runtime, 'constants') and name in self.runtime.constants:
            return self.runtime.constants[name]
        return None

    def get_variable(self, name):
        """Get a variable from the current scope with enhanced error reporting."""
        # Search from innermost to outermost scope
        for scope in reversed(self.current_scope):
            if name in scope:
                value = scope[name]
                # Moved value: accessing a moved variable is a hard error
                try:
                    from ..stdlib.smart_pointers import MovedValue
                    if isinstance(value, MovedValue):
                        raise NLPLRuntimeError(
                            f"use of moved value: '{name}' was moved out and cannot be accessed",
                            error_type_key="runtime_error",
                            full_source=self.source,
                        )
                except ImportError:
                    pass
                return value
        
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
            available_names=available_names,
            error_type_key="undefined_variable",
            full_source=self.source
        )
        
    def set_variable(self, name, value):
        """Set a variable in the current scope.

        Raises if the variable is currently borrowed (immutably or mutably),
        since mutation of a borrowed variable violates the borrow contract.
        """
        borrow = self._borrow_tracker.get(name)
        if borrow and (borrow["immutable_count"] > 0 or borrow["is_mutable"]):
            kind = "mutably" if borrow["is_mutable"] else "immutably"
            raise NLPLRuntimeError(
                f"cannot assign to '{name}': it is currently borrowed {kind}; "
                f"call 'drop borrow {name}' first",
                error_type_key="runtime_error",
                full_source=self.source,
            )
        self.current_scope[-1][name] = value
        return value
        
    def enter_scope(self):
        """Enter a new scope."""
        self.current_scope.append({})
        
    def exit_scope(self):
        """Exit the current scope.

        Performs RAII-style reference-count decrement for any Rc / Arc / Weak
        values that are bound in the scope being popped.  If an Rc/Arc strong
        count reaches zero after decrement we record the drop (value is freed).
        """
        if len(self.current_scope) > 1:
            # Clean up: release any borrows registered for variables in the scope
            # being popped so outer code is not left with stale borrow records.
            scope = self.current_scope[-1]
            for var_name in scope:
                if var_name in self._borrow_tracker:
                    del self._borrow_tracker[var_name]
            # RAII: decrement ref-counts for smart pointer values in this scope.
            try:
                from ..stdlib.smart_pointers import RcValue, ArcValue, WeakValue
                for val in scope.values():
                    if isinstance(val, (RcValue, ArcValue, WeakValue)):
                        val.drop()
            except Exception:
                pass  # Never let RAII errors abort program cleanup
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
                
            # If the module name has dots (package.module), use the last part
            if '.' in module_name:
                module_name = module_name.split('.')[-1]
                
            # Add the module to the current scope
            self.set_variable(module_name, module)
            
            return None
        except (ImportError, CircularImportError) as e:
            raise NLPLRuntimeError(
                message=f"Import error: {str(e)}",
                line=getattr(node, 'line', None),
                column=getattr(node, 'column', None),
                error_type_key="module_not_found" if isinstance(e, ImportError) else "circular_import",
                full_source=self.source,
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
                        column=getattr(node, 'column', None),
                        error_type_key="undefined_attribute",
                        full_source=self.source
                    )
                    
            return None
        except (ImportError, CircularImportError) as e:
            raise NLPLRuntimeError(
                message=f"Import error: {str(e)}",
                line=getattr(node, 'line', None),
                column=getattr(node, 'column', None),
                error_type_key="module_not_found" if isinstance(e, ImportError) else "circular_import",
                full_source=self.source,
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
                column=getattr(node, 'column', None),
                error_type_key="undefined_attribute",
                full_source=self.source
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

        # Handle allocator hints on collection types:
        #   set items to List of Integer with allocator arena_alloc
        # The AllocatorHint tells us to route collection construction through the
        # specified allocator so that the backing memory is tracked by it.
        if hasattr(node, 'type_annotation') and isinstance(node.type_annotation, AllocatorHint):
            alloc_name = node.type_annotation.allocator_name
            try:
                allocator = self.get_variable(alloc_name)
            except NLPLNameError:
                raise NLPLRuntimeError(
                    f"Allocator '{alloc_name}' is not defined in the current scope",
                    line=getattr(node, 'line_number', None),
                    error_type_key="undefined_variable",
                    full_source=self.source,
                )
            # Record the allocation with the allocator (for stats and tracking)
            if allocator is not None and hasattr(allocator, 'allocate'):
                element_count = len(value) if hasattr(value, '__len__') else 1
                # Estimate 8 bytes per element (conservative pointer-sized approximation)
                allocator.allocate(element_count * 8, alignment=8)

        self.set_variable(node.name, value)
        return value

    def execute_index_assignment(self, node):
        """Execute an index assignment: set array[index] to value."""
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
                    column=getattr(node, 'column', None),
                    error_type_key="index_out_of_range",
                    full_source=self.source
                )
            elif isinstance(e, TypeError):
                raise NLPLTypeError(
                    message=f"Cannot assign to index on type {type(container).__name__}",
                    expected_type="list or dict",
                    got_type=type(container).__name__,
                    line=getattr(node, 'line', None),
                    column=getattr(node, 'column', None),
                    error_type_key="invalid_operation",
                    full_source=self.source
                )
            else:
                raise NLPLRuntimeError(
                    message=f"Failed to assign to index {index}: {e}",
                    line=getattr(node, 'line', None),
                    column=getattr(node, 'column', None),
                    error_type_key="key_not_found",
                    full_source=self.source
                )
        
    def execute_function_definition(self, node):
        """Execute a function definition.
        
        Stores the function definition and creates a callable function value
        that can be used as a first-class value (assigned to variables, passed as arguments, etc.)
        """
        self.functions[node.name] = node
        
        # Create a callable wrapper and store it as a variable too
        # This enables first-class function support
        function_value = self.create_function_wrapper(node)
        
        # Apply decorators if any
        if hasattr(node, 'decorators') and node.decorators:
            for decorator in reversed(node.decorators):  # Apply decorators bottom-up
                function_value = self.apply_decorator(decorator, function_value, node)
        
        self.set_variable(node.name, function_value)
        
        return node.name
    
    def apply_decorator(self, decorator_node, function_value, function_def):
        """Apply a decorator to a function."""
        from nlpl.decorators import get_decorator
        
        # Evaluate decorator arguments
        args = {}
        for arg_name, arg_expr in decorator_node.arguments.items():
            args[arg_name] = self.execute(arg_expr)
        
        # Get the decorator implementation
        decorator_func = get_decorator(decorator_node.name)
        if decorator_func is None:
            raise NLPLRuntimeError(
                f"Unknown decorator: @{decorator_node.name}",
                line=decorator_node.line,
                error_type_key="undefined_function",
                full_source=self.source,
            )
        
        # Apply decorator based on type
        # Decorators that take arguments need to be called first to get the actual decorator
        if args and decorator_node.name in ("deprecated", "retry", "validate_args"):
            # Call with arguments to get the actual decorator
            actual_decorator = decorator_func(**args)
            return actual_decorator(function_value)
        else:
            # Decorator without arguments or simple decorator
            return decorator_func(function_value)
    
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

    def execute_parallel_for_loop(self, node):
        """Execute a parallel for-each loop.

        Each iteration runs in its own thread from a thread pool.
        Iterations are isolated: each one receives a snapshot of the enclosing
        scope and any variables written inside an iteration are local to that
        iteration only (preventing data races by construction).

        Break/continue are not supported inside parallel loops.

        Example NLPL::

            parallel for each item in data
                set result to process item
                print text result
            end
        """
        # Use self.__class__ to avoid a circular import of interpreter.py
        _Interp = self.__class__
        import copy

        iterable = self.execute(node.iterable)
        if not hasattr(iterable, '__iter__'):
            raise NLPLRuntimeError(
                f"'parallel for each' requires an iterable collection, got {type(iterable).__name__}",
                line=getattr(node, 'line_number', None),
                error_type_key="type_mismatch",
                full_source=self.source,
            )
        items = list(iterable)
        if not items:
            return None

        # Build a shallow snapshot of the current scope for read-only access
        scope_snapshot = {}
        for scope_level in self.current_scope:
            scope_snapshot.update(scope_level)

        errors = []
        errors_lock = __import__("threading").Lock()

        cpu_count = __import__("multiprocessing").cpu_count()
        max_workers = max(1, min(cpu_count, len(items)))

        def run_iteration(item):
            """Execute the loop body for one item in its own interpreter child."""
            child = _Interp(self.runtime)
            # Populate child scope with parent snapshot (read-only bindings)
            child.enter_scope()
            for name, val in scope_snapshot.items():
                child.set_variable(name, val)
            # Set the loop variable for this iteration
            child.set_variable(node.var_name, item)
            # Copy function definitions so the body can call functions
            child.functions.update(self.functions)
            child.classes.update(self.classes)
            child.source = self.source
            try:
                for stmt in node.body:
                    child.execute(stmt)
            except Exception as exc:
                with errors_lock:
                    errors.append(exc)
            finally:
                child.exit_scope()

        with _cf.ThreadPoolExecutor(max_workers=max_workers) as pool:
            futures = [pool.submit(run_iteration, item) for item in items]
            _cf.wait(futures)

        if errors:
            raise NLPLRuntimeError(
                f"Error in parallel for each iteration: {errors[0]}",
                line=getattr(node, 'line_number', None),
                error_type_key="runtime_error",
                full_source=self.source,
            )
        return None

    
    def execute_repeat_n_times_loop(self, node):
        """Execute a repeat-n-times loop."""
        result = None
        
        # Evaluate the count expression to get number of iterations
        count = self.execute(node.count)
        
        # Ensure count is an integer
        if not isinstance(count, (int, float)):
            raise NLPLTypeError(
                f"Repeat count must be a number, got {type(count).__name__}",
                expected_type="Integer or Float",
                got_type=type(count).__name__,
                line=getattr(node, 'line', None),
                error_type_key="type_mismatch",
                full_source=self.source,
            )
        
        count = int(count)
        
        # Validate count is non-negative
        if count < 0:
            raise NLPLRuntimeError(
                f"Repeat count must be non-negative, got {count}",
                line=getattr(node, 'line', None),
                error_type_key="invalid_operation",
                full_source=self.source,
            )
        
        # Execute the loop body 'count' times
        # DO NOT create a new scope - loops should access outer scope variables
        try:
            for iteration in range(count):
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
    
    def execute_repeat_while_loop(self, node):
        """Execute a repeat-while loop (natural language while loop)."""
        result = None
        loop_completed = False
        
        # Execute the loop while condition is true
        # DO NOT create a new scope - loops should access outer scope variables
        try:
            while self.execute(node.condition):
                try:
                    for statement in node.body:
                        result = self.execute(statement)
                except ContinueException:
                    # Continue to next iteration
                    continue
        except BreakException:
            # Break was called, loop did not complete normally
            pass
        else:
            # Loop completed without break
            loop_completed = True
        
        # Execute else block if loop completed without break
        if loop_completed and node.else_body:
            for statement in node.else_body:
                result = self.execute(statement)
        
        return result
        
    def execute_switch_statement(self, node):
        """Execute a switch statement for multi-way branching.
        
        Evaluates the switch expression once and compares it against each case value.
        Executes the matching case body and stops (no fallthrough by default).
        Executes default case if no match found.
        """
        # Evaluate the switch expression once
        switch_value = self.execute(node.expression)
        
        # Try to match against each case
        for case in node.cases:
            case_value = self.execute(case.value)
            
            # Check if values match (using Python equality)
            if switch_value == case_value:
                # Execute the case body
                result = None
                for statement in case.body:
                    result = self.execute(statement)
                # No fallthrough - return after first match
                return result
        
        # No case matched - execute default case if present
        if node.default_case:
            result = None
            for statement in node.default_case:
                result = self.execute(statement)
            return result
        
        # No match and no default - return None
        return None
    
    def execute_match_expression(self, node):
        """Execute a pattern matching expression.
        
        Evaluates the match expression and tries to match against each case pattern.
        When a pattern matches, binds any variables and executes the case body.
        Supports:
        - Literal patterns: case 42, case "hello"
        - Identifier patterns: case x (binds x to the value)
        - Wildcard pattern: case _ (matches anything)
        - Option patterns: case Some with value, case None
        - Result patterns: case Ok with value, case Err with error
        - Variant patterns: case Ok value, case Some x
        
        Returns the result of the matching case body, or None if no match.
        """
        # Evaluate the expression to match against
        match_value = self.execute(node.expression)
        
        # Try each case in order (first match wins)
        for case in node.cases:
            # Check if pattern matches and get any bindings
            matched, bindings = self._match_pattern(case.pattern, match_value)
            
            if matched:
                # Check guard condition if present
                if case.guard:
                    # Enter scope for bindings during guard evaluation
                    self.enter_scope()
                    try:
                        # Bind variables for guard evaluation
                        for var_name, var_value in bindings.items():
                            self.set_variable(var_name, var_value)
                        
                        # Evaluate guard condition
                        guard_result = self.execute(case.guard)
                        
                        # Guard must be truthy to proceed
                        if not guard_result:
                            continue
                    finally:
                        self.exit_scope()
                
                # Pattern matched (and guard passed if present)
                # Enter new scope and bind pattern variables
                self.enter_scope()
                try:
                    # Bind all pattern variables
                    for var_name, var_value in bindings.items():
                        self.set_variable(var_name, var_value)
                    
                    # Execute the case body
                    result = None
                    for statement in case.body:
                        result = self.execute(statement)
                    
                    return result
                finally:
                    self.exit_scope()
        
        # No pattern matched
        raise NLPLRuntimeError(
            f"Non-exhaustive pattern match: no pattern matched the value {match_value!r}",
            line=node.line_number,
            error_type_key="invalid_operation",
            full_source=self.source
        )
    
    def _match_pattern(self, pattern, value):
        """Check if a pattern matches a value.
        
        Args:
            pattern: Pattern AST node
            value: Runtime value to match against
            
        Returns:
            Tuple of (matched: bool, bindings: dict)
            - matched: True if pattern matches value
            - bindings: Dict of variable names to values for identifier patterns
        """
        # Literal pattern: case 42, case "hello", case true
        if isinstance(pattern, LiteralPattern):
            # pattern.value is a Literal AST node - need to extract the actual value
            if hasattr(pattern.value, 'value'):
                pattern_value = pattern.value.value
            else:
                pattern_value = pattern.value
            
            # For string literals, strip surrounding quotes if present
            if isinstance(pattern_value, str) and len(pattern_value) >= 2:
                if (pattern_value[0] == '"' and pattern_value[-1] == '"') or \
                   (pattern_value[0] == "'" and pattern_value[-1] == "'"):
                    pattern_value = pattern_value[1:-1]
            
            matched = (pattern_value == value)
            return (matched, {})
        
        # Identifier pattern: case x (binds x to the value)
        elif isinstance(pattern, IdentifierPattern):
            # Always matches, binds the identifier to the value
            return (True, {pattern.name: value})
        
        # Wildcard pattern: case _ (matches anything, no binding)
        elif isinstance(pattern, WildcardPattern):
            return (True, {})
        
        # Option pattern: case Some with value, case None
        elif isinstance(pattern, OptionPattern):
            # Import Option class for type checking
            from nlpl.stdlib.option_result import Option
            
            if not isinstance(value, Option):
                return (False, {})
            
            # Check variant type
            if pattern.variant == "Some":
                if value.is_some():
                    # Bind the contained value if binding specified
                    if pattern.binding:
                        return (True, {pattern.binding: value.unwrap()})
                    return (True, {})
                return (False, {})
            
            elif pattern.variant == "None":
                if value.is_none():
                    return (True, {})
                return (False, {})
        
        # Result pattern: case Ok with value, case Err with error
        elif isinstance(pattern, ResultPattern):
            # Import Result class for type checking
            from nlpl.stdlib.option_result import Result
            
            if not isinstance(value, Result):
                return (False, {})
            
            # Check variant type
            if pattern.variant == "Ok":
                if value.is_ok():
                    # Bind the success value if binding specified
                    if pattern.binding:
                        return (True, {pattern.binding: value.unwrap()})
                    return (True, {})
                return (False, {})
            
            elif pattern.variant == "Err":
                if value.is_err():
                    # Bind the error value if binding specified
                    if pattern.binding:
                        return (True, {pattern.binding: value.unwrap_err()})
                    return (True, {})
                return (False, {})
        
        # Variant pattern: case Ok value, case Some x (generic variant matching)
        elif isinstance(pattern, VariantPattern):
            # Try to match against Option/Result types first
            from nlpl.stdlib.option_result import Option, Result
            
            if isinstance(value, Option):
                # Match Option variants
                if pattern.variant_name == "Some" and value.is_some():
                    bindings = {}
                    if pattern.bindings:
                        # Bind the contained value to the first binding name
                        bindings[pattern.bindings[0]] = value.unwrap()
                    return (True, bindings)
                elif pattern.variant_name == "None" and value.is_none():
                    return (True, {})
                return (False, {})
            
            elif isinstance(value, Result):
                # Match Result variants
                if pattern.variant_name == "Ok" and value.is_ok():
                    bindings = {}
                    if pattern.bindings:
                        # Bind the success value to the first binding name
                        bindings[pattern.bindings[0]] = value.unwrap()
                    return (True, bindings)
                elif pattern.variant_name == "Err" and value.is_err():
                    bindings = {}
                    if pattern.bindings:
                        # Bind the error value to the first binding name
                        bindings[pattern.bindings[0]] = value.unwrap_err()
                    return (True, bindings)
                return (False, {})
            
            # Future: Support for custom variant types (enums, structs)
            # For now, just fail to match
            return (False, {})
        
        # Unknown pattern type
        else:
            raise NLPLRuntimeError(
                f"Unknown pattern type: {type(pattern).__name__}",
                line=getattr(pattern, 'line_number', None),
                error_type_key="invalid_operation",
                full_source=self.source,
            )
    
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
    
    def execute_interface_definition(self, node):
        """Execute an interface definition.
        
        Interfaces are stored for type checking purposes.
        They don't create runtime objects, just define contracts.
        """
        # Store the interface definition for type checking
        if not hasattr(self, 'interfaces'):
            self.interfaces = {}
        self.interfaces[node.name] = node
        return node.name
    
    def execute_abstract_class_definition(self, node):
        """Execute an abstract class definition.
        
        Abstract classes are like regular classes but cannot be instantiated directly.
        They can contain both abstract methods (no implementation) and concrete methods.
        """
        # Store like a regular class - the type system will enforce abstract rules
        self.classes[node.name] = node
        return node.name
    
    def execute_trait_definition(self, node):
        """Execute a trait definition.
        
        Traits define reusable behavior that can be mixed into classes.
        They contain method signatures (required_methods) and optionally 
        default implementations (provided_methods).
        
        Traits are similar to interfaces but can provide default implementations.
        They support composition and multiple trait usage in a single class.
        """
        # Store trait definition for type checking and class composition
        if not hasattr(self, 'traits'):
            self.traits = {}
        self.traits[node.name] = node
        return node.name
    
    def execute_struct_definition(self, node):
        """Execute a struct definition.
        
        Registers the struct as a type that can be instantiated.
        Structs are like classes but with explicit memory layout control.
        Supports packed structs and explicit alignment.
        """
        # Extract fields and their types from StructField nodes
        fields = []
        for field in node.fields:
            # field is StructField with name, type_annotation, bit_width
            type_name = field.type_annotation
            if not type_name:
                type_name = "Pointer"  # Default to pointer size if unknown
            
            # TODO: Handle bit_width for bit fields (e.g., field.bit_width = 4 for 4-bit field)
            # For now, bit fields are stored as full bytes
            
            fields.append((field.name, type_name))
            
        # Create runtime definition with packed and alignment support
        definition = RuntimeStructDefinition(
            node.name, 
            fields, 
            packed=node.packed if hasattr(node, 'packed') else False,
            alignment=node.alignment if hasattr(node, 'alignment') else None
        )
        
        # Store original fields for FFI marshalling
        definition._original_fields = fields
        
        self.classes[node.name] = definition
        
        # Also store methods if this is a C++-style struct with methods
        if hasattr(node, 'methods') and node.methods:
            # Store methods on the definition for later binding
            definition.methods = node.methods
        
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
        Size is determined by the largest field.
        """
        # Extract fields and their types from StructField nodes
        fields = []
        for field in node.fields:
            # field is StructField with name, type_annotation, bit_width
            type_name = field.type_annotation
            if not type_name:
                type_name = "Pointer"  # Default to pointer size if unknown
            fields.append((field.name, type_name))
            
        # Create runtime definition and store in classes map
        # Unions don't support packed/alignment (they're already minimal)
        definition = RuntimeUnionDefinition(node.name, fields)
        self.classes[node.name] = definition
        return node.name
    
    def execute_enum_definition(self, node):
        """Execute an enum definition.
        
        Creates an enum type with named constant values.
        The enum is accessible as a namespace with member values.
        Supports auto-numbering, explicit values, and string enums.
        
        Examples:
            enum Color
                Red
                Green
                Blue
            end
            # Auto-numbered: Red=0, Green=1, Blue=2
            
            enum Status
                Success = 0
                Error = 1
                Pending = 2
            end
            
            enum LogLevel
                Debug = "DEBUG"
                Info = "INFO"
                Error = "ERROR"
            end
            
            # Access: Color.Red, Status.Success, LogLevel.Debug
        """
        # Create an enum class-like object
        class EnumType:
            """Runtime representation of an enum type."""
            def __init__(self, name, members):
                self._name = name
                self._members = members
                self._value_to_name = {v: k for k, v in members.items()}
                # Add members as attributes
                for member_name, member_value in members.items():
                    setattr(self, member_name, member_value)
            
            def __repr__(self):
                return f"<Enum {self._name}>"
            
            def __getitem__(self, key):
                """Allow dict-like access: Color["Red"]"""
                return self._members[key]
            
            def __contains__(self, value):
                """Check if value is in enum: 0 in Color"""
                return value in self._value_to_name
            
            def get_name(self, value):
                """Get name for a value: Color.get_name(0) -> "Red" """
                return self._value_to_name.get(value)
            
            def values(self):
                """Get all enum values"""
                return list(self._members.values())
            
            def names(self):
                """Get all enum names"""
                return list(self._members.keys())
        
        # Build member dictionary with auto-numbering
        members = {}
        auto_value = 0
        
        for member in node.members:
            if hasattr(member, 'value') and member.value is not None:
                # Explicit value provided
                value = self.execute(member.value)
                # Update auto_value for next implicit member
                if isinstance(value, (int, float)):
                    auto_value = int(value) + 1
            else:
                # Auto-numbered value
                value = auto_value
                auto_value += 1
            
            members[member.name] = value
        
        # Create enum type instance
        enum_type = EnumType(node.name, members)
        
        # Store the enum type in classes (for type checking) and variables (for access)
        self.classes[node.name] = node
        self.set_variable(node.name, enum_type)
        
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
        except NLPLUserException as e:
            # Check if exception type matches the catch block
            # If no type is specified, it matches all NLPL user exceptions
            matches = True
            if node.exception_type:
                # Type name "Error" matches everything
                if node.exception_type != "Error" and node.exception_type != e.exception_type:
                    matches = False
            
            if matches:
                # Store for re-raising
                self.last_exception = e

                # Bind exception variable in the current scope (no inner scope, so
                # assignments inside the catch body update variables in the outer scope)
                exc_value = e.message if e.message else e.exception_type
                exc_var = node.exception_var if node.exception_var else "error"
                self.set_variable(exc_var, exc_value)

                # Bind exception properties if specified (e.g., "catch error with message")
                if hasattr(node, 'exception_properties') and node.exception_properties:
                    for prop in node.exception_properties:
                        if prop == 'message':
                            self.set_variable(prop, e.message if e.message else str(exc_value))
                        elif prop == 'type':
                            self.set_variable(prop, e.exception_type)
                        elif prop == 'code':
                            self.set_variable(prop, getattr(e, 'code', None))
                        else:
                            self.set_variable(prop, getattr(e, prop, None))

                result = None
                for statement in node.catch_block:
                    result = self.execute(statement)
                return result
            else:
                # Re-raise NLPLUserException if type doesn't match
                raise e
        except (NLPLRuntimeError, NLPLTypeError, NLPLNameError) as e:
            # Handle runtime errors from the interpreter itself
            # Check if exception type matches based on nlpl_type
            matches = True
            if node.exception_type and node.exception_type != "Error":
                if node.exception_type != getattr(e, 'nlpl_type', None):
                    matches = False
            
            if matches:
                exc_message = str(e)
                exc_var = node.exception_var if node.exception_var else "error"
                self.set_variable(exc_var, exc_message)

                # Bind exception properties if specified
                if hasattr(node, 'exception_properties') and node.exception_properties:
                    for prop in node.exception_properties:
                        if prop == 'message':
                            self.set_variable(prop, exc_message)
                        elif prop == 'type':
                            self.set_variable(prop, getattr(e, 'nlpl_type', type(e).__name__))
                        else:
                            self.set_variable(prop, getattr(e, prop, None))

                result = None
                for statement in node.catch_block:
                    result = self.execute(statement)
                return result
            else:
                raise e
        except Exception as e:
            # Handle other Python exceptions (e.g., ZeroDivisionError)
            if node.exception_type and node.exception_type != "Error":
                raise e

            exc_message = str(e)
            exc_var = node.exception_var if node.exception_var else "error"
            self.set_variable(exc_var, exc_message)

            # Bind exception properties if specified (e.g., "catch error with message")
            if hasattr(node, 'exception_properties') and node.exception_properties:
                for prop in node.exception_properties:
                    if prop == 'message':
                        self.set_variable(prop, exc_message)
                    elif prop == 'type':
                        self.set_variable(prop, type(e).__name__)
                    else:
                        self.set_variable(prop, getattr(e, prop, None))

            result = None
            for statement in node.catch_block:
                result = self.execute(statement)
            return result

    def execute_raise_statement(self, node):
        """Execute a raise statement."""
        exception_type = node.exception_type
        message = None
        if node.message:
            message = self.execute(node.message)
            
        # If it's a re-raise: "raise Error" with no message
        if exception_type == "Error" and message is None:
            if self.last_exception:
                raise self.last_exception
            else:
                # Fallback to looking in scope if last_exception is lost
                try:
                    error_val = self.get_variable("error")
                    raise NLPLUserException("Error", str(error_val), getattr(node, 'line', None))
                except:
                    # No exception to re-raise
                    raise NLPLRuntimeError(
                        message="Nothing to re-raise",
                        line=getattr(node, 'line', None),
                        error_type_key="invalid_operation",
                        full_source=self.source,
                    )
                
        raise NLPLUserException(exception_type, message, getattr(node, 'line', None))
    
    def _nlpl_type_to_ctype(self, nlpl_type):
        """Convert NLPL type string to ctypes type."""
        import ctypes
        
        # Normalize type name
        type_name = str(nlpl_type).lower().strip()
        
        # Map NLPL types to ctypes types
        type_map = {
            'integer': ctypes.c_long,
            'int': ctypes.c_long,
            'i32': ctypes.c_int,
            'i64': ctypes.c_longlong,
            'float': ctypes.c_double,
            'double': ctypes.c_double,
            'f32': ctypes.c_float,
            'f64': ctypes.c_double,
            'boolean': ctypes.c_bool,
            'bool': ctypes.c_bool,
            'pointer': ctypes.c_void_p,
            'string': ctypes.c_char_p,
            'void': None,
        }
        
        if type_name in type_map:
            return type_map[type_name]
        
        # Default to void pointer for unknown types
        return ctypes.c_void_p
    
    def _struct_to_ctype(self, struct_def):
        """Convert NLPL StructDefinition to ctypes.Structure class.
        
        Creates a dynamic ctypes.Structure class that matches the NLPL struct layout.
        Handles nested structs, arrays, and proper field types.
        """
        import ctypes
        
        if not isinstance(struct_def, RuntimeStructDefinition):
            raise NLPLTypeError(
                f"Expected RuntimeStructDefinition, got {type(struct_def)}",
                expected_type="RuntimeStructDefinition",
                got_type=type(struct_def).__name__,
                error_type_key="type_mismatch",
                full_source=self.source,
            )
        
        # Create fields list for ctypes.Structure
        # Format: [(field_name, ctype), ...]
        ctype_fields = []
        
        for field_name, field_obj in struct_def.fields.items():
            # Get the NLPL type name from the original fields
            # We need to find the original type name from the definition
            type_name = None
            for fname, ftype in [(f[0], f[1]) for f in getattr(struct_def, '_original_fields', [])]:
                if fname == field_name:
                    type_name = ftype
                    break
            
            if not type_name:
                # Fallback: infer from struct format code
                code_to_type = {
                    'q': ctypes.c_longlong,  # INTEGER
                    'd': ctypes.c_double,     # FLOAT
                    '?': ctypes.c_bool,       # BOOLEAN
                    'b': ctypes.c_byte,       # BYTE
                    'c': ctypes.c_char,       # CHAR
                    'Q': ctypes.c_void_p,     # POINTER
                }
                ctype = code_to_type.get(field_obj.type_code, ctypes.c_void_p)
            else:
                # Check if this is a nested struct
                if type_name in self.classes and isinstance(self.classes[type_name], RuntimeStructDefinition):
                    # Recursive: convert nested struct
                    ctype = self._struct_to_ctype(self.classes[type_name])
                else:
                    # Regular type
                    ctype = self._nlpl_type_to_ctype(type_name)
            
            ctype_fields.append((field_name, ctype))
        
        # Dynamically create ctypes.Structure subclass
        struct_class = type(
            struct_def.name,
            (ctypes.Structure,),
            {
                '_fields_': ctype_fields,
                '_pack_': 1 if struct_def.packed else None,
            }
        )
        
        # Handle explicit alignment
        if struct_def.explicit_alignment:
            struct_class._align_ = struct_def.explicit_alignment
        
        return struct_class
    
    def _structure_instance_to_cstruct(self, struct_instance, cstruct_class):
        """Convert NLPL StructureInstance to ctypes.Structure instance.
        
        Copies all field values from NLPL struct to C struct with proper type conversion.
        """
        import ctypes
        from nlpl.runtime.structures import StructureInstance
        
        if not isinstance(struct_instance, StructureInstance):
            raise NLPLTypeError(
                f"Expected StructureInstance, got {type(struct_instance)}",
                expected_type="StructureInstance",
                got_type=type(struct_instance).__name__,
                error_type_key="type_mismatch",
                full_source=self.source,
            )
        
        # Create C struct instance
        c_struct = cstruct_class()
        
        # Copy fields
        for field_name in struct_instance.definition.fields:
            nlpl_value = struct_instance.get_field(field_name)
            
            # Handle nested structs
            if isinstance(nlpl_value, StructureInstance):
                # Get the nested struct's ctype class
                nested_ctype = self._struct_to_ctype(nlpl_value.definition)
                nested_c_struct = self._structure_instance_to_cstruct(nlpl_value, nested_ctype)
                setattr(c_struct, field_name, nested_c_struct)
            else:
                # Regular field - direct assignment (ctypes handles conversion)
                setattr(c_struct, field_name, nlpl_value)
        
        return c_struct
    
    def _cstruct_to_structure_instance(self, c_struct, struct_def):
        """Convert ctypes.Structure instance back to NLPL StructureInstance.
        
        Creates a new NLPL struct and populates it from the C struct.
        """
        from nlpl.runtime.structures import StructureInstance
        
        # Create NLPL struct instance
        nlpl_struct = StructureInstance(struct_def)
        
        # Copy fields from C struct
        for field_name in struct_def.fields:
            c_value = getattr(c_struct, field_name)
            
            # Handle nested structs
            if hasattr(c_value, '_fields_'):  # It's a ctypes.Structure
                # Find the nested struct definition
                nested_struct_def = None
                for fname, ftype in getattr(struct_def, '_original_fields', []):
                    if fname == field_name and ftype in self.classes:
                        nested_struct_def = self.classes[ftype]
                        break
                
                if nested_struct_def:
                    nested_nlpl = self._cstruct_to_structure_instance(c_value, nested_struct_def)
                    nlpl_struct.set_field(field_name, nested_nlpl)
                else:
                    # Can't convert, store as-is
                    nlpl_struct.set_field(field_name, c_value)
            else:
                # Regular field
                nlpl_struct.set_field(field_name, c_value)
        
        return nlpl_struct
    
    def _python_to_ctype_value(self, value, ctype):
        """Convert Python value to ctypes-compatible value."""
        import ctypes
        from nlpl.runtime.structures import StructureInstance
        
        if ctype is None or ctype == "void":
            return None
        
        # Handle NLPL struct instances
        if isinstance(value, StructureInstance):
            # Convert to ctypes.Structure
            cstruct_class = self._struct_to_ctype(value.definition)
            return self._structure_instance_to_cstruct(value, cstruct_class)
        
        if ctype == ctypes.c_char_p:
            if isinstance(value, str):
                return value.encode('utf-8')
            elif isinstance(value, bytes):
                return value
            else:
                return str(value).encode('utf-8')
        
        # For numeric types, convert to appropriate type
        if ctype in [ctypes.c_long, ctypes.c_int, ctypes.c_longlong]:
            return int(value) if value is not None else 0
        elif ctype in [ctypes.c_float, ctypes.c_double]:
            return float(value) if value is not None else 0.0
        elif ctype == ctypes.c_bool:
            return bool(value)
        elif ctype == ctypes.c_void_p:
            # Handle pointer values
            if isinstance(value, int):
                return value
            elif hasattr(value, '_address'):
                return value._address
            else:
                return 0
        
        return value
    
    def _ctype_value_to_python(self, value, ctype):
        """Convert ctypes return value to Python value."""
        import ctypes
        
        if ctype is None or ctype == "void":
            return None
        
        # Handle ctypes.Structure instances (struct return values)
        if hasattr(value, '_fields_'):
            # This is a ctypes.Structure - need to find the corresponding NLPL struct
            # Try to match by structure name
            struct_name = type(value).__name__
            if struct_name in self.classes:
                struct_def = self.classes[struct_name]
                return self._cstruct_to_structure_instance(value, struct_def)
            # Can't convert, return as-is
            return value
        
        if ctype == ctypes.c_char_p:
            if isinstance(value, bytes):
                return value.decode('utf-8', errors='replace')
            return value
        
        # Numeric types
        return value
    
    def execute_extern_function_declaration(self, node):
        """Execute an extern function declaration.
        
        Registers a C function binding so it can be called from NLPL.
        
        Example:
            extern function printf with format as Pointer returns Integer from library "c"
        """
        import ctypes
        import platform
        
        func_name = node.name
        library_name = node.library
        calling_convention = getattr(node, 'calling_convention', 'cdecl')
        variadic = getattr(node, 'variadic', False)
        
        if not library_name:
            raise NLPLRuntimeError(
                f"Extern function '{func_name}' must specify a library",
                line=getattr(node, 'line_number', None),
                error_type_key="invalid_operation",
                full_source=self.source,
            )
        
        try:
            # Load the library based on platform
            system = platform.system()
            
            # First try to find the library using ctypes.util
            full_library_path = ctypes.util.find_library(library_name)
            
            # Special handling for common library names
            if not full_library_path:
                if system == 'Windows':
                    if library_name == 'c':
                        full_library_path = 'msvcrt.dll'
                    elif library_name == 'm':
                        full_library_path = 'msvcrt.dll'  # Math functions in msvcrt on Windows
                    else:
                        full_library_path = library_name
                elif system == 'Darwin':  # macOS
                    if library_name == 'c':
                        full_library_path = 'libc.dylib'
                    elif library_name == 'm':
                        full_library_path = 'libm.dylib'
                    else:
                        full_library_path = library_name
                else:  # Linux and other Unix-like
                    if library_name == 'c':
                        full_library_path = 'libc.so.6'
                    elif library_name == 'm':
                        full_library_path = 'libm.so.6'
                    else:
                        full_library_path = library_name
            
            if system == 'Windows':
                if calling_convention == 'stdcall':
                    library = ctypes.WinDLL(full_library_path)
                else:
                    library = ctypes.CDLL(full_library_path)
            else:
                library = ctypes.CDLL(full_library_path)
            
            # Get the C function
            c_func = getattr(library, func_name)
            
            # Parse return type
            return_type = node.return_type if node.return_type else "Void"
            c_return_type = self._nlpl_type_to_ctype(return_type)
            c_func.restype = c_return_type
            
            # Parse parameter types and names
            param_types = []
            param_names = []
            for param in node.parameters:
                param_names.append(param.name)
                param_types.append(self._nlpl_type_to_ctype(param.type_annotation))
            
            # For non-variadic functions, set argtypes
            # For variadic functions, only set argtypes for fixed parameters
            if param_types and not variadic:
                c_func.argtypes = param_types
            elif param_types and variadic:
                # Set argtypes only for fixed params, variadic params handled differently
                c_func.argtypes = param_types
            
            # Create wrapper that handles type conversion
            def nlpl_wrapper(*args):
                """Wrapper that converts NLPL values to C values and back."""
                # Convert arguments
                c_args = []
                # Keep references to prevent garbage collection
                temp_refs = []
                
                for i, arg in enumerate(args):
                    if i < len(param_types):
                        # Fixed parameter - use declared type
                        ctype = param_types[i]
                    else:
                        # Variadic parameter - infer type from Python value
                        if isinstance(arg, bool):
                            ctype = ctypes.c_int  # C promotes bool to int
                        elif isinstance(arg, int):
                            ctype = ctypes.c_long
                        elif isinstance(arg, float):
                            ctype = ctypes.c_double
                        elif isinstance(arg, str):
                            ctype = ctypes.c_char_p
                        elif isinstance(arg, bytes):
                            ctype = ctypes.c_char_p
                        else:
                            ctype = ctypes.c_void_p
                    
                    # Special handling for strings passed to variadic functions
                    if ctype == ctypes.c_char_p and isinstance(arg, str):
                        # Convert string to bytes and create c_char_p
                        encoded = arg.encode('utf-8')
                        char_ptr = ctypes.c_char_p(encoded)
                        temp_refs.append(char_ptr)  # Keep alive
                        c_args.append(char_ptr)
                    # Special handling for void pointers (format strings in printf)
                    elif ctype == ctypes.c_void_p and isinstance(arg, str):
                        # Convert string to bytes and create c_char_p
                        encoded = arg.encode('utf-8')
                        char_ptr = ctypes.c_char_p(encoded)
                        temp_refs.append(char_ptr)  # Keep alive
                        c_args.append(char_ptr)
                    else:
                        converted = self._python_to_ctype_value(arg, ctype)
                        # For variadic args, explicitly cast to the expected type
                        if i >= len(param_types) and variadic:
                            if ctype == ctypes.c_double and isinstance(converted, (int, float)):
                                converted = ctypes.c_double(float(converted))
                            elif ctype == ctypes.c_long and isinstance(converted, int):
                                converted = ctypes.c_long(converted)
                        c_args.append(converted)
                
                # Call C function
                try:
                    result = c_func(*c_args)
                except Exception as e:
                    raise NLPLRuntimeError(
                        f"Error calling C function '{func_name}': {str(e)}",
                        line=getattr(node, 'line_number', None),
                        error_type_key="function_call_error",
                        full_source=self.source,
                    )
                
                # Convert result back to Python
                return self._ctype_value_to_python(result, c_return_type)
            
            # Register the function in the runtime
            self.runtime.register_function(func_name, nlpl_wrapper)
            
            # Also store in current scope as a variable for direct access
            self.set_variable(func_name, nlpl_wrapper)
            
            return func_name
            
        except OSError as e:
            raise NLPLRuntimeError(
                f"Failed to load library '{library_name}' for extern function '{func_name}': {str(e)}",
                line=getattr(node, 'line_number', None),
                error_type_key="module_not_found",
                full_source=self.source,
            )
        except AttributeError as e:
            raise NLPLRuntimeError(
                f"Function '{func_name}' not found in library '{library_name}': {str(e)}",
                line=getattr(node, 'line_number', None),
                error_type_key="undefined_function",
                full_source=self.source,
            )
    
    def execute_extern_variable_declaration(self, node):
        """Execute an extern variable declaration.
        
        Accesses a global variable from a C library.
        
        Example:
            extern variable errno as Integer from library "c"
        """
        import ctypes
        import platform
        
        var_name = node.name
        library_name = node.library
        var_type = node.type_annotation
        
        if not library_name:
            raise NLPLRuntimeError(
                f"Extern variable '{var_name}' must specify a library",
                line=getattr(node, 'line_number', None),
                error_type_key="invalid_operation",
                full_source=self.source,
            )
        
        try:
            # Load the library
            system = platform.system()
            if system == 'Windows':
                library = ctypes.CDLL(library_name)
            else:
                # Unix-like systems
                if library_name == 'c':
                    if system == 'Darwin':  # macOS
                        library_name = 'libc.dylib'
                    else:  # Linux
                        library_name = 'libc.so.6'
                
                library = ctypes.CDLL(library_name)
            
            # Get the variable address
            var_address = ctypes.addressof(ctypes.py_object(library))
            
            # Create a ctypes object to hold the variable
            ctype = self._nlpl_type_to_ctype(var_type)
            if ctype is None:
                ctype = ctypes.c_void_p
            
            # Store the variable reference in the current scope
            # For now, we store the address and type info
            self.set_variable(var_name, {
                'address': var_address,
                'type': var_type,
                'library': library,
                'ctype': ctype,
                'c_var_name': var_name
            })
            
            return var_name
            
        except OSError as e:
            raise NLPLRuntimeError(
                f"Failed to load library '{library_name}' for extern variable '{var_name}': {str(e)}",
                line=getattr(node, 'line_number', None),
                error_type_key="module_not_found",
                full_source=self.source,
            )
    
    def execute_inline_assembly(self, node):
        """Execute inline assembly block.
        
        Note: Inline assembly is primarily supported in compiled mode.
        In interpreter mode, we skip execution with a warning (printed once).
        
        For limited interpreter support of hardcoded x86 instructions,
        use the execute_asm() stdlib function from nlpl.stdlib.asm
        """
        # Print warning once
        if not hasattr(self, '_inline_asm_warned'):
            print("Warning: Inline assembly is only fully supported in compiled mode.")
            print("         Assembly blocks are skipped in interpreter mode.")
            print("         Compile with 'nlplc' to generate actual inline assembly.")
            self._inline_asm_warned = True
        
        # Skip execution - inline assembly requires compiled native code
        return None
            
    def execute_print_statement(self, node):
        """Execute a print statement with optional type conversion."""
        value = self.execute(node.expression)
        
        # Apply type conversion if hint is provided
        if node.print_type == "text":
            value = str(value)
        elif node.print_type == "number":
            try:
                if isinstance(value, str):
                    if "." in value:
                        value = float(value)
                    else:
                        value = int(value)
                else:
                    value = float(value)
            except (ValueError, TypeError):
                # Fallback or error if conversion fails
                pass
                
        self.runtime.print(value)
        return value

    # Expression execution methods
    
    def execute_type_cast_expression(self, node):
        """Execute a type cast expression."""
        value = self.execute(node.expression)
        target = node.target_type.lower()
        
        if target == "string":
            return str(value)
        elif target == "integer":
            if isinstance(value, str):
                if "." in value:
                    return int(float(value))
                return int(value)
            return int(value)
        elif target == "float":
            return float(value)
        elif target == "uppercase":
            if isinstance(value, str):
                return value.upper()
            return str(value).upper()
        elif target == "lowercase":
            if isinstance(value, str):
                return value.lower()
            return str(value).lower()
        
        return value

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
            supported = ['+', '-', '*', '/', '//', '%', '**', '==', '!=', '<', '>', '<=', '>=', 
                       'and', 'or', 'in', 'not in', 'is', 'is not', '&', '|', '^', '<<', '>>']
            raise NLPLTypeError(
                f"Unsupported binary operator: '{node.operator}'.\n"
                f"  Supported operators: {', '.join(supported)}\n"
                f"  This is a language limitation - operator '{node.operator}' is not available.",
                error_type_key="invalid_operation",
                full_source=self.source,
            )
    
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
            supported = ['not', '-', '+', '~', 'address of', 'dereference']
            raise NLPLTypeError(
                f"Unsupported unary operator: '{node.operator}'.\n"
                f"  Supported operators: {', '.join(supported)}\n"
                f"  This is a language limitation - operator '{node.operator}' is not available.",
                error_type_key="invalid_operation",
                full_source=self.source,
            )
            
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
    
    def execute_lambda_expression(self, node):
        """Execute a lambda expression, creating a closure."""
        # Create a closure that captures the current scope
        captured_scope = dict(self.current_scope[-1])  # Copy current scope
        
        # Store lambda metadata
        lambda_func = {
            'type': 'lambda',
            'parameters': node.parameters,
            'body': node.body,
            'return_type': node.return_type,
            'captured_scope': captured_scope,
            'interpreter': self  # Reference to interpreter for execution
        }
        
        return lambda_func
    
    def _create_closure(self, lambda_node):
        """Create a Python callable closure from a lambda/block AST node.
        
        This wraps the lambda/block execution in a proper Python callable
        that can be passed as an argument and called later.
        
        Args:
            lambda_node: LambdaExpression AST node representing the block
            
        Returns:
            Python callable that executes the block when called
        """
        # Capture current scope
        captured_scope = dict(self.current_scope[-1]) if self.current_scope else {}
        
        def closure(*args):
            """Closure that executes the block with the given arguments."""
            # Enter new scope with captured variables
            self.enter_scope()
            
            # Restore captured scope
            for var, val in captured_scope.items():
                self.set_variable(var, val)
            
            # Bind block parameters to arguments
            for i, param in enumerate(lambda_node.parameters):
                if i < len(args):
                    self.set_variable(param.name, args[i])
            
            # Execute block body
            result = None
            try:
                for stmt in lambda_node.body:
                    result = self.execute(stmt)
            except ReturnException as ret:
                # Block used explicit return
                result = ret.value
            finally:
                self.exit_scope()
            
            return result
        
        return closure
    
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
    
    def execute_list_comprehension(self, node):
        """Execute a list comprehension."""
        # Syntax: [expr for var in iterable if condition]
        result = []
        iterable = self.execute(node.iterable)
        
        # Save current scope
        old_scope = self.current_scope.copy()
        
        for item in iterable:
            # Set loop variable
            self.set_variable(node.target.name, item)
            
            # Check condition if present
            if node.condition is None or self.execute(node.condition):
                # Evaluate expression and add to result
                value = self.execute(node.expr)
                result.append(value)
        
        # Restore scope (remove loop variable)
        self.current_scope = old_scope
        
        return result
    
    def execute_dict_comprehension(self, node):
        """Execute a dictionary comprehension."""
        # Syntax: {key: value for var in iterable if condition}
        result = {}
        iterable = self.execute(node.iterable)
        
        # Save current scope
        old_scope = self.current_scope.copy()
        
        for item in iterable:
            # Set loop variable
            self.set_variable(node.target.name, item)
            
            # Check condition if present
            if node.condition is None or self.execute(node.condition):
                # Evaluate key and value expressions
                key = self.execute(node.key)
                value = self.execute(node.value)
                result[key] = value
        
        # Restore scope (remove loop variable)
        self.current_scope = old_scope
        
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
                column=getattr(node, 'column', None),
                nlpl_type="IndexError",
                error_type_key="index_out_of_range",
                full_source=self.source
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
                    source_line=getattr(node, 'source_line', None),
                    error_type_key="undefined_variable",
                    full_source=self.source
                )
            raise NLPLRuntimeError(
                message=f"Key '{index}' not found",
                line=getattr(node, 'line', None),
                column=getattr(node, 'column', None),
                nlpl_type="IndexError",
                error_type_key="key_not_found",
                full_source=self.source
            )
        except TypeError as e:
            raise NLPLTypeError(
                message=f"Cannot use index on type {type(array).__name__}",
                expected_type="list, dict, or string",
                got_type=type(array).__name__,
                line=getattr(node, 'line', None),
                column=getattr(node, 'column', None),
                error_type_key="invalid_operation",
                full_source=self.source,
            )

    def execute_slice_expression(self, node):
        """Execute a slice expression (e.g., s[0:5] or s[1:10:2])."""
        seq = self.execute(node.expr)
        start = self.execute(node.start) if node.start is not None else None
        end = self.execute(node.end) if node.end is not None else None
        step = self.execute(node.step) if node.step is not None else None
        try:
            return seq[slice(start, end, step)]
        except (TypeError, AttributeError) as e:
            raise NLPLRuntimeError(
                message=f"Cannot slice value of type {type(seq).__name__}",
                line=getattr(node, 'line', None),
                column=getattr(node, 'column', None),
                nlpl_type="TypeError",
                error_type_key="invalid_operation",
                full_source=self.source,
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
        """Execute a function call with positional and/or named arguments.
        
        Supports both:
        - Direct function calls: add with 5 and 10
        - Named arguments: add with x: 5 and y: 10
        - Mixed arguments: add with 5 and y: 10
        - Module function calls: module.function with args
        - Callable values: (function stored in variable or passed as argument)
        - Trailing blocks: func do ... end
        """
        function_name = node.name
        
        # Evaluate positional arguments
        positional_args = [self.execute(arg) for arg in node.arguments]
        
        # Evaluate named arguments
        named_args = {}
        if hasattr(node, 'named_arguments') and node.named_arguments:
            # Defensive: ensure named_arguments is a dict
            if isinstance(node.named_arguments, dict):
                for param_name, arg_expr in node.named_arguments.items():
                    named_args[param_name] = self.execute(arg_expr)
        
        # Handle trailing block - create closure and add as last positional argument
        if hasattr(node, 'trailing_block') and node.trailing_block:
            block_closure = self._create_closure(node.trailing_block)
            positional_args.append(block_closure)
        
        # If function_name is already a callable (function value), call it directly
        if callable(function_name):
            # Python functions - pass positional and kwargs
            return function_name(*positional_args, **named_args)
        
        # Handle expressions that evaluate to callables (e.g., function pointers)
        # Check if function_name is actually an expression node
        if not isinstance(function_name, str):
            # It's an expression - evaluate it to get the callable
            func_value = self.execute(function_name)
            if callable(func_value):
                return func_value(*positional_args, **named_args)
            else:
                raise NLPLTypeError(
                    f"Cannot call non-function value: {type(func_value).__name__}",
                    error_type_key="function_call_error",
                    full_source=self.source,
                )
        
        # Check if function_name is a variable holding a callable (e.g., closure, function reference)
        # This enables: block() where block is a variable containing a closure
        # Use get_variable_or_none to avoid expensive NLPLNameError + difflib on every miss;
        # the name-not-found case is normal here (most calls go to functions, not variables).
        _var_value = self.get_variable_or_none(function_name)
        if _var_value is not None and callable(_var_value):
            return _var_value(*positional_args, **named_args)
        # If _var_value is not None but not callable, fall through (e.g. int stored under same name)
        
        # Handle module.function calls (function_name contains a dot)
        if '.' in function_name:
            parts = function_name.split('.')
            if len(parts) == 2:
                module_name, member_name = parts
                # Use get_variable_or_none: module might not be a local variable at all
                # (e.g. it could be a runtime-registered module name) — no error construction on miss.
                module = self.get_variable_or_none(module_name)
                if module is not None:
                    if hasattr(module, member_name):
                        func = getattr(module, member_name)
                        if callable(func):
                            return func(*positional_args, **named_args)
                        else:
                            raise NLPLTypeError(
                                f"{module_name}.{member_name} is not callable",
                                error_type_key="function_call_error",
                                full_source=self.source,
                            )
                    else:
                        raise AttributeError(f"Module '{module_name}' has no attribute '{member_name}'")
        
        # Check for built-in functions in the runtime
        if function_name in self.runtime.functions:
            import inspect
            func = self.runtime.functions[function_name]
            sig = inspect.signature(func)
            params = list(sig.parameters.keys())
            
            # Check if first parameter is 'runtime' - if so, inject it
            if params and params[0] == 'runtime':
                positional_args = [self.runtime] + list(positional_args)
            
            # For runtime functions, we need to handle named args manually
            # since most Python stdlib functions don't accept them by name
            if named_args:
                # Try calling with kwargs first
                try:
                    return func(*positional_args, **named_args)
                except TypeError:
                    # Fall back to positional-only if kwargs not supported
                    # This is for backward compatibility with existing functions
                    all_args = list(positional_args) + list(named_args.values())
                    return func(*all_args)
            else:
                return func(*positional_args)
        
        # Check for user-defined functions
        if function_name in self.functions:
            function_def = self.functions[function_name]
            
            # Combine positional and named arguments
            args = self._resolve_function_arguments(
                function_def, 
                positional_args, 
                named_args,
                function_name
            )
            
            # Debugger hook: trace function call
            if self.debugger:
                local_vars = {param.name: args[i] if i < len(args) else None 
                             for i, param in enumerate(function_def.parameters)}
                self.debugger.trace_call(
                    function_name,
                    getattr(function_def, 'file', self.current_file or '<unknown>'),
                    getattr(function_def, 'line', self.current_line or 0),
                    local_vars
                )
            
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
            try:
                for statement in function_def.body:
                    result = self.execute(statement)
            except ReturnException as ret:
                # Properly capture the return value
                result = ret.value
            finally:
                # Debugger hook: trace function return
                if self.debugger:
                    self.debugger.trace_return(function_name, result)
                
                # Always clean up the function scope
                self.exit_scope()
            
            return result
        
        # Try to get it as a variable (might be a function value stored after definition)
        # Use get_variable_or_none to avoid NLPLNameError + difflib construction on miss.
        _func_value = self.get_variable_or_none(function_name)
        if _func_value is not None and callable(_func_value):
            return _func_value(*positional_args, **named_args)
        
        raise NLPLNameError(
            name=function_name,
            available_names=list(self.functions.keys()) + list(self.runtime.functions.keys()),
            error_type_key="undefined_function",
            full_source=self.source,
        )
    
    def _resolve_function_arguments(self, function_def, positional_args, named_args, function_name):
        """Resolve positional and named arguments into a single argument list.
        
        Handles:
        - Positional arguments
        - Named arguments (param: value)
        - Default parameter values
        - Variadic parameters (*args)
        - Keyword-only parameters (after * separator)
        
        Args:
            function_def: FunctionDefinition AST node
            positional_args: List of positional argument values
            named_args: Dict of parameter_name -> value
            function_name: Name of function (for error messages)
            
        Returns:
            List of argument values in parameter order
        """
        params = function_def.parameters
        
        # Find variadic parameter and keyword-only parameters
        variadic_param_index = None
        first_keyword_only_index = None
        for i, param in enumerate(params):
            if hasattr(param, 'is_variadic') and param.is_variadic:
                variadic_param_index = i
            if hasattr(param, 'keyword_only') and param.keyword_only and first_keyword_only_index is None:
                first_keyword_only_index = i
        
        # Validate positional args don't fill keyword-only parameters
        if first_keyword_only_index is not None and len(positional_args) > first_keyword_only_index:
            # Count how many non-variadic positional params before keyword-only
            non_kw_count = first_keyword_only_index
            raise NLPLTypeError(
                f"Function '{function_name}' takes at most {non_kw_count} positional arguments "
                f"but {len(positional_args)} were given. Parameters after '*' must be passed by name.",
                error_type_key="wrong_argument_count",
                full_source=self.source,
            )
        
        resolved_args = [None] * len(params)
        
        # Fill in positional arguments first
        if variadic_param_index is not None:
            # If there's a variadic parameter, collect excess args into it
            for i, arg in enumerate(positional_args):
                if i < variadic_param_index:
                    # Regular parameter
                    resolved_args[i] = arg
                elif i == variadic_param_index:
                    # Start of variadic args - collect all remaining into a list
                    resolved_args[i] = positional_args[i:]
                    break
        else:
            # No variadic parameter - strict argument count
            for i, arg in enumerate(positional_args):
                if i >= len(params):
                    raise NLPLTypeError(
                        f"Function '{function_name}' takes {len(params)} parameters but {len(positional_args)} positional arguments were given",
                        error_type_key="wrong_argument_count",
                        full_source=self.source,
                    )
                # Check if this parameter is keyword-only
                if hasattr(params[i], 'keyword_only') and params[i].keyword_only:
                    raise NLPLTypeError(
                        f"Parameter '{params[i].name}' is keyword-only and cannot be passed positionally in '{function_name}'",
                        error_type_key="wrong_argument_count",
                        full_source=self.source,
                    )
                resolved_args[i] = arg
        
        # Fill in named arguments
        for param_name, value in named_args.items():
            # Find parameter index by name
            param_index = None
            for i, param in enumerate(params):
                if param.name == param_name:
                    param_index = i
                    break
            
            if param_index is None:
                raise NLPLTypeError(
                    f"Function '{function_name}' has no parameter named '{param_name}'",
                    error_type_key="wrong_argument_count",
                    full_source=self.source,
                )
            
            # Check if this parameter was already filled by positional arg
            if resolved_args[param_index] is not None:
                raise NLPLTypeError(
                    f"Function '{function_name}' got multiple values for parameter '{param_name}'",
                    error_type_key="wrong_argument_count",
                    full_source=self.source,
                )
            
            resolved_args[param_index] = value
        
        # Check that all keyword-only parameters without defaults were provided
        for i, param in enumerate(params):
            if hasattr(param, 'keyword_only') and param.keyword_only:
                if resolved_args[i] is None and not (hasattr(param, 'default_value') and param.default_value is not None):
                    raise NLPLTypeError(
                        f"Missing required keyword-only parameter '{param.name}' in call to '{function_name}'",
                        error_type_key="wrong_argument_count",
                        full_source=self.source,
                    )
        
        # Fill in default values for missing parameters
        for i, (arg, param) in enumerate(zip(resolved_args, params)):
            if arg is None:
                # Check if this is a variadic parameter
                if hasattr(param, 'is_variadic') and param.is_variadic:
                    # Variadic parameter with no args gets empty list
                    resolved_args[i] = []
                # Check if parameter has a default value
                elif hasattr(param, 'default_value') and param.default_value is not None:
                    # Execute the default value expression to get the actual value
                    resolved_args[i] = self.execute(param.default_value)
                # If no default and no value, it remains None (which will cause an error later)
        
        return resolved_args
        
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
                column=getattr(node, 'column', None),
                error_type_key="type_mismatch",
                full_source=self.source,
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
            raise NLPLRuntimeError(
                f"Unknown struct/union type: {struct_name}",
                line=getattr(node, 'line', None),
                error_type_key="undefined_class",
                full_source=self.source
            )
        
        struct_def = self.classes[struct_name]
        
        if field_name not in struct_def.fields:
            raise NLPLRuntimeError(
                f"Field '{field_name}' not found in {struct_name}",
                line=getattr(node, 'line', None),
                error_type_key="undefined_attribute",
                full_source=self.source
            )
            
        return struct_def.fields[field_name].offset
    
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
        # Handle built-in types
        if class_name == "List" or class_name.startswith("List ") or class_name.startswith("List<"):
            return []
        elif class_name == "Dictionary" or class_name.startswith("Dictionary ") or class_name.startswith("Map ") or class_name.startswith("Map<"):
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
            from ..errors import NLPLNameError
            raise NLPLNameError(
                name=class_name,
                line=node.line_number,
                available_names=list(self.classes.keys()),
                error_type_key="undefined_class",
                full_source=self.source
            )
            
        # Handle Generics: Check if this is a generic class instantiation
        # Node has type_arguments: Box<Integer> -> type_arguments=['Integer']
        type_args_map = {}
        if hasattr(node, 'type_arguments') and node.type_arguments:
            from ..errors import NLPLTypeError
            if not hasattr(class_def, 'generic_parameters') or not class_def.generic_parameters:
                raise NLPLTypeError(
                    f"Class '{class_name}' is not generic but was given type arguments",
                    line=getattr(node, 'line', None),
                    column=getattr(node, 'column', None),
                    error_type_key="invalid_generic_args",
                    full_source=self.source
                )
            
            if len(node.type_arguments) != len(class_def.generic_parameters):
                raise NLPLTypeError(
                    f"Class '{class_name}' expects {len(class_def.generic_parameters)} type arguments, got {len(node.type_arguments)}",
                    line=getattr(node, 'line', None),
                    column=getattr(node, 'column', None),
                    error_type_key="invalid_generic_args",
                    full_source=self.source
                )
            
            # Map parameters T to arguments Integer
            # class_def.generic_parameters is a list of TypeParameter nodes OR strings
            # node.type_arguments is a list of type names or Type nodes (depending on parser)
            
            for param, arg in zip(class_def.generic_parameters, node.type_arguments):
                # Param could be a TypeParameter node with .name, or just a string
                if hasattr(param, 'name'):
                    param_name = param.name
                else:
                    param_name = str(param)
                
                # Arg could be different depending on parser version. 
                # Assuming simple strings for now based on current test.
                # If complex type, it might be a node.
                if hasattr(arg, 'name'):
                    arg_name = arg.name
                else:
                    arg_name = str(arg)
                    
                type_args_map[param_name] = arg_name

        # Handle Structs and Unions
        if isinstance(class_def, (RuntimeStructDefinition, RuntimeUnionDefinition)):
            instance = StructureInstance(class_def)
            
            # Auto-initialize nested struct fields
            if isinstance(class_def, RuntimeStructDefinition) and hasattr(class_def, '_original_fields'):
                for field_name, type_name in class_def._original_fields:
                    # Check if this field type is another struct
                    if type_name in self.classes and isinstance(self.classes[type_name], RuntimeStructDefinition):
                        # Create nested struct instance
                        nested_instance = StructureInstance(self.classes[type_name])
                        # Set it as the field value
                        instance.set_field(field_name, nested_instance)
            
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
            
        # Handle runtime.Object instances (official objects)
        from ..runtime.runtime import Object
        if isinstance(obj, Object):
            if node.is_method_call:
                # Method call
                if member_name in obj.methods:
                    method_def = obj.methods[member_name]
                    
                    # Enter new scope for method execution
                    self.enter_scope()
                    
                    try:
                        # Bind instance to 'self'
                        self.set_variable("self", obj)

                        # Bind instance properties to scope (implicit self)
                        for key, value in obj.properties.items():
                            self.set_variable(key, value)
                        
                        # Bind method parameters
                        if hasattr(method_def, 'parameters') and method_def.parameters:
                            # Evaluate arguments
                            args = [self.execute(arg) for arg in node.arguments] if hasattr(node, 'arguments') and node.arguments else []
                            
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
                                if isinstance(statement, ReturnStatement):
                                    break
                        
                        # Update instance properties from scope
                        for key in obj.properties.keys():
                            try:
                                obj.set_property(key, self.get_variable(key))
                            except:
                                pass
                        
                        return result
                    finally:
                        self.exit_scope()
                else:
                    # Try to see if it's a property that is a callable
                    if member_name in obj.properties:
                        prop = obj.get_property(member_name)
                        if callable(prop):
                            args = [self.execute(arg) for arg in node.arguments] if hasattr(node, 'arguments') and node.arguments else []
                            return prop(*args)
                    
                    raise NLPLNameError(
                        message=f"Object of type '{obj.class_name}' has no method '{member_name}'",
                        name=member_name,
                        line=getattr(node, 'line', None),
                        error_type_key="undefined_function",
                        full_source=self.source
                    )
            else:
                # Property access
                try:
                    return obj.get_property(member_name)
                except AttributeError:
                    raise NLPLNameError(
                        message=f"Object of type '{obj.class_name}' has no property '{member_name}'",
                        name=member_name,
                        line=getattr(node, 'line', None),
                        error_type_key="undefined_attribute",
                        full_source=self.source
                    )

        # Handle dict-based objects (legacy/fallback)
        if isinstance(obj, dict):
            if node.is_method_call:
                # Evaluate arguments once for reuse below
                args = [self.execute(arg) for arg in node.arguments] if hasattr(node, 'arguments') and node.arguments else []

                # ── Native Python dict operations ────────────────────────────
                # These are mapped from natural NLPL method names so that
                # keywords like 'has', 'set', 'add', 'contains', 'insert',
                # 'update' work correctly as method calls on dict objects.
                if member_name == 'has' or member_name == 'contains':
                    # dict.has(key)  /  dict.contains(key) → key in dict
                    if not args:
                        raise NLPLRuntimeError("has() requires a key argument",
                                               line=getattr(node, 'line', None), full_source=self.source)
                    return args[0] in obj

                elif member_name == 'get':
                    # dict.get(key)  /  dict.get(key, default)
                    if not args:
                        raise NLPLRuntimeError("get() requires a key argument",
                                               line=getattr(node, 'line', None), full_source=self.source)
                    return obj.get(args[0], args[1] if len(args) > 1 else None)

                elif member_name == 'set' or member_name == 'insert' or member_name == 'put':
                    # dict.set(key, value)  /  dict.insert(key, value)  /  dict.put(key, value)
                    if len(args) < 2:
                        raise NLPLRuntimeError(f"{member_name}() requires key and value arguments",
                                               line=getattr(node, 'line', None), full_source=self.source)
                    obj[args[0]] = args[1]
                    return None

                elif member_name == 'remove' or member_name == 'delete':
                    # dict.remove(key)  /  dict.delete(key)
                    if not args:
                        raise NLPLRuntimeError("remove() requires a key argument",
                                               line=getattr(node, 'line', None), full_source=self.source)
                    obj.pop(args[0], None)
                    return None

                elif member_name == 'pop':
                    # dict.pop(key)  /  dict.pop(key, default)
                    if not args:
                        raise NLPLRuntimeError("pop() requires a key argument",
                                               line=getattr(node, 'line', None), full_source=self.source)
                    return obj.pop(args[0]) if len(args) == 1 else obj.pop(args[0], args[1])

                elif member_name == 'keys':
                    return list(obj.keys())

                elif member_name == 'values':
                    return list(obj.values())

                elif member_name == 'items':
                    return list(obj.items())

                elif member_name == 'update' or member_name == 'merge':
                    # dict.update(other_dict)
                    if args and isinstance(args[0], dict):
                        obj.update(args[0])
                    return None

                elif member_name == 'clear':
                    obj.clear()
                    return None

                elif member_name == 'copy':
                    return dict(obj)

                elif member_name == 'size' or member_name == 'length':
                    return len(obj)

                elif member_name == 'is_empty':
                    return len(obj) == 0

                # ── User-defined methods via __method_*__ ────────────────────
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
                    raise NLPLRuntimeError(
                        f"Unknown method: {member_name}",
                        line=getattr(node, 'line', None),
                        error_type_key="undefined_function",
                        full_source=self.source
                    )
            else:
                # Property/field access
                if member_name in obj:
                    return obj[member_name]
                else:
                    raise NLPLRuntimeError(
                        f"Unknown field: {member_name}",
                        line=getattr(node, 'line', None),
                        error_type_key="undefined_attribute",
                        full_source=self.source
                    )
        
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
            raise NLPLRuntimeError(
                f"Object has no member: {member_name}",
                line=getattr(node, 'line', None),
                error_type_key="undefined_attribute",
                full_source=self.source
            )
    
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
            
        raise NLPLRuntimeError(
            f"Cannot assign to member '{member_name}' on object of type {type(target_obj)}",
            line=getattr(node, 'line', None),
            error_type_key="invalid_operation",
            full_source=self.source
        )
    
    def execute_generic_type_instantiation(self, node):
        """
        Execute generic type instantiation.
        Syntax: create list of Integer, create dict of String to Integer
        
        Creates typed collections using the GenericTypeRegistry.
        """
        from collections import deque
        
        generic_name = node.generic_name.lower()
        type_args = node.type_args
        
        # Create typed Python collections based on generic name
        # Integrates with GenericTypeRegistry for type checking
        
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
        
        elif generic_name in ("dict", "dictionary", "map"):
            # Create a dictionary/map
            if node.initial_value:
                initial = self.execute(node.initial_value)
                if isinstance(initial, dict):
                    return initial.copy()
                else:
                    raise NLPLTypeError(
                        "Dictionary initial value must be a dictionary",
                        error_type_key="type_mismatch",
                        full_source=self.source,
                    )
            else:
                return {}
        
        elif generic_name == "set":
            # Create a set with optional initial values
            if node.initial_value:
                initial = self.execute(node.initial_value)
                if isinstance(initial, (list, tuple, set)):
                    return set(initial)
                else:
                    return {initial}
            else:
                return set()
        
        elif generic_name == "queue":
            # Create a queue (deque) with optional initial values
            if node.initial_value:
                initial = self.execute(node.initial_value)
                if isinstance(initial, (list, tuple)):
                    return deque(initial)
                else:
                    return deque([initial])
            else:
                return deque()
        
        elif generic_name == "stack":
            # Create a stack (list used as stack) with optional initial values
            if node.initial_value:
                initial = self.execute(node.initial_value)
                if isinstance(initial, (list, tuple)):
                    return list(initial)
                else:
                    return [initial]
            else:
                return []
        
        elif generic_name == "tuple":
            # Create an immutable tuple
            if node.initial_value:
                initial = self.execute(node.initial_value)
                if isinstance(initial, (list, tuple)):
                    return tuple(initial)
                else:
                    return (initial,)
            else:
                return ()
        
        elif generic_name == "optional":
            # Create an Optional value (can be None or a value)
            if node.initial_value:
                return self.execute(node.initial_value)
            else:
                return None
        
        else:
            # Unknown generic type - provide helpful error message
            supported = ["List", "Dict", "Set", "Queue", "Stack", "Tuple", "Optional", "Map"]
            raise NLPLTypeError(
                f"Unsupported generic type: '{generic_name}'.\n"
                f"  Supported generic types: {', '.join(supported)}\n"
                f"  Note: This is a language limitation, not incomplete implementation.",
                line=getattr(node, 'line', None),
                error_type_key="invalid_generic_args",
                full_source=self.source
            )

    def execute_TryExpression(self, node):
        """Execute ? operator for error propagation."""
        from ..stdlib.option_result import Result
        
        result = self.execute(node.expression)
        
        if not isinstance(result, Result):
            raise NLPLRuntimeError(
                f'? operator requires Result type, got {type(result).__name__}',
                line=getattr(node, 'line', None),
                error_type_key="type_mismatch",
                full_source=self.source
            )
        
        if result.is_ok():
            return result.unwrap()
        else:
            self.return_value = result
            return None
    
    def execute_macro_definition(self, node):
        """Execute a macro definition - store it in registry."""
        self.macros[node.name] = node
        return None
    
    def execute_macro_expansion(self, node):
        """Execute a macro expansion - substitute parameters and execute body."""
        # Get macro definition
        if node.name not in self.macros:
            raise NLPLRuntimeError(
                f"Undefined macro: {node.name}",
                line=node.line,
                error_type_key="undefined_function",
                full_source=self.source,
            )
        
        macro_def = self.macros[node.name]
        
        # Evaluate all argument expressions
        evaluated_args = {}
        for arg_name, arg_expr in node.arguments.items():
            evaluated_args[arg_name] = self.execute(arg_expr)
        
        # Create a new scope for macro expansion
        old_scope = self.current_scope.copy()
        
        # Bind macro parameters to argument values
        for i, param_name in enumerate(macro_def.parameters):
            if param_name in evaluated_args:
                self.set_variable(param_name, evaluated_args[param_name])
            else:
                raise NLPLRuntimeError(
                    f"Macro {node.name} missing argument: {param_name}",
                    line=node.line,
                    error_type_key="wrong_argument_count",
                    full_source=self.source,
                )
        
        # Execute macro body
        result = None
        for stmt in macro_def.body:
            result = self.execute(stmt)
        
        # Restore scope
        self.current_scope = old_scope
        
        return result

    # ------------------------------------------------------------------
    # Ownership / borrow execution methods
    # ------------------------------------------------------------------

    def execute_move_expression(self, node):
        """Execute 'move x' — transfer ownership, leaving source as MovedValue.

        After a move:
        - The moved-to binding holds the original value.
        - Accessing the source variable raises a 'use of moved value' error.

        Syntax:  set dest to move source
        """
        from ..stdlib.smart_pointers import MovedValue

        var_name = node.var_name
        # Check the variable is not currently borrowed
        borrow = self._borrow_tracker.get(var_name)
        if borrow and (borrow["immutable_count"] > 0 or borrow["is_mutable"]):
            kind = "mutably" if borrow["is_mutable"] else "immutably"
            raise NLPLRuntimeError(
                f"cannot move '{var_name}': it is currently borrowed {kind}; "
                f"call 'drop borrow {var_name}' before moving",
                line=getattr(node, 'line_number', None),
                error_type_key="runtime_error",
                full_source=self.source,
            )

        # Read the current value (will raise on MovedValue automatically)
        value = self.get_variable(var_name)

        # Invalidate the source by replacing with a MovedValue sentinel
        for scope in reversed(self.current_scope):
            if var_name in scope:
                scope[var_name] = MovedValue(var_name)
                break

        return value

    def execute_borrow_expression(self, node):
        """Execute 'borrow x' / 'borrow mutable x' — register a borrow.

        Immutable borrow:  multiple simultaneous immutable borrows are allowed;
                           the variable cannot be written while any borrow holds.
        Mutable borrow:    only one mutable borrow at a time;
                           no other borrow (immutable or mutable) may exist;
                           the variable cannot be written or read-borrowed while
                           the mutable borrow holds.

        Returns the current value of the variable (a snapshot, not a reference).

        Syntax:
            set b to borrow x
            set m to borrow mutable x
        """
        var_name = node.var_name
        mutable = node.mutable
        line = getattr(node, 'line_number', None)

        borrow = self._borrow_tracker.get(var_name, {"immutable_count": 0, "is_mutable": False})

        if mutable:
            # Mutable borrow: nothing else may be borrowed
            if borrow["immutable_count"] > 0:
                raise NLPLRuntimeError(
                    f"cannot borrow '{var_name}' as mutable: it is already borrowed "
                    f"immutably ({borrow['immutable_count']} active borrow(s))",
                    line=line,
                    error_type_key="runtime_error",
                    full_source=self.source,
                )
            if borrow["is_mutable"]:
                raise NLPLRuntimeError(
                    f"cannot borrow '{var_name}' as mutable: already mutably borrowed",
                    line=line,
                    error_type_key="runtime_error",
                    full_source=self.source,
                )
            self._borrow_tracker[var_name] = {"immutable_count": 0, "is_mutable": True}
        else:
            # Immutable borrow: not allowed if mutably borrowed
            if borrow["is_mutable"]:
                raise NLPLRuntimeError(
                    f"cannot borrow '{var_name}' immutably: it is already mutably borrowed",
                    line=line,
                    error_type_key="runtime_error",
                    full_source=self.source,
                )
            self._borrow_tracker[var_name] = {
                "immutable_count": borrow["immutable_count"] + 1,
                "is_mutable": False,
            }

        return self.get_variable(var_name)

    def execute_drop_borrow_statement(self, node):
        """Execute 'drop borrow x' / 'drop borrow mutable x' — release a borrow.

        Decrements the borrow count.  The variable becomes writable again once
        all borrows have been dropped.
        """
        var_name = node.var_name
        mutable = node.mutable
        line = getattr(node, 'line_number', None)

        borrow = self._borrow_tracker.get(var_name)

        if mutable:
            if not borrow or not borrow["is_mutable"]:
                raise NLPLRuntimeError(
                    f"no active mutable borrow of '{var_name}' to drop",
                    line=line,
                    error_type_key="runtime_error",
                    full_source=self.source,
                )
            self._borrow_tracker[var_name] = {"immutable_count": 0, "is_mutable": False}
        else:
            if not borrow or borrow["immutable_count"] <= 0:
                raise NLPLRuntimeError(
                    f"no active immutable borrow of '{var_name}' to drop",
                    line=line,
                    error_type_key="runtime_error",
                    full_source=self.source,
                )
            new_count = borrow["immutable_count"] - 1
            if new_count == 0 and not borrow["is_mutable"]:
                del self._borrow_tracker[var_name]
            else:
                self._borrow_tracker[var_name] = {"immutable_count": new_count, "is_mutable": borrow["is_mutable"]}

        return None

    def execute_borrow_expression_with_lifetime(self, node):
        """Execute a borrow expression that carries a lifetime annotation.

        At runtime the lifetime label is purely a static analysis artifact and
        has no effect on program execution.  This handler therefore delegates
        directly to the standard borrow logic, which enforces the runtime borrow
        rules (no double-mutable borrow, no borrow while moved, etc.).

        Syntax::

            set ref to borrow x with lifetime outer
            set mut_ref to borrow mutable y with lifetime inner
        """
        # Delegate to the standard borrow handler.  The BorrowExpressionWithLifetime
        # node has the same var_name / mutable attributes, so it is duck-type
        # compatible here.
        return self.execute_borrow_expression(node)

    # ------------------------------------------------------------------
    # Smart pointer execution methods
    # ------------------------------------------------------------------

    def execute_rc_creation(self, node):
        """Execute Rc/Arc/Weak creation.

        Syntax (NLPL):
            set ptr to Rc of Integer with 42
            set shared to Arc of String with "hello"
            set w to Weak of Integer with 0   # rarely used directly; prefer downgrade
        """
        from ..stdlib.smart_pointers import RcValue, ArcValue, WeakValue

        value = self.execute(node.value) if node.value is not None else None
        kind = getattr(node, 'rc_kind', 'rc')

        if kind == 'rc':
            return RcValue(value)
        elif kind == 'arc':
            return ArcValue(value)
        elif kind == 'weak':
            # A standalone Weak creation wraps a freshly-allocated inner that
            # immediately has strong_count=0 (the Weak is the only reference).
            # The idiomatic way to create a Weak is via 'downgrade ptr', not
            # via 'Weak of T with val'.  Support the literal form anyway.
            rc_temp = RcValue(value)   # strong=1
            weak = rc_temp.downgrade() # weak=1
            rc_temp.drop()             # strong -> 0 (data kept alive by weak ref)
            return weak
        else:
            raise NLPLRuntimeError(
                f"Unknown smart pointer kind: {kind!r}",
                line=getattr(node, 'line_number', None),
                error_type_key="internal_error",
                full_source=self.source,
            )

    def execute_downgrade_expression(self, node):
        """Execute 'downgrade rc_value' — convert Rc<T>/Arc<T> to Weak<T>."""
        from ..stdlib.smart_pointers import RcValue, ArcValue

        rc = self.execute(node.rc_expr)
        if isinstance(rc, (RcValue, ArcValue)):
            return rc.downgrade()
        raise NLPLRuntimeError(
            f"downgrade requires an Rc or Arc value, got {type(rc).__name__}",
            line=getattr(node, 'line_number', None),
            error_type_key="type_error",
            full_source=self.source,
        )

    def execute_upgrade_expression(self, node):
        """Execute 'upgrade weak_value' — attempt to recover a strong Rc/Arc.

        Returns the Rc/Arc value on success, or None if the data has been
        dropped (all strong counts reached zero).
        """
        from ..stdlib.smart_pointers import WeakValue

        weak = self.execute(node.weak_expr)
        if isinstance(weak, WeakValue):
            return weak.upgrade()   # returns RcValue / ArcValue or None
        raise NLPLRuntimeError(
            f"upgrade requires a Weak value, got {type(weak).__name__}",
            line=getattr(node, 'line_number', None),
            error_type_key="type_error",
            full_source=self.source,
        )

