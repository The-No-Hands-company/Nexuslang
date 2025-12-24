"""
C Code Generator for NLPL
==========================

Generates C code from NLPL AST for compilation to native executables.

Strategy:
- NLPL variables → C variables
- NLPL functions → C functions
- NLPL classes → C structs + function pointers
- Memory management → malloc/free (with RAII wrappers)
- Standard library → Link against NLPL C runtime library
"""

from typing import Any, Dict, List
from nlpl.compiler import CodeGenerator
from nlpl.parser.ast import *


class CCodeGenerator(CodeGenerator):
    """Generate C code from NLPL AST."""
    
    def __init__(self, target: str):
        super().__init__(target)
        self.includes = set()
        self.forward_declarations = []
        self.global_variables = {}
        self.functions = {}
        self.symbol_table = {}  # Track variable types for type inference
        self.function_types = {}  # Track function return types
        self.current_class = None  # Track current class being processed
        self.class_properties = {}  # Map class_name -> set of property names
        self.property_types = {}  # Map (class_name, property_name) -> C type
        
    def generate(self, ast: Program) -> str:
        """Generate complete C program from AST."""
        self.reset()
        
        # Add default required includes
        self.includes.add("<stdio.h>")
        self.includes.add("<stdlib.h>")
        self.includes.add("<string.h>")
        self.includes.add("<stdbool.h>")
        
        # Generate program statements (this will add more includes as needed)
        # First pass: collect classes, globals and function definitions
        for stmt in ast.statements:
            if isinstance(stmt, ClassDefinition):
                self._generate_class_definition(stmt)
            elif isinstance(stmt, FunctionDefinition):
                self._generate_function_declaration(stmt)
            elif isinstance(stmt, ExternFunctionDeclaration):
                self._generate_extern_function(stmt)
            elif isinstance(stmt, ExternVariableDeclaration):
                # TODO: Handle global extern variables
                pass
        
        # Check if user defined a main function
        has_user_main = any(isinstance(stmt, FunctionDefinition) and stmt.name == "main" for stmt in ast.statements)
        
        if not has_user_main:
            # Generate default main function for top-level statements
            self.emit_raw("int main(int argc, char** argv) {")
            self.indent()
        
            # Generate top-level statements
            for stmt in ast.statements:
                if not isinstance(stmt, (FunctionDefinition, ClassDefinition)):
                    self._generate_statement(stmt)
            
            self.emit("return 0;")
            self.dedent()
            self.emit_raw("}")
        else:
            # User defined main, just emit top-level statements (global init) if needed
            # For now, warn if there are regular statements outside functions
            # In a real compiler, we might put these in an _init function called by start
            pass
        
        # Now prepend header and includes to the generated code
        header_lines = [
            "/*",
            " * Generated C code from NLPL",
            " * DO NOT EDIT - This file is auto-generated",
            " */",
            "",
        ]
        
        # Add includes
        for include in sorted(self.includes):
            header_lines.append(f"#include {include}")
        header_lines.append("")
        
        # Add forward declarations if any
        if self.forward_declarations:
            header_lines.extend(self.forward_declarations)
            header_lines.append("")
        
        # Prepend header to output buffer
        self.output_buffer = header_lines + self.output_buffer
        
        return self.get_output()
    
    def _generate_function_declaration(self, node: FunctionDefinition) -> None:
        """Generate function declaration."""
        # Determine return type
        if node.return_type:
            return_type = self._map_type(node.return_type)
        else:
            return_type = "void"
        
        # Track function return type for type inference
        self.function_types[node.name] = return_type
        
        # Generate parameter list
        if node.parameters:
            params = []
            for param in node.parameters:
                # Use explicit type annotation if provided
                if hasattr(param, 'type_annotation') and param.type_annotation:
                    param_type = self._map_type(param.type_annotation)
                else:
                    # Infer type from function body usage
                    param_type = self._infer_parameter_type(param.name, node.body, node.return_type)
                
                params.append(f"{param_type} {param.name}")
                # Add parameters to symbol table for type inference within function
                self.symbol_table[param.name] = param_type
            param_str = ", ".join(params)
        else:
            param_str = "void"
        
        # Function signature
        self.emit_raw(f"{return_type} {node.name}({param_str}) {{")
        self.indent()
        
        # Generate function body
        if node.body:
            for stmt in node.body:
                self._generate_statement(stmt)
        
        self.dedent()
        self.emit_raw("}")
        self.emit_raw("")
        
        # Clear function-local variables from symbol table
        # (Keep only global scope variables)
        if node.parameters:
            for param in node.parameters:
                if param.name in self.symbol_table:
                    del self.symbol_table[param.name]
    
    def _generate_class_definition(self, node: ClassDefinition) -> None:
        """Generate C struct and methods for a class definition."""
        class_name = node.name
        
        # Track properties for this class
        property_names = {prop.name for prop in node.properties}
        self.class_properties[class_name] = property_names
        
        # Generate struct definition
        self.emit_raw(f"// Class: {class_name}")
        if node.parent_classes:
            parent_name = node.parent_classes[0]  # Single inheritance only for now
            self.emit_raw(f"// Inherits from: {parent_name}")
        
        self.emit_raw(f"typedef struct {class_name} {{")
        self.indent()
        
        # If there's a parent, include it as first member for inheritance
        if node.parent_classes:
            parent_name = node.parent_classes[0]
            self.emit(f"{parent_name} parent;  // Inherited members")
        
        # Generate properties as struct members
        for prop in node.properties:
            if prop.type_annotation:
                c_type = self._map_type(prop.type_annotation)
            else:
                c_type = "void*"  # Default to generic pointer if no type specified
            
            # Track property type for type inference
            self.property_types[(class_name, prop.name)] = c_type
            
            self.emit(f"{c_type} {prop.name};")
        
        # Generate function pointers for methods
        for method in node.methods:
            # Determine return type
            if method.return_type:
                return_type = self._map_type(method.return_type)
            else:
                return_type = "void"
            
            # Generate method function pointer type
            # Methods get implicit 'this' pointer as first parameter
            param_types = [f"struct {class_name}*"]  # 'this' pointer
            
            if method.parameters:
                for param in method.parameters:
                    if hasattr(param, 'type_annotation') and param.type_annotation:
                        param_type = self._map_type(param.type_annotation)
                    else:
                        param_type = "void*"
                    param_types.append(param_type)
            
            params_str = ", ".join(param_types)
            self.emit(f"{return_type} (*{method.name})({params_str});")
        
        self.dedent()
        self.emit_raw(f"}} {class_name};")
        self.emit_raw("")
        
        # Generate method implementations
        for method in node.methods:
            self._generate_method_implementation(class_name, method)
        
        # Generate constructor function
        self._generate_constructor(class_name, node)
    
    def _generate_method_implementation(self, class_name: str, method: MethodDefinition) -> None:
        """Generate implementation for a class method."""
        # Determine return type
        if method.return_type:
            return_type = self._map_type(method.return_type)
        else:
            return_type = "void"
        
        # Generate parameters (with 'this' as first parameter)
        params = [f"{class_name}* this"]
        
        if method.parameters:
            for param in method.parameters:
                if hasattr(param, 'type_annotation') and param.type_annotation:
                    param_type = self._map_type(param.type_annotation)
                else:
                    param_type = "void*"
                params.append(f"{param_type} {param.name}")
                # Add to symbol table for method body
                self.symbol_table[param.name] = param_type
        
        params_str = ", ".join(params)
        
        # Method naming: ClassName_methodName
        method_c_name = f"{class_name}_{method.name}"
        
        self.emit_raw(f"{return_type} {method_c_name}({params_str}) {{")
        self.indent()
        
        # Set current class context for property access resolution
        self.current_class = class_name
        
        # Generate method body
        if method.body:
            for stmt in method.body:
                self._generate_statement(stmt)
        
        # Clear class context
        self.current_class = None
        
        self.dedent()
        self.emit_raw("}")
        self.emit_raw("")
        
        # Clear method parameters from symbol table
        if method.parameters:
            for param in method.parameters:
                if param.name in self.symbol_table:
                    del self.symbol_table[param.name]
    
    def _generate_constructor(self, class_name: str, node: ClassDefinition) -> None:
        """Generate constructor function for a class."""
        # stdlib.h is already included by default in generate()
        
        constructor_name = f"{class_name}_new"
        
        self.emit_raw(f"{class_name}* {constructor_name}() {{")
        self.indent()
        
        # Allocate memory for the object
        self.emit(f"{class_name}* obj = ({class_name}*)malloc(sizeof({class_name}));")
        
        # Initialize properties to zero/null
        for prop in node.properties:
            if prop.type_annotation:
                c_type = self._map_type(prop.type_annotation)
                if c_type == "int" or c_type == "double":
                    self.emit(f"obj->{prop.name} = 0;")
                elif c_type == "bool":
                    self.emit(f"obj->{prop.name} = false;")
                elif c_type == "const char*":
                    self.emit(f'obj->{prop.name} = "";')
                else:
                    self.emit(f"obj->{prop.name} = NULL;")
        
        # Bind methods to function pointers
        for method in node.methods:
            method_c_name = f"{class_name}_{method.name}"
            self.emit(f"obj->{method.name} = {method_c_name};")
        
        self.emit("return obj;")
        
        self.dedent()
        self.emit_raw("}")
        self.emit_raw("")
    
    def _generate_statement(self, node: Any) -> None:
        """Generate C code for a statement."""
        if isinstance(node, VariableDeclaration):
            self._generate_variable_declaration(node)
        elif isinstance(node, FunctionCall):
            expr = self._generate_expression(node)
            self.emit(f"{expr};")
        elif isinstance(node, FunctionDefinition):
            # Functions are generated separately, not inline
            # They should be handled at the top level
            pass
        elif isinstance(node, ExternFunctionDeclaration):
            self._generate_extern_function(node)
        elif isinstance(node, ReturnStatement):
            if node.value:
                expr = self._generate_expression(node.value)
                self.emit(f"return {expr};")
            else:
                self.emit("return;")
        elif isinstance(node, IfStatement):
            self._generate_if_statement(node)
        elif isinstance(node, WhileLoop):
            self._generate_while_loop(node)
        elif isinstance(node, ForLoop):
            self._generate_for_loop(node)
        elif isinstance(node, TryCatch):
            self._generate_try_catch(node)
        else:
            # Try to handle as expression
            try:
                expr = self._generate_expression(node)
                self.emit(f"{expr};")
            except:
                self.emit(f"/* Unhandled statement: {type(node).__name__} */")
    
    def _generate_variable_declaration(self, node: VariableDeclaration) -> None:
        """Generate variable declaration or assignment."""
        # Check if the "name" is actually a MemberAccess (object.property = value)
        if isinstance(node.name, MemberAccess):
            # This is an assignment to a member: object.property = value
            lhs = self._generate_expression(node.name)
            value_expr = self._generate_expression(node.value)
            self.emit(f"{lhs} = {value_expr};")
            return
        
        # Check if variable already exists in symbol table
        if node.name in self.symbol_table:
            # Variable exists - generate assignment only
            value_expr = self._generate_expression(node.value)
            self.emit(f"{node.name} = {value_expr};")
        else:
            # New variable - generate declaration with type
            value_expr = self._generate_expression(node.value)
            var_type = self._infer_type(node.value)
            
            # Store in symbol table
            self.symbol_table[node.name] = var_type
            
            # Handle array type declarations specially
            if "[]" in var_type:
                # Array type: extract base type and array dimensions
                # e.g., "int[][]" → base="int", dims="[][]"
                base_type = var_type
                dims = ""
                while base_type.endswith("[]"):
                    dims += "[]"
                    base_type = base_type[:-2]
                self.emit(f"{base_type} {node.name}{dims} = {value_expr};")
            else:
                # Regular type
                self.emit(f"{var_type} {node.name} = {value_expr};")
    
    def _infer_parameter_type(self, param_name: str, body: List[Any], return_type: Any = None) -> str:
        """
        Infer parameter type from how it's used in the function body.
        
        Strategy:
        1. Check arithmetic operations (plus, minus, etc.) → int or double
        2. Check string operations (concatenation, print) → const char*
        3. Check comparison operations → infer from context
        4. If used in return statement, match return type
        5. Default to int for numeric contexts
        """
        if not body:
            return "int"  # Default
        
        # Analyze all usages of the parameter
        usages = self._find_parameter_usages(param_name, body)
        
        for usage_type in usages:
            if usage_type == "arithmetic":
                # Used in arithmetic → numeric type
                # Default to int unless we have evidence of floating point
                return "int"
            elif usage_type == "string":
                # Used as string (print, concatenation)
                return "const char*"
            elif usage_type == "return":
                # Returned directly → match return type
                if return_type:
                    return self._map_type(return_type)
        
        # Default to int (most common for general parameters)
        return "int"
    
    def _find_parameter_usages(self, param_name: str, body: List[Any]) -> List[str]:
        """
        Find how a parameter is used in the function body.
        Returns list of usage types: 'arithmetic', 'string', 'return', etc.
        """
        usages = []
        
        for stmt in body:
            if isinstance(stmt, VariableDeclaration):
                # Check if parameter is in the value expression
                usages.extend(self._analyze_expression_for_param(param_name, stmt.value))
            elif isinstance(stmt, ReturnStatement):
                if isinstance(stmt.value, Identifier) and stmt.value.name == param_name:
                    usages.append("return")
                else:
                    usages.extend(self._analyze_expression_for_param(param_name, stmt.value))
            elif isinstance(stmt, FunctionCall):
                # Check standalone function calls (like print statements)
                usages.extend(self._analyze_expression_for_param(param_name, stmt))
        
        return usages
    
    def _analyze_expression_for_param(self, param_name: str, expr: Any) -> List[str]:
        """Analyze an expression to see how a parameter is used."""
        usages = []
        
        if expr is None:
            return usages
        
        if isinstance(expr, Identifier) and expr.name == param_name:
            # Found the parameter, but need context to determine type
            return ["unknown"]
        
        elif isinstance(expr, BinaryOperation):
            from ...parser.lexer import TokenType
            
            # Check operator type
            op_type = expr.operator.type if hasattr(expr.operator, 'type') else expr.operator
            
            # Arithmetic operators
            arithmetic_ops = {
                TokenType.PLUS, TokenType.MINUS, 
                TokenType.TIMES, TokenType.DIVIDED_BY
            }
            
            if op_type in arithmetic_ops:
                # Check if parameter is in this operation
                if self._expression_contains_param(param_name, expr.left) or \
                   self._expression_contains_param(param_name, expr.right):
                    usages.append("arithmetic")
            
            # Recursively check sub-expressions
            usages.extend(self._analyze_expression_for_param(param_name, expr.left))
            usages.extend(self._analyze_expression_for_param(param_name, expr.right))
        
        elif isinstance(expr, FunctionCall):
            # Check if parameter is passed to print → string
            if expr.name == "print" or expr.name == "printf":
                for arg in expr.arguments:
                    if isinstance(arg, Identifier) and arg.name == param_name:
                        usages.append("string")
        
        return usages
    
    def _expression_contains_param(self, param_name: str, expr: Any) -> bool:
        """Check if an expression contains a parameter."""
        if isinstance(expr, Identifier):
            return expr.name == param_name
        elif isinstance(expr, BinaryOperation):
            return (self._expression_contains_param(param_name, expr.left) or
                    self._expression_contains_param(param_name, expr.right))
        return False
    
    def _infer_type(self, expr: Any) -> str:
        """Infer C type from NLPL expression."""
        if isinstance(expr, Literal):
            if expr.type == "string":
                return "const char*"
            elif expr.type == "integer":
                return "int"
            elif expr.type == "float":
                return "double"
            elif expr.type == "boolean":
                return "bool"
            else:
                return "void*"
        
        elif isinstance(expr, BinaryOperation):
            # Infer from operands
            left_type = self._infer_type(expr.left)
            right_type = self._infer_type(expr.right)
            
            # If both are same numeric type, result is that type
            if left_type == right_type and left_type in ["int", "double"]:
                return left_type
            
            # If one is double and other is int, result is double
            if set([left_type, right_type]) == {"int", "double"}:
                return "double"
            
            # If both are int, result is int
            if left_type == "int" and right_type == "int":
                return "int"
            
            # Comparison operators return bool
            from ...parser.lexer import TokenType
            comparison_ops = {
                TokenType.EQUAL_TO, TokenType.NOT_EQUAL_TO,
                TokenType.LESS_THAN, TokenType.GREATER_THAN,
                TokenType.LESS_THAN_OR_EQUAL_TO, TokenType.GREATER_THAN_OR_EQUAL_TO
            }
            
            op_type = expr.operator.type if hasattr(expr.operator, 'type') else expr.operator
            if op_type in comparison_ops:
                return "bool"
            
            # Default to left operand type
            return left_type
        
        elif isinstance(expr, Identifier):
            # Check if it's a property in the current class
            if self.current_class and (self.current_class, expr.name) in self.property_types:
                return self.property_types[(self.current_class, expr.name)]
            
            # Look up variable type from symbol table
            if expr.name in self.symbol_table:
                return self.symbol_table[expr.name]
            
            # Default to int if not found
            return "int"
        
        elif isinstance(expr, UnaryOperation):
            # Unary operations preserve the type of the operand
            return self._infer_type(expr.operand)
        
        elif isinstance(expr, ObjectInstantiation):
            # Object instantiation returns pointer to class type
            return f"{expr.class_name}*"
        
        elif isinstance(expr, FunctionCall):
            # Look up function return type from function_types table
            if expr.name in self.function_types:
                return self.function_types[expr.name]
            # Default to int for unknown functions
            return "int"
        
        elif isinstance(expr, ListExpression):
            # Infer array type from elements
            if expr.elements:
                # Check all elements to find the most general type
                element_types = [self._infer_type(elem) for elem in expr.elements]
                
                # If any element is double, the array should be double
                if "double" in element_types:
                    return "double[]"
                # If all are int, use int
                elif all(t == "int" for t in element_types):
                    return "int[]"
                # If all are const char*, use const char*
                elif all(t == "const char*" for t in element_types):
                    return "const char*[]"
                # If all are bool, use bool
                elif all(t == "bool" for t in element_types):
                    return "bool[]"
                # Otherwise use the first element's type
                else:
                    return f"{element_types[0]}[]"
            else:
                # Empty array defaults to int[]
                return "int[]"
        
        elif isinstance(expr, IndexExpression):
            # Array indexing returns the element type
            array_type = self._infer_type(expr.array_expr)
            # Strip the [] suffix to get element type
            if array_type.endswith("[]"):
                return array_type[:-2]
            # If it's a pointer type (e.g., "int*"), strip the *
            elif array_type.endswith("*"):
                return array_type[:-1]
            # Default to the same type (might be void*)
            return array_type
        
        else:
            return "void*"
    
    def _generate_extern_function(self, node: ExternFunctionDeclaration) -> None:
        """Generate extern function declaration for FFI."""
        # For C, we need to add the function declaration to forward declarations
        
        # Map NLPL type to C type
        return_type = self._map_type(node.return_type) if node.return_type else "void"
        
        # Build parameter list
        params = []
        for param in node.parameters:
            param_type = self._map_type(param.type_annotation) if param.type_annotation else "void*"
            params.append(f"{param_type} {param.name}")
        
        # Handle variadic functions
        if node.variadic:
            params.append("...")
        
        # Generate extern declaration
        params_str = ", ".join(params) if params else "void"
        extern_decl = f"extern {return_type} {node.name}({params_str});"
        
        if extern_decl not in self.forward_declarations:
            self.forward_declarations.append(extern_decl)
            
        # Add library to required libraries for linking
        if hasattr(node, 'library') and node.library:
            self.required_libraries.add(node.library)
    
    def _generate_if_statement(self, node: IfStatement) -> None:
        """Generate if statement."""
        condition = self._generate_expression(node.condition)
        
        self.emit(f"if ({condition}) {{")
        self.indent()
        
        if hasattr(node, 'then_block') and node.then_block:
            for stmt in node.then_block:
                self._generate_statement(stmt)
        
        self.dedent()
        self.emit("}")
        
        if hasattr(node, 'else_block') and node.else_block:
            self.emit("else {")
            self.indent()
            
            for stmt in node.else_block:
                self._generate_statement(stmt)
            
            self.dedent()
            self.emit("}")
    
    def _generate_while_loop(self, node: WhileLoop) -> None:
        """Generate while loop."""
        condition = self._generate_expression(node.condition)
        
        self.emit(f"while ({condition}) {{")
        self.indent()
        
        if node.body:
            for stmt in node.body:
                self._generate_statement(stmt)
        
        self.dedent()
        self.emit("}")
    
    def _generate_for_loop(self, node: ForLoop) -> None:
        """Generate for loop."""
        # For NLPL's "for each x in collection" style loops
        # Generate as C for loop with index
        
        collection_expr = self._generate_expression(node.iterable)
        iterator = node.iterator
        
        # Determine the collection type and how to get its length
        collection_type = self._infer_type(node.iterable)
        
        # Check if we can determine the array size
        if isinstance(node.iterable, ListExpression):
            # Direct array literal - we know the size
            array_size = len(node.iterable.elements)
            
            # Infer element type
            element_type = self._infer_type(node.iterable.elements[0]) if node.iterable.elements else "int"
            
            self.emit(f"/* For each loop over array literal */")
            self.emit(f"for (int _i = 0; _i < {array_size}; _i++) {{")
            self.indent()
            self.emit(f"{element_type} {iterator} = {collection_expr}[_i];")
            
        elif isinstance(node.iterable, Identifier):
            # Variable reference - look up its type
            var_name = node.iterable.name
            if var_name in self.symbol_table:
                var_type = self.symbol_table[var_name]
                
                if var_type.endswith("[]"):
                    # It's an array - get element type
                    element_type = var_type[:-2]
                    
                    # For arrays, we need sizeof to get length
                    # Note: This only works for stack-allocated arrays, not pointers
                    self.emit(f"/* For each loop over array */")
                    self.emit(f"for (int _i = 0; _i < sizeof({collection_expr})/sizeof({element_type}); _i++) {{")
                    self.indent()
                    self.emit(f"{element_type} {iterator} = {collection_expr}[_i];")
                else:
                    # Unknown collection type - use placeholder
                    self.emit(f"/* For each loop - collection type unknown */")
                    self.emit(f"for (int _i = 0; _i < /* length */; _i++) {{")
                    self.indent()
                    self.emit(f"/* Unknown type */ {iterator} = {collection_expr}[_i];")
            else:
                # Variable not in symbol table
                self.emit(f"/* For each loop - variable not found */")
                self.emit(f"for (int _i = 0; _i < /* length */; _i++) {{")
                self.indent()
                self.emit(f"int {iterator} = {collection_expr}[_i];")
        else:
            # Some other expression
            self.emit(f"/* For each loop - generic */")
            self.emit(f"for (int _i = 0; _i < /* length */; _i++) {{")
            self.indent()
            self.emit(f"int {iterator} = {collection_expr}[_i];")
        
        # Generate loop body
        if node.body:
            for stmt in node.body:
                self._generate_statement(stmt)
        
        self.dedent()
        self.emit("}")
    
    def _generate_try_catch(self, node: Any) -> None:
        """Generate C code for try-catch error handling using setjmp/longjmp."""
        # Include setjmp.h for error handling
        self.includes.add("<setjmp.h>")
        
        # Generate unique label for this try-catch block
        import random
        label_id = random.randint(1000, 9999)
        jmp_buf_name = f"err_jmp_buf_{label_id}"
        
        # Declare jump buffer for this try-catch block
        self.emit(f"jmp_buf {jmp_buf_name};")
        self.emit(f"if (setjmp({jmp_buf_name}) == 0) {{")
        self.indent()
        
        # Generate try block code
        if isinstance(node.try_block, list):
            for stmt in node.try_block:
                self._generate_statement(stmt)
        else:
            self._generate_statement(node.try_block)
        
        self.dedent()
        self.emit("} else {")
        self.indent()
        
        # Generate catch block code
        # If there's an exception variable, declare it
        if hasattr(node, 'exception_var') and node.exception_var:
            self.emit(f"const char* {node.exception_var} = \"Error occurred\";")
        
        if isinstance(node.catch_block, list):
            for stmt in node.catch_block:
                self._generate_statement(stmt)
        else:
            self._generate_statement(node.catch_block)
        
        self.dedent()
        self.emit("}")
    
    def _generate_expression(self, node: Any) -> str:
        """Generate C expression code."""
        if isinstance(node, Literal):
            return self._generate_literal(node)
        
        elif isinstance(node, Identifier):
            # Check if we're in a method and this is a property reference
            if self.current_class and self.current_class in self.class_properties:
                if node.name in self.class_properties[self.current_class]:
                    return f"this->{node.name}"
            return node.name
        
        elif isinstance(node, ObjectInstantiation):
            return self._generate_object_instantiation(node)
        
        elif isinstance(node, MemberAccess):
            return self._generate_member_access(node)
        
        elif isinstance(node, IndexExpression):
            return self._generate_index_expression(node)
        
        elif isinstance(node, ListExpression):
            return self._generate_list_expression(node)
        
        elif isinstance(node, DictExpression):
            return self._generate_dict_expression(node)
        
        elif isinstance(node, BinaryOperation):
            return self._generate_binary_operation(node)
        
        elif isinstance(node, UnaryOperation):
            return self._generate_unary_operation(node)
        
        elif isinstance(node, FunctionCall):
            return self._generate_function_call(node)
        
        else:
            return f"/* Unhandled expression: {type(node).__name__} */"
    
    def _generate_literal(self, node: Literal) -> str:
        """Generate literal value."""
        if node.type == "string":
            # Escape special characters in string
            escaped = str(node.value).replace('\\', '\\\\')  # Escape backslashes first
            escaped = escaped.replace('"', '\\"')  # Escape quotes
            escaped = escaped.replace('\n', '\\n')  # Escape newlines
            escaped = escaped.replace('\t', '\\t')  # Escape tabs
            escaped = escaped.replace('\r', '\\r')  # Escape carriage returns
            return f'"{escaped}"'
        elif node.type == "integer":
            return str(node.value)
        elif node.type == "float":
            return str(node.value)
        elif node.type == "boolean":
            return "true" if node.value else "false"
        else:
            return f"{node.value}"
    
    def _generate_binary_operation(self, node: BinaryOperation) -> str:
        """Generate binary operation."""
        left = self._generate_expression(node.left)
        right = self._generate_expression(node.right)
        
        # Map NLPL operators to C operators
        from ...parser.lexer import TokenType
        
        # Check for string concatenation (PLUS operator with string operands)
        if hasattr(node.operator, 'type'):
            op_type = node.operator.type
        else:
            op_type = node.operator
            
        # Handle string concatenation specially
        if op_type == TokenType.PLUS:
            # Infer types of operands
            left_type = self._infer_type(node.left)
            right_type = self._infer_type(node.right)
            
            # If both are strings, use string concatenation
            if left_type == "const char*" or right_type == "const char*":
                # Include string.h for string operations
                self.includes.add("<string.h>")
                
                # Generate code for string concatenation using malloc and strcpy/strcat
                # This allocates a new string with enough space for both strings
                return f"({{ char* _tmp = malloc(strlen({left}) + strlen({right}) + 1); strcpy(_tmp, {left}); strcat(_tmp, {right}); _tmp; }})"
        
        op_map = {
            TokenType.PLUS: "+",
            TokenType.MINUS: "-",
            TokenType.TIMES: "*",
            TokenType.DIVIDED_BY: "/",
            TokenType.MODULO: "%",
            TokenType.POWER: "pow",  # Will need to include math.h
            TokenType.FLOOR_DIVIDE: "/",  # C integer division is floor by default
            TokenType.EQUAL_TO: "==",
            TokenType.NOT_EQUAL_TO: "!=",
            TokenType.LESS_THAN: "<",
            TokenType.GREATER_THAN: ">",
            TokenType.LESS_THAN_OR_EQUAL_TO: "<=",
            TokenType.GREATER_THAN_OR_EQUAL_TO: ">=",
            TokenType.AND: "&&",
            TokenType.OR: "||",
            TokenType.BITWISE_AND: "&",
            TokenType.BITWISE_OR: "|",
            TokenType.BITWISE_XOR: "^",
            TokenType.LEFT_SHIFT: "<<",
            TokenType.RIGHT_SHIFT: ">>",
        }
        
        # Special handling for power operator
        if op_type == TokenType.POWER:
            self.includes.add("<math.h>")
            return f"pow({left}, {right})"
        
        c_op = op_map.get(op_type, "/* unknown operator */")
        
        return f"({left} {c_op} {right})"
    
    def _generate_unary_operation(self, node: UnaryOperation) -> str:
        """Generate unary operation."""
        operand = self._generate_expression(node.operand)
        
        from ...parser.lexer import TokenType
        
        op_map = {
            TokenType.NOT: "!",
            TokenType.MINUS: "-",
            TokenType.BITWISE_NOT: "~",
        }
        
        if hasattr(node.operator, 'type'):
            op_type = node.operator.type
        else:
            op_type = node.operator
        
        c_op = op_map.get(op_type, "/* unknown operator */")
        
        return f"({c_op}{operand})"
    
    def _generate_object_instantiation(self, node: ObjectInstantiation) -> str:
        """Generate C code for object instantiation (new ClassName)."""
        constructor_name = f"{node.class_name}_new"
        
        # For now, we don't pass constructor arguments (constructors with params not yet implemented)
        # Just call the constructor function
        return f"{constructor_name}()"
    
    def _generate_member_access(self, node: MemberAccess) -> str:
        """Generate C code for member access (object.property or object.method())."""
        object_expr = self._generate_expression(node.object_expr)
        
        if node.is_method_call:
            # Method call: object->method(object, args...)
            # The first argument is 'this' pointer
            args = [object_expr]  # 'this' pointer
            for arg in node.arguments:
                args.append(self._generate_expression(arg))
            args_str = ", ".join(args)
            
            # Call through function pointer: object->method(object, ...)
            return f"{object_expr}->{node.member_name}({args_str})"
        else:
            # Property access: object->property
            return f"{object_expr}->{node.member_name}"
    
    def _generate_function_call(self, node: FunctionCall) -> str:
        """Generate function call."""
        # Handle built-in functions specially
        if node.name == "print":
            # Map to printf with appropriate format
            if node.arguments:
                # Infer type of argument to determine format specifier
                arg = node.arguments[0]
                arg_expr = self._generate_expression(arg)
                arg_type = self._infer_type(arg)
                
                # Choose format specifier based on type
                if arg_type == "const char*":
                    return f'printf("%s\\n", {arg_expr})'
                elif arg_type == "int":
                    return f'printf("%d\\n", {arg_expr})'
                elif arg_type == "double":
                    return f'printf("%f\\n", {arg_expr})'
                elif arg_type == "bool":
                    return f'printf("%s\\n", {arg_expr} ? "true" : "false")'
                else:
                    # Default to pointer
                    return f'printf("%p\\n", {arg_expr})'
            return 'printf("\\n")'
        
        # Map NLPL stdlib functions to C equivalents
        elif node.name in self._get_stdlib_mappings():
            return self._generate_stdlib_call(node)
        
        else:
            # Regular function call
            if node.arguments:
                arg_exprs = [self._generate_expression(arg) for arg in node.arguments]
                args_str = ", ".join(arg_exprs)
            else:
                args_str = ""
            
            return f"{node.name}({args_str})"
    
    def _generate_index_expression(self, node: IndexExpression) -> str:
        """Generate C code for array indexing: array[index]."""
        array_expr = self._generate_expression(node.array_expr)
        index_expr = self._generate_expression(node.index_expr)
        
        # In C, array indexing is straightforward: array[index]
        return f"{array_expr}[{index_expr}]"
    
    def _generate_list_expression(self, node: ListExpression) -> str:
        """Generate C code for list literal: [1, 2, 3]."""
        # For now, generate as C array initializer: {1, 2, 3}
        # In the future, this could create dynamic arrays or use a list struct
        if node.elements:
            element_exprs = [self._generate_expression(elem) for elem in node.elements]
            elements_str = ", ".join(element_exprs)
            return f"{{{elements_str}}}"
        else:
            # Empty list
            return "{}"
    
    def _generate_dict_expression(self, node: Any) -> str:
        """Generate C code for dictionary literal.
        
        Note: C doesn't have native dictionaries. This generates a comment for now.
        A real implementation would need a hash table library or struct-based approach.
        """
        # For now, generate a comment indicating this needs manual implementation
        # In the future, could use a hash table library like uthash
        return "/* Dictionary literals not yet supported in C generation - use a hash table library */"
    
    def _get_stdlib_mappings(self):
        """Get mapping of NLPL stdlib functions to C functions."""
        return {
            # String functions
            "length": "strlen",
            "uppercase": "strupr",  # Note: non-standard, may need custom implementation
            "lowercase": "strlwr",  # Note: non-standard, may need custom implementation
            "concatenate": "strcat",
            
            # Math functions
            "sqrt": "sqrt",
            "abs": "abs",
            "power": "pow",
            "floor": "floor",
            "ceil": "ceil",
            "round": "round",
            "sin": "sin",
            "cos": "cos",
            "tan": "tan",
            
            # File I/O - will need custom wrappers
            "read_file": "nlpl_read_file",
            "write_file": "nlpl_write_file",
            "file_exists": "nlpl_file_exists",
        }
    
    def _generate_stdlib_call(self, node: FunctionCall) -> str:
        """Generate stdlib function call with appropriate C mapping."""
        mapping = self._get_stdlib_mappings()[node.name]
        
        # Generate arguments
        if node.arguments:
            arg_exprs = [self._generate_expression(arg) for arg in node.arguments]
            args_str = ", ".join(arg_exprs)
        else:
            args_str = ""
        
        # Add required includes based on function
        if node.name in ["sqrt", "power", "abs", "floor", "ceil", "round", "sin", "cos", "tan"]:
            self.includes.add("<math.h>")
        elif node.name in ["length", "uppercase", "lowercase", "concatenate"]:
            self.includes.add("<string.h>")
        
        return f"{mapping}({args_str})"
    
    def _map_type(self, nlpl_type: str) -> str:
        """Map NLPL type to C type."""
        type_map = {
            "Integer": "int",
            "Float": "double",
            "String": "const char*",
            "Boolean": "bool",
            "Void": "void",
            "Nothing": "void",  # NLPL uses "Nothing" for void return type
        }
        
        return type_map.get(nlpl_type, "void*")
