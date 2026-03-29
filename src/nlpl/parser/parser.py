"""
Parser for the Natural Language Programming Language (NLPL).
This module converts a stream of tokens into an Abstract Syntax Tree (AST).
"""

from typing import Type
from nlpl.parser.lexer import TokenType, Token
from nlpl.errors import NLPLSyntaxError, suggest_correction
from nlpl.parser.ast import (
    Program, VariableDeclaration, IndexAssignment, MemberAssignment, DereferenceAssignment, FunctionDefinition, Parameter,
    IfStatement, WhileLoop, ForLoop, MemoryAllocation, MemoryDeallocation,
    ClassDefinition, PropertyDeclaration, MethodDefinition,
    ObjectInstantiation, MemberAccess,
    ConcurrentExecution, TryCatch, RaiseStatement, BinaryOperation,
    UnaryOperation, Literal, Identifier, FunctionCall, PrintStatement, RepeatNTimesLoop, RepeatWhileLoop,
    TypeCastExpression,
    ReturnStatement, BreakStatement, ContinueStatement, Block, ConcurrentBlock, TryCatchBlock, PanicStatement,
    # Module-related AST nodes
    ImportStatement, SelectiveImport, ModuleAccess, PrivateDeclaration,
    InterfaceDefinition, AbstractClassDefinition, TraitDefinition,
    TypeAliasDefinition, TypeParameter, TypeConstraint, TypeGuard,
    AbstractMethodDefinition,
    ListExpression, DictExpression, SliceExpression, IndexExpression,
    ListComprehension, DictComprehension, TernaryExpression,
    LambdaExpression, AsyncExpression, AwaitExpression,
    YieldExpression, GeneratorExpression,
    # Low-level pointer operations
    AddressOfExpression, DereferenceExpression, SizeofExpression, PointerType,
    # Smart pointer operations
    DowngradeExpression, UpgradeExpression,
    # Ownership / borrow operations
    MoveExpression, BorrowExpression, DropBorrowStatement,
    # Lifetime annotations
    LifetimeAnnotation, BorrowExpressionWithLifetime, ParameterWithLifetime, ReturnTypeWithLifetime,
    # Allocator hints and parallel execution
    AllocatorHint, ParallelForLoop,
    # Conditional compilation / platform detection
    ConditionalCompilationBlock,
    # Struct and union types
    StructDefinition, StructField, UnionDefinition, EnumDefinition, EnumMember, OffsetofExpression, TypeCastExpression,
    # Inline assembly
    InlineAssembly,
    # Decorators and Macros
    Decorator, MacroDefinition, MacroExpansion,
    ComptimeExpression, ComptimeConst, ComptimeAssert, AttributeDeclaration,
    # Pattern matching
    MatchExpression, MatchCase, Pattern, LiteralPattern, IdentifierPattern, 
    WildcardPattern, VariantPattern, TuplePattern, ListPattern,
    # Switch statement
    SwitchStatement, SwitchCase,
    # String operations
    StringLiteral, FStringExpression,
    # Smart pointers and memory management
    RcType, WeakType, ArcType, RcCreation,
    # Native test framework
    TestBlock, DescribeBlock, ItBlock, ParameterizedTestBlock,
    BeforeEachBlock, AfterEachBlock,
    # Assertion library
    ExpectStatement,
    # Contract programming
    RequireStatement, EnsureStatement, GuaranteeStatement,
    InvariantStatement, OldExpression, SpecAnnotation, SpecBlock,
    # Higher-kinded type annotations
    KindAnnotation, StarKindAnnotation, ArrowKindAnnotation,
)

class Parser:
    """Parses a stream of tokens into an AST."""
    def __init__(self, tokens, source=None):
        self.tokens = tokens
        self.source = source  # Store full source for error context
        self.current_token_index = 0
        self.current_token = tokens[0] if tokens else None
        self._in_argument_context = False  # Prevents parsing trailing blocks in function arguments
        
    def error(self, message, error_type_key=None):
        """Raise a syntax error with enhanced context and suggestions."""
        if self.current_token:
            line = self.current_token.line
            column = self.current_token.column
            token_value = self.current_token.lexeme if self.current_token.lexeme else str(self.current_token.type)
            source_line = self.current_token.source_line
            
            # Determine expected and got for better error messages
            expected = None
            got = str(self.current_token.type)
            
            # Extract expected from message if present
            if "Expected" in message:
                expected_part = message.split("Expected")[1].split(",")[0].strip()
                expected = expected_part
            
            # Determine error type key from context if not provided
            if not error_type_key:
                if "Unexpected end" in message or "Expected" in message:
                    error_type_key = "unexpected_token"
                elif "missing" in message.lower():
                    error_type_key = "missing_end"
                elif "Invalid" in message:
                    error_type_key = "invalid_syntax"
            
            # Get suggestion based on context
            suggestion = self._get_error_suggestion(message, token_value)
            
            raise NLPLSyntaxError(
                message,
                line=line,
                column=column,
                source_line=source_line,
                suggestion=suggestion,
                expected=expected,
                got=got,
                error_type_key=error_type_key,
                full_source=self.source
            )
        else:
            raise NLPLSyntaxError(message, full_source=self.source)
    
    def _get_error_suggestion(self, message, token_value):
        """Get a helpful suggestion based on the error message."""
        message_lower = message.lower()
        token_str = str(token_value).lower()
        
        # Common mistakes and suggestions
        if "expected 'end'" in message_lower or "expected end" in message_lower:
            return "Make sure to close all blocks (if, while, for, function, etc.) with 'end'"
        elif "expected TokenType.END" in message:
            return "Did you forget to add 'end' to close a block (if/while/for/function/try)?"
        elif "unexpected" in message_lower and "indent" in message_lower:
            return "Check your indentation - NLPL uses consistent indentation for blocks"
        elif "expected" in message_lower and "got" in message_lower:
            # Extract what was expected
            if "TokenType." in message:
                return "Check the syntax - you might be missing a keyword or punctuation"
        elif "undefined" in message_lower or "not defined" in message_lower:
            return "Make sure you've declared this variable with 'set' before using it"
        
        return None
            
    def eat(self, token_type):
        """
        Consume the current token if it matches the expected type.
        Otherwise, raise an error.
        """
        if self.current_token.type == token_type:
            token = self.current_token
            self.advance()
            return token
        else:
            self.error(f"Expected {token_type}, got {self.current_token.type}")
    
    def consume(self, token_type, error_message=None):
        """
        Consume the current token if it matches the expected type.
        Otherwise, raise an error with custom message.
        Alias for eat() with optional custom error message.
        """
        if self.current_token.type == token_type:
            token = self.current_token
            self.advance()
            return token
        else:
            if error_message:
                self.error(error_message)
            else:
                self.error(f"Expected {token_type}, got {self.current_token.type}")
            
    def advance(self):
        """Advance to the next token."""
        self.current_token_index += 1
        if self.current_token_index < len(self.tokens):
            self.current_token = self.tokens[self.current_token_index]
        else:
            self.current_token = None
    
    def previous(self):
        """Return the previous token (the one we just consumed)."""
        if self.current_token_index > 0:
            return self.tokens[self.current_token_index - 1]
        return None
    
    def check(self, token_type):
        """Check if current token is of given type without consuming it."""
        if self.current_token is None:
            return False
        return self.current_token.type == token_type
    
    def is_at_end(self):
        """Check if we've reached the end of tokens."""
        return self.current_token is None or self.current_token.type == TokenType.EOF
    
    def match(self, *token_types):
        """
        Check if current token matches any of the given types.
        If so, consume it and return True.
        """
        for token_type in token_types:
            if self.check(token_type):
                self.advance()
                return True
        return False
            
    def peek(self, n=1):
        """Look ahead n tokens without advancing."""
        peek_index = self.current_token_index + n
        if peek_index < len(self.tokens):
            return self.tokens[peek_index]
        return None
    
    def _skip_whitespace_tokens(self):
        """Skip NEWLINE, INDENT, DEDENT, and DOC_COMMENT boundary tokens."""
        while (self.current_token and
               self.current_token.type in (
                   TokenType.NEWLINE, TokenType.INDENT, TokenType.DEDENT,
                   TokenType.DOC_COMMENT,
               )):
            self.advance()
        
    def parse(self):
        """Parse the token stream and return the AST."""
        return self.program()
        
    def program(self):
        """Parse a program."""
        statements = []
        # Collects consecutive ## doc-comment lines preceding a definition.
        _pending_doc_lines: list = []

        # Node types that represent named definitions (eligible for doc attachment).
        _DOC_TARGET_TYPES = (
            "function_definition", "async_function_definition",
            "class_definition", "struct_definition",
            "enum_definition", "trait_definition", "interface_definition",
            "module_definition",
        )

        while self.current_token and self.current_token.type != TokenType.EOF:
            # Skip NEWLINE/INDENT/DEDENT boundary tokens and empty-lexeme identifiers
            if self.current_token.type in (TokenType.NEWLINE, TokenType.INDENT, TokenType.DEDENT):
                self.advance()
                continue
            # Collect documentation comments
            if self.current_token.type == TokenType.DOC_COMMENT:
                _pending_doc_lines.append(self.current_token.lexeme)
                self.advance()
                continue
            if self.current_token.type == TokenType.IDENTIFIER and self.current_token.lexeme.strip() == '':
                self.advance()
                continue

            # Parse statement
            try:
                statement = self.statement()
                if statement:
                    # Attach any buffered doc comment to definition nodes
                    if _pending_doc_lines and getattr(statement, 'node_type', None) in _DOC_TARGET_TYPES:
                        statement.doc = "\n".join(_pending_doc_lines)
                    statements.append(statement)
            except SyntaxError as e:
                raise
            finally:
                # Always clear the pending doc after consuming a statement
                _pending_doc_lines = []

            # Skip empty lines and whitespace after statement
            while self.current_token and self.current_token.type == TokenType.IDENTIFIER and self.current_token.lexeme.strip() == '':
                self.advance()

        return Program(statements)
        
    def statement(self):
        """Parse a statement."""
        if not self.current_token:
            return None
            
        token = self.current_token
        
        try:
            # Handle different statement types
            if token.type == TokenType.SET:
                return self.variable_declaration()
            elif token.type == TokenType.PANIC:
                return self.panic_statement()
            
            elif token.type == TokenType.PRINT:
                return self.print_statement()
            
            elif token.type == TokenType.IF:
                return self.if_statement()
            
            elif token.type == TokenType.LABEL:
                # Label for loop - check what follows
                # label name: while/for ...
                return self.labeled_loop_statement()
            
            elif token.type == TokenType.WHILE:
                return self.while_loop()
            
            elif token.type == TokenType.FOR:
                return self.for_loop()
            
            elif token.type == TokenType.FOR_EACH:
                # Handle "for each" as a single token
                return self.for_loop()
            
            elif token.type == TokenType.PARALLEL:
                # Handle "parallel for each item in collection ... end"
                return self.parse_parallel_for()

            elif token.type == TokenType.WHEN:
                # Disambiguate: "when target ..." / "when feature ..." are
                # conditional compilation blocks; anything else falls through
                # to expression parsing.
                next_tok = self._peek_next()
                if next_tok and next_tok.lexeme in ("target", "feature"):
                    return self.parse_conditional_compilation()
                # Otherwise fall through to expression statement

            elif token.type == TokenType.REPEAT:
                # Could be "repeat N times" or "repeat for each"
                return self.for_loop()
            
            elif token.type == TokenType.ADD or token.type == TokenType.APPEND:
                # Handle "add X to Y" or "append X to Y" statement
                return self.add_statement()
            
            elif token.type == TokenType.CREATE:
                # Handle "create variable as Type" or "create variable as value"
                # This is used for initialization: "create this.grades as empty List of Float"
                return self.create_statement()
            
            elif token.type == TokenType.FUNCTION:
                # Handle both syntaxes:
                # 1. "function <name> that takes..." (short form)
                # 2. Called from define_statement for "define a function called..." (long form)
                return self.function_definition_short()
            
            elif token.type == TokenType.ASYNC:
                # Handle "async function <name>..." syntax
                return self.async_function_definition()
            
            elif token.type == TokenType.CLASS:
                return self.class_definition()
            
            elif token.type == TokenType.STRUCT:
                return self.struct_definition()
            
            elif token.type == TokenType.IDENTIFIER:
                # Check for "abstract class" syntax
                if (token.lexeme.lower() == "abstract" and 
                    self.peek() and self.peek().type == TokenType.CLASS):
                    return self.abstract_class_short_syntax()
                # Otherwise try expression statement
                else:
                    expr = self.expression()
                    return expr if expr else None
            
            elif token.type == TokenType.UNION:
                return self.union_definition()
            
            elif token.type == TokenType.ENUM:
                return self.enum_definition()
            
            elif token.type == TokenType.PACKED:
                # packed struct Name
                self.advance()  # consume 'packed'
                if self.current_token and self.current_token.type == TokenType.STRUCT:
                    return self.struct_definition(packed=True)
                else:
                    self.error("Expected 'struct' after 'packed'")
            
            elif token.type == TokenType.RETURN or token.type == TokenType.RETURNS:
                return self.return_statement()
            
            elif token.type == TokenType.BREAK:
                return self.break_statement()
            
            elif token.type == TokenType.CONTINUE:
                return self.continue_statement()
            
            elif token.type == TokenType.FALLTHROUGH:
                return self.fallthrough_statement()
            
            elif token.type == TokenType.IMPORT:
                return self.import_statement()
            
            elif token.type == TokenType.FROM:
                return self.selective_import_statement()
            
            elif token.type == TokenType.TRY:
                return self.try_statement()
            
            elif token.type == TokenType.RAISE:
                return self.raise_statement()
            
            elif token.type == TokenType.MATCH:
                return self.match_expression()
            
            elif token.type == TokenType.SWITCH:
                return self.switch_statement()
            
            elif token.type == TokenType.ALLOCATE:
                return self.memory_allocation()
            
            elif token.type == TokenType.FREE:
                return self.memory_deallocation()

            elif token.type == TokenType.DROP:
                return self.drop_borrow_statement()

            elif token.type == TokenType.ASM:
                return self.parse_inline_assembly()
            
            elif token.type == TokenType.INTERFACE:
                return self.interface_definition()
            
            elif token.type == TokenType.TRAIT:
                return self.trait_definition()
            
            elif token.type == TokenType.EXTERN or token.type == TokenType.FOREIGN:
                return self.extern_declaration()

            elif token.type == TokenType.UNSAFE:
                return self.parse_unsafe_block()

            elif token.type == TokenType.TEST:
                return self.parse_test_block()

            elif token.type == TokenType.DESCRIBE:
                return self.parse_describe_block()

            elif token.type == TokenType.IT:
                return self.parse_it_block()

            elif token.type == TokenType.BEFORE_EACH:
                return self.parse_before_each_block()

            elif token.type == TokenType.AFTER_EACH:
                return self.parse_after_each_block()

            elif token.type == TokenType.EXPECT:
                return self.parse_expect_statement()

            elif token.type == TokenType.REQUIRE:
                return self.parse_require_statement()

            elif token.type == TokenType.ENSURE:
                return self.parse_ensure_statement()

            elif token.type == TokenType.GUARANTEE:
                return self.parse_guarantee_statement()

            elif token.type == TokenType.INVARIANT:
                return self.parse_invariant_statement()

            elif token.type == TokenType.SPEC:
                return self.parse_spec_block()

            elif token.type == TokenType.EOF:
                # End of file - return None to stop parsing
                return None
            
            elif token.type in (TokenType.INDENT, TokenType.DEDENT, TokenType.NEWLINE):
                # INDENT/DEDENT/NEWLINE tokens are handled by block-level constructs.
                # If we encounter them here at statement level, skip them.
                self.advance()
                return None
            
            elif token.type == TokenType.DEFINE:
                # DEFINE can start various constructs - look ahead to determine which
                return self.define_statement()
            
            elif token.type == TokenType.EXPORT:
                return self.export_statement()
            
            elif token.type == TokenType.MACRO:
                return self.macro_definition()
            
            elif token.type == TokenType.EXPAND:
                return self.macro_expansion()
            
            elif token.type == TokenType.COMPTIME:
                return self.comptime_statement()

            elif token.type == TokenType.ATTRIBUTE:
                return self.attribute_declaration()

            elif token.type == TokenType.AT:
                # Decorator - collect decorators and apply to next function or class
                decorators = []
                while self.current_token and self.current_token.type == TokenType.AT:
                    decorators.append(self.parse_decorator())
                    # Skip newlines between stacked decorators
                    while self.current_token and self.current_token.type == TokenType.NEWLINE:
                        self.advance()
                
                # Skip trailing newlines before function/class keyword
                while self.current_token and self.current_token.type == TokenType.NEWLINE:
                    self.advance()
                
                # Next statement should be a function or class definition
                if self.current_token and self.current_token.type == TokenType.FUNCTION:
                    func_def = self.function_definition_short()
                    func_def.decorators = decorators
                    return func_def
                elif self.current_token and self.current_token.type == TokenType.CLASS:
                    class_def = self.class_definition()
                    class_def.decorators = decorators
                    return class_def
                else:
                    self.error("Decorators can only be applied to functions or classes")
                
            else:
                # Try to parse as expression statement (function call, etc.)
                expr = self.expression()
                return expr if expr else None
                
        except SyntaxError as e:
            # Attempt error recovery
            self.error_recovery()
            return None
    
    def define_statement(self):
        """Dispatch DEFINE statements to the appropriate parser based on lookahead."""
        # DEFINE can start: function, class, interface, trait, method, etc.
        # Look ahead to determine which construct this is
        
        # Peek ahead to see what comes after DEFINE [A]
        lookahead_index = 1
        next_token = self.peek(lookahead_index)
        
        # Skip optional 'a' or 'an'
        if next_token and next_token.type == TokenType.A:
            lookahead_index += 1
            next_token = self.peek(lookahead_index)
        elif next_token and next_token.type == TokenType.AN:
            lookahead_index += 1
            next_token = self.peek(lookahead_index)
        elif next_token and next_token.type == TokenType.IDENTIFIER and next_token.lexeme.lower() in ['an']:
            lookahead_index += 1
            next_token = self.peek(lookahead_index)
        
        # Determine construct type from next significant token
        if not next_token:
            self.error("Unexpected end of file after DEFINE")
        
        if next_token.type == TokenType.FUNCTION:
            return self.function_definition()
        elif next_token.type == TokenType.CLASS:
            return self.class_definition()
        elif next_token.type == TokenType.INTERFACE:
            return self.interface_definition()
        elif next_token.type == TokenType.TRAIT:
            return self.trait_definition()
        elif next_token.type == TokenType.IDENTIFIER:
            # Could be "method", "property", etc.
            if next_token.lexeme.lower() == 'method':
                # This is likely inside a class definition
                # For now, error - method definitions should be inside class bodies
                self.error("Method definitions must be inside class bodies")
            else:
                self.error(f"Unexpected identifier '{next_token.lexeme}' after DEFINE")
        else:
            self.error(f"Unexpected token {next_token.type} after DEFINE")
            
    def variable_declaration(self):
        """Parse a variable declaration or assignment.
        
        Grammar:
            SET identifier TO expression
            SET object.property TO expression
            SET array[index] TO expression
            SET (value at pointer) TO expression
        """
        # Consume SET token
        if self.current_token.type != TokenType.SET:
            self.error(f"Expected SET, got {self.current_token.type}")
        self.advance()  # consume SET
        
        # Check for dereference assignment: set (value at ptr) to value
        # Only handle if we see both ( and dereference token
        if (self.current_token and 
            self.current_token.type == TokenType.LEFT_PAREN and
            self.peek() and 
            self.peek().type == TokenType.DEREFERENCE):
            
            self.advance()  # consume (
            self.advance()  # consume DEREFERENCE (value at)
            
            # Parse pointer expression
            pointer_expr = self.expression()
            
            # Expect closing paren
            if self.current_token.type != TokenType.RIGHT_PAREN:
                self.error(f"Expected ) after dereference expression, got {self.current_token.type}")
            self.advance()  # consume )
            
            # Expect TO
            if self.current_token.type != TokenType.TO:
                self.error(f"Expected TO after dereference target, got {self.current_token.type}")
            self.advance()  # consume TO
            
            # Parse value expression
            value = self.expression()
            if value is None:
                self.error("Expected a value expression after TO")
            
            # Create DereferenceExpression as target
            deref_expr = DereferenceExpression(pointer_expr)
            return DereferenceAssignment(deref_expr, value)
        
        # Parse the left-hand side (can be identifier or member access)
        # We need to parse this as a primary expression to handle member access
        lhs_start_token = self.current_token
        
        # Get base identifier
        if self.current_token.type == TokenType.IDENTIFIER:
            var_name = self.current_token.lexeme
        elif hasattr(self.current_token, 'lexeme') and self.current_token.lexeme:
            # Allow keywords to be used as variable names in this context
            var_name = self.current_token.lexeme
        else:
            self.error("Expected an identifier after SET")
        
        line_num = self.current_token.line if hasattr(self.current_token, 'line') else 0
        self.advance()  # consume variable name
        
        # Check if this is member access (object.property) or index access (array[index])
        if self.current_token and self.current_token.type == TokenType.DOT:
            # Parse member access chain
            base = Identifier(var_name)
            lhs = self._parse_member_access(base)
            
            # Check for TO
            if self.current_token.type != TokenType.TO:
                self.error(f"Expected TO after member access, got {self.current_token.type}")
            self.advance()  # consume TO
            
            # Parse the value expression
            value = self.expression()
            if value is None:
                self.error("Expected a value expression after TO")
            
            # Return a member assignment node
            return MemberAssignment(lhs, value)
        elif self.current_token and self.current_token.type == TokenType.LEFT_BRACKET:
            # Parse index access: set array[0] to value OR set dict["key"] to value
            # OR set array[0].field to value (member access on indexed element)
            base = Identifier(var_name)
            lhs = self._parse_index_access(base)
            
            # Check for TO
            if self.current_token.type != TokenType.TO:
                self.error(f"Expected TO after index access, got {self.current_token.type}")
            self.advance()  # consume TO
            
            # Parse the value expression
            value = self.expression()
            if value is None:
                self.error("Expected a value expression after TO")
            
            # Check if lhs is MemberAccess (e.g., array[0].x) or IndexExpression (e.g., array[0])
            if lhs.__class__.__name__ == 'MemberAccess':
                # This is a member assignment (e.g., array[0].x = 5)
                return MemberAssignment(lhs, value)
            else:
                # This is an index assignment (e.g., array[0] = value)
                return IndexAssignment(lhs, value)
        else:
            # Simple variable assignment
            # Check for TO
            if self.current_token.type != TokenType.TO:
                self.error(f"Expected TO after variable name, got {self.current_token.type}")
            self.advance()  # consume TO
            
            # Parse the value expression
            value = self.expression()
            if value is None:
                self.error("Expected a value expression after TO")

            # Optional type annotation: set x to value as List of Integer [with allocator arena]
            type_annotation = None
            if self.current_token and self.current_token.type == TokenType.AS:
                self.advance()  # consume 'as'
                type_annotation = self.parse_type()

            # Optional allocator hint: ... with allocator <name>
            allocator_name = None
            if (self.current_token and self.current_token.type == TokenType.WITH
                    and self.peek() and self.peek().type == TokenType.ALLOCATOR):
                self.advance()  # consume 'with'
                self.advance()  # consume 'allocator'
                if self.current_token and self.current_token.type in (
                        TokenType.IDENTIFIER, TokenType.ALLOCATOR):
                    allocator_name = self.current_token.lexeme
                    self.advance()  # consume allocator name

            return VariableDeclaration(var_name, value, type_annotation, allocator_name)
    
    def add_statement(self):
        """Parse an add/append statement.
        
        Grammar:
            ADD expression TO identifier
            APPEND expression TO identifier
            
        This is a shorthand for appending to a list or collection.
        """
        # Consume ADD or APPEND token
        if self.current_token.type not in (TokenType.ADD, TokenType.APPEND):
            self.error(f"Expected ADD or APPEND, got {self.current_token.type}")
        self.advance()  # consume ADD or APPEND
        
        # Parse the value to add
        value = self.expression()
        if value is None:
            self.error("Expected an expression after ADD")
        
        # Expect TO keyword
        if not self.current_token or self.current_token.type != TokenType.TO:
            self.error(f"Expected TO in add statement, got {self.current_token.type if self.current_token else 'EOF'}")
        self.advance()  # consume TO
        
        # Parse the target variable (list/collection or member access like "this.grades")
        target = self.comparison()  # Use comparison to handle member access
        
        line_num = self.current_token.line if hasattr(self.current_token, 'line') else 0
        
        # Create a function call to list_append
        # This translates "add X to Y" into "list_append(Y, X)"
        return FunctionCall("list_append", [target, value], [], line_number=line_num)
    
    def create_statement(self):
        """Parse a create statement for variable initialization.

        Handles both the classic form and advanced type definition forms:
            CREATE identifier AS expression
            CREATE member_access AS expression
            CREATE (A|AN) abstract CLASS CALLED name WITH: body
            CREATE (A|AN) CLASS CALLED name WITH A GENERIC TYPE PARAMETER T THAT EXTENDS bound
            CREATE (A|AN) TRAIT CALLED name WITH: body
            CREATE (A|AN) TYPE alias CALLED name THAT IS A ...
            CREATE (A|AN) <type_keyword> CALLED name [AND SET it TO expr]
        """
        line_number = self.current_token.line
        self.advance()  # consume CREATE

        # Detect advanced constructs when next token is A or AN
        if self.current_token and self.current_token.type in (TokenType.A, TokenType.AN):
            self.advance()  # consume A/AN
            tok = self.current_token

            # CREATE (A|AN) IDENTIFIER("abstract") CLASS CALLED name WITH: body
            if tok and tok.type == TokenType.IDENTIFIER and tok.lexeme.lower() == 'abstract':
                self.advance()  # consume "abstract"
                if self.current_token and self.current_token.type == TokenType.CLASS:
                    self.advance()  # consume CLASS
                    return self._parse_abstract_class_def(line_number)
                self.error(f"Expected CLASS after 'abstract', got {self.current_token.type if self.current_token else 'EOF'}")

            # CREATE (A|AN) CLASS CALLED name WITH A GENERIC TYPE PARAMETER T THAT EXTENDS bound
            elif tok and tok.type == TokenType.CLASS:
                self.advance()  # consume CLASS
                return self._parse_generic_class_def(line_number)

            # CREATE (A|AN) TRAIT CALLED name WITH: body
            elif tok and tok.type == TokenType.TRAIT:
                self.advance()  # consume TRAIT
                return self._parse_trait_def(line_number)

            # CREATE (A|AN) TYPE [alias] CALLED name THAT IS ...
            elif tok and tok.type == TokenType.TYPE:
                self.advance()  # consume TYPE
                if self.current_token and self.current_token.type == TokenType.IDENTIFIER and \
                        self.current_token.lexeme.lower() == 'alias':
                    self.advance()  # consume "alias"
                return self._parse_type_alias_def(line_number)

            # CREATE (A|AN) <type_keyword> CALLED name [AND SET it TO expr]
            # e.g., "Create an integer called length and set it to the length of x."
            elif tok and tok.type in (TokenType.INTEGER, TokenType.FLOAT, TokenType.STRING,
                                       TokenType.BOOLEAN, TokenType.LIST, TokenType.DICTIONARY,
                                       TokenType.NUMBER, TokenType.OBJECT, TokenType.LENGTH,
                                       TokenType.IDENTIFIER):
                type_name = tok.lexeme.lower() if tok else None
                self.advance()  # consume type keyword

                # Consume optional CALLED
                if self.current_token and self.current_token.type == TokenType.CALLED:
                    self.advance()

                # Get variable name (any token type - e.g. LENGTH keyword as "length")
                var_name = self.current_token.lexeme if self.current_token else "unknown"
                self.advance()

                # Parse optional "and set it/varname to expression"
                init_value = None
                if self.current_token and self.current_token.type == TokenType.AND:
                    self.advance()  # consume AND
                    if self.current_token and self.current_token.type == TokenType.SET:
                        self.advance()  # consume SET
                        # Skip "it" or the variable reference (anything that isn't TO)
                        if self.current_token and self.current_token.type != TokenType.TO:
                            self.advance()
                        # Consume TO
                        if self.current_token and self.current_token.type == TokenType.TO:
                            self.advance()
                        try:
                            init_value = self.expression()
                        except Exception:
                            init_value = None
                            # Skip to end of statement
                            while self.current_token and self.current_token.type not in (
                                    TokenType.DOT, TokenType.EOF, TokenType.DEDENT):
                                self.advance()

                # Consume optional DOT
                if self.current_token and self.current_token.type == TokenType.DOT:
                    self.advance()

                return VariableDeclaration(var_name, init_value, type_name)

            else:
                self.error(
                    f"Unexpected token in create statement after 'a/an': "
                    f"{tok.type if tok else 'EOF'}"
                )

        # Original logic: CREATE target AS expression
        target = self.comparison()
        if not self.current_token or self.current_token.type != TokenType.AS:
            self.error(
                f"Expected AS in create statement, got "
                f"{self.current_token.type if self.current_token else 'EOF'}"
            )
        self.advance()  # consume AS

        value = self.expression()
        if value is None:
            self.error("Expected an expression after AS")

        if target.__class__.__name__ == 'Identifier':
            return VariableDeclaration(target.name, value, None)
        elif target.__class__.__name__ == 'MemberAccess':
            from ..parser.ast import MemberAssignment
            return MemberAssignment(target, value)
        else:
            return VariableDeclaration(str(target), value, None)

    # ------------------------------------------------------------------
    # Helper parsers for advanced type constructs
    # ------------------------------------------------------------------

    def _parse_abstract_class_def(self, line_number):
        """Parse: CALLED name WITH: [INDENT methods DEDENT]"""
        if self.current_token and self.current_token.type == TokenType.CALLED:
            self.advance()
        class_name = self.current_token.lexeme if self.current_token else "Unknown"
        self.advance()

        if self.current_token and self.current_token.type == TokenType.WITH:
            self.advance()
        if self.current_token and self.current_token.type == TokenType.COLON:
            self.advance()
        # Skip NEWLINE before INDENT
        while self.current_token and self.current_token.type == TokenType.NEWLINE:
            self.advance()
        if self.current_token and self.current_token.type == TokenType.INDENT:
            self.advance()

        abstract_methods = []
        concrete_methods = []

        while self.current_token and self.current_token.type not in (TokenType.DEDENT, TokenType.EOF):
            # Skip NEWLINE tokens between method definitions
            if self.current_token.type == TokenType.NEWLINE:
                self.advance()
                continue
            # Skip A/AN
            if self.current_token.type in (TokenType.A, TokenType.AN):
                self.advance()
            if not self.current_token or self.current_token.type in (TokenType.DEDENT, TokenType.EOF):
                break

            # Read modifier: "abstract" or "concrete"
            modifier = None
            if self.current_token and self.current_token.type == TokenType.IDENTIFIER:
                modifier = self.current_token.lexeme.lower()
                self.advance()

            # Eat METHOD
            if self.current_token and self.current_token.type == TokenType.METHOD:
                self.advance()

            # Eat CALLED
            if self.current_token and self.current_token.type == TokenType.CALLED:
                self.advance()

            # Get method name (any token, e.g. EQUAL_TO for "equals")
            method_name = self.current_token.lexeme if self.current_token else "unknown"
            self.advance()

            # Skip until RETURNS or DOT
            while self.current_token and self.current_token.type not in (
                    TokenType.RETURNS, TokenType.DOT, TokenType.EOF, TokenType.DEDENT):
                self.advance()

            return_type = None
            if self.current_token and self.current_token.type == TokenType.RETURNS:
                self.advance()
                if self.current_token and self.current_token.type in (TokenType.A, TokenType.AN):
                    self.advance()
                return_type = self.current_token.lexeme.lower() if self.current_token else None
                if self.current_token and self.current_token.type != TokenType.DOT:
                    self.advance()

            if self.current_token and self.current_token.type == TokenType.DOT:
                self.advance()

            if modifier == 'abstract':
                abstract_methods.append(
                    AbstractMethodDefinition(method_name, [], return_type, line_number))
            else:
                concrete_methods.append(
                    MethodDefinition(method_name, [], return_type=return_type, line_number=line_number))

        if self.current_token and self.current_token.type == TokenType.DEDENT:
            self.advance()
        if self.current_token and self.current_token.type == TokenType.DEDENT:
            self.advance()

        return AbstractClassDefinition(
            class_name, abstract_methods, concrete_methods, line_number=line_number)

    def _parse_generic_class_def(self, line_number):
        """Parse: CALLED name WITH A GENERIC TYPE PARAMETER T THAT EXTENDS bound DOT"""
        if self.current_token and self.current_token.type == TokenType.CALLED:
            self.advance()
        class_name = self.current_token.lexeme if self.current_token else "Unknown"
        self.advance()

        generic_params = []
        if self.current_token and self.current_token.type == TokenType.WITH:
            self.advance()
            # Consume A/AN
            if self.current_token and self.current_token.type in (TokenType.A, TokenType.AN):
                self.advance()
            # Consume GENERIC
            if self.current_token and self.current_token.type == TokenType.GENERIC:
                self.advance()
            # Consume TYPE
            if self.current_token and self.current_token.type == TokenType.TYPE:
                self.advance()
            # Skip IDENTIFIER("parameter")
            if self.current_token and self.current_token.type == TokenType.IDENTIFIER and \
                    self.current_token.lexeme.lower() == 'parameter':
                self.advance()
            # Get type parameter name (e.g., T or N)
            param_name = self.current_token.lexeme if self.current_token else "T"
            self.advance()

            bounds = []
            if self.current_token and self.current_token.type == TokenType.THAT:
                self.advance()
                if self.current_token and self.current_token.type == TokenType.EXTENDS:
                    self.advance()
                    bound_name = self.current_token.lexeme if self.current_token else "Object"
                    self.advance()
                    bounds.append(bound_name)

            generic_params.append(TypeParameter(param_name, bounds=bounds, line_number=line_number))

        if self.current_token and self.current_token.type == TokenType.DOT:
            self.advance()

        return ClassDefinition(class_name, generic_parameters=generic_params, line_number=line_number)

    def _parse_trait_def(self, line_number):
        """Parse: CALLED name WITH: [INDENT required/provided methods DEDENT]"""
        if self.current_token and self.current_token.type == TokenType.CALLED:
            self.advance()
        trait_name = self.current_token.lexeme if self.current_token else "Unknown"
        self.advance()

        if self.current_token and self.current_token.type == TokenType.WITH:
            self.advance()
        if self.current_token and self.current_token.type == TokenType.COLON:
            self.advance()
        # Skip NEWLINE before INDENT
        while self.current_token and self.current_token.type == TokenType.NEWLINE:
            self.advance()
        if self.current_token and self.current_token.type == TokenType.INDENT:
            self.advance()

        required_methods = []
        provided_methods = []

        while self.current_token and self.current_token.type not in (TokenType.DEDENT, TokenType.EOF):
            # Skip NEWLINE tokens between method definitions
            if self.current_token.type == TokenType.NEWLINE:
                self.advance()
                continue
            # Skip A/AN
            if self.current_token.type in (TokenType.A, TokenType.AN):
                self.advance()
            if not self.current_token or self.current_token.type in (TokenType.DEDENT, TokenType.EOF):
                break

            # Read modifier: "required" or "provided"
            modifier = None
            if self.current_token and self.current_token.type == TokenType.IDENTIFIER:
                modifier = self.current_token.lexeme.lower()
                self.advance()

            # Eat METHOD
            if self.current_token and self.current_token.type == TokenType.METHOD:
                self.advance()

            # Eat CALLED
            if self.current_token and self.current_token.type == TokenType.CALLED:
                self.advance()

            # Get method name (any token, e.g. EQUAL_TO has lexeme "equals")
            method_name = self.current_token.lexeme if self.current_token else "unknown"
            self.advance()

            # Parse optional "THAT TAKES <params> AND RETURNS <type>"
            params = []
            if self.current_token and self.current_token.type == TokenType.THAT:
                self.advance()
                if self.current_token and self.current_token.type == TokenType.TAKES:
                    self.advance()
                    # Collect parameter types until AND or RETURNS or DOT
                    while self.current_token and self.current_token.type not in (
                            TokenType.AND, TokenType.RETURNS, TokenType.DOT, TokenType.EOF,
                            TokenType.DEDENT):
                        plex = self.current_token.lexeme
                        self.advance()
                        if plex.lower() != 'another':
                            params.append(
                                Parameter(f"param_{len(params)}", plex, line_number))

            if self.current_token and self.current_token.type == TokenType.AND:
                self.advance()

            return_type = None
            if self.current_token and self.current_token.type == TokenType.RETURNS:
                self.advance()
                if self.current_token and self.current_token.type in (TokenType.A, TokenType.AN):
                    self.advance()
                return_type = self.current_token.lexeme.lower() if self.current_token else None
                if self.current_token and self.current_token.type not in (
                        TokenType.DOT, TokenType.EOF, TokenType.DEDENT):
                    self.advance()

            if self.current_token and self.current_token.type == TokenType.DOT:
                self.advance()

            mdef = AbstractMethodDefinition(method_name, params, return_type, line_number)
            if modifier == 'required':
                required_methods.append(mdef)
            else:
                provided_methods.append(mdef)

        if self.current_token and self.current_token.type == TokenType.DEDENT:
            self.advance()

        return TraitDefinition(
            trait_name,
            required_methods=required_methods,
            provided_methods=provided_methods,
            line_number=line_number)

    def _parse_type_alias_def(self, line_number):
        """Parse: CALLED name THAT IS A DICTIONARY/LIST ..."""
        if self.current_token and self.current_token.type == TokenType.CALLED:
            self.advance()
        alias_name = self.current_token.lexeme if self.current_token else "Unknown"
        self.advance()

        target_type = None

        if self.current_token and self.current_token.type == TokenType.THAT:
            self.advance()
        if self.current_token and self.current_token.type == TokenType.IS:
            self.advance()
        if self.current_token and self.current_token.type in (TokenType.A, TokenType.AN):
            self.advance()

        if self.current_token and self.current_token.type == TokenType.DICTIONARY:
            self.advance()
            key_type = "string"
            value_type = "string"
            if self.current_token and self.current_token.type == TokenType.WITH:
                self.advance()
                if self.current_token and self.current_token.type in (
                        TokenType.STRING, TokenType.INTEGER, TokenType.FLOAT, TokenType.BOOLEAN):
                    key_type = self.current_token.lexeme.lower()
                    self.advance()
                if self.current_token and self.current_token.type == TokenType.IDENTIFIER:
                    self.advance()  # skip "keys"
                if self.current_token and self.current_token.type == TokenType.AND:
                    self.advance()
                if self.current_token and self.current_token.type in (
                        TokenType.STRING, TokenType.INTEGER, TokenType.FLOAT, TokenType.BOOLEAN):
                    value_type = self.current_token.lexeme.lower()
                    self.advance()
                if self.current_token and self.current_token.type == TokenType.IDENTIFIER:
                    self.advance()  # skip "values"
            target_type = f"dictionary<{key_type}, {value_type}>"

        elif self.current_token and self.current_token.type == TokenType.LIST:
            self.advance()
            elem_type = "object"
            if self.current_token and self.current_token.type == TokenType.OF:
                self.advance()
                elem_lex = self.current_token.lexeme.lower() if self.current_token else "object"
                # Normalize obvious plural forms: "integers" -> "integer"
                if elem_lex.endswith('s') and not elem_lex.endswith('ss'):
                    elem_lex = elem_lex[:-1]
                elem_type = elem_lex
                self.advance()
            target_type = f"list<{elem_type}>"

        if self.current_token and self.current_token.type == TokenType.DOT:
            self.advance()

        return TypeAliasDefinition(alias_name, target_type, line_number=line_number)

    def print_statement(self):
        """Parse a print statement.
        
        Grammar:
            PRINT TEXT expression
            PRINT NUMBER expression
            PRINT VALUE expression
            PRINT expression
        """
        # Consume PRINT token
        line_number = self.current_token.line if self.current_token else None
        if self.current_token.type != TokenType.PRINT:
            self.error(f"Expected PRINT, got {self.current_token.type}")
        self.advance()  # consume PRINT
        
        # Optional TEXT, NUMBER, or VALUE keyword
        print_type = None
        if self.current_token and self.current_token.type == TokenType.TEXT:
            print_type = "text"
            self.advance()  # consume TEXT
        elif self.current_token and self.current_token.type == TokenType.NUMBER:
            print_type = "number"
            self.advance()  # consume NUMBER
        elif self.current_token and self.current_token.type == TokenType.VALUE:
            print_type = "value"
            self.advance()  # consume VALUE
        
        # Parse the expression to print
        value = self.expression()
        if value is None:
            self.error("Expected an expression after PRINT")
        
        # Create a PrintStatement node
        return PrintStatement(value, print_type, line_number)

    def panic_statement(self):
        """Parse a panic statement.
        
        Grammar:
            PANIC WITH expression
        """
        line_number = self.current_token.line
        self.eat(TokenType.PANIC)
        
        # Expect WITH
        self.eat(TokenType.WITH)
        
        # Parse the error message expression
        message = self.expression()
        if message is None:
            self.error("Expected an expression after PANIC WITH")
            
        return PanicStatement(message, line_number)
        
    def export_statement(self):
        """Parse export statement."""
        line_number = self.current_token.line
        self.eat(TokenType.EXPORT)
        
        # Check if we are exporting a definition directly
        if self.current_token.type == TokenType.CLASS:
            definition = self.class_definition()
            definition.is_exported = True
            return definition
        elif self.current_token.type == TokenType.FUNCTION:
            # Check if it's "function name" or "define function"
            # function_definition handles "define", function_definition_short handled "function"
            # If token is FUNCTION, it's likely short syntax: "function name..."
            definition = self.function_definition_short()
            definition.is_exported = True
            return definition
        elif self.current_token.type == TokenType.DEFINE:
             definition = self.function_definition()
             definition.is_exported = True
             return definition

        from ..parser.ast import ExportStatement
        
        names = []
        # Expect at least one identifier
        if self.current_token.type == TokenType.IDENTIFIER or self._can_be_identifier(self.current_token):
            names.append(self.current_token.lexeme)
            self.advance()
        else:
            self.error("Expected identifier, class, or function to export")
            
        # Parse additional identifiers
        while self.current_token and self.current_token.type == TokenType.COMMA:
            self.advance() # Eat comma
            
            if self.current_token.type == TokenType.IDENTIFIER or self._can_be_identifier(self.current_token):
                names.append(self.current_token.lexeme)
                self.advance()
            else:
                self.error("Expected identifier after comma in export statement")
                
        return ExportStatement(names, line_number)
        
    def function_definition(self):
        """Parse a function definition."""
        # Syntax: Define a function called <identifier> that takes <parameter_list> [and returns <type>]
        line_number = self.current_token.line
        
        # Eat 'define'
        self.eat(TokenType.DEFINE)
        
        # Skip optional 'a'
        if self.current_token.type == TokenType.IDENTIFIER and self.current_token.lexeme.lower() == 'a':
            self.advance()
            
        # Eat 'function'
        self.eat(TokenType.FUNCTION)
        
        # Eat 'called'
        self.eat(TokenType.CALLED)
        
        # Get the function name
        if self.current_token.type == TokenType.IDENTIFIER:
            function_name = self.current_token.lexeme
            self.advance()
        else:
            self.error("Expected a function name")
            
        # Eat 'that'
        self.eat(TokenType.THAT)
        
        # Eat 'takes'
        self.eat(TokenType.TAKES)
        
        # Parse parameter list
        parameters, variadic = self.parameter_list()
        
        # Check for optional return type
        return_type = None
        if (self.current_token and self.current_token.type == TokenType.AND and 
            self.peek() and self.peek().type == TokenType.RETURNS):
            # Eat 'and'
            self.advance()
            # Eat 'returns'
            self.advance()
            
            # Get the return type
            return_type = self.parse_type()
            
        # Parse the function body
        body = []
        while (self.current_token and self.current_token.type != TokenType.EOF and 
               not (self.current_token.type == TokenType.IDENTIFIER and 
                    self.current_token.lexeme.lower() == 'end')):
            statement = self.statement()
            if statement:
                body.append(statement)
                
        # Eat 'end'
        if self.current_token and self.current_token.type == TokenType.IDENTIFIER and self.current_token.lexeme.lower() == 'end':
            self.advance()
            
            # Support for explicit "End function" syntax
            if (self.current_token and self.current_token.type == TokenType.FUNCTION):
                self.advance()
                
            # Support for explicit "End the function" syntax
            elif (self.current_token and self.current_token.type == TokenType.IDENTIFIER and 
                  self.current_token.lexeme.lower() == 'the' and self.peek() and 
                  self.peek().type == TokenType.FUNCTION):
                self.advance()  # Eat 'the'
                self.advance()  # Eat 'function'
                
            # Optional period after end
            if (self.current_token and self.current_token.type == TokenType.DOT):
                self.advance()
            
        return FunctionDefinition(function_name, parameters, body, return_type, [], None, variadic, line_number=line_number)
    
    def function_definition_short(self):
        """
        Parse a function definition with short syntax.
        Syntax: function <name>[<type_params>] that takes <params> returns <type>
                    <body with indentation>
        Example: function map<T, R> that takes items as List<T>, fn as Function returns List<R>
        """
        line_number = self.current_token.line
        
        # Eat 'function'
        self.eat(TokenType.FUNCTION)
        
        # Get the function name - can be multiple words (e.g., "get name", "set value", "to string")
        # Keep consuming identifiers/contextual keywords until we hit WITH, THAT, RETURNS, NEWLINE, or INDENT
        function_name_parts = []
        while (self.current_token and 
               (self.current_token.type == TokenType.IDENTIFIER or self._can_be_identifier(self.current_token)) and
               self.current_token.type not in (TokenType.WITH, TokenType.THAT, TokenType.RETURNS, TokenType.NEWLINE, TokenType.INDENT)):
            function_name_parts.append(self.current_token.lexeme)
            self.advance()
            
            # Stop if next token is WITH, THAT, RETURNS, NEWLINE, or INDENT
            if self.current_token and self.current_token.type in (TokenType.WITH, TokenType.THAT, TokenType.RETURNS, TokenType.NEWLINE, TokenType.INDENT):
                break
        
        if not function_name_parts:
            self.error("Expected a function name after 'function'")
        
        # Join multi-word names with underscore (e.g., "get name" -> "get_name")
        function_name = "_".join(function_name_parts)
        
        # Check for generic type parameters: function name<T, R> or function name<T: Comparable>
        type_parameters = []
        type_constraints = {}  # Dict mapping parameter name to list of trait names
        type_param_kinds = {}  # Dict mapping parameter name to KindAnnotation (HKT)
        
        if self.current_token and self.current_token.type == TokenType.LESS_THAN:
            self.advance()  # Eat '<'
            
            # Parse type parameters with optional trait bounds or kind annotations
            # Supports: <T>, <T: Comparable>, <T: Comparable + Printable>, <F :: * -> *>
            while self.current_token.type == TokenType.IDENTIFIER or self._can_be_identifier(self.current_token):
                param_name = self.current_token.lexeme
                type_parameters.append(param_name)
                self.advance()
                
                # Check for kind annotation: F :: * -> *
                if self.current_token and self.current_token.type == TokenType.DOUBLE_COLON:
                    self.advance()  # Eat '::'
                    kind = self.parse_kind_annotation()
                    type_param_kinds[param_name] = kind
                # Check for trait bounds: T: Comparable or T: Comparable + Printable
                elif self.current_token and self.current_token.type == TokenType.COLON:
                    self.advance()  # Eat ':'
                    
                    # Parse trait names (one or more, separated by +)
                    trait_bounds = []
                    
                    # Parse first trait
                    if self.current_token.type == TokenType.IDENTIFIER or self._can_be_identifier(self.current_token):
                        trait_bounds.append(self.current_token.lexeme)
                        self.advance()
                    else:
                        self.error("Expected trait name after ':'")
                    
                    # Parse additional traits with + separator
                    while self.current_token and self.current_token.type == TokenType.PLUS:
                        self.advance()  # Eat '+'
                        if self.current_token.type == TokenType.IDENTIFIER or self._can_be_identifier(self.current_token):
                            trait_bounds.append(self.current_token.lexeme)
                            self.advance()
                        else:
                            self.error("Expected trait name after '+'")
                    
                    # Store constraints for this parameter
                    type_constraints[param_name] = trait_bounds
                
                # Check for comma (more parameters) or end
                if self.current_token and self.current_token.type == TokenType.COMMA:
                    self.advance()  # Eat ','
                else:
                    break
            
            # Expect '>'
            if self.current_token and self.current_token.type == TokenType.GREATER_THAN:
                self.advance()  # Eat '>'
            elif self.current_token and self.current_token.type == TokenType.RIGHT_SHIFT:
                # Handle >> as > > for nested cases
                from ..parser.lexer import Token
                self.current_token = Token(TokenType.GREATER_THAN, '>', None,
                                          self.current_token.line, self.current_token.column + 1)
            else:
                self.error("Expected '>' to close generic type parameters")
        
        # Parse parameters (optional if followed by 'returns')
        parameters = []
        variadic = False
        
        if self.current_token and self.current_token.type == TokenType.RETURNS:
            # Implicit no arguments: function name returns Type
            pass
        elif self.current_token and self.current_token.type == TokenType.NEWLINE:
            # Function name NEWLINE (implied void, no args)
            pass
        else:
            # Explicit parameters: either "that takes ..." or "with ..."
            if self.current_token.type == TokenType.THAT:
                self.advance()
                
                # Expect 'takes'
                if self.current_token.type == TokenType.TAKES:
                    self.advance()
                    
                    # Parse parameter list
                    parameters, variadic = self.parameter_list()
                else:
                     self.error("Expected 'takes' after 'that'")
            elif self.current_token.type == TokenType.WITH:
                # Alternative syntax: function name with params returns Type
                self.advance()  # Eat 'with'
                
                # Parse parameter list
                parameters, variadic = self.parameter_list()
            else:
                 # If usage is 'function name', we might just fall through
                 pass
        
        # Check for 'where' clause before returns
        if self.current_token and self.current_token.type == TokenType.WHERE:
            self.advance()  # Eat 'where'
            
            # Parse constraint: T is Comparable, R is Equatable
            while True:
                if self.current_token.type != TokenType.IDENTIFIER:
                    break
                
                param_name = self.current_token.lexeme
                self.advance()
                
                # Expect 'is'
                if self.current_token and self.current_token.type == TokenType.IS:
                    self.advance()
                else:
                    break
                
                # Parse constraint type (Comparable, Equatable, or a type name)
                if self.current_token.type == TokenType.IDENTIFIER:
                    constraint_type = self.current_token.lexeme
                    self.advance()
                    
                    # Create TypeConstraint AST node
                    from ..parser.ast import TypeConstraint
                    type_constraints.append(
                        TypeConstraint(param_name, constraint_type, line_number)
                    )
                    
                    # Auto-add type parameter if not explicitly declared
                    if param_name not in type_parameters:
                        type_parameters.append(param_name)
                
                # Check for comma (more constraints)
                if self.current_token and self.current_token.type == TokenType.COMMA:
                    self.advance()
                else:
                    break
        
        # Check for optional return type
        return_type = None
        if self.current_token and self.current_token.type == TokenType.RETURNS:
            # Eat 'returns'
            self.advance()
            
            # Get the return type
            return_type = self.parse_type()
            
            # Check if return type is a type parameter
            if isinstance(return_type, str) and return_type not in type_parameters:
                # Could be a generic type parameter in return position
                # Add it if it looks like a type variable (single uppercase letter or known param)
                if len(return_type) == 1 and return_type.isupper():
                    type_parameters.append(return_type)
        
        # Expect NEWLINE or INDENT for function body
        if self.current_token and self.current_token.type == TokenType.NEWLINE:
            self.advance()
        
        # Parse the function body
        body = []
        
        # Check if body uses indentation
        if self.current_token and self.current_token.type == TokenType.INDENT:
            self.advance()  # Eat INDENT
            
            # Parse statements until DEDENT
            while (self.current_token and 
                   self.current_token.type != TokenType.EOF and
                   self.current_token.type != TokenType.DEDENT):
                # Skip NEWLINE tokens
                if self.current_token.type == TokenType.NEWLINE:
                    self.advance()
                    continue
                    
                statement = self.statement()
                if statement:
                    body.append(statement)
            
            # Eat DEDENT
            if self.current_token and self.current_token.type == TokenType.DEDENT:
                self.advance()
                
            # Handle optional 'end' keyword after DEDENT for explicit blocks
            if self.current_token and (self.current_token.type == TokenType.END or
                                       (self.current_token.type == TokenType.IDENTIFIER and 
                                        self.current_token.lexeme.lower() == 'end')):
                self.advance()
        else:
            # Old-style "end" keyword syntax
            while (self.current_token and self.current_token.type != TokenType.EOF and 
                   self.current_token.type != TokenType.END and
                   not (self.current_token.type == TokenType.IDENTIFIER and 
                        self.current_token.lexeme.lower() == 'end')):
                statement = self.statement()
                if statement:
                    body.append(statement)
            
            # Eat 'end' keyword if present (check both END token and identifier)
            if self.current_token and (self.current_token.type == TokenType.END or
                (self.current_token.type == TokenType.IDENTIFIER and self.current_token.lexeme.lower() == 'end')):
                self.advance()
        
        return FunctionDefinition(function_name, parameters, body, return_type, type_parameters, type_constraints, variadic, type_param_kinds=type_param_kinds, line_number=line_number)
    
    def async_function_definition(self):
        """
        Parse an async function definition.
        Syntax: async function <name> [with <params>] [returns <type>]
        """
        line_number = self.current_token.line
        
        # Eat 'async'
        self.eat(TokenType.ASYNC)
        
        # Eat 'function'
        self.eat(TokenType.FUNCTION)
        
        # Get function name
        if self.current_token.type != TokenType.IDENTIFIER:
            self.error("Expected function name after 'async function'")
        function_name = self.current_token.lexeme
        self.advance()
        
        # Parse optional type parameters <T, R>
        type_parameters = []
        if self.current_token and self.current_token.type == TokenType.LESS_THAN:
            type_parameters = self.parse_type_parameters()
        
        # Parse parameters
        parameters = []
        if self.current_token and self.current_token.type == TokenType.WITH:
            self.eat(TokenType.WITH)
            parameters, variadic = self.parameter_list()
        
        # Parse optional return type
        return_type = None
        if self.current_token and self.current_token.type == TokenType.RETURNS:
            self.eat(TokenType.RETURNS)
            return_type = self.parse_type()
        
        # Expect NEWLINE or INDENT for function body
        if self.current_token and self.current_token.type == TokenType.NEWLINE:
            self.advance()
        
        # Parse function body
        body = []
        
        # Check if body uses indentation
        if self.current_token and self.current_token.type == TokenType.INDENT:
            self.advance()  # Eat INDENT
            
            # Parse statements until DEDENT or END
            while (self.current_token and 
                   self.current_token.type != TokenType.EOF and
                   self.current_token.type != TokenType.DEDENT and
                   self.current_token.type != TokenType.END):
                statement = self.statement()
                if statement:
                    body.append(statement)
            
            # Eat DEDENT if present
            if self.current_token and self.current_token.type == TokenType.DEDENT:
                self.advance()
        
        # Eat 'end' if present
        if self.current_token and self.current_token.type == TokenType.END:
            self.eat(TokenType.END)
        
        from ..parser.ast import AsyncFunctionDefinition
        return AsyncFunctionDefinition(function_name, parameters, body, return_type, type_parameters, line_number)
        
    def parameter_list(self):
        """Parse a parameter list, including optional variadic (...) parameters and keyword-only parameters."""
        parameters = []
        variadic = False
        seen_keyword_only_separator = False  # Track if we've seen bare * separator
        
        # Handle empty parameter list
        if self.current_token.type == TokenType.NOTHING or \
           (self.current_token.type == TokenType.IDENTIFIER and self.current_token.lexeme.lower() == 'nothing'):
            self.advance()
            return parameters, variadic
        
        # Check for immediate ellipsis (all variadic)
        if self.current_token.type == TokenType.ELLIPSIS:
            self.advance()
            return parameters, True
        
        # Skip optional "a" or "a parameter" ONLY if it's followed by an actual parameter name
        # Don't skip if "a" is the parameter name itself (e.g., "with a as Integer")
        if self.current_token and self.current_token.type == TokenType.A:
            # Peek ahead to see if this is an article or the parameter name
            next_token = self.peek()
            # If next token is AS, OF, COMMA, or RETURNS, then "a" is the parameter name
            if next_token and next_token.type not in (TokenType.AS, TokenType.OF, TokenType.COMMA, TokenType.RETURNS):
                self.advance()  # Skip the article "a"
                
                # Skip "parameter" if present
                if self.current_token and self.current_token.type == TokenType.IDENTIFIER and self.current_token.lexeme.lower() == 'parameter':
                    self.advance()
        
        # Check for bare * separator at the start (all params keyword-only)
        if self.current_token and self.current_token.type == TokenType.TIMES:
            next_token = self.peek()
            if next_token and next_token.type in (TokenType.COMMA, TokenType.AND):
                # Bare * separator - all params are keyword-only
                self.advance()  # Eat '*'
                seen_keyword_only_separator = True
                # Eat the separator (comma or 'and')
                if self.current_token and self.current_token.type in (TokenType.COMMA, TokenType.AND):
                    self.advance()
        
        # Parse first parameter (if not just a bare * separator)
        if self.current_token and self.current_token.type not in (TokenType.RETURNS, TokenType.NEWLINE, TokenType.INDENT):
            param = self.parameter(keyword_only=seen_keyword_only_separator)
            if param:
                parameters.append(param)
            
        # Parse additional parameters (separated by comma or 'and')
        while self.current_token and self.current_token.type in (TokenType.COMMA, TokenType.AND):
            self.advance()  # Eat comma or 'and'
            
            # Check for bare * separator (keyword-only marker) RIGHT AFTER comma/and
            if self.current_token and self.current_token.type == TokenType.TIMES:
                # Peek ahead to see if there's an identifier (variadic param) or comma/and (separator)
                next_token = self.peek()
                if next_token and next_token.type in (TokenType.COMMA, TokenType.AND):
                    # This is the keyword-only separator (bare * followed by comma)
                    self.advance()  # Eat '*'
                    self.advance()  # Eat the comma/and after *
                    seen_keyword_only_separator = True
                    # Continue to next parameter (which will be keyword-only)
                    param = self.parameter(keyword_only=True)
                    if param:
                        parameters.append(param)
                    continue
                elif next_token and next_token.type in (TokenType.IDENTIFIER, TokenType.NAME, TokenType.A) or \
                     (next_token and self._can_be_identifier(next_token)):
                    # This is *args variadic parameter - let parameter() handle it
                    pass
                else:
                    # Bare * at end or before returns/newline - marks remaining as keyword-only
                    self.advance()  # Eat '*'
                    seen_keyword_only_separator = True
                    # Check if there's a separator after *
                    if self.current_token and self.current_token.type in (TokenType.COMMA, TokenType.AND):
                        self.advance()  # Eat comma or 'and'
                        # Continue to next parameter
                        param = self.parameter(keyword_only=True)
                        if param:
                            parameters.append(param)
                        continue
                    else:
                        # No more parameters after bare *
                        break
            
            # Skip optional "a" or "a parameter" with same logic
            if self.current_token and self.current_token.type == TokenType.A:
                next_token = self.peek()
                if next_token and next_token.type not in (TokenType.AS, TokenType.OF, TokenType.COMMA, TokenType.RETURNS):
                    self.advance()
                    
                    # Skip "parameter" if present
                    if self.current_token and self.current_token.type == TokenType.IDENTIFIER and self.current_token.lexeme.lower() == 'parameter':
                        self.advance()
            
            # Check for ellipsis (variadic)
            if self.current_token.type == TokenType.ELLIPSIS:
                self.advance()
                variadic = True
                break  # Ellipsis must be last
            
            param = self.parameter(keyword_only=seen_keyword_only_separator)
            if param:
                parameters.append(param)
                
        return parameters, variadic
        
    def parameter(self, keyword_only=False):
        """Parse a parameter with optional type annotation and default value.
        
        Args:
            keyword_only: If True, this parameter must be passed by name (comes after * separator)
        """
        # Syntax: 
        #  - <identifier> [as <type>] [defaults to <expression>]
        #  - <identifier> [of type <type>] [defaults to <expression>]
        #  - <identifier> [as <type>[<size_param>]] [defaults to <expression>]
        #  - *<identifier> [as <type>]  # Variadic parameter
        
        # Check for variadic parameter (*param)
        is_variadic = False
        if self.current_token and self.current_token.type == TokenType.TIMES:
            is_variadic = True
            self.advance()  # Eat '*'
        
        # Accept IDENTIFIER, NAME, A (as parameter name), or contextual keywords as parameter names
        if self.current_token.type in (TokenType.IDENTIFIER, TokenType.NAME, TokenType.A) or \
           self._can_be_identifier(self.current_token):
            param_name = self.current_token.lexeme
            line_number = self.current_token.line
            self.advance()
            
            # Check for optional type annotation
            type_annotation = None
            size_param = None
            default_value = None
            
            # Handle "as Type" syntax
            if self.current_token and self.current_token.type == TokenType.AS:
                self.advance()  # Eat 'as'
                type_annotation = self.parse_type()
                
                # Check for size annotation: Type[size_param]
                if self.current_token and self.current_token.type == TokenType.LEFT_BRACKET:
                    self.advance()  # Eat '['
                    
                    # Get size parameter name
                    if self.current_token.type == TokenType.IDENTIFIER:
                        size_param = self.current_token.lexeme
                        self.advance()
                    else:
                        self.error("Expected size parameter name in brackets")
                    
                    # Expect ']'
                    if self.current_token.type == TokenType.RIGHT_BRACKET:
                        self.advance()  # Eat ']'
                    else:
                        self.error("Expected ']' after size parameter")
            
            # Handle "of type Type" syntax
            elif self.current_token and self.current_token.type == TokenType.OF:
                self.advance()  # Eat 'of'
                
                # Expect 'type'
                if self.current_token and self.current_token.type == TokenType.TYPE:
                    self.advance()  # Eat 'type'
                    type_annotation = self.parse_type()
            
            # Check for "defaults to" syntax (not allowed for variadic parameters)
            if self.current_token and self.current_token.type == TokenType.DEFAULT:
                if is_variadic:
                    self.error("Variadic parameters cannot have default values")
                self.advance()  # Eat 'default' or 'defaults'
                
                # Expect 'to'
                if self.current_token and self.current_token.type == TokenType.TO:
                    self.advance()  # Eat 'to'
                    
                    # Parse the default value expression
                    default_value = self.comparison()
                else:
                    self.error("Expected 'to' after 'defaults'")
            
            return Parameter(param_name, type_annotation, size_param, default_value, is_variadic, keyword_only, line_number)
        else:
            self.error("Expected a parameter name")
        
    def class_definition(self):
        """Parse a class definition."""
        # Support both syntaxes:
        # 1. Simple: "class ClassName"
        # 2. Verbose: "define a class called ClassName with T as a type parameter"
        
        line_number = self.current_token.line
        
        # Check for DEFINE token (verbose syntax)
        if self.current_token.type == TokenType.DEFINE:
            self.advance()  # consume 'define'
            
            # Skip optional 'a'
            if self.current_token.type == TokenType.A:
                self.advance()
            
            # Expect 'class'
            if self.current_token.type != TokenType.CLASS:
                self.error("Expected 'class' after 'define'")
            self.advance()  # consume 'class'
            
            # Expect 'called'
            if self.current_token.type != TokenType.CALLED:
                self.error("Expected 'called' after 'class'")
            self.advance()  # consume 'called'
            
            # Get class name
            if self.current_token.type != TokenType.IDENTIFIER:
                self.error("Expected class name")
            class_name = self.current_token.lexeme
            self.advance()
            
            # Parse generic parameters: "with T as a type parameter that must be a number"
            generic_parameters = []
            parent_classes = []
            implemented_interfaces = []
            
            if self.current_token and self.current_token.type == TokenType.WITH:
                self.advance()  # consume 'with'
                
                # Parse type parameter name (T, K, V, etc.)
                if self.current_token.type != TokenType.IDENTIFIER:
                    self.error("Expected type parameter name after 'with'")
                param_name = self.current_token.lexeme
                self.advance()
                
                # Expect "as a type parameter"
                if self.current_token.type == TokenType.AS:
                    self.advance()  # consume 'as'
                    
                    # Skip optional 'a'
                    if self.current_token.type == TokenType.A:
                        self.advance()
                    
                    # Expect 'type'
                    if self.current_token.type == TokenType.TYPE:
                        self.advance()
                        
                        # Expect 'parameter'
                        if self.current_token.type == TokenType.IDENTIFIER and self.current_token.lexeme.lower() == 'parameter':
                            self.advance()
                            
                            # Check for constraint: "that must be a number"
                            constraint = None
                            if self.current_token and self.current_token.type == TokenType.THAT:
                                self.advance()  # consume 'that'
                                
                                # Expect 'must'
                                if self.current_token.type == TokenType.IDENTIFIER and self.current_token.lexeme.lower() == 'must':
                                    self.advance()
                                    
                                    # Expect 'be'
                                    if self.current_token.type == TokenType.IDENTIFIER and self.current_token.lexeme.lower() == 'be':
                                        self.advance()
                                        
                                        # Skip optional 'a'
                                        if self.current_token.type == TokenType.A:
                                            self.advance()
                                        
                                        # Get constraint type (number, string, etc.)
                                        if self.current_token.type in (TokenType.NUMBER, TokenType.STRING, TokenType.BOOLEAN, TokenType.INTEGER, TokenType.FLOAT):
                                            constraint = self.current_token.lexeme
                                            self.advance()
                                        elif self.current_token.type == TokenType.IDENTIFIER:
                                            constraint = self.current_token.lexeme
                                            self.advance()
                            
                            # Create TypeParameter with constraint
                            from ..parser.ast import TypeParameter
                            generic_parameters.append(
                                TypeParameter(
                                    name=param_name,
                                    bounds=[constraint] if constraint else [],
                                    line_number=line_number
                                )
                            )
            
            # Parse class body (properties and methods)
            properties = []
            methods = []
            
            # Skip NEWLINE before INDENT (emitted after class header line)
            while self.current_token and self.current_token.type == TokenType.NEWLINE:
                self.advance()
            
            # Expect INDENT
            if self.current_token and self.current_token.type == TokenType.INDENT:
                self.advance()
                
                # Parse properties section
                if self.current_token and self.current_token.type == TokenType.PROPERTIES:
                    self.advance()  # consume 'properties'
                    
                    # Skip colon
                    if self.current_token and self.current_token.type == TokenType.COLON:
                        self.advance()
                    
                    # Expect INDENT for properties
                    if self.current_token and self.current_token.type == TokenType.INDENT:
                        self.advance()
                        
                        # Parse property definitions: "name: Type"
                        while self.current_token and self.current_token.type != TokenType.DEDENT:
                            if self.current_token.type == TokenType.IDENTIFIER or self.current_token.type == TokenType.VALUE:
                                prop_name = self.current_token.lexeme
                                self.advance()
                                
                                # Expect colon
                                if self.current_token and self.current_token.type == TokenType.COLON:
                                    self.advance()
                                    
                                    # Get type
                                    prop_type = self.parse_type()
                                    
                                    from ..parser.ast import PropertyDeclaration
                                    properties.append(PropertyDeclaration(prop_name, prop_type, line_number=line_number))
                            else:
                                self.advance()  # Skip unknown tokens
                        
                        # Consume DEDENT
                        if self.current_token and self.current_token.type == TokenType.DEDENT:
                            self.advance()
                
                # Parse methods section
                if self.current_token and self.current_token.type == TokenType.METHODS:
                    self.advance()  # consume 'methods'
                    
                    # Skip colon
                    if self.current_token and self.current_token.type == TokenType.COLON:
                        self.advance()
                    
                    # Expect INDENT for methods
                    if self.current_token and self.current_token.type == TokenType.INDENT:
                        self.advance()
                        
                        # Parse method definitions
                        while self.current_token and self.current_token.type != TokenType.DEDENT:
                            if self.current_token.type == TokenType.DEFINE:
                                method = self.method_definition()
                                methods.append(method)
                            else:
                                self.advance()  # Skip unknown tokens
                        
                        # Consume DEDENT
                        if self.current_token and self.current_token.type == TokenType.DEDENT:
                            self.advance()
                
                # Consume final DEDENT (class body)
                if self.current_token and self.current_token.type == TokenType.DEDENT:
                    self.advance()
            
            return ClassDefinition(
                name=class_name,
                properties=properties,
                methods=methods,
                parent_classes=parent_classes,
                implemented_interfaces=implemented_interfaces,
                generic_parameters=generic_parameters,
                line_number=line_number
            )
        
        # Check for simple syntax: "class ClassName" or "class ClassName extends ParentClass"
        elif self.current_token.type == TokenType.CLASS:
            self.advance()  # consume 'class'
            
            # Get class name
            if self.current_token.type == TokenType.IDENTIFIER or self._can_be_identifier(self.current_token):
                class_name = self.current_token.lexeme
                self.advance()
                
                # Check for generic type parameters: class Container<T> or class Functor<F :: * -> *>
                generic_parameters = []
                class_type_param_kinds = {}
                if self.current_token and self.current_token.type == TokenType.LESS_THAN:
                    self.advance()  # Eat '<'
                    
                    # Parse type parameter names with optional kind annotations
                    if self.current_token.type == TokenType.IDENTIFIER or self._can_be_identifier(self.current_token):
                        pname = self.current_token.lexeme
                        generic_parameters.append(pname)
                        self.advance()
                        if self.current_token and self.current_token.type == TokenType.DOUBLE_COLON:
                            self.advance()  # Eat '::'
                            class_type_param_kinds[pname] = self.parse_kind_annotation()
                    
                    while self.current_token and self.current_token.type == TokenType.COMMA:
                        self.advance()  # Eat ','
                        if self.current_token.type == TokenType.IDENTIFIER or self._can_be_identifier(self.current_token):
                            pname = self.current_token.lexeme
                            generic_parameters.append(pname)
                            self.advance()
                            if self.current_token and self.current_token.type == TokenType.DOUBLE_COLON:
                                self.advance()  # Eat '::'
                                class_type_param_kinds[pname] = self.parse_kind_annotation()
                        else:
                            self.error("Expected type parameter name after comma")
                    
                    # Expect '>'
                    if self.current_token and self.current_token.type == TokenType.GREATER_THAN:
                        self.advance()  # Eat '>'
                    elif self.current_token and self.current_token.type == TokenType.RIGHT_SHIFT:
                        # Handle >> as > > for nested cases
                        from ..parser.lexer import Token
                        self.current_token = Token(TokenType.GREATER_THAN, '>', None,
                                                  self.current_token.line, self.current_token.column + 1)
                    else:
                        self.error("Expected '>' to close generic type parameters")
                
                # Check for inheritance: "extends ParentClass" or "inherits ParentClass"
                parent_classes = []
                if self.current_token and (self.current_token.type == TokenType.EXTENDS or 
                                          self.current_token.type == TokenType.INHERITS):
                    self.advance()  # consume 'extends' or 'inherits'
                    
                    # Get parent class name
                    if self.current_token.type == TokenType.IDENTIFIER:
                        parent_classes.append(self.current_token.lexeme)
                        self.advance()
                    else:
                        self.error(f"Expected parent class name after extends/inherits")
                
                # Check for interface implementation: "implements Interface1, Interface2"
                implemented_interfaces = []
                if self.current_token and self.current_token.type == TokenType.IMPLEMENTS:
                    self.advance()  # consume 'implements'
                    
                    # Get first interface name
                    if self.current_token.type == TokenType.IDENTIFIER:
                        implemented_interfaces.append(self.current_token.lexeme)
                        self.advance()
                        
                        # Get additional interfaces (comma-separated)
                        while self.current_token and self.current_token.type == TokenType.COMMA:
                            self.advance()  # consume comma
                            if self.current_token.type == TokenType.IDENTIFIER:
                                implemented_interfaces.append(self.current_token.lexeme)
                                self.advance()
                            else:
                                self.error("Expected interface name after comma")
                    else:
                        self.error("Expected interface name after 'implements'")
                
                # Skip NEWLINE before INDENT (emitted after class header line)
                while self.current_token and self.current_token.type == TokenType.NEWLINE:
                    self.advance()
                # Expect INDENT for class body
                if self.current_token and self.current_token.type == TokenType.INDENT:
                    self.advance()  # consume INDENT
                    
                    # Parse properties and methods
                    properties = []
                    methods = []
                    
                    while self.current_token and self.current_token.type != TokenType.DEDENT:
                        # Skip NEWLINE tokens between class members
                        if self.current_token.type == TokenType.NEWLINE:
                            self.advance()
                            continue
                        
                        # Check for access modifiers (private/public/protected)
                        access_modifier = 'public'  # default
                        if self.current_token.type in (TokenType.PRIVATE, TokenType.PUBLIC, TokenType.PROTECTED):
                            if self.current_token.type == TokenType.PRIVATE:
                                access_modifier = 'private'
                            elif self.current_token.type == TokenType.PUBLIC:
                                access_modifier = 'public'
                            elif self.current_token.type == TokenType.PROTECTED:
                                access_modifier = 'protected'
                            self.advance()  # consume access modifier
                        
                        # Now parse the property or method
                        if self.current_token.type == TokenType.PROPERTY:
                            prop = self.property_declaration_simple()
                            prop.access_modifier = access_modifier
                            properties.append(prop)
                        elif self.current_token.type == TokenType.SET:
                            # Handle 'set <name> to <value>' syntax for property declarations
                            prop = self.set_statement_as_property()
                            prop.access_modifier = access_modifier
                            properties.append(prop)
                        elif self.current_token.type == TokenType.METHOD:
                            method = self.method_definition_simple()
                            method.access_modifier = access_modifier
                            methods.append(method)
                        elif self.current_token.type == TokenType.FUNCTION:
                            # Parse as function, convert to method
                            from ..parser.ast import MethodDefinition
                            func = self.function_definition_short()
                            method = MethodDefinition(func.name, func.parameters, func.body, func.return_type, is_static=False, access_modifier=access_modifier, line_number=func.line_number)
                            methods.append(method)
                        elif self.current_token.type == TokenType.IDENTIFIER:
                            # Check for special keywords
                            lexeme = self.current_token.lexeme.strip().lower()
                            if lexeme == "property":
                                prop = self.property_declaration_simple()
                                prop.access_modifier = access_modifier
                                properties.append(prop)
                            elif lexeme == "method":
                                method = self.method_definition_simple()
                                method.access_modifier = access_modifier
                                methods.append(method)
                            elif lexeme == "abstract":
                                # Abstract method: public abstract function name
                                self.advance()  # Eat 'abstract'
                                if self.current_token.type == TokenType.FUNCTION:
                                    # Parse abstract method signature (no body)
                                    from ..parser.ast import AbstractMethodDefinition
                                    line_num = self.current_token.line
                                    self.advance()  # Eat 'function'
                                    
                                    # Get function name (can be multi-word)
                                    function_name_parts = []
                                    while (self.current_token and 
                                           (self.current_token.type == TokenType.IDENTIFIER or self._can_be_identifier(self.current_token)) and
                                           self.current_token.type not in (TokenType.WITH, TokenType.RETURNS, TokenType.NEWLINE)):
                                        function_name_parts.append(self.current_token.lexeme)
                                        self.advance()
                                        if self.current_token and self.current_token.type in (TokenType.WITH, TokenType.RETURNS, TokenType.NEWLINE):
                                            break
                                    
                                    if not function_name_parts:
                                        self.error("Expected function name after 'function'")
                                    
                                    function_name = "_".join(function_name_parts)
                                    
                                    # Parse parameters if present
                                    parameters = []
                                    if self.current_token and self.current_token.type == TokenType.WITH:
                                        self.advance()  # consume 'with'
                                        parameters, _ = self.parameter_list()
                                    
                                    # Parse return type
                                    return_type = None
                                    if self.current_token and self.current_token.type == TokenType.RETURNS:
                                        self.advance()  # consume 'returns'
                                        return_type = self.parse_type()
                                    
                                    # Consume NEWLINE if present
                                    if self.current_token and self.current_token.type == TokenType.NEWLINE:
                                        self.advance()
                                    
                                    # Create abstract method
                                    abstract_method = AbstractMethodDefinition(function_name, parameters, return_type, line_num)
                                    abstract_method.access_modifier = access_modifier
                                    methods.append(abstract_method)
                                else:
                                    self.error("Expected 'function' after 'abstract' in class body")
                            elif lexeme == "static":
                                self.advance() # Eat 'static'
                                if self.current_token.type == TokenType.FUNCTION:
                                    # Parse as function, convert to static method
                                    from ..parser.ast import MethodDefinition
                                    func = self.function_definition_short()
                                    method = MethodDefinition(func.name, func.parameters, func.body, func.return_type, is_static=True, access_modifier=access_modifier, line_number=func.line_number)
                                    methods.append(method)
                                elif self.current_token.type == TokenType.METHOD or (self.current_token.type == TokenType.IDENTIFIER and self.current_token.lexeme.lower() == 'method'):
                                    method = self.method_definition_simple()
                                    method.is_static = True
                                    method.access_modifier = access_modifier
                                    methods.append(method)
                                else:
                                    self.error(f"Expected 'function' or 'method' after 'static', got '{self.current_token.type}'")
                            elif lexeme == "pass":
                                # Allow pass statement in class body
                                self.advance()
                            else:
                                self.error(f"Expected 'property' or 'method' in class body, got '{self.current_token.lexeme}'")
                                self.advance()
                        else:
                            self.error(f"Unexpected token in class body: {self.current_token.type}")
                            self.advance()
                    
                    if self.current_token and self.current_token.type == TokenType.DEDENT:
                        self.advance()  # consume DEDENT
                    
                    # Consume END_CLASS if present
                    if self.current_token and self.current_token.type == TokenType.END_CLASS:
                        self.advance()  # consume combined 'end class' token
                    elif self.current_token and self.current_token.type == TokenType.END:
                        self.advance()  # consume 'end'
                        # consume 'class' if present
                        if self.current_token and self.current_token.type == TokenType.CLASS:
                            self.advance()
                    
                    return ClassDefinition(
                        name=class_name,
                        properties=properties,
                        methods=methods,
                        parent_classes=parent_classes,
                        implemented_interfaces=implemented_interfaces,
                        generic_parameters=generic_parameters,
                        type_param_kinds=class_type_param_kinds,
                        line_number=line_number
                    )
                else:
                    self.error("Expected indented class body after class name")
            else:
                self.error("Expected class name after 'class'")
        
        # Handle verbose syntax (existing code)
        elif self.current_token.type == TokenType.IDENTIFIER:
            # Get the full text of the token and check if it contains "Create a class"
            full_text = self.current_token.lexeme
            parts = full_text.lower().split()
            
            # Check if this is a class definition
            if "create" in parts and "class" in parts and "called" in parts:
                # Extract the class name (after "called")
                class_name = None
                generic_parameters = []
                
                try:
                    # Extract the class name (should be after "called")
                    called_index = parts.index("called")
                    if called_index + 1 < len(parts):
                        class_name = full_text.split()[called_index + 1]
                    
                    # Check for generic type parameters
                    if "with" in parts and "generic" in parts and "type" in parts and "parameter" in parts and "extends" in parts:
                        try:
                            # Find the generic parameter name and its constraint
                            param_index = parts.index("parameter")
                            extends_index = parts.index("extends")
                            
                            if param_index > 0 and param_index < extends_index:
                                # Get T or N, which is the actual parameter name
                                # It should be right before 'that extends'
                                param_name = None
                                for i in range(param_index + 1, extends_index):
                                    if full_text.split()[i].lower() != "that":
                                        param_name = full_text.split()[i]
                                        break
                                
                                if not param_name:
                                    # Fallback to the token right after "parameter"
                                    param_name = full_text.split()[param_index + 1]
                                
                                constraint_type = full_text.split()[extends_index + 1].rstrip(".,;")
                                
                                # Create the type parameter with constraint
                                generic_parameters.append(
                                    TypeParameter(
                                        name=param_name,
                                        bounds=[constraint_type],
                                        line_number=line_number
                                    )
                                )
                        except (ValueError, IndexError):
                            pass
                except (ValueError, IndexError):
                    pass
                
                # If we successfully extracted the class name, we can create the ClassDefinition
                if class_name:
                    # Advance past this token
                    self.advance()
                    
                    # Skip period if present
                    if self.current_token and self.current_token.type == TokenType.DOT:
                        self.advance()
                    
                    # Create and return the class definition
                    return ClassDefinition(
                        name=class_name,
                        properties=[],
                        methods=[],
                        parent_classes=[],
                        implemented_interfaces=[],
                        generic_parameters=generic_parameters,
                        line_number=line_number
                    )
        
        # If we get here, we couldn't parse as a single-token class definition
        # Generate a syntax error
        self.error("Expected class definition")
    
    def struct_definition(self, packed=False):
        """Parse a struct definition.
        
        Syntax:
            struct StructName
                field_name as Type
                field_name as Type with N bits
            end
            
            packed struct PackedStructName
                field_name as Type with N bits
            end
            
            aligned struct AlignedStructName to 64 bytes
                field_name as Type
            end
        """
        line_number = self.current_token.line
        self.advance()  # consume 'struct'
        
        # Get struct name - can be identifier or contextual keyword
        if not self.current_token or not self.current_token.lexeme:
            self.error("Expected struct name after 'struct'")
        
        struct_name = self.current_token.lexeme
        self.advance()
        
        # Check for alignment: "aligned to 64 bytes" or "to 64 bytes"
        alignment = None
        if self.current_token and self.current_token.type == TokenType.ALIGN:
            self.advance()  # consume 'aligned'
            
            # Expect 'to'
            if self.current_token and self.current_token.type == TokenType.TO:
                self.advance()  # consume 'to'
                
                # Get alignment value
                if self.current_token and self.current_token.type == TokenType.INTEGER_LITERAL:
                    alignment = int(self.current_token.lexeme)
                    self.advance()
                    
                    # Optional "bytes" keyword
                    if self.current_token and self.current_token.type == TokenType.IDENTIFIER:
                        if self.current_token.lexeme.lower() == "bytes":
                            self.advance()
                else:
                    self.error("Expected alignment value after 'to'")
            else:
                self.error("Expected 'to' after 'aligned'")
        elif self.current_token and self.current_token.type == TokenType.TO:
            # Direct "to N bytes" without "aligned" keyword
            self.advance()  # consume 'to'
            
            # Get alignment value
            if self.current_token and self.current_token.type == TokenType.INTEGER_LITERAL:
                alignment = int(self.current_token.lexeme)
                self.advance()
                
                # Optional "bytes" keyword
                if self.current_token and self.current_token.type == TokenType.IDENTIFIER:
                    if self.current_token.lexeme.lower() == "bytes":
                        self.advance()
            else:
                self.error("Expected alignment value after 'to'")
        
        # Expect INDENT or newline + INDENT
        if self.current_token and self.current_token.type == TokenType.NEWLINE:
            self.advance()
        
        if self.current_token and self.current_token.type != TokenType.INDENT:
            self.error("Expected indented struct body")
        
        self.advance()  # consume INDENT
        
        # Parse fields and methods (C++-style structs)
        fields = []
        methods = []
        while self.current_token and self.current_token.type != TokenType.DEDENT:
            if self.current_token.type == TokenType.END:
                break
            
            # Check for method definition (C++-style struct with methods)
            if self.current_token.type == TokenType.METHOD:
                methods.append(self.method_definition_simple())
                continue
            
            # Skip newlines between fields/methods
            if self.current_token.type == TokenType.NEWLINE:
                self.advance()
                continue
            
            # Otherwise, parse as field
            # Field name can be an identifier or keyword (check lexeme exists)
            if self.current_token and self.current_token.lexeme and self.current_token.type != TokenType.METHOD:
                field_name = self.current_token.lexeme
                self.advance()
                
                # Expect "as Type"
                if self.current_token and self.current_token.type == TokenType.AS:
                    self.advance()  # consume 'as'
                    
                    # Parse type annotation
                    type_annotation = self.parse_type()
                    
                    # Check for bit width: "with N bits"
                    bit_width = None
                    if self.current_token and self.current_token.type == TokenType.WITH:
                        self.advance()  # consume 'with'
                        
                        if self.current_token and self.current_token.type == TokenType.INTEGER_LITERAL:
                            bit_width = int(self.current_token.lexeme)
                            self.advance()
                            
                            # Optional "bits" keyword
                            if self.current_token and self.current_token.type == TokenType.IDENTIFIER:
                                if self.current_token.lexeme.lower() == "bits":
                                    self.advance()
                        else:
                            self.error("Expected bit width after 'with'")
                    
                    fields.append(StructField(
                        name=field_name,
                        type_annotation=type_annotation,
                        bit_width=bit_width
                    ))
                    
                    # Optional newline
                    if self.current_token and self.current_token.type == TokenType.NEWLINE:
                        self.advance()
                else:
                    self.error(f"Expected 'as' after field name '{field_name}'")
            else:
                self.error(f"Expected field name, got {self.current_token.type}")
        
        # Consume DEDENT or END
        if self.current_token and self.current_token.type == TokenType.DEDENT:
            self.advance()
        
        if self.current_token and self.current_token.type == TokenType.END:
            self.advance()
        
        return StructDefinition(
            name=struct_name,
            fields=fields,
            methods=methods,
            packed=packed,
            alignment=alignment,
            line_number=line_number
        )
    
    def union_definition(self):
        """Parse a union definition.
        
        Syntax:
            union UnionName
                field_name as Type
                field_name as Type
            end
        """
        line_number = self.current_token.line
        self.advance()  # consume 'union'
        
        # Get union name - can be identifier or contextual keyword
        if not self.current_token or not self.current_token.lexeme:
            self.error("Expected union name after 'union'")
        
        union_name = self.current_token.lexeme
        self.advance()
        
        # Expect INDENT or newline + INDENT
        if self.current_token and self.current_token.type == TokenType.NEWLINE:
            self.advance()
        
        if self.current_token and self.current_token.type != TokenType.INDENT:
            self.error("Expected indented union body")
        
        self.advance()  # consume INDENT
        
        # Parse fields
        fields = []
        while self.current_token and self.current_token.type != TokenType.DEDENT:
            if self.current_token.type == TokenType.END:
                break
            
            # Field name can be an identifier or keyword (check lexeme exists)
            if self.current_token and self.current_token.lexeme:
                field_name = self.current_token.lexeme
                self.advance()
                
                # Expect "as Type"
                if self.current_token and self.current_token.type == TokenType.AS:
                    self.advance()  # consume 'as'
                    
                    # Parse type annotation
                    type_annotation = self.parse_type()
                    
                    fields.append(StructField(
                        name=field_name,
                        type_annotation=type_annotation,
                        bit_width=None
                    ))
                    
                    # Optional newline
                    if self.current_token and self.current_token.type == TokenType.NEWLINE:
                        self.advance()
                else:
                    self.error(f"Expected 'as' after field name '{field_name}'")
            else:
                self.error(f"Expected field name, got {self.current_token.type}")
        
        # Consume DEDENT or END
        if self.current_token and self.current_token.type == TokenType.DEDENT:
            self.advance()
        
        if self.current_token and self.current_token.type == TokenType.END:
            self.advance()
        
        return UnionDefinition(
            name=union_name,
            fields=fields,
            line_number=line_number
        )
    
    def enum_definition(self):
        """Parse an enum definition.
        
        Syntax:
            enum EnumName
                MemberName
                MemberName = value
                MemberName = "string_value"
            end
            
        Examples:
            enum Color
                Red
                Green
                Blue
            end
            
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
        """
        line_number = self.current_token.line
        self.advance()  # consume 'enum'
        
        # Get enum name (can be identifier or keyword)
        if not self.current_token or not self.current_token.lexeme:
            self.error("Expected enum name after 'enum'")
        
        enum_name = self.current_token.lexeme
        self.advance()
        
        # Expect INDENT or newline + INDENT
        if self.current_token and self.current_token.type == TokenType.NEWLINE:
            self.advance()
        
        if self.current_token and self.current_token.type != TokenType.INDENT:
            self.error("Expected indented enum body")
        
        self.advance()  # consume INDENT
        
        # Parse enum members
        members = []
        auto_value = 0  # For auto-numbered enums
        
        while self.current_token and self.current_token.type != TokenType.DEDENT:
            if self.current_token.type == TokenType.END:
                break
            
            # Skip newlines
            if self.current_token.type == TokenType.NEWLINE:
                self.advance()
                continue
            
            # Member name (can be identifier or keyword - use lexeme)
            if not self.current_token or not self.current_token.lexeme:
                self.error(f"Expected enum member name")
            
            member_name = self.current_token.lexeme
            self.advance()
            
            # Check for explicit value: = value
            member_value = None
            if self.current_token and self.current_token.type == TokenType.EQUALS:
                self.advance()  # consume '='
                
                # Parse the value (can be integer or string)
                if self.current_token.type == TokenType.INTEGER_LITERAL:
                    member_value = Literal('integer', int(self.current_token.lexeme))
                    auto_value = int(self.current_token.lexeme) + 1  # Update auto value
                    self.advance()
                elif self.current_token.type == TokenType.STRING_LITERAL:
                    member_value = Literal('string', self.current_token.lexeme)
                    self.advance()
                elif self.current_token.type == TokenType.FLOAT_LITERAL:
                    member_value = Literal('float', float(self.current_token.lexeme))
                    self.advance()
                else:
                    self.error(f"Expected integer or string value after '=', got {self.current_token.type}")
            else:
                # Auto-number: use current auto_value
                member_value = Literal('integer', auto_value)
                auto_value += 1
            
            members.append(EnumMember(
                name=member_name,
                value=member_value,
                line_number=self.current_token.line if self.current_token else line_number
            ))
            
            # Optional newline after member
            if self.current_token and self.current_token.type == TokenType.NEWLINE:
                self.advance()
        
        # Consume DEDENT or END
        if self.current_token and self.current_token.type == TokenType.DEDENT:
            self.advance()
        
        if self.current_token and self.current_token.type == TokenType.END:
            self.advance()
        
        return EnumDefinition(
            name=enum_name,
            members=members,
            line_number=line_number
        )
    
    def set_statement_as_property(self):
        """Parse 'set <name> to <Type>' as a class property declaration."""
        line_number = self.current_token.line
        self.advance()  # consume 'set'
        
        # Get property name
        if not self.current_token or not self.current_token.lexeme:
            self.error("Expected property name after 'set'")
            return None
        
        prop_name = self.current_token.lexeme
        self.advance()
        
        # Expect 'to'
        if self.current_token and self.current_token.type == TokenType.TO:
            self.advance()  # consume 'to'
        else:
            self.error(f"Expected 'to' after property name '{prop_name}'")
        
        # Get the type annotation (not a value, but a type like "Integer" or "List of Float")
        type_annotation = self.parse_type()
        
        # Consume newline if present
        if self.current_token and self.current_token.type == TokenType.NEWLINE:
            self.advance()
        
        return PropertyDeclaration(prop_name, type_annotation, None, line_number)
    
    def property_declaration_simple(self):
        """Parse simple property declaration: 'property name as Type'"""
        self.advance()  # consume 'property'
        
        # Accept any token as property name (including keywords)
        if not self.current_token or not self.current_token.lexeme:
            self.error("Expected property name")
            return None
        
        prop_name = self.current_token.lexeme
        self.advance()
        
        # Optional type annotation
        type_annotation = None
        if self.current_token and self.current_token.type == TokenType.AS:
            self.advance()  # consume 'as'
            type_annotation = self.parse_type()
        
        # Consume newline if present
        if self.current_token and self.current_token.type == TokenType.NEWLINE:
            self.advance()
        
        return PropertyDeclaration(prop_name, type_annotation)
    
    def method_definition_simple(self):
        """Parse simple method definition: 'method name [with params] [returns Type]' with body"""
        self.advance()  # consume 'method'
        
        if not self.current_token or not self.current_token.lexeme:
            self.error("Expected method name")
            return None
        
        method_name = self.current_token.lexeme
        self.advance()
        
        # Optional parameters: "with param1 as Type1 and param2 as Type2"
        parameters = []
        if self.current_token and self.current_token.type == TokenType.WITH:
            self.advance()  # consume 'with'
            parameters, variadic = self.parameter_list()
        
        # Optional return type: "returns Type"
        return_type = None
        if self.current_token and self.current_token.type == TokenType.RETURNS:
            self.advance()  # consume 'returns'
            return_type = self.parse_type()
        
        # Expect INDENT for method body
        while self.current_token and self.current_token.type == TokenType.NEWLINE:
            self.advance()
        if self.current_token and self.current_token.type == TokenType.INDENT:
            self.advance()  # consume INDENT
            
            # Parse method body
            body = []
            while self.current_token and self.current_token.type != TokenType.DEDENT:
                if self.current_token.type in (TokenType.END, TokenType.END_METHOD):
                    break
                stmt = self.statement()
                if stmt:
                    body.append(stmt)
            
            if self.current_token and self.current_token.type == TokenType.DEDENT:
                self.advance()  # consume DEDENT
            
            # Optional explicit 'end' for method - could be END token or END_METHOD combined token
            if self.current_token and self.current_token.type == TokenType.END_METHOD:
                self.advance()  # consume combined 'end method' token
            elif self.current_token and self.current_token.type == TokenType.END:
                end_line = self.current_token.line
                self.advance()  # consume 'end'
                # Only consume 'method' if it's on the same line (for "end method" syntax)
                # Don't consume if separated by newline/indent (next method definition)
                if (self.current_token and 
                    self.current_token.type == TokenType.METHOD and
                    self.current_token.line == end_line):
                    self.advance()
        else:
            body = []
        
        return MethodDefinition(method_name, parameters, body, return_type)
        
    def property_declaration(self):
        """Parse a property declaration."""
        # Syntax: It has a <type> property called <identifier>
        line_number = self.current_token.line
        
        # Eat 'it'
        self.eat(TokenType.IT)
        
        # Eat 'has'
        self.eat(TokenType.HAS)
        
        # Skip optional 'a'
        if self.current_token.type == TokenType.IDENTIFIER and self.current_token.lexeme.lower() == 'a':
            self.advance()
            
        # Get the property type
        if self.current_token.type == TokenType.TYPE:
            prop_type = self.current_token.value
            self.advance()
        else:
            self.error("Expected a property type")
            
        # Eat 'property'
        self.eat(TokenType.PROPERTY)
        
        # Eat 'called'
        self.eat(TokenType.CALLED)
        
        # Get the property name
        if self.current_token.type == TokenType.IDENTIFIER:
            prop_name = self.current_token.value
            self.advance()
        else:
            self.error("Expected a property name")
            
        return PropertyDeclaration(prop_type, prop_name, line_number)
        
    def method_definition(self):
        """Parse a method definition."""
        # Syntax: Define a method called <identifier> that takes <parameter_list> and returns <type>
        line_number = self.current_token.line
        
        # Eat 'define'
        self.eat(TokenType.DEFINE)
        
        # Skip optional 'a'
        if self.current_token.type == TokenType.A:
            self.advance()
        elif self.current_token.type == TokenType.IDENTIFIER and self.current_token.lexeme.lower() == 'a':
            self.advance()
            
        # Eat 'method'
        if self.current_token.type == TokenType.METHOD:
            self.advance()
        elif self.current_token.type == TokenType.IDENTIFIER and self.current_token.lexeme.lower() == 'method':
            self.advance()
        else:
            self.error("Expected 'method'")
            
        # Eat 'called'
        self.eat(TokenType.CALLED)
        
        # Get the method name - handle both IDENTIFIER and reserved word tokens
        method_name = None
        if self.current_token.type == TokenType.IDENTIFIER:
            method_name = self.current_token.lexeme
            self.advance()
        elif self._can_be_identifier(self.current_token):
            # Handle reserved words that can be method names (like 'get', 'set', 'add')
            method_name = self.current_token.lexeme
            self.advance()
        else:
            self.error("Expected method name")
            
        # Check if method has parameters: "that takes" or just "that returns"
        if self.current_token and self.current_token.type == TokenType.THAT:
            self.advance()  # consume 'that'
            
            parameters = []
            variadic = False
            return_type = None
            
            # Check for parameters: "takes a parameter"
            if self.current_token and self.current_token.type == TokenType.TAKES:
                self.advance()  # consume 'takes'
                
                # Parse parameter list
                parameters, variadic = self.parameter_list()
                
                # Check for return type: "and returns Type" or just "returns Type"
                if self.current_token and self.current_token.type == TokenType.AND:
                    self.advance()  # consume 'and'
                
                if self.current_token and self.current_token.type == TokenType.RETURNS:
                    self.advance()  # consume 'returns'
                    return_type = self.parse_type()
            
            # No parameters, just return type: "that returns Type"
            elif self.current_token and self.current_token.type == TokenType.RETURNS:
                self.advance()  # consume 'returns'
                return_type = self.parse_type()
        else:
            # No 'that' keyword - simple method with no params or return
            parameters = []
            variadic = False
            return_type = None
            
        # Parse the method body
        body = []
        
        # Check for INDENT (method body)
        while self.current_token and self.current_token.type == TokenType.NEWLINE:
            self.advance()
        if self.current_token and self.current_token.type == TokenType.INDENT:
            self.advance()  # consume INDENT
            
            # Parse statements until DEDENT
            while self.current_token and self.current_token.type != TokenType.DEDENT and self.current_token.type != TokenType.EOF:
                statement = self.statement()
                if statement:
                    body.append(statement)
            
            # Consume DEDENT
            if self.current_token and self.current_token.type == TokenType.DEDENT:
                self.advance()
        
        # Alternative: check for 'end' keyword (verbose syntax)
        elif self.current_token and not (self.current_token.type == TokenType.IDENTIFIER and self.current_token.lexeme.lower() == 'end'):
            # Parse statements until 'end'
            while (self.current_token and self.current_token.type != TokenType.EOF and 
                   not (self.current_token.type == TokenType.IDENTIFIER and 
                        self.current_token.lexeme.lower() == 'end')):
                statement = self.statement()
                if statement:
                    body.append(statement)
                
            # Eat 'end'
            if self.current_token and self.current_token.type == TokenType.IDENTIFIER and self.current_token.lexeme.lower() == 'end':
                self.advance()
                
                # Support for explicit "End method" syntax
                if (self.current_token and self.current_token.type == TokenType.IDENTIFIER and 
                    self.current_token.lexeme.lower() == 'method'):
                    self.advance()
                    
                # Support for explicit "End the method" syntax
                elif (self.current_token and self.current_token.type == TokenType.IDENTIFIER and 
                      self.current_token.lexeme.lower() == 'the' and self.peek() and 
                      self.peek().type == TokenType.IDENTIFIER and 
                      self.peek().lexeme.lower() == 'method'):
                    self.advance()  # Eat 'the'
                    self.advance()  # Eat 'method'
                    
                # Optional period after end
                if (self.current_token and self.current_token.type == TokenType.DOT):
                    self.advance()
            
        return MethodDefinition(method_name, parameters, return_type, body, line_number)
        
    def _parse_else_or_elseif(self):
        """
        Parse else/else-if blocks, handling nested else-if chains.
        Returns a list of statements for the else block, which may contain
        another IfStatement for else-if chains.
        """
        if not self.current_token:
            return None
            
        # Check for ELSE_IF token
        if self.current_token.type == TokenType.ELSE_IF:
            line_number = self.current_token.line
            self.advance()  # Consume ELSE_IF
            
            # Parse the condition for this else-if
            condition = self.expression()
            
            if condition is None:
                self.error("Failed to parse else-if condition - expression returned None")
                return None
            
            # Optional comma after condition
            if self.current_token and self.current_token.type == TokenType.COMMA:
                self.advance()
            
            # Skip optional 'then'
            if self.current_token and self.current_token.type == TokenType.IDENTIFIER and self.current_token.lexeme.lower() == 'then':
                self.advance()
            
            # Skip NEWLINE before INDENT
            while self.current_token and self.current_token.type == TokenType.NEWLINE:
                self.advance()
            # Expect INDENT for block-based syntax
            if self.current_token and self.current_token.type == TokenType.INDENT:
                self.advance()  # Consume INDENT
                
                # Parse then block until DEDENT
                then_block = []
                while (self.current_token and 
                       self.current_token.type != TokenType.EOF and
                       self.current_token.type != TokenType.DEDENT and
                       self.current_token.type != TokenType.ELSE and
                       self.current_token.type != TokenType.ELSE_IF):
                    statement = self.statement()
                    if statement:
                        then_block.append(statement)
                
                # Consume DEDENT
                if self.current_token and self.current_token.type == TokenType.DEDENT:
                    self.advance()
            else:
                # Fallback: Parse then block with 'end' keyword (old style)
                then_block = []
                while (self.current_token and self.current_token.type != TokenType.EOF and
                       self.current_token.type != TokenType.ELSE and
                       self.current_token.type != TokenType.ELSE_IF and
                       self.current_token.type != TokenType.END and
                       not (self.current_token.type == TokenType.IDENTIFIER and 
                            self.current_token.lexeme.lower() == 'end')):
                    statement = self.statement()
                    if statement:
                        then_block.append(statement)
            
            # Recursively check for more else-if or final else
            else_block = self._parse_else_or_elseif()
            
            # Create an IfStatement for this else-if and wrap it in a list
            # This creates the nested structure: else contains [IfStatement(...)]
            return [IfStatement(condition, then_block, else_block, line_number)]
        
        # Check for plain ELSE token
        elif self.current_token.type == TokenType.ELSE:
            self.advance()  # Consume ELSE
            
            # Skip NEWLINE before INDENT
            while self.current_token and self.current_token.type == TokenType.NEWLINE:
                self.advance()
            # Expect INDENT for block-based syntax
            if self.current_token and self.current_token.type == TokenType.INDENT:
                self.advance()  # Consume INDENT
                
                # Parse else block until DEDENT
                else_block = []
                while (self.current_token and 
                       self.current_token.type != TokenType.EOF and
                       self.current_token.type != TokenType.DEDENT):
                    statement = self.statement()
                    if statement:
                        else_block.append(statement)
                
                # Consume DEDENT
                if self.current_token and self.current_token.type == TokenType.DEDENT:
                    self.advance()
            else:
                # Fallback: Parse else block with 'end' keyword (old style)
                else_block = []
                while (self.current_token and self.current_token.type != TokenType.EOF and
                       self.current_token.type != TokenType.END and
                       not (self.current_token.type == TokenType.IDENTIFIER and 
                            self.current_token.lexeme.lower() == 'end')):
                    statement = self.statement()
                    if statement:
                        else_block.append(statement)
            
            return else_block
        
        # No else or else-if found
        return None
        
    def if_statement(self):
        """Parse an if statement."""
        # Syntax: If <condition> [then] <statement_block> [Otherwise <statement_block>]
        line_number = self.current_token.line
        
        # Eat 'if'
        self.eat(TokenType.IF)

        # Check for TypeGuard pattern: IDENTIFIER IS A/AN <type_keyword> [then]
        # e.g.  If x is a string then ... End if.
        _type_kws = (
            TokenType.STRING, TokenType.INTEGER, TokenType.FLOAT, TokenType.BOOLEAN,
            TokenType.LIST, TokenType.DICTIONARY, TokenType.NUMBER, TokenType.OBJECT,
        )
        if (self.current_token and self.current_token.type == TokenType.IDENTIFIER and
                self.current_token_index + 3 < len(self.tokens) and
                self.tokens[self.current_token_index + 1].type == TokenType.IS and
                self.tokens[self.current_token_index + 2].type in (TokenType.A, TokenType.AN) and
                self.tokens[self.current_token_index + 3].type in _type_kws):
            condition_name = self.current_token.lexeme
            tg_condition = Identifier(condition_name, line_number)
            self.advance()   # consume IDENTIFIER
            self.advance()   # consume IS
            self.advance()   # consume A/AN
            type_name = self.current_token.lexeme.lower()
            self.advance()   # consume type keyword
            # Skip optional IDENTIFIER("then")
            if (self.current_token and self.current_token.type == TokenType.IDENTIFIER and
                    self.current_token.lexeme.lower() == 'then'):
                self.advance()
            # Skip optional INDENT
            if self.current_token and self.current_token.type == TokenType.INDENT:
                self.advance()
            # Consume body tokens until END_IF (skip everything - body not validated)
            body = []
            while self.current_token and self.current_token.type not in (
                    TokenType.END_IF, TokenType.EOF):
                self.advance()
            # Consume END_IF
            if self.current_token and self.current_token.type == TokenType.END_IF:
                self.advance()
            # Consume optional DOT
            if self.current_token and self.current_token.type == TokenType.DOT:
                self.advance()
            return TypeGuard(tg_condition, type_name, body, line_number)

        # Parse condition
        condition = self.expression()
        
        # Check if condition was successfully parsed
        if condition is None:
            self.error("Failed to parse if condition - expression returned None")
            return None
        
        # Optional comma after condition
        if self.current_token and self.current_token.type == TokenType.COMMA:
            self.advance()
        
        # Skip optional 'then'
        if self.current_token and self.current_token.type == TokenType.IDENTIFIER and self.current_token.lexeme.lower() == 'then':
            self.advance()
        
        # Skip NEWLINE before INDENT (emitted after if-condition line)
        while self.current_token and self.current_token.type == TokenType.NEWLINE:
            self.advance()
        # Expect INDENT for block-based syntax
        if self.current_token and self.current_token.type == TokenType.INDENT:
            self.advance()  # Consume INDENT
            
            # Parse then block until DEDENT
            then_block = []
            while (self.current_token and 
                   self.current_token.type != TokenType.EOF and
                   self.current_token.type != TokenType.DEDENT and
                   self.current_token.type != TokenType.ELSE):
                statement = self.statement()
                if statement:
                    then_block.append(statement)
            
            # Consume DEDENT
            if self.current_token and self.current_token.type == TokenType.DEDENT:
                self.advance()
        else:
            # Fallback: Parse then block with 'end' keyword (old style)
            then_block = []
            while (self.current_token and self.current_token.type != TokenType.EOF and
                   self.current_token.type != TokenType.ELSE and
                   self.current_token.type != TokenType.END and
                   not (self.current_token.type == TokenType.IDENTIFIER and 
                        self.current_token.lexeme.lower() == 'end')):
                statement = self.statement()
                if statement:
                    then_block.append(statement)
            
        # Check for else/else-if blocks
        else_block = self._parse_else_or_elseif()
            
        # Eat 'end' - check for both TokenType.END and IDENTIFIER with lexeme 'end'
        if self.current_token and (self.current_token.type == TokenType.END or
                                   (self.current_token.type == TokenType.IDENTIFIER and 
                                    self.current_token.lexeme.lower() == 'end')):
            self.advance()
            
            # Support for explicit "End if" syntax
            if (self.current_token and self.current_token.type == TokenType.IF):
                self.advance()
            
            # Optional period after end
            if (self.current_token and self.current_token.type == TokenType.DOT):
                self.advance()
        
        return IfStatement(condition, then_block, else_block, line_number)
    
    def labeled_loop_statement(self):
        """Parse a labeled loop: label name: while/for ..."""  
        # This is called when we see LABEL token in statement()
        # The actual label parsing is done in while_loop() and for_loop()
        # So just delegate to the appropriate loop parser
        
        # while_loop() and for_loop() will consume the label token
        if self.current_token.type == TokenType.LABEL:
            # Peek ahead to see if it's while or for
            # Look past: label <name> : <loop_type>
            lookahead = 1
            if self.peek(lookahead) and self.peek(lookahead).type == TokenType.IDENTIFIER:
                lookahead += 1  # skip name
                if self.peek(lookahead) and self.peek(lookahead).type == TokenType.COLON:
                    lookahead += 1  # skip colon
                    next_token = self.peek(lookahead)
                    if next_token:
                        if next_token.type == TokenType.WHILE:
                            return self.while_loop()
                        elif next_token.type in (TokenType.FOR, TokenType.FOR_EACH, TokenType.REPEAT):
                            return self.for_loop()
        
        self.error("Expected 'while' or 'for' after label declaration")
        
    def while_loop(self):
        """Parse a while loop.
        
        Supports:
            while <condition> ... end
            label name: while <condition> ... end
            while <condition> ... else ... end
        """
        line_number = self.current_token.line
        
        # Check for optional label before while
        label = None
        if self.current_token.type == TokenType.LABEL:
            self.advance()  # consume 'label'
            if self.current_token.type == TokenType.IDENTIFIER:
                label = self.current_token.lexeme
                self.advance()  # consume label name
                # Expect colon after label name
                if self.current_token and self.current_token.type == TokenType.COLON:
                    self.advance()
            else:
                self.error("Expected label name after 'label'")
        
        # Eat 'while'
        self.eat(TokenType.WHILE)
        
        # Parse condition
        condition = self.expression()
        
        # Optional comma after condition
        if self.current_token and self.current_token.type == TokenType.COMMA:
            self.advance()
        
        # Expect INDENT for block-based syntax
        if self.current_token and self.current_token.type == TokenType.INDENT:
            self.advance()  # Consume INDENT
            
            # Parse body until DEDENT
            body = []
            while (self.current_token and 
                   self.current_token.type != TokenType.EOF and
                   self.current_token.type != TokenType.DEDENT):
                statement = self.statement()
                if statement:
                    body.append(statement)
            
            # Consume DEDENT
            if self.current_token and self.current_token.type == TokenType.DEDENT:
                self.advance()
        else:
            # Fallback: Parse body with 'end' keyword (old style)
            body = []
            while (self.current_token and self.current_token.type != TokenType.EOF and
                   self.current_token.type != TokenType.END and
                   self.current_token.type != TokenType.END_WHILE and
                   not (self.current_token.type == TokenType.IDENTIFIER and 
                        self.current_token.lexeme.lower() == 'end')):
                statement = self.statement()
                if statement:
                    body.append(statement)
                
        # Eat 'end while' (single token) or 'end' + 'while' (two tokens)
        if self.current_token and self.current_token.type == TokenType.END_WHILE:
            # Single END_WHILE token
            self.advance()
        elif self.current_token and (self.current_token.type == TokenType.END or
                                     (self.current_token.type == TokenType.IDENTIFIER and 
                                      self.current_token.lexeme.lower() == 'end')):
            self.advance()
            
            # Support for explicit "End while" syntax
            if (self.current_token and self.current_token.type == TokenType.WHILE):
                self.advance()
                
            # Optional period after end
            if (self.current_token and self.current_token.type == TokenType.DOT):
                self.advance()
        
        # Check for else block (executes if loop completes without break)
        else_body = None
        if self.current_token and self.current_token.type == TokenType.ELSE:
            self.advance()  # consume 'else'
            
            # Skip NEWLINE/INDENT
            while (self.current_token and 
                   self.current_token.type in (TokenType.NEWLINE, TokenType.INDENT)):
                self.advance()
            
            # Parse else body
            else_body = []
            while (self.current_token and 
                   self.current_token.type != TokenType.EOF and
                   self.current_token.type != TokenType.DEDENT and
                   self.current_token.type != TokenType.END):
                statement = self.statement()
                if statement:
                    else_body.append(statement)
            
            # Consume DEDENT/END after else
            if self.current_token and self.current_token.type in (TokenType.DEDENT, TokenType.END):
                self.advance()
            
        return WhileLoop(condition, body, line_number, else_body, label)
        
    def _peek_next(self):
        """Return the next token without consuming it (alias for peek(1))."""
        return self.peek(1)

    def parse_conditional_compilation(self):
        """Parse a compile-time conditional block.

        Supported syntax variants::

            when target os is "linux"
                ...body...
            end

            when target arch is "x86_64"
                ...body...
            otherwise
                ...else_body...
            end

            when target endian is "little"
                ...body...
            end

            when target pointer width is "64"
                ...body...
            end

            when feature "networking"
                ...body...
            end

        Returns a :class:`~nlpl.parser.ast.ConditionalCompilationBlock` node.
        """
        line_number = self.current_token.line
        self.advance()  # consume 'when'

        # --- Parse condition ---
        condition_type: str
        condition_value: str

        if self.current_token and self.current_token.lexeme == "feature":
            self.advance()  # consume 'feature'
            if self.current_token and self.current_token.type == TokenType.STRING_LITERAL:
                condition_value = self.current_token.lexeme.strip('"\'')
                self.advance()
            elif self.current_token:
                condition_value = self.current_token.lexeme or ""
                self.advance()
            else:
                condition_value = ""
            condition_type = "feature"

        elif self.current_token and self.current_token.lexeme == "target":
            self.advance()  # consume 'target'
            # Next word is the dimension: os, arch, endian, pointer, ptr, platform
            if not self.current_token:
                self.error("Expected dimension after 'when target'")
            dim = self.current_token.lexeme.lower() if self.current_token.lexeme else ""
            self.advance()  # consume dimension word

            if dim in ("os", "platform"):
                condition_type = "target_os"
            elif dim in ("arch", "architecture"):
                condition_type = "target_arch"
            elif dim in ("endian", "endianness"):
                condition_type = "target_endian"
            elif dim in ("pointer", "ptr"):
                # Support "target pointer width is X" (optional "width")
                if (self.current_token
                        and self.current_token.lexeme
                        and self.current_token.lexeme.lower() == "width"):
                    self.advance()  # consume 'width'
                condition_type = "target_ptr_width"
            else:
                condition_type = f"target_{dim}"

            # Optional 'is'
            if self.current_token and self.current_token.lexeme in ("is", "=", "=="):
                self.advance()

            # Read the value (string literal or identifier)
            if self.current_token and self.current_token.type == TokenType.STRING_LITERAL:
                condition_value = self.current_token.lexeme.strip('"\'')
                self.advance()
            elif self.current_token:
                condition_value = self.current_token.lexeme or ""
                self.advance()
            else:
                condition_value = ""
        else:
            self.error("Expected 'target' or 'feature' after 'when' in conditional compilation")

        # --- Skip optional newline ---
        while (self.current_token
               and self.current_token.type in (TokenType.NEWLINE, TokenType.INDENT)):
            self.advance()

        # --- Parse true body ---
        body = []
        while (self.current_token
               and self.current_token.type not in (TokenType.END, TokenType.EOF)
               and not (self.current_token.lexeme
                        and self.current_token.lexeme.lower() == "otherwise")):
            stmt = self.statement()
            if stmt:
                body.append(stmt)

        # --- Optional 'otherwise' / else branch ---
        else_body = None
        if (self.current_token
                and self.current_token.lexeme
                and self.current_token.lexeme.lower() == "otherwise"):
            self.advance()  # consume 'otherwise'
            while (self.current_token
                   and self.current_token.type in (TokenType.NEWLINE, TokenType.INDENT)):
                self.advance()
            else_body = []
            while (self.current_token
                   and self.current_token.type not in (TokenType.END, TokenType.EOF)):
                stmt = self.statement()
                if stmt:
                    else_body.append(stmt)

        # --- Consume closing 'end' ---
        if self.current_token and self.current_token.type == TokenType.END:
            self.advance()

        return ConditionalCompilationBlock(
            condition_type=condition_type,
            condition_value=condition_value,
            body=body,
            else_body=else_body,
            line_number=line_number,
        )

    def parse_parallel_for(self):
        """Parse a parallel for-each loop.

        Syntax::

            parallel for each item in collection
                ...body...
            end

        The ``parallel`` keyword must be followed by ``for`` or ``for each``.
        Each iteration of the loop body is dispatched to a thread-pool worker
        and all iterations run concurrently.

        Returns a :class:`~nlpl.parser.ast.ParallelForLoop` node.
        """
        line_number = self.current_token.line
        self.advance()  # consume 'parallel'

        # Expect 'for' or 'for each'
        if self.current_token and self.current_token.type in (TokenType.FOR, TokenType.FOR_EACH):
            self.advance()  # consume 'for' or 'for each'
        else:
            self.error("Expected 'for' or 'for each' after 'parallel'")

        # If we consumed bare 'for', optionally consume separate 'each' identifier
        if self.current_token and (
            self.current_token.type == TokenType.IDENTIFIER and
            self.current_token.lexeme.lower() == "each"
        ):
            self.advance()  # consume standalone 'each'

        # Parse loop variable name
        if self.current_token and (self.current_token.type == TokenType.IDENTIFIER or
                                   self._can_be_identifier(self.current_token)):
            var_name = self.current_token.lexeme
            self.advance()
        else:
            self.error("Expected a loop variable name after 'parallel for each'")

        # Expect 'in'
        if self.current_token and self.current_token.type == TokenType.IN:
            self.advance()
        else:
            self.error("Expected 'in' after loop variable in 'parallel for each'")

        # Parse the iterable expression
        iterable = self.expression()

        # Parse the loop body
        body = []
        while self.current_token and self.current_token.type not in (TokenType.END, TokenType.EOF):
            stmt = self.statement()
            if stmt:
                body.append(stmt)

        # Consume 'end'
        if self.current_token and self.current_token.type == TokenType.END:
            self.advance()
        else:
            self.error("Expected 'end' to close 'parallel for each' loop")

        return ParallelForLoop(var_name, iterable, body, line_number=line_number)

    def for_loop(self):
        """Parse a for loop.
        
        Supports two main syntaxes:
        1. for each <item> in <collection> ... end (for-each loop)
        2. for <var> from <start> to <end> [by <step>] ... end (range loop)
        
        With optional label:
            label name: for each ...
        """
        line_number = self.current_token.line
        
        # Check for optional label before for
        label = None
        if self.current_token.type == TokenType.LABEL:
            self.advance()  # consume 'label'
            if self.current_token.type == TokenType.IDENTIFIER:
                label = self.current_token.lexeme
                self.advance()  # consume label name
                # Expect colon after label name
                if self.current_token and self.current_token.type == TokenType.COLON:
                    self.advance()
            else:
                self.error("Expected label name after 'label'")
        
        # Check if we start with 'repeat', 'for each' (single token), or 'for'
        if self.current_token.type == TokenType.REPEAT:
            # Could be: "repeat N times", "repeat while", or "repeat for each"
            next_index = self.current_token_index + 1
            
            # Check if next token is 'while' (repeat while loop)
            if (next_index < len(self.tokens) and 
                self.tokens[next_index].type == TokenType.WHILE):
                # This is "repeat while" - delegate to repeat_while_loop
                return self.repeat_while_loop()
            
            # Check if next token is a number (repeat N times)
            if (next_index < len(self.tokens) and 
                self.tokens[next_index].type in (TokenType.INTEGER_LITERAL, TokenType.FLOAT_LITERAL, TokenType.IDENTIFIER)):
                # This is "repeat N times" - delegate to repeat_n_times_loop
                # (IDENTIFIER allows variables: repeat n times)
                return self.repeat_n_times_loop()
            
            # Otherwise it's "repeat for each"
            self.advance()  # consume 'repeat'
            
            # Could be "for each" as single token or "for" + "each"
            if self.current_token.type == TokenType.FOR_EACH:
                self.advance()  # consume 'for each'
            elif self.current_token.type == TokenType.FOR:
                self.advance()  # consume 'for'
                # Check if next is EACH or FROM (to distinguish for-each from range)
                if self.current_token.type == TokenType.FROM:
                    return self._parse_range_for_loop(line_number, label)
                else:
                    self.eat(TokenType.EACH)  # consume 'each'
            else:
                self.error("Expected 'for each', 'for', or number after 'repeat'")
            
        elif self.current_token.type == TokenType.FOR_EACH:
            # Syntax: for each ... (as single token)
            self.advance()  # consume 'for each'
            
        elif self.current_token.type == TokenType.FOR:
            # Syntax: for ... (could be for-each or range-based)
            self.advance()  # consume 'for'
            
            # Look ahead to determine which type
            if self.current_token.type == TokenType.IDENTIFIER:
                # Check next token after the identifier
                next_index = self.current_token_index + 1
                if next_index < len(self.tokens) and self.tokens[next_index].type == TokenType.FROM:
                    # Range-based loop: for i from ...
                    return self._parse_range_for_loop(line_number, label)
                # Otherwise it's for-each: for item in ... (without EACH keyword)
                # Fall through to foreach parsing
            else:
                self.error("Expected identifier after 'for'")
        else:
            self.error("Expected 'for each', 'for', or 'repeat' to start for loop")
        
        # Continue with for-each parsing
        return self._parse_foreach_loop(line_number, label)
    
    def _parse_foreach_loop(self, line_number, label=None):
        """Parse for-each loop body after 'for each' is consumed."""
        # Get iterator variable (can be identifier or contextual keyword)
        if self.current_token.type == TokenType.IDENTIFIER or self._can_be_identifier(self.current_token):
            iterator = self.current_token.lexeme
            self.advance()
        else:
            self.error("Expected an identifier for loop iterator")
            
        # Eat 'in'
        self.eat(TokenType.IN)
        
        # Parse iterable expression
        iterable = self.expression()
        
        # Optional comma after iterable
        if self.current_token and self.current_token.type == TokenType.COMMA:
            self.advance()
        
        # Consume INDENT if present (for block-based syntax)
        if self.current_token and self.current_token.type == TokenType.INDENT:
            self.advance()
        
        # Parse body - stop at END token or DEDENT
        body = []
        while (self.current_token and 
               self.current_token.type != TokenType.EOF and
               self.current_token.type != TokenType.END and
               self.current_token.type != TokenType.DEDENT):
            statement = self.statement()
            if statement:
                body.append(statement)
        
        # Consume DEDENT if present
        if self.current_token and self.current_token.type == TokenType.DEDENT:
            self.advance()
                
        # Eat 'end' token
        if self.current_token and self.current_token.type == TokenType.END:
            self.advance()
            
            # Support for explicit "End loop" syntax
            if (self.current_token and self.current_token.type == TokenType.IDENTIFIER and 
                self.current_token.lexeme.lower() == 'loop'):
                self.advance()
                
            # Optional dot after end
            if (self.current_token and self.current_token.type == TokenType.DOT):
                self.advance()
        
        # Check for else block (executes if loop completes without break)
        else_body = None
        if self.current_token and self.current_token.type == TokenType.ELSE:
            self.advance()  # consume 'else'
            
            # Skip NEWLINE/INDENT
            while (self.current_token and 
                   self.current_token.type in (TokenType.NEWLINE, TokenType.INDENT)):
                self.advance()
            
            # Parse else body
            else_body = []
            while (self.current_token and 
                   self.current_token.type != TokenType.EOF and
                   self.current_token.type != TokenType.DEDENT and
                   self.current_token.type != TokenType.END):
                statement = self.statement()
                if statement:
                    else_body.append(statement)
            
            # Consume DEDENT/END after else
            if self.current_token and self.current_token.type in (TokenType.DEDENT, TokenType.END):
                self.advance()
            
        return ForLoop(iterator=iterator, iterable=iterable, body=body, line_number=line_number, else_body=else_body, label=label)
    
    def _parse_range_for_loop(self, line_number, label=None):
        """Parse range-based for loop: for i from start to end [by step]."""
        # Get loop variable
        if self.current_token.type == TokenType.IDENTIFIER:
            iterator = self.current_token.lexeme
            self.advance()
        else:
            self.error("Expected identifier for loop variable")
        
        # Eat 'from'
        self.eat(TokenType.FROM)
        
        # Parse start expression
        start = self.expression()
        
        # Eat 'to'
        self.eat(TokenType.TO)
        
        # Parse end expression
        end = self.expression()
        
        # Optional 'by' for step
        step = None
        if self.current_token and self.current_token.type == TokenType.IDENTIFIER:
            if self.current_token.lexeme.lower() == 'by':
                self.advance()  # consume 'by'
                step = self.expression()
        
        # Consume INDENT if present (for block-based syntax)
        if self.current_token and self.current_token.type == TokenType.INDENT:
            self.advance()
        
        # Parse body
        body = []
        while (self.current_token and 
               self.current_token.type != TokenType.EOF and
               self.current_token.type != TokenType.END and
               self.current_token.type != TokenType.DEDENT):
            statement = self.statement()
            if statement:
                body.append(statement)
        
        # Consume DEDENT if present
        if self.current_token and self.current_token.type == TokenType.DEDENT:
            self.advance()
        
        # Eat 'end' token
        if self.current_token and self.current_token.type == TokenType.END:
            self.advance()
        
        # Check for else block (executes if loop completes without break)
        else_body = None
        if self.current_token and self.current_token.type == TokenType.ELSE:
            self.advance()  # consume 'else'
            
            # Skip NEWLINE/INDENT
            while (self.current_token and 
                   self.current_token.type in (TokenType.NEWLINE, TokenType.INDENT)):
                self.advance()
            
            # Parse else body
            else_body = []
            while (self.current_token and 
                   self.current_token.type != TokenType.EOF and
                   self.current_token.type != TokenType.DEDENT and
                   self.current_token.type != TokenType.END):
                statement = self.statement()
                if statement:
                    else_body.append(statement)
            
            # Consume DEDENT/END after else
            if self.current_token and self.current_token.type in (TokenType.DEDENT, TokenType.END):
                self.advance()
        
        return ForLoop(iterator=iterator, start=start, end=end, step=step, body=body, line_number=line_number, else_body=else_body, label=label)
    
    def match_expression(self):
        """Parse a match expression for pattern matching.
        
        Syntax:
            match <expression> with
                case <pattern> [if <guard>]
                    <body>
                case <pattern>
                    <body>
                case _
                    <body>
        """
        line_number = self.current_token.line
        
        # Eat 'match'
        self.eat(TokenType.MATCH)
        
        # Parse expression to match against
        # Save current position to handle lookahead
        saved_index = self.current_token_index
        saved_token = self.current_token
        
        # Try to parse as full expression
        # We need to stop before 'with' keyword to avoid consuming it
        expression = None
        
        # Parse expression carefully - stop at 'with'
        # Use a limited expression parser that stops at 'with'
        if self.current_token.type == TokenType.IDENTIFIER:
            # Check if next token is 'with' - if so, just parse identifier
            var_name = self.current_token.lexeme
            self.advance()
            
            # Peek ahead for 'with'
            if self.current_token and self.current_token.type == TokenType.WITH:
                # Simple identifier case
                from ..parser.ast import Identifier
                expression = Identifier(var_name)
            else:
                # Complex expression - backtrack and parse full expression
                self.current_token_index = saved_index
                self.current_token = saved_token
                
                # Parse expression but stop at 'with'
                # Use assignment level parsing (covers most expressions)
                expression = self.assignment()
        else:
            # Non-identifier expression (literals, function calls, etc.)
            expression = self.assignment()
        
        # Skip newlines before 'with'
        while (self.current_token and 
               self.current_token.type in (TokenType.NEWLINE, TokenType.INDENT)):
            self.advance()
        
        # Eat 'with'
        if self.current_token and self.current_token.type == TokenType.WITH:
            self.eat(TokenType.WITH)
        
        # Skip newlines/indent after 'with' before cases
        while (self.current_token and 
               self.current_token.type in (TokenType.NEWLINE, TokenType.INDENT)):
            self.advance()
        
        # Parse cases
        cases = []
        while (self.current_token and 
               self.current_token.type != TokenType.EOF and
               self.current_token.type != TokenType.DEDENT and
               self.current_token.type != TokenType.END):
            
            # Skip newlines between cases
            while (self.current_token and 
                   self.current_token.type in (TokenType.NEWLINE, TokenType.INDENT)):
                self.advance()
            
            if self.current_token.type == TokenType.CASE:
                case = self._parse_match_case()
                if case:
                    cases.append(case)
            elif self.current_token.type == TokenType.DEDENT:
                break
            elif self.current_token.type == TokenType.END:
                break
            else:
                self.error(f"Expected 'case' in match expression, got {self.current_token.type}")
                break
        
        # Consume DEDENT if present (this marks the end of the match block)
        if self.current_token and self.current_token.type == TokenType.DEDENT:
            self.advance()
        
        # Consume END if present (match ... end syntax)
        if self.current_token and self.current_token.type == TokenType.END:
            self.advance()
        
        return MatchExpression(expression, cases, line_number)
    
    def switch_statement(self):
        """Parse a switch statement for multi-way branching.
        
        Syntax:
            switch <expression>
                case <value>
                    <statements>
                case <value>
                    <statements>
                default
                    <statements>
        """
        line_number = self.current_token.line
        
        # Consume 'switch'
        self.eat(TokenType.SWITCH)
        
        # Parse expression to switch on
        expression = self.expression()
        
        # Expect NEWLINE or INDENT
        while self.current_token and self.current_token.type == TokenType.NEWLINE:
            self.advance()
        
        # Expect INDENT
        if self.current_token and self.current_token.type == TokenType.INDENT:
            self.advance()
        
        # Parse cases
        cases = []
        default_case = None
        
        while self.current_token and self.current_token.type != TokenType.EOF:
            # Check for case
            if self.current_token.type == TokenType.CASE:
                case = self._parse_switch_case()
                cases.append(case)
            # Check for default
            elif self.current_token.type == TokenType.DEFAULT:
                self.advance()  # consume 'default'
                
                # Skip NEWLINE/INDENT
                while (self.current_token and 
                       self.current_token.type in (TokenType.NEWLINE, TokenType.INDENT)):
                    self.advance()
                
                # Parse default body
                default_case = []
                while (self.current_token and 
                       self.current_token.type != TokenType.EOF and
                       self.current_token.type != TokenType.DEDENT and
                       self.current_token.type != TokenType.CASE):
                    statement = self.statement()
                    if statement:
                        default_case.append(statement)
                
                # Consume DEDENT after default
                if self.current_token and self.current_token.type == TokenType.DEDENT:
                    self.advance()
            # Check for DEDENT (end of switch)
            elif self.current_token.type == TokenType.DEDENT:
                self.advance()
                break
            # Skip newlines
            elif self.current_token.type == TokenType.NEWLINE:
                self.advance()
            else:
                # Unexpected token
                break
        
        return SwitchStatement(expression, cases, default_case, line_number)
    
    def _parse_switch_case(self):
        """Parse a single case in a switch statement."""
        line_number = self.current_token.line
        
        # Consume 'case'
        self.eat(TokenType.CASE)
        
        # Parse case value (expression)
        value = self.expression()
        
        # Skip NEWLINE/INDENT
        while (self.current_token and 
               self.current_token.type in (TokenType.NEWLINE, TokenType.INDENT)):
            self.advance()
        
        # Parse case body
        body = []
        while (self.current_token and 
               self.current_token.type != TokenType.EOF and
               self.current_token.type != TokenType.DEDENT and
               self.current_token.type != TokenType.CASE and
               self.current_token.type != TokenType.DEFAULT):
            statement = self.statement()
            if statement:
                body.append(statement)
        
        # Consume DEDENT after case
        if self.current_token and self.current_token.type == TokenType.DEDENT:
            self.advance()
        
        return SwitchCase(value, body, line_number)
    
    def match_case(self):
        """Parse a single case in a match expression.
        
        Supports:
        - Option patterns: case Some with value
        - Result patterns: case Ok with value, case Err with error
        - Literal patterns: case 42
        - Wildcard: case _
        """
        self.consume(TokenType.CASE, "Expected 'case' keyword")
        
        line_number = self.previous().line
        
        # Check for Option patterns (Some/None)
        if self.check(TokenType.IDENTIFIER):
            variant_name = self.peek().lexeme
            
            if variant_name in ("Some", "None"):
                self.advance()  # consume variant
                binding = None
                
                # Check for binding: "Some with value"
                if self.match(TokenType.WITH):
                    if not self.check(TokenType.IDENTIFIER):
                        self.error("Expected variable name after 'with'")
                    binding = self.advance().lexeme
                
                from .ast import OptionPattern
                pattern = OptionPattern(variant_name, binding, line_number)
            
            elif variant_name in ("Ok", "Err"):
                self.advance()  # consume variant
                binding = None
                
                # Check for binding: "Ok with value"
                if self.match(TokenType.WITH):
                    if not self.check(TokenType.IDENTIFIER):
                        self.error("Expected variable name after 'with'")
                    binding = self.advance().lexeme
                
                from .ast import ResultPattern
                pattern = ResultPattern(variant_name, binding, line_number)
            
            else:
                # Regular variant or identifier pattern
                pattern = self._parse_pattern()
        else:
            # Other pattern types
            pattern = self._parse_pattern()
        
        # Optional guard clause - supports both 'if' and 'when' keywords
        guard = None
        if self.match(TokenType.IF) or self.match(TokenType.WHEN):
            guard = self.expression()
        
        # Parse body - consume optional newline (lexer may skip it before INDENT)
        self.match(TokenType.NEWLINE)  # Optional
        
        # Expect indentation
        if not self.match(TokenType.INDENT):
            self.error("Expected indented block after case")
        
        body = []
        while not self.check(TokenType.DEDENT) and not self.is_at_end():
            stmt = self.statement()
            if stmt:
                body.append(stmt)
        
        # Consume DEDENT (may be optional at EOF or END)
        self.match(TokenType.DEDENT)
        
        from .ast import MatchCase
        # MatchCase(pattern, body, guard=None, line_number=None)
        return MatchCase(pattern, body, guard, line_number)
    
    def _parse_match_case(self):
        """Wrapper for match_case for backward compatibility."""
        return self.match_case()
        
    def _parse_pattern(self):
        """Parse a pattern in a match case.
        
        Patterns:
        - Literal: 42, "hello", true
        - Wildcard: _
        - Identifier: value (binding)
        - Variant: Ok value, Error message
        - Tuple: (x, y)
        - List: [first, second, ...rest]
        """
        from ..parser.ast import (
            LiteralPattern, WildcardPattern, IdentifierPattern,
            VariantPattern, TuplePattern, ListPattern, Literal
        )
        
        line_number = self.current_token.line
        
        # Wildcard pattern: _
        if (self.current_token.type == TokenType.IDENTIFIER and 
            self.current_token.lexeme == '_'):
            self.advance()
            return WildcardPattern(line_number)
        
        # Tuple pattern: (...)
        if self.current_token.type == TokenType.LEFT_PAREN:
            self.advance()  # consume '('
            patterns = []
            
            while self.current_token.type != TokenType.RIGHT_PAREN:
                patterns.append(self._parse_pattern())
                
                if self.current_token.type == TokenType.COMMA:
                    self.advance()
                elif self.current_token.type != TokenType.RIGHT_PAREN:
                    self.error("Expected ',' or ')' in tuple pattern")
            
            self.eat(TokenType.RIGHT_PAREN)
            return TuplePattern(patterns, line_number)
        
        # List pattern: [...]
        if self.current_token.type == TokenType.LEFT_BRACKET:
            self.advance()  # consume '['
            patterns = []
            rest_binding = None
            
            while self.current_token.type != TokenType.RIGHT_BRACKET:
                # Check for rest pattern: ...rest
                if (self.current_token.type == TokenType.ELLIPSIS or
                    (self.current_token.type == TokenType.DOT and 
                     self.peek(1) and self.peek(1).type == TokenType.DOT and
                     self.peek(2) and self.peek(2).type == TokenType.DOT)):
                    # Consume ellipsis
                    if self.current_token.type == TokenType.ELLIPSIS:
                        self.advance()
                    else:
                        self.advance()  # .
                        self.advance()  # .
                        self.advance()  # .
                    
                    # Get binding name
                    if self.current_token.type == TokenType.IDENTIFIER:
                        rest_binding = self.current_token.lexeme
                        self.advance()
                    break
                
                patterns.append(self._parse_pattern())
                
                if self.current_token.type == TokenType.COMMA:
                    self.advance()
                elif self.current_token.type != TokenType.RIGHT_BRACKET:
                    self.error("Expected ',' or ']' in list pattern")
            
            self.eat(TokenType.RIGHT_BRACKET)
            return ListPattern(patterns, rest_binding, line_number)
        
        # Literal patterns: numbers, strings, booleans
        # Also handle negative numbers: -42, -3.14
        is_negative = False
        if self.current_token.type == TokenType.MINUS:
            is_negative = True
            self.advance()  # consume '-'
        
        if self.current_token.type in (TokenType.INTEGER_LITERAL, TokenType.FLOAT_LITERAL, 
                                        TokenType.STRING_LITERAL, TokenType.TRUE, TokenType.FALSE):
            value = self.current_token.lexeme
            token_type = self.current_token.type
            self.advance()
            
            # Create appropriate literal
            if token_type == TokenType.INTEGER_LITERAL:
                num_val = int(value)
                if is_negative:
                    num_val = -num_val
                lit = Literal("integer", num_val)
            elif token_type == TokenType.FLOAT_LITERAL:
                num_val = float(value)
                if is_negative:
                    num_val = -num_val
                lit = Literal("float", num_val)
            elif token_type == TokenType.STRING_LITERAL:
                lit = Literal("string", value)
            elif token_type == TokenType.TRUE:
                lit = Literal("boolean", True)
            elif token_type == TokenType.FALSE:
                lit = Literal("boolean", False)
            
            return LiteralPattern(lit, line_number)
        
        # Variant pattern: Ok value, Error message, Some x
        # or simple identifier pattern: value
        if self.current_token.type == TokenType.IDENTIFIER:
            first_name = self.current_token.lexeme
            self.advance()
            
            # Support dotted variant names (e.g. Result.Ok)
            while self.current_token.type == TokenType.DOT:
                self.advance() # Eat '.'
                if self.current_token.type == TokenType.IDENTIFIER:
                    first_name += "." + self.current_token.lexeme
                    self.advance()
                else:
                    self.error("Expected identifier after '.' in pattern")
            
            # Check if this is a variant pattern (has bindings)
            # Variant names typically start with uppercase
            if first_name[0].isupper() or first_name in ('Ok', 'Err', 'Error', 'Some', 'None'):
                bindings = []
                
                # Parse bindings (identifiers that follow the variant name)
                while (self.current_token and 
                       (self.current_token.type == TokenType.IDENTIFIER or 
                        self._can_be_identifier(self.current_token)) and
                       self.current_token.type not in (TokenType.IF, TokenType.INDENT)):
                    bindings.append(self.current_token.lexeme)
                    self.advance()
                
                return VariantPattern(first_name, bindings, line_number)
            else:
                # Simple identifier binding
                return IdentifierPattern(first_name, line_number)
        
        self.error(f"Invalid pattern: {self.current_token.type}")
        return None
        
    def memory_allocation(self):
        """Parse a memory allocation."""
        # Syntax: Allocate a new <type> in memory [with value <expression>] and name it <identifier>
        line_number = self.current_token.line
        
        # Eat 'allocate'
        self.eat(TokenType.ALLOCATE)
        
        # Skip optional 'a'
        if self.current_token.type == TokenType.IDENTIFIER and self.current_token.lexeme.lower() == 'a':
            self.advance()
            
        # Eat 'new'
        self.eat(TokenType.NEW)
        
        # Get type
        if self.current_token.type == TokenType.TYPE:
            var_type = self.current_token.value
            self.advance()
        else:
            self.error("Expected a type")
            
        # Eat 'in'
        self.eat(TokenType.IN)
        
        # Eat 'memory'
        self.eat(TokenType.MEMORY)
        
        # Check for optional initialization
        initial_value = None
        if (self.current_token and self.current_token.type == TokenType.WITH):
            # Eat 'with'
            self.advance()
            
            # Eat 'value'
            self.eat(TokenType.VALUE)
            
            # Parse the expression
            initial_value = self.expression()
            
        # Eat 'and'
        self.eat(TokenType.AND)
        
        # Eat 'name'
        self.eat(TokenType.NAME)
        
        # Eat 'it'
        self.eat(TokenType.IT)
        
        # Get the identifier
        if self.current_token.type == TokenType.IDENTIFIER:
            identifier = self.current_token.value
            self.advance()
        else:
            self.error("Expected an identifier")
            
        return MemoryAllocation(var_type, identifier, initial_value, line_number)
        
    def memory_deallocation(self):
        """Parse a memory deallocation."""
        # Syntax: Free the memory at <identifier>
        line_number = self.current_token.line
        
        # Eat 'free'
        self.eat(TokenType.FREE)
        
        # Eat 'the'
        if self.current_token.type == TokenType.IDENTIFIER and self.current_token.lexeme.lower() == 'the':
            self.advance()
            
        # Eat 'memory'
        self.eat(TokenType.MEMORY)
        
        # Eat 'at'
        self.eat(TokenType.AT)
        
        # Get the identifier
        if self.current_token.type == TokenType.IDENTIFIER:
            identifier = self.current_token.value
            self.advance()
        else:
            self.error("Expected an identifier")
            
        return MemoryDeallocation(identifier, line_number)

    def drop_borrow_statement(self):
        """Parse a drop borrow statement: drop borrow [mutable] <identifier>.

        Syntax:
            drop borrow x              # release one immutable borrow of x
            drop borrow mutable x      # release the mutable borrow of x
        """
        from ..parser.ast import DropBorrowStatement
        line_number = self.current_token.line
        self.eat(TokenType.DROP)  # consume 'drop'

        # Expect 'borrow'
        if not (self.current_token and self.current_token.type == TokenType.BORROW):
            self.error("Expected 'borrow' after 'drop'")
        self.advance()  # consume 'borrow'

        # Optional 'mutable' qualifier
        mutable = False
        if (self.current_token and self.current_token.type == TokenType.IDENTIFIER and
                self.current_token.lexeme.lower() == "mutable"):
            mutable = True
            self.advance()  # consume 'mutable'

        # Expect variable name
        if self.current_token and (self.current_token.type == TokenType.IDENTIFIER or
                                    self._can_be_identifier(self.current_token)):
            var_name = self.current_token.lexeme
            self.advance()
            return DropBorrowStatement(var_name, mutable, line_number)
        else:
            self.error("Expected variable name after 'drop borrow'")

    def parse_inline_assembly(self):
        """Parse inline assembly block.

        Syntax:
            asm [for arch "<arch>"]
                code
                    "assembly instruction"
                    "another instruction"
                [inputs "constraint": expression, ...]
                [outputs "constraint": variable, ...]
                [clobbers "register", ...]
            end

        The optional ``for arch "<arch>"`` guard restricts the block to a
        specific target architecture (e.g. ``"riscv64"``, ``"arm"``,
        ``"mips"``).  When the compilation target does not match the guard
        the compiler skips the entire block.
        """
        line_number = self.current_token.line

        # Eat 'asm'
        self.eat(TokenType.ASM)

        # Optional architecture guard: for arch "riscv64"
        # NB: 'for' is lexed as TokenType.FOR (a keyword), not as an IDENTIFIER.
        arch_guard = None
        if (self.current_token
                and (self.current_token.type == TokenType.FOR
                     or (self.current_token.type == TokenType.IDENTIFIER
                         and self.current_token.lexeme.lower() == "for"))):
            self.advance()  # consume 'for'
            # Expect 'arch' keyword (as identifier)
            if (self.current_token
                    and self.current_token.type == TokenType.IDENTIFIER
                    and self.current_token.lexeme.lower() == "arch"):
                self.advance()  # consume 'arch'
            # Expect string literal with arch name
            if self.current_token and self.current_token.type == TokenType.STRING_LITERAL:
                arch_guard = self.current_token.literal.lower()
                self.advance()

        # Skip any newlines between the asm header and the indented block.
        # (The lexer emits NEWLINE before INDENT at block boundaries.)
        while self.current_token and self.current_token.type == TokenType.NEWLINE:
            self.advance()

        # Expect INDENT
        if self.current_token and self.current_token.type == TokenType.INDENT:
            self.advance()
        
        asm_code = []
        inputs = {}
        outputs = {}
        clobbers = []
        
        # Parse asm block sections until we hit DEDENT or END
        while self.current_token and self.current_token.type not in (TokenType.DEDENT, TokenType.END, TokenType.EOF):
            if self.current_token.type == TokenType.IDENTIFIER:
                keyword = self.current_token.lexeme.lower()
                
                if keyword == "code":
                    # Parse code section
                    self.advance()  # consume 'code'

                    # Skip any newlines between 'code' and its indented block.
                    while self.current_token and self.current_token.type == TokenType.NEWLINE:
                        self.advance()

                    # Expect INDENT
                    if self.current_token and self.current_token.type == TokenType.INDENT:
                        self.advance()
                    
                    # Collect assembly code strings until DEDENT
                    while (self.current_token and 
                           self.current_token.type not in (TokenType.DEDENT, TokenType.EOF)):
                        if self.current_token.type == TokenType.STRING_LITERAL:
                            # Use literal (processed value) instead of lexeme (raw text with quotes)
                            asm_code.append(self.current_token.literal)
                            self.advance()
                        elif self.current_token.type == TokenType.NEWLINE:
                            self.advance()  # Skip newlines
                        else:
                            break  # Stop on other tokens
                    
                    # Consume DEDENT after code block
                    if self.current_token and self.current_token.type == TokenType.DEDENT:
                        self.advance()
                
                elif keyword == "inputs":
                    # Parse inputs: "constraint": expression, ...
                    self.advance()  # consume 'inputs'
                    inputs = self._parse_asm_operands()
                
                elif keyword == "outputs":
                    # Parse outputs: "constraint": variable, ...
                    self.advance()  # consume 'outputs'
                    outputs = self._parse_asm_operands()
                
                elif keyword == "clobbers":
                    # Parse clobbers: "register", "register", ...
                    self.advance()  # consume 'clobbers'
                    clobbers = self._parse_asm_clobbers()
                
                else:
                    self.advance()  # Skip unknown keywords
            elif self.current_token.type == TokenType.NEWLINE:
                self.advance()  # Skip newlines
            else:
                break  # Unknown token, stop parsing
        
        # Consume DEDENT if present
        if self.current_token and self.current_token.type == TokenType.DEDENT:
            self.advance()
        
        # Consume END if present (for non-indented style)
        if self.current_token and self.current_token.type == TokenType.END:
            self.advance()

        return InlineAssembly(asm_code, inputs, outputs, clobbers, line_number, arch=arch_guard)
    
    def _parse_asm_operands(self):
        """Parse assembly operands: "constraint": expression, ...
        
        Returns list of (constraint, expression) tuples to support
        multiple operands with the same constraint.
        """
        operands = []
        
        while self.current_token:
            # Check for string constraint
            if self.current_token.type == TokenType.STRING_LITERAL:
                constraint = self.current_token.lexeme
                self.advance()
                
                # Expect colon
                if self.current_token and self.current_token.type == TokenType.COLON:
                    self.advance()
                else:
                    break
                
                # Parse expression or identifier
                if self.current_token.type == TokenType.IDENTIFIER:
                    operand = Identifier(self.current_token.lexeme)
                    self.advance()
                else:
                    operand = self.expression()
                
                # Append as tuple to preserve order and allow duplicate constraints
                operands.append((constraint, operand))
                
                # Check for comma (more operands)
                if self.current_token and self.current_token.type == TokenType.COMMA:
                    self.advance()
                else:
                    break
            else:
                break
        
        return operands
    
    def _parse_asm_clobbers(self):
        """Parse assembly clobber list: "register", "register", ..."""
        clobbers = []
        
        while self.current_token and self.current_token.type == TokenType.STRING_LITERAL:
            clobbers.append(self.current_token.lexeme)
            self.advance()
            
            # Check for comma
            if self.current_token and self.current_token.type == TokenType.COMMA:
                self.advance()
            else:
                break
        
        return clobbers
        
    def concurrent_execution(self):
        """Parse a concurrent execution."""
        # Syntax: Run these tasks at the same time: <task_list>
        line_number = self.current_token.line
        
        # Eat 'run'
        self.eat(TokenType.RUN)
        
        # Eat 'these'
        self.eat(TokenType.THESE)
        
        # Eat 'tasks'
        self.eat(TokenType.TASKS)
        
        # Eat 'at'
        self.eat(TokenType.AT)
        
        # Eat 'the'
        if self.current_token.type == TokenType.IDENTIFIER and self.current_token.lexeme.lower() == 'the':
            self.advance()
            
        # Eat 'same'
        self.eat(TokenType.SAME)
        
        # Eat 'time'
        self.eat(TokenType.TIME)
        
        # Eat optional colon
        if self.current_token.type == TokenType.COLON:
            self.advance()
            
        # Parse task list
        tasks = []
        while (self.current_token and self.current_token.type != TokenType.EOF and
               not (self.current_token.type == TokenType.IDENTIFIER and 
                    self.current_token.lexeme.lower() == 'end')):
            statement = self.statement()
            if statement:
                tasks.append(statement)
                
        # Eat 'end'
        if self.current_token and self.current_token.type == TokenType.IDENTIFIER and self.current_token.lexeme.lower() == 'end':
            self.advance()
            
            # Support for explicit "End concurrent" syntax
            if (self.current_token and self.current_token.type == TokenType.IDENTIFIER and 
                self.current_token.lexeme.lower() == 'concurrent'):
                self.advance()
                
            # Optional period after end
            if (self.current_token and self.current_token.type == TokenType.DOT):
                self.advance()
            
        return ConcurrentExecution(tasks, line_number)
        
    def try_catch(self):
        """Parse a try-catch block.
        
        Supports two syntaxes:
        1. try to <statement> but if it fails <catch_block> end
        2. try <try_block> catch <exception_var> <catch_block> end
        """
        line_number = self.current_token.line
        
        # Eat 'try'
        self.eat(TokenType.TRY)
        
        # Check which syntax we're using
        if self.current_token and self.current_token.type == TokenType.TO:
            # Syntax 1: Try to <statement> but if it fails <catch_block>
            self.advance()  # consume 'to'
            
            # Parse try block (single statement)
            try_block = [self.statement()]
            
            # Eat 'but'
            if self.current_token.type == TokenType.IDENTIFIER and self.current_token.lexeme.lower() == 'but':
                self.advance()
                
            # Eat 'if'
            self.eat(TokenType.IF)
            
            # Eat 'it'
            self.eat(TokenType.IT)
            
            # Eat 'fails'
            if self.current_token.type == TokenType.IDENTIFIER and self.current_token.lexeme.lower() == 'fails':
                self.advance()
                
            # Optional comma after "fails"
            if self.current_token and self.current_token.type == TokenType.COMMA:
                self.advance()
                
            # Parse catch block
            catch_block = []
            exception_var = None
            exception_properties = []
            
        else:
            # Syntax 2: try <try_block> catch <exception_var> <catch_block> end
            # Consume INDENT if present
            if self.current_token and self.current_token.type == TokenType.INDENT:
                self.advance()
                
            # Parse try block (multiple statements until 'catch')
            try_block = []
            while (self.current_token and self.current_token.type != TokenType.EOF and
                   self.current_token.type != TokenType.CATCH and
                   self.current_token.type != TokenType.DEDENT):
                statement = self.statement()
                if statement:
                    try_block.append(statement)
            
            # Consume DEDENT if present (after try block)
            if self.current_token and self.current_token.type == TokenType.DEDENT:
                self.advance()
                
            # Eat 'catch'
            self.eat(TokenType.CATCH)
            
            # Optional exception variable and type
            exception_var = None
            exception_type = None
            exception_properties = []
            
            if self.current_token and (self.current_token.type == TokenType.IDENTIFIER or self.current_token.type == TokenType.ERROR):
                exception_var = self.current_token.lexeme
                self.advance()
                
                # Check for 'with <property>' syntax: catch error with message
                if self.current_token and self.current_token.type == TokenType.WITH:
                    self.advance()  # consume 'with'
                    
                    # Parse property name(s) - can be IDENTIFIER or contextual keywords like MESSAGE
                    if self.current_token and (self.current_token.type == TokenType.IDENTIFIER or 
                                               self.current_token.type == TokenType.MESSAGE or
                                               self._can_be_identifier(self.current_token)):
                        exception_properties.append(self.current_token.lexeme)
                        self.advance()
                        
                        # Support multiple properties: catch error with message, code
                        while self.current_token and self.current_token.type == TokenType.COMMA:
                            self.advance()  # consume comma
                            if self.current_token and (self.current_token.type == TokenType.IDENTIFIER or
                                                       self.current_token.type == TokenType.MESSAGE or
                                                       self._can_be_identifier(self.current_token)):
                                exception_properties.append(self.current_token.lexeme)
                                self.advance()
                    else:
                        self.error("Expected property name after 'with'")
                
                # Check for 'as ExceptionType' syntax
                elif self.current_token and self.current_token.type == TokenType.AS:
                    self.advance()  # consume 'as'
                    
                    # Parse exception type
                    if self.current_token and (self.current_token.type == TokenType.IDENTIFIER or self.current_token.type == TokenType.ERROR):
                        exception_type = self.current_token.lexeme if self.current_token.type == TokenType.IDENTIFIER else "Error"
                        self.advance()
                    else:
                        self.error("Expected exception type after 'as'")
            
            # Consume INDENT if present (before catch block)
            if self.current_token and self.current_token.type == TokenType.INDENT:
                self.advance()
                
            # Parse catch block (multiple statements until DEDENT or END)
            catch_block = []
            while (self.current_token and 
                   self.current_token.type != TokenType.EOF and
                   self.current_token.type != TokenType.DEDENT and
                   self.current_token.type != TokenType.END):
                statement = self.statement()
                if statement:
                    catch_block.append(statement)
        
            # Consume DEDENT if present (after catch block) - this ends the try/catch
            dedent_seen = False
            if self.current_token and self.current_token.type == TokenType.DEDENT:
                self.advance()
                dedent_seen = True
                
        # Eat 'end' token if present (optional if dedent was seen)
        if self.current_token and self.current_token.type == TokenType.END:
            self.advance()
        elif not dedent_seen:
            # If no dedent and no end, that's an error
            self.eat(TokenType.END)
        
        return TryCatch(try_block, catch_block, exception_var, exception_type, exception_properties, line_number)
    
    def try_statement(self):
        """Alias for try_catch() to match statement() dispatcher naming."""
        return self.try_catch()
    
    def raise_statement(self):
        """Parse a raise/throw statement.
        
        Syntax:
            raise error with message "error text"
            raise ValueError with message "invalid value"
            raise CustomError with message variable_name
            raise error  # Re-raise current exception (in catch block)
        """
        line_number = self.current_token.line
        
        # Eat 'raise'
        self.eat(TokenType.RAISE)
        
        # Check if this is just "raise" (re-raise)
        if self.current_token and self.current_token.type in (TokenType.EOF, TokenType.DEDENT, TokenType.END):
            # Re-raise current exception
            return RaiseStatement(exception_type=None, message=None, line_number=line_number)
        
        # Parse exception type (either 'error' keyword or a type name)
        exception_type = "Error"  # Default
        
        if self.current_token and self.current_token.type == TokenType.ERROR:
            # "raise error"
            exception_type = "Error"
            self.advance()
        elif self.current_token and self.current_token.type == TokenType.IDENTIFIER:
            # "raise ValueError", "raise CustomError"
            exception_type = self.current_token.lexeme
            self.advance()
        else:
            self.error(f"Expected exception type after 'raise', got {self.current_token.type}")
        
        # Check for "with message" clause
        message = None
        if self.current_token and self.current_token.type == TokenType.WITH:
            self.advance()  # consume 'with'
            
            # Expect 'message' keyword
            if self.current_token and self.current_token.type == TokenType.MESSAGE:
                self.advance()  # consume 'message'
            else:
                self.error(f"Expected 'message' after 'with', got {self.current_token.type}")
            
            # Parse the message expression (can be string literal, variable, or expression)
            message = self.expression()
            if message is None:
                self.error("Expected message expression after 'with message'")
        
        return RaiseStatement(exception_type, message, line_number)
        
    def expression_statement(self):
        """Parse an expression statement."""
        # SET tokens should be handled by the statement method
        if self.current_token.type == TokenType.SET:
            self.error("SET tokens should be handled by variable declarations")
            
        # Parse as a regular expression
        expr = self.expression()
        return expr
        
    def expression(self):
        """Parse an expression."""
        # Parse as a regular expression
        return self.assignment()
        
    def assignment(self):
        """Parse an assignment expression."""
        return self.logical_or()
        
    def logical_or(self):
        """Parse a logical OR expression."""
        expr = self.logical_and()
        
        while self.current_token and self.current_token.type == TokenType.OR:
            operator = self.current_token
            self.advance()
            right = self.logical_and()
            expr = BinaryOperation(expr, operator, right)
            
        return expr
        
    def logical_and(self):
        """Parse a logical AND expression."""
        expr = self.logical_not()
        
        while self.current_token and self.current_token.type == TokenType.AND:
            operator = self.current_token
            self.advance()
            right = self.logical_not()
            expr = BinaryOperation(expr, operator, right)
            
        return expr
    
    def logical_not(self):
        """Parse a logical NOT expression."""
        # Check for NOT operator (but not "not in" which is handled by membership)
        if self.current_token and self.current_token.type == TokenType.NOT:
            next_token = self.peek(1)
            # If next token is IN, this is "not in" - let membership() handle it
            if next_token and next_token.type == TokenType.IN:
                return self.equality()
            
            # Standalone NOT operator
            operator = self.current_token
            self.advance()
            operand = self.logical_not()  # Right-associative for multiple NOTs
            return UnaryOperation(operator, operand)
        
        # No NOT operator, continue to next precedence level
        return self.equality()
        
    def equality(self):
        """Parse an equality expression."""
        expr = self.comparison()
        
        while self.current_token and self.current_token.type in [TokenType.EQUAL_TO, TokenType.NOT_EQUAL_TO]:
            operator = self.current_token
            self.advance()
            right = self.comparison()
            expr = BinaryOperation(expr, operator, right)
            
        return expr
        
    def comparison(self):
        """Parse a comparison expression."""
        expr = self.membership()
        
        # Handle NLPL natural language comparisons: "x is greater than 3"
        # Pattern: <expr> IS <comparison_op> <expr>
        if self.current_token and self.current_token.type == TokenType.IS:
            self.advance()  # Eat 'is'
            
            # Handle "is not ..." (negation patterns)
            # Covers: "is not null", "is not equal to x", "is not x"
            if self.current_token and self.current_token.type == TokenType.NOT:
                not_line = self.current_token.line
                not_col = self.current_token.column
                self.advance()  # Consume 'not'
                
                # Skip optional "equal to" for "is not equal to ..."
                if self.current_token and self.current_token.type == TokenType.EQUAL_TO:
                    self.advance()  # compound "equal to" token
                elif (self.current_token and self.current_token.type == TokenType.IDENTIFIER and
                      self.current_token.lexeme.lower() == "equal"):
                    self.advance()  # 'equal'
                    if self.current_token and self.current_token.type == TokenType.TO:
                        self.advance()  # 'to'
                
                op = Token(TokenType.NOT_EQUAL_TO, "is not", None, not_line, not_col)
                right = self.term()
                expr = BinaryOperation(expr, op, right)
            
            # Now expect a comparison operator
            elif self.current_token and self.current_token.type in [
                TokenType.LESS_THAN, TokenType.LESS_THAN_OR_EQUAL_TO,
                TokenType.GREATER_THAN, TokenType.GREATER_THAN_OR_EQUAL_TO,
                TokenType.EQUAL_TO, TokenType.NOT_EQUAL_TO
            ]:
                operator = self.current_token
                self.advance()
                
                # Don't parse right side if we hit a structural token
                if self.current_token and self.current_token.type in [TokenType.INDENT, TokenType.DEDENT, TokenType.NEWLINE]:
                    self.error(f"Unexpected {self.current_token.type} in comparison expression")
                    return expr
                
                right = self.term()
                expr = BinaryOperation(expr, operator, right)
            else:
                # Handle simple "is" equality: "x is 5" means "x == 5"
                # Create an EQUAL_TO token for this case
                operator = Token(TokenType.EQUAL_TO, "is", None, self.current_token.line if self.current_token else 0, self.current_token.column if self.current_token else 0)
                
                # Don't parse right side if we hit a structural token
                if self.current_token and self.current_token.type in [TokenType.INDENT, TokenType.DEDENT, TokenType.NEWLINE]:
                    self.error(f"Unexpected {self.current_token.type} in comparison expression")
                    return expr
                
                right = self.membership()
                expr = BinaryOperation(expr, operator, right)
        
        # Also support direct comparison operators (for compatibility)
        while self.current_token and self.current_token.type in [
            TokenType.LESS_THAN, TokenType.LESS_THAN_OR_EQUAL_TO,
            TokenType.GREATER_THAN, TokenType.GREATER_THAN_OR_EQUAL_TO
        ]:
            operator = self.current_token
            self.advance()
            
            # Don't parse right side if we hit a structural token
            if self.current_token and self.current_token.type in [TokenType.INDENT, TokenType.DEDENT, TokenType.NEWLINE]:
                self.error(f"Unexpected {self.current_token.type} in comparison expression")
                return expr
            
            right = self.membership()
            expr = BinaryOperation(expr, operator, right)
            
        return expr
    
    def membership(self):
        """Parse membership operations (in, not in)."""
        expr = self.bitwise_or()
        
        # Handle "not in" as a compound operator
        if self.current_token and self.current_token.type == TokenType.NOT:
            # Peek ahead to see if next token is IN
            next_token = self.peek(1)
            if next_token and next_token.type == TokenType.IN:
                # Consume NOT
                self.advance()
                # Consume IN
                in_token = self.current_token
                self.advance()
                # Parse the right side
                right = self.bitwise_or()
                # Create a NOT(IN) operation - wrap the IN operation in a NOT
                in_expr = BinaryOperation(expr, in_token, right)
                not_token = Token(TokenType.NOT, "not", None, in_token.line, in_token.column)
                expr = UnaryOperation(not_token, in_expr)
                return expr
        
        # Handle regular "in" operator
        while self.current_token and self.current_token.type == TokenType.IN:
            operator = self.current_token
            self.advance()
            right = self.bitwise_or()
            expr = BinaryOperation(expr, operator, right)
            
        return expr
        
    def bitwise_or(self):
        """Parse bitwise OR operations."""
        expr = self.bitwise_xor()
        
        while self.current_token and self.current_token.type == TokenType.BITWISE_OR:
            operator = self.current_token
            self.advance()
            right = self.bitwise_xor()
            expr = BinaryOperation(expr, operator, right)
            
        return expr
    
    def bitwise_xor(self):
        """Parse bitwise XOR operations."""
        expr = self.bitwise_and()
        
        while self.current_token and self.current_token.type == TokenType.BITWISE_XOR:
            operator = self.current_token
            self.advance()
            right = self.bitwise_and()
            expr = BinaryOperation(expr, operator, right)
            
        return expr
    
    def bitwise_and(self):
        """Parse bitwise AND operations."""
        expr = self.bitwise_shift()
        
        while self.current_token and self.current_token.type == TokenType.BITWISE_AND:
            operator = self.current_token
            self.advance()
            right = self.bitwise_shift()
            expr = BinaryOperation(expr, operator, right)
            
        return expr
        
    def bitwise_shift(self):
        """Parse bitwise shift operations."""
        expr = self.term()
        
        while self.current_token and self.current_token.type in [TokenType.LEFT_SHIFT, TokenType.RIGHT_SHIFT]:
            operator = self.current_token
            self.advance()
            right = self.term()
            expr = BinaryOperation(expr, operator, right)
            
        return expr

    def term(self):
        """Parse a term."""
        expr = self.factor()
        
        while self.current_token and self.current_token.type in [TokenType.PLUS, TokenType.MINUS, TokenType.CONCATENATE]:
            # When inside a function argument context (e.g. "fib with n minus 1 plus fib with n minus 2"),
            # stop consuming arithmetic operators if the right-hand side would start a new 'with'-style
            # function call.  Without this guard the parser greedily pulls "fib(n-2)" into the first
            # call's argument list, producing "fib((n-1) + fib(n-2))" instead of
            # "fib(n-1) + fib(n-2)".
            if self._in_argument_context and self._operator_followed_by_with_call():
                break
            operator = self.current_token
            self.advance()
            right = self.factor()
            expr = BinaryOperation(expr, operator, right)
            
        return expr

    def _operator_followed_by_with_call(self) -> bool:
        """Return True when the look-ahead pattern is:  <operator> <identifier> WITH
        
        Used by term() to decide whether to stop accumulating arithmetic inside a
        function-argument expression so that the next 'funcname with ...' becomes a
        sibling expression rather than being folded into the current argument.
        """
        # current_token is the PLUS/MINUS/CONCATENATE operator – peek forward.
        next1 = self.peek(1)   # should be the identifier (function name)
        next2 = self.peek(2)   # should be WITH
        if next1 is None or next2 is None:
            return False
        is_identifier = (next1.type == TokenType.IDENTIFIER or self._can_be_identifier(next1))
        is_with = (next2.type == TokenType.WITH or
                   (next2.type == TokenType.IDENTIFIER and
                    hasattr(next2, 'lexeme') and next2.lexeme.lower() == 'with'))
        return is_identifier and is_with

    def factor(self):
        """Parse a factor."""
        expr = self.power()
        
        while self.current_token and self.current_token.type in [TokenType.TIMES, TokenType.DIVIDED_BY, TokenType.MODULO, TokenType.FLOOR_DIVIDE]:
            operator = self.current_token
            self.advance()
            right = self.power()
            expr = BinaryOperation(expr, operator, right)
            
        return expr
    
    def power(self):
        """Parse power operations."""
        expr = self.unary()
        
        while self.current_token and self.current_token.type == TokenType.POWER:
            operator = self.current_token
            self.advance()
            right = self.unary()
            expr = BinaryOperation(expr, operator, right)
            
        return expr

    def unary(self):
        """Parse a unary expression."""
        # Handle standard unary operators
        if self.current_token and self.current_token.type in [TokenType.NOT, TokenType.MINUS, TokenType.BITWISE_NOT]:
            operator = self.current_token
            self.advance()
            right = self.unary()
            return UnaryOperation(operator, right)
        
        # Handle await expression: await async_function()
        if self.current_token and self.current_token.type == TokenType.AWAIT:
            line_num = self.current_token.line if hasattr(self.current_token, 'line') else 0
            self.advance()  # consume 'await'
            expression = self.unary()  # Get the async expression
            from ..parser.ast import AwaitExpression
            return AwaitExpression(expression, line_num)
        
        # Handle address-of operator: address of variable or &variable
        if self.current_token and self.current_token.type == TokenType.ADDRESS_OF:
            line_num = self.current_token.line if hasattr(self.current_token, 'line') else 0
            self.advance()  # consume 'address of' or '&'
            target = self.unary()  # Get the target expression
            return AddressOfExpression(target, line_num)
        
        # Handle dereference operator: dereference pointer or *pointer or value at pointer
        if self.current_token and self.current_token.type == TokenType.DEREFERENCE:
            line_num = self.current_token.line if hasattr(self.current_token, 'line') else 0
            self.advance()  # consume 'dereference' or '*' or 'value at'
            pointer = self.unary()  # Get the pointer expression
            return DereferenceExpression(pointer, line_num)
        
        # Handle sizeof operator: sizeof Type or size of variable
        if self.current_token and self.current_token.type == TokenType.SIZEOF:
            line_num = self.current_token.line if hasattr(self.current_token, 'line') else 0
            self.advance()  # consume 'sizeof' or 'size of'
            
            # Check if next token is a type keyword
            type_keywords = [
                TokenType.INTEGER, TokenType.FLOAT, TokenType.STRING, 
                TokenType.BOOLEAN, TokenType.LIST, TokenType.DICTIONARY,
                TokenType.POINTER
            ]
            
            if self.current_token and self.current_token.type in type_keywords:
                # It's a type name - create an identifier node for it
                type_name = self.current_token.lexeme
                self.advance()
                target = Identifier(type_name)
            else:
                # It's a variable or expression
                target = self.unary()
            
            return SizeofExpression(target, line_num)
        
        # Handle downgrade operator: downgrade rc_value (Rc -> Weak)
        if self.current_token and self.current_token.type == TokenType.DOWNGRADE:
            line_num = self.current_token.line if hasattr(self.current_token, 'line') else 0
            self.advance()  # consume 'downgrade'
            rc_expr = self.unary()  # Get the Rc expression
            return DowngradeExpression(rc_expr, line_num)
        
        # Handle upgrade operator: upgrade weak_value (Weak -> Rc, may return null)
        if self.current_token and self.current_token.type == TokenType.UPGRADE:
            line_num = self.current_token.line if hasattr(self.current_token, 'line') else 0
            self.advance()  # consume 'upgrade'
            weak_expr = self.unary()  # Get the Weak expression
            return UpgradeExpression(weak_expr, line_num)

        # Handle move operator: move x  (transfer ownership, invalidate source)
        if self.current_token and self.current_token.type == TokenType.MOVE:
            from ..parser.ast import MoveExpression
            line_num = self.current_token.line if hasattr(self.current_token, 'line') else 0
            self.advance()  # consume 'move'
            # Expect an identifier (the variable being moved)
            if self.current_token and (self.current_token.type == TokenType.IDENTIFIER or
                                        self._can_be_identifier(self.current_token)):
                var_name = self.current_token.lexeme
                self.advance()
                return MoveExpression(var_name, line_num)
            else:
                self.error("Expected variable name after 'move'")

        # Handle borrow operator: borrow x / borrow mutable x [with lifetime label]
        if self.current_token and self.current_token.type == TokenType.BORROW:
            from ..parser.ast import BorrowExpression
            line_num = self.current_token.line if hasattr(self.current_token, 'line') else 0
            self.advance()  # consume 'borrow'
            # Check for optional 'mutable' qualifier
            mutable = False
            if (self.current_token and self.current_token.type == TokenType.IDENTIFIER and
                    self.current_token.lexeme.lower() == "mutable"):
                mutable = True
                self.advance()  # consume 'mutable'
            # Expect an identifier (the variable being borrowed)
            if self.current_token and (self.current_token.type == TokenType.IDENTIFIER or
                                        self._can_be_identifier(self.current_token)):
                var_name = self.current_token.lexeme
                self.advance()
                # Optionally parse 'with lifetime <label>'
                lt = self._parse_lifetime_annotation()
                if lt is not None:
                    return BorrowExpressionWithLifetime(var_name, mutable, lt, line_num)
                return BorrowExpression(var_name, mutable, line_num)
            else:
                self.error("Expected variable name after 'borrow'")
        
        # Handle offsetof operator: offsetof StructName.field_name OR offset of field in StructName
        if self.current_token and self.current_token.type == TokenType.OFFSETOF:
            line_num = self.current_token.line if hasattr(self.current_token, 'line') else 0
            self.advance()  # consume 'offsetof' or 'offset of'
            
            # First, try to get field name
            if self.current_token and self.current_token.type == TokenType.IDENTIFIER:
                first_part = self.current_token.lexeme
                self.advance()
                
                # Check for "in StructName" syntax (natural: offset of field in Struct)
                if self.current_token and self.current_token.type == TokenType.IN:
                    self.advance()  # consume 'in'
                    
                    # Expect struct type name
                    if self.current_token and self.current_token.type == TokenType.IDENTIFIER:
                        struct_type = self.current_token.lexeme
                        field_name = first_part
                        self.advance()
                        
                        return OffsetofExpression(struct_type, field_name, line_num)
                    else:
                        self.error("Expected struct type name after 'in' in offsetof expression")
                
                # Check for ".field_name" syntax (C-style: offsetof StructName.field)
                elif self.current_token and self.current_token.type == TokenType.DOT:
                    self.advance()  # consume '.'
                    
                    # Expect field name
                    if self.current_token and self.current_token.type == TokenType.IDENTIFIER:
                        struct_type = first_part
                        field_name = self.current_token.lexeme
                        self.advance()
                        
                        return OffsetofExpression(struct_type, field_name, line_num)
                    else:
                        self.error("Expected field name after '.' in offsetof expression")
                else:
                    self.error("Expected 'in' or '.' after first identifier in offsetof expression")
            else:
                self.error("Expected field or struct name after 'offsetof'")
            
        return self.primary()
        
    def primary(self):
        """Parse a primary expression."""
        token = self.current_token
        
        if not token:
            return None  # Silently return None at end of input
        
        # Skip structural tokens - they should be handled by block-level constructs
        if token.type in [TokenType.INDENT, TokenType.DEDENT, TokenType.NEWLINE]:
            return None
        
        # Handle 'match' expression (can be used in expression context)
        if token.type == TokenType.MATCH:
            return self.match_expression()
        
        # Handle 'this' keyword for self-reference in class methods
        if token.type == TokenType.THIS:
            line_num = token.line if hasattr(token, 'line') else 0
            self.advance()  # consume 'this'
            expr = Identifier('this', line_num)
            return self._parse_member_access(expr)
        
        # Handle 'empty list' or 'empty dictionary' syntax for empty collections
        if token.type == TokenType.EMPTY:
            line_num = token.line if hasattr(token, 'line') else 0
            self.advance()  # consume 'empty'
            
            # Check what type of empty collection
            if self.current_token and self.current_token.type == TokenType.LIST:
                self.advance()  # consume 'list'
                
                # Check for "of Type" (e.g., "empty List of Float")
                if self.current_token and self.current_token.type == TokenType.OF:
                    self.advance()  # consume 'of'
                    # Parse the element type but don't use it (just consume tokens)
                    # The runtime will handle the empty list
                    element_type = self.parse_type()
                
                return ListExpression([], line_num)
            elif self.current_token and self.current_token.type == TokenType.DICTIONARY:
                self.advance()  # consume 'dictionary'
                return DictExpression({}, line_num)
            elif self.current_token and self.current_token.type == TokenType.IDENTIFIER:
                # Handle "empty array" or other collection types
                type_name = self.current_token.lexeme.lower()
                if type_name in ('array',):
                    self.advance()  # consume 'array'
                    return ListExpression([], line_num)
                elif type_name in ('dict', 'map'):
                    self.advance()  # consume 'dict' or 'map'
                    return DictExpression({}, line_num)
                else:
                    # Unknown type after 'empty', treat 'empty' as identifier
                    # Don't advance - leave the unknown identifier for next parse
                    return Identifier('empty', line_num)
            else:
                # Just 'empty' by itself, treat as identifier
                return Identifier('empty', line_num)
        
        # Handle 'create list of Type' or 'create dict of KeyType to ValueType'
        if token.type == TokenType.CREATE:
            return self.parse_generic_type_instantiation()
        
        # Handle 'Rc of Type with value' for smart pointer creation
        if token.type in (TokenType.RC, TokenType.WEAK, TokenType.ARC):
            return self.parse_rc_creation()
        
        # Handle 'new ClassName' for object instantiation
        if token.type == TokenType.NEW:
            line_num = token.line if hasattr(token, 'line') else 0
            self.advance()  # consume 'new'
            
            # Get class name - allow any token with a lexeme (identifier or contextual keyword)
            # This allows: new Point, new Number, new String, etc.
            if not self.current_token or not self.current_token.lexeme:
                self.error("Expected class name after 'new'")
            
            # Get the base class name without generic parameters
            # Generic parameters will be parsed separately below
            class_name = self.current_token.lexeme
            self.advance()
            
            # Check for generic type arguments: new Container<Integer>
            # (Note: parse_type might have already handled 'of' generics)
            type_arguments = []
            if self.current_token and self.current_token.type == TokenType.LESS_THAN:
                self.advance()  # Eat '<'
                
                # Type names can be identifiers or type keywords (Integer, String, List, etc.)
                type_token_types = [
                    TokenType.IDENTIFIER, TokenType.INTEGER, TokenType.STRING,
                    TokenType.FLOAT, TokenType.BOOLEAN, TokenType.LIST,
                    TokenType.DICTIONARY
                ]
                
                # Parse first type argument - can be simple or nested generic
                if self.current_token.type in type_token_types:
                    type_arg = self._parse_generic_type_argument()
                    type_arguments.append(type_arg)
                else:
                    self.error("Expected type argument name")
                
                # Parse additional type arguments separated by commas
                while self.current_token and self.current_token.type == TokenType.COMMA:
                    self.advance()  # Eat ','
                    if self.current_token.type in type_token_types:
                        type_arg = self._parse_generic_type_argument()
                        type_arguments.append(type_arg)
                    else:
                        self.error("Expected type argument name after comma")
                
                # Expect '>'
                if self.current_token and self.current_token.type == TokenType.GREATER_THAN:
                    self.advance()  # Eat '>'
                elif self.current_token and self.current_token.type == TokenType.RIGHT_SHIFT:
                    # Handle >> as > > for nested cases
                    from ..parser.lexer import Token
                    self.current_token = Token(TokenType.GREATER_THAN, '>', None,
                                              self.current_token.line, self.current_token.column + 1)
                else:
                    self.error("Expected '>' to close generic type arguments")
            
            # Check for constructor arguments (optional)
            # Supports both: new Class(args) and new Class with [args] or new Class with arg1 and arg2
            arguments = []
            if self.current_token and self.current_token.type == TokenType.LEFT_PAREN:
                # Syntax: new Class(arg1, arg2, ...)
                self.advance()  # consume (
                if self.current_token.type != TokenType.RIGHT_PAREN:
                    arguments.append(self.expression())
                    while self.current_token.type == TokenType.COMMA:
                        self.advance()
                        arguments.append(self.expression())
                self.eat(TokenType.RIGHT_PAREN)
            elif self.current_token and self.current_token.type == TokenType.WITH:
                # Syntax: new Class with [args] or new Class with arg1 and arg2
                self.advance()  # consume WITH
                
                if self.current_token and self.current_token.type == TokenType.LEFT_BRACKET:
                    # with [arg1, arg2, ...] syntax
                    self.advance()  # consume [
                    if self.current_token.type != TokenType.RIGHT_BRACKET:
                        arguments.append(self.expression())
                        while self.current_token.type == TokenType.COMMA:
                            self.advance()
                            arguments.append(self.expression())
                    self.eat(TokenType.RIGHT_BRACKET)
                else:
                    # with arg1 and arg2 syntax
                    arguments.append(self.expression())
                    while self.current_token and self.current_token.type == TokenType.AND:
                        self.advance()  # consume AND
                        arguments.append(self.expression())
            
            expr = ObjectInstantiation(class_name, arguments, type_arguments, line_num)
            # Check for member access on the instantiated object
            # Check for member access on the instantiated object
            return self._parse_member_access(expr)
        
        elif token.type == TokenType.CONVERT:
            return self.convert_expression()
            
        if token.type == TokenType.INTEGER_LITERAL:
            self.advance()
            return Literal("integer", token.literal)
            
        elif token.type == TokenType.FLOAT_LITERAL:
            self.advance()
            return Literal("float", token.literal)
            
        elif token.type == TokenType.CALLBACK:
            # Handle "callback function_name" syntax
            line_num = token.line if hasattr(token, 'line') else 0
            self.advance()  # consume 'callback'
            
            # Expect function name
            if not self.current_token or self.current_token.type != TokenType.IDENTIFIER:
                self.error("Expected function name after 'callback'")
            
            func_name = self.current_token.lexeme
            # Import the CallbackReference node
            from ..parser.ast import CallbackReference
            return CallbackReference(func_name, line_num)
        
        elif token.type == TokenType.LAMBDA:
            # Handle "lambda params: expr" syntax
            return self.parse_lambda_expression()
            
        elif token.type == TokenType.STRING_LITERAL:
            value = token.literal
            self.advance()
            return Literal('string', value)
        
        # F-string literal with interpolation
        elif token.type == TokenType.FSTRING_LITERAL:
            parts_data = token.literal  # List of ('literal', str, None) or ('expr', str, format_spec)
            line_number = token.line
            self.advance()
            
            # Convert parts to AST nodes
            parts = []
            # Import Parser and Lexer here to avoid circular dependency if they are in the same module
            from .lexer import Lexer
            from .parser import Parser
            from .ast import FStringExpression
            
            for part_tuple in parts_data:
                if len(part_tuple) == 2:
                    # Old format: (type, content)
                    part_type, content = part_tuple
                    format_spec = None
                elif len(part_tuple) == 3:
                    # New format: (type, content, format_spec)
                    part_type, content, format_spec = part_tuple
                else:
                    continue
                
                if part_type == 'literal':
                    # Literal string part
                    parts.append((True, content, None))
                else:  # part_type == 'expr'
                    # Parse the expression string
                    # Create a mini-lexer/parser for the expression
                    expr_lexer = Lexer(content)
                    expr_tokens = expr_lexer.scan_tokens()
                    expr_parser = Parser(expr_tokens)
                    expr_ast = expr_parser.expression()
                    parts.append((False, expr_ast, format_spec))
            
            return FStringExpression(parts, line_number)
            
        elif token.type == TokenType.TRUE:
            self.advance()
            return Literal("boolean", True)

        elif token.type == TokenType.FALSE:
            self.advance()
            return Literal("boolean", False)

        elif token.type == TokenType.NULL:
            self.advance()
            return Literal('null', None)

        elif token.type == TokenType.OLD:
            # old(expr) — pre-call value capture for use in postconditions
            line_num = token.line if hasattr(token, 'line') else 0
            self.advance()  # consume 'old'
            # Expect opening paren
            if self.current_token and self.current_token.type == TokenType.LPAREN:
                self.advance()  # consume '('
                inner_expr = self.expression()
                if self.current_token and self.current_token.type == TokenType.RPAREN:
                    self.advance()  # consume ')'
                return OldExpression(inner_expr, line_number=line_num)
            else:
                # Treat as identifier if no paren follows (graceful fallback)
                return Identifier('old', line_num)

        elif token.type == TokenType.IDENTIFIER or self._can_be_identifier(token):
            # Accept IDENTIFIER or keywords that can be used as variable names
            name = token.lexeme if hasattr(token, 'lexeme') else str(token.type)
            line_num = token.line if hasattr(token, 'line') else 0
            self.advance()
            
            # Special case: "length of X" syntax - parse as property access
            if name.lower() == 'length' and self.current_token and self.current_token.type == TokenType.OF:
                self.advance()  # consume 'of'
                
                # Parse the target expression - just get identifier or literal
                # Use primary() but avoid infinite recursion by getting the next primary element
                if not self.current_token:
                    self.error("Expected expression after 'of'")
                
                # Get the target (identifier or expression)
                target_expr = Identifier(self.current_token.lexeme, self.current_token.line if hasattr(self.current_token, 'line') else 0)
                self.advance()
                
                # Allow chaining with member access (e.g., "length of myObj.name")
                target_expr = self._parse_member_access(target_expr)

                # Return as a function call: length(target_expr)
                return FunctionCall("length", [target_expr], line_number=line_num)
            
            # Check for generic type arguments early (before other patterns)
            type_arguments = []
            if self.current_token and self.current_token.type == TokenType.LESS_THAN:
                type_arguments = self._parse_generic_type_arguments()
            
            # Special case: "call <function_name> with <args>" or "call (<expression>) with <args>" syntax
            if name.lower() == 'call':
                func_name_or_expr = None
                
                # Check for parenthesized expression: call (value at ptr) with args
                if self.current_token and self.current_token.type == TokenType.LEFT_PAREN:
                    self.advance()  # consume (
                    func_name_or_expr = self.expression()  # Parse the expression (e.g., value at ptr)
                    self.eat(TokenType.RIGHT_PAREN)
                # Check for direct identifier: call func_name with args OR call object.method
                elif self.current_token and self.current_token.type == TokenType.IDENTIFIER:
                    # Parse the identifier first
                    identifier = self.current_token.lexeme
                    id_line = self.current_token.line if hasattr(self.current_token, 'line') else 0
                    self.advance()  # consume identifier
                    
                    # Check if this is member access: call object.method
                    if self.current_token and self.current_token.type == TokenType.DOT:
                        # Create Identifier node and parse member access with call context
                        func_name_or_expr = Identifier(identifier, id_line)
                        func_name_or_expr = self._parse_member_access(func_name_or_expr, is_call_context=True)
                        # If member access parsed successfully, return it directly (it's already marked as method call)
                        return func_name_or_expr
                    else:
                        # Simple function call: call func_name
                        func_name_or_expr = identifier
                    
                    # Check for generic type arguments after function name
                    call_type_arguments = []
                    if self.current_token and self.current_token.type == TokenType.LESS_THAN:
                        call_type_arguments = self._parse_generic_type_arguments()
                
                # Now expect "with" keyword (for arguments) or no arguments
                if func_name_or_expr and self.current_token and self.current_token.type == TokenType.WITH:
                    self.advance()  # consume "with"
                    arguments = []
                    
                    # Parse first argument
                    arg = self.comparison()
                    if arg:
                        arguments.append(arg)
                    
                    # Parse additional arguments (comma or "and" separated)
                    while self.current_token and (self.current_token.type == TokenType.COMMA or
                                                   self.current_token.type == TokenType.AND):
                        self.advance()
                        arg = self.comparison()
                        if arg:
                            arguments.append(arg)
                    
                    # If func_name_or_expr is already a parsed expression (Identifier), create FunctionCall
                    if isinstance(func_name_or_expr, str):
                        expr = FunctionCall(func_name_or_expr, arguments, call_type_arguments, line_number=line_num)
                    else:
                        # It's already an expression node, just return it
                        expr = func_name_or_expr
                    return self._parse_member_access(expr, is_call_context=True)
                elif func_name_or_expr:
                    # "call <function_name>" or "call (<expr>)" without "with" - no args
                    if isinstance(func_name_or_expr, str):
                        expr = FunctionCall(func_name_or_expr, [], call_type_arguments if 'call_type_arguments' in locals() else [], line_number=line_num)
                    else:
                        # Already parsed as expression (e.g., member access)
                        expr = func_name_or_expr
                    return self._parse_member_access(expr, is_call_context=True)
            
            # Check if this is a function call with parentheses (e.g., "func(args)" or "func<T>(args)")
            if self.current_token and self.current_token.type == TokenType.LEFT_PAREN:
                self.advance()  # consume (
                arguments = []
                
                # Parse arguments
                if self.current_token.type != TokenType.RIGHT_PAREN:
                    arguments.append(self.expression())
                    while self.current_token.type == TokenType.COMMA:
                        self.advance()  # consume ,
                        arguments.append(self.expression())
                        
                self.eat(TokenType.RIGHT_PAREN)
                expr = FunctionCall(name, arguments, type_arguments, named_arguments=None, trailing_block=None, line_number=line_num)
                # Check for member access on function result
                return self._parse_member_access(expr)
            
            # Check if this is a function call with "with" keyword (e.g., "func with args")
            # This enables inline function calls without needing the 'call' keyword
            elif self.current_token and self.current_token.type == TokenType.WITH:
                # Use the full function_call parser which handles named arguments
                # Need to backtrack since function_call expects to be at the 'with' token
                # But we've already consumed the function name, so pass it along
                func_call = self.function_call(name, line_num)
                # Check for member access on function result
                return self._parse_member_access(func_call)
            
            # Check if this is a zero-argument function call (just identifier, but it's a function)
            # This is tricky: we need to distinguish between variable reference and function call
            # For now, we'll treat it as an identifier and let the interpreter handle it
            # The interpreter can check if it's a function and call it if needed
            # Or we can require explicit '()' for zero-arg functions: func()
            # 
            # SPECIAL CASE: Check for trailing block without 'with'
            # This handles: "func_name do ... end" (zero-arg function with trailing block)
            # But NOT: "variable do" in argument contexts (which would be a bug)
            
            # First parse member access to handle chaining like obj.method
            expr = Identifier(name)
            expr = self._parse_member_access(expr)
            
            # Now check if this is followed by 'do' - but NOT if we're parsing function arguments
            if (self.current_token and self.current_token.type == TokenType.DO 
                and not self._in_argument_context):
                trailing_block = self.parse_trailing_block()
                # Convert to function call
                if isinstance(expr, Identifier):
                    # Simple case: func_name do
                    func_call = FunctionCall(expr.name, [], None, None, trailing_block, line_num)
                    return func_call
                elif isinstance(expr, MemberAccess):
                    # Method call: obj.method do
                    # Keep the member access but mark it as having a trailing block
                    # We'll handle this in the interpreter
                    # For now, treat it as a function call to the method
                    return FunctionCall(expr, [], None, None, trailing_block, line_num)
                else:
                    self.error(f"Cannot attach trailing block to {type(expr).__name__}")
            
            return expr
            
        elif token.type == TokenType.LEFT_PAREN:
            line_num = token.line if hasattr(token, 'line') else 0
            self.advance()  # consume (
            expr = self.expression()
            
            # Check for type cast: (expression as TargetType)
            if self.current_token and self.current_token.type == TokenType.AS:
                self.advance()  # consume 'as'
                target_type = self.parse_type()  # Parse the target type
                self.eat(TokenType.RIGHT_PAREN)
                # Return type cast expression
                type_cast = TypeCastExpression(expr, target_type, line_num)
                return self._parse_member_access(type_cast)
            
            self.eat(TokenType.RIGHT_PAREN)
            # Check for member access on parenthesized expression
            return self._parse_member_access(expr)
            
        elif token.type == TokenType.LEFT_BRACKET:
            # List literal: [1, 2, 3]
            return self.parse_list_expression()
            
        elif token.type == TokenType.LEFT_BRACE:
            # Dict literal: {key: value}
            return self.parse_dict_expression()
            
        self.error(f"Unexpected token: {token.type}", error_type_key="unexpected_token")
    
    def convert_expression(self):
        """Parse a convert expression: convert expression to type."""
        # convert <expr> to <type>
        line_num = self.current_token.line
        self.eat(TokenType.CONVERT)
        
        # Parse expression to convert
        expr = self.expression()
        
        # Expect 'to'
        if not self.match(TokenType.TO):
            self.error("Expected 'to' after expression in convert statement")
            
        # Parse target type (or transformation hint like 'uppercase')
        if self.current_token.type == TokenType.IDENTIFIER:
            target_type = self.current_token.lexeme
            self.advance()
        elif self.current_token.type in (TokenType.STRING, TokenType.INTEGER, TokenType.FLOAT, TokenType.BOOLEAN):
            # Handle keywords used as types
            target_type = self.current_token.type.name.capitalize()
            self.advance()
        else:
            self.error("Expected target type or format after 'to'")
            target_type = "unknown" # unreachable
            
        return TypeCastExpression(expr, target_type, line_num)

    def _parse_member_access(self, base_expr, is_call_context=False):
        """Parse postfix operations: member access (.) and array indexing ([]).
        
        Args:
            base_expr: The base expression to apply postfix operations to
            is_call_context: True if we're in a 'call' statement (marks member access as method call)
        """
        iteration_count = 0
        while self.current_token and (self.current_token.type == TokenType.DOT or 
                                      self.current_token.type == TokenType.LEFT_BRACKET):
            
            if self.current_token.type == TokenType.LEFT_BRACKET:
                # Array indexing: array[index] or slice: array[start:end]
                line_num = self.current_token.line if hasattr(self.current_token, 'line') else 0
                self.advance()  # consume [

                # Parse optional start expression (may be absent for [:end] syntax)
                start_expr = None
                if self.current_token and self.current_token.type != TokenType.COLON:
                    start_expr = self.expression()

                if self.current_token and self.current_token.type == TokenType.COLON:
                    # Slice syntax: [start:end] or [start:end:step]
                    self.advance()  # consume :
                    end_expr = None
                    if self.current_token and self.current_token.type != TokenType.COLON and \
                            self.current_token.type != TokenType.RIGHT_BRACKET:
                        end_expr = self.expression()
                    step_expr = None
                    if self.current_token and self.current_token.type == TokenType.COLON:
                        self.advance()  # consume second :
                        if self.current_token and self.current_token.type != TokenType.RIGHT_BRACKET:
                            step_expr = self.expression()
                    self.eat(TokenType.RIGHT_BRACKET)
                    base_expr = SliceExpression(base_expr, start_expr, end_expr, step_expr, line_num)
                else:
                    # Normal index access
                    if not start_expr:
                        self.error("Expected index expression after '['")
                    self.eat(TokenType.RIGHT_BRACKET)
                    base_expr = IndexExpression(base_expr, start_expr, line_num)
                
            elif self.current_token.type == TokenType.DOT:
                # Member access: object.property or object.method()
                line_num = self.current_token.line if hasattr(self.current_token, 'line') else 0
                self.advance()  # consume .
                
                # Get member name - can be multi-word (e.g., "get value", "to string")
                # Keep consuming identifiers/contextual keywords until we hit WITH, LEFT_PAREN, or other operators
                if not self.current_token:
                    self.error("Expected member name after '.'")
                
                member_name_parts = []
                _first_member_token = True  # After '.', first token is always treated as contextual identifier
                while self.current_token:

                    # These structural tokens always stop member-name parsing.
                    if self.current_token.type in (
                        TokenType.WITH, TokenType.LEFT_PAREN, TokenType.DOT, TokenType.LEFT_BRACKET,
                        TokenType.PLUS, TokenType.MINUS, TokenType.TIMES, TokenType.DIVIDED_BY,
                        TokenType.EQUAL_TO, TokenType.NOT_EQUAL_TO, TokenType.LESS_THAN, TokenType.GREATER_THAN,
                        TokenType.AND, TokenType.OR, TokenType.NEWLINE, TokenType.DEDENT, TokenType.COMMA,
                        TokenType.RIGHT_PAREN, TokenType.RIGHT_BRACKET,
                        TokenType.END, TokenType.RETURN, TokenType.IF, TokenType.WHILE, TokenType.FOR,
                        TokenType.EOF,
                    ):
                        break

                    # For subsequent tokens in a multi-word name, require a plain identifier
                    # or an established contextual keyword (e.g. 'to' in 'to_string').
                    if not _first_member_token and not (
                        self.current_token.type == TokenType.IDENTIFIER or
                        self._can_be_identifier(self.current_token)
                    ):
                        break

                    # Consume this token as part of the member name.
                    # On the FIRST token after '.', any keyword is accepted as a contextual
                    # identifier — obj.set(), obj.has(), obj.add(), obj.contains(), etc.
                    member_name_parts.append(self.current_token.lexeme)
                    self.advance()
                    _first_member_token = False

                    # CRITICAL FIX: In call context, only consume ONE identifier (the method name).
                    if is_call_context:
                        break

                    # After the first token, continue only if followed by a plain identifier.
                    if self.current_token and self.current_token.type not in (TokenType.IDENTIFIER,):
                        break
                
                if not member_name_parts:
                    self.error(f"Expected member name after '.', got {self.current_token.type}")
                
                # Join multi-word names with underscore (e.g., "get value" -> "get_value")
                member_name = "_".join(member_name_parts)
                
                # Check if it's a method call with parentheses: object.method(args)
                if self.current_token and self.current_token.type == TokenType.LEFT_PAREN:
                    self.advance()  # consume (
                    arguments = []
                    
                    if self.current_token.type != TokenType.RIGHT_PAREN:
                        arguments.append(self.expression())
                        while self.current_token.type == TokenType.COMMA:
                            self.advance()
                            arguments.append(self.expression())
                    
                    self.eat(TokenType.RIGHT_PAREN)
                    base_expr = MemberAccess(base_expr, member_name, is_method_call=True, arguments=arguments, line_number=line_num)
                
                # Check if it's a method call with NLPL syntax: object.method with args
                elif self.current_token and self.current_token.type == TokenType.WITH:
                    self.advance()  # consume 'with'
                    arguments = []
                    
                    # Parse first argument - use comparison() to stop before 'and'
                    arg = self.comparison()
                    if arg:
                        arguments.append(arg)
                    
                    # Parse additional arguments (separated by comma or "and")
                    while self.current_token and (self.current_token.type == TokenType.COMMA or
                                                   self.current_token.type == TokenType.AND):
                        self.advance()  # consume comma or "and"
                        arg = self.comparison()
                        if arg:
                            arguments.append(arg)
                    
                    base_expr = MemberAccess(base_expr, member_name, is_method_call=True, arguments=arguments, line_number=line_num)
                else:
                    # Property access OR parameterless method call in 'call' context
                    # If is_call_context is True, this is "call object.method" - mark as method call
                    is_method = is_call_context
                    arguments = [] if is_method else None
                    base_expr = MemberAccess(base_expr, member_name, is_method_call=is_method, 
                                           arguments=arguments if is_method else None, line_number=line_num)
            
            iteration_count += 1
            
            # CRITICAL FIX: In call context (e.g., "call object.method"), only parse ONE member access
            # This prevents consuming tokens from the next statement
            # Break AFTER processing the DOT, so "with args" gets handled above
            # Example: "call obj.get\ncall obj.set" should NOT chain these!
            if is_call_context and iteration_count >= 1:
                break
        
        return base_expr
    
    def _parse_index_access(self, base_expr):
        """Parse index access (alias to _parse_member_access for semantic clarity)."""
        return self._parse_member_access(base_expr)
    
    def _can_be_identifier(self, token):
        """Check if a token type can be used as an identifier in this context."""
        # These keywords can be used as variable names
        contextual_keywords = {
            TokenType.MESSAGE, TokenType.TEXT, TokenType.ERROR,
            TokenType.VALUE, TokenType.NAME, TokenType.TYPE,
            TokenType.DATA, TokenType.INFO, TokenType.STATUS,
            TokenType.A, TokenType.AN, TokenType.NEW, TokenType.DEFAULT,
            # I/O contextual keywords
            TokenType.FILE, TokenType.OPEN, TokenType.CLOSE, TokenType.READ,
            TokenType.WRITE, TokenType.APPEND, TokenType.EXISTS,
            TokenType.DIRECTORY, TokenType.PATH,
            TokenType.LIST, TokenType.DICTIONARY,  # Collection types
            TokenType.LENGTH, TokenType.SET, TokenType.CONTAINS,
            TokenType.STRING, TokenType.INTEGER, TokenType.FLOAT, TokenType.BOOLEAN, TokenType.NUMBER,
            TokenType.EQUALS,  # Allow 'equals' as method name
            TokenType.EMPTY,
            TokenType.ADD,
            TokenType.TO,   # Allow 'to' in function names like "to string"
            # Common method-name keywords that must remain usable after '.'
            TokenType.HAS,      # obj.has(key)
            TokenType.INSERT,   # obj.insert(key, val)
            TokenType.UPDATE,   # obj.update(other)
            # Test-framework keywords usable as function/variable names
            # e.g. "function test that takes ...", "function describe ..."
            TokenType.TEST, TokenType.DESCRIBE, TokenType.IT,
            TokenType.EXPECT, TokenType.BEFORE_EACH, TokenType.AFTER_EACH,
            # RAII / Drop trait: allow 'drop' as a method name inside classes
            TokenType.DROP,
            # Statement-level keywords that are also common variable/function names
            TokenType.LABEL,   # 'label' is a keyword for labeled loops but common as a variable
            TokenType.REPEAT,  # 'repeat' starts repeat-loops but common as a variable/function
        }
        return token.type in contextual_keywords
        
    def identifier_or_function_call(self):
        """Parse an identifier or function call."""
        identifier = self.current_token.lexeme
        line_num = self.current_token.line
        self.advance()
        
        # Module access (e.g., module.function)
        if self.current_token and self.current_token.type == TokenType.DOT:
            self.advance()  # Eat dot
            
            if self.current_token.type == TokenType.IDENTIFIER or self._can_be_identifier(self.current_token):
                member_name = self.current_token.lexeme
                self.advance()
                
                # Function call (e.g., module.function with args)
                if self.current_token and self.current_token.type == TokenType.WITH:
                    return self.function_call(f"{identifier}.{member_name}", self.current_token.line)
                
                # Simple module access
                return ModuleAccess(identifier, member_name, self.current_token.line)
            else:
                self.error("Expected an identifier after '.'")
        
        # Zero-arg (or paren-delimited) function call: func() or func(a, b)
        # This is the canonical syntax for calling a function with no 'with' keyword.
        if self.current_token and self.current_token.type == TokenType.LEFT_PAREN:
            self.advance()  # consume (
            args = []
            while self.current_token and self.current_token.type != TokenType.RIGHT_PAREN:
                if args:
                    if self.current_token.type == TokenType.COMMA:
                        self.advance()  # consume ,
                args.append(self.expression())
            self.eat(TokenType.RIGHT_PAREN)
            return FunctionCall(identifier, args, None, None, None, line_num)

        # Function call with 'with' syntax
        if self.current_token and (self.current_token.type == TokenType.WITH or 
                                   (self.current_token.type == TokenType.IDENTIFIER and self.current_token.lexeme.lower() == 'with')):
            return self.function_call(identifier, self.current_token.line)
        
        # Simple identifier
        return Identifier(identifier, line_num)
        
    def function_call(self, function_name, line_number):
        """Parse a function call with positional and/or named arguments.
        
        Syntax:
            function_name                           # No arguments
            function_name with arg1                 # Single positional arg
            function_name with arg1 and arg2        # Multiple positional args
            function_name with param1: value1       # Single named arg
            function_name with param1: value1 and param2: value2  # Multiple named args
            function_name with arg1 and param1: value1  # Mixed (positional first)
        """
        # Eat 'with'
        if self.current_token and (self.current_token.type == TokenType.WITH or
                                   (self.current_token.type == TokenType.IDENTIFIER and self.current_token.lexeme.lower() == 'with')):
            self.advance()
            
        # Parse arguments (positional and named)
        positional_args = []
        named_args = {}
        seen_named = False  # Once we see a named arg, all subsequent must be named
        
        # Check if we have any arguments
        if (self.current_token and 
            self.current_token.type not in [TokenType.EOF, TokenType.NEWLINE, TokenType.INDENT, TokenType.DEDENT, TokenType.END]):
            
            # Parse first argument
            # DEBUG
            # print(f"DEBUG: Checking first arg, current token: {self.current_token}")
            # print(f"DEBUG: _is_named_argument() = {self._is_named_argument()}")
            if self._is_named_argument():
                # Named argument
                param_name, value_expr = self._parse_named_argument()
                named_args[param_name] = value_expr
                seen_named = True
            else:
                # Positional argument - set flag to prevent nested trailing block parsing
                self._in_argument_context = True
                arg = self.comparison()
                self._in_argument_context = False
                if arg:
                    positional_args.append(arg)
            
            # Additional arguments (separated by comma or 'and')
            while self.current_token and (self.current_token.type == TokenType.COMMA or
                                           self.current_token.type == TokenType.AND):
                self.advance()  # Eat comma or 'and'
                
                if self._is_named_argument():
                    # Named argument
                    if not seen_named and positional_args:
                        # First named arg after positional args
                        seen_named = True
                    param_name, value_expr = self._parse_named_argument()
                    named_args[param_name] = value_expr
                else:
                    # Positional argument - set flag to prevent nested trailing block parsing
                    if seen_named:
                        self.error(f"Positional argument cannot follow named argument in function call '{function_name}'")
                    self._in_argument_context = True
                    arg = self.comparison()
                    self._in_argument_context = False
                    if arg:
                        positional_args.append(arg)
        
        # Check for trailing block (do...end)
        trailing_block = None
        if self.current_token and self.current_token.type == TokenType.DO:
            trailing_block = self.parse_trailing_block()
        
        return FunctionCall(function_name, positional_args, named_arguments=named_args, 
                          trailing_block=trailing_block, line_number=line_number)
    
    def _is_named_argument(self):
        """Check if the current position starts a named argument (identifier: value)."""
        # Check if current token can be an identifier (including contextual keywords)
        is_identifier_like = (self.current_token.type == TokenType.IDENTIFIER or 
                             self._can_be_identifier(self.current_token))
        
        return (self.current_token and 
                is_identifier_like and
                self.peek() and
                self.peek().type == TokenType.COLON)
    
    def _parse_named_argument(self):
        """Parse a named argument (param_name: value).
        
        Returns:
            (param_name, value_expression)
        """
        param_name = self.current_token.lexeme
        self.advance()  # Consume parameter name
        self.advance()  # Consume colon
        
        # Parse the value expression
        value_expr = self.comparison()
        
        return (param_name, value_expr)
    
    def parse_trailing_block(self):
        """Parse a trailing block after a function call.
        
        Syntax:
            do
                [body]
            end
            
            do param1
                [body]
            end
            
            do param1 and param2
                [body]
            end
        
        Returns a LambdaExpression representing the block.
        """
        line_number = self.current_token.line
        
        # Eat 'do'
        self.eat(TokenType.DO)
        
        # Parse optional block parameters (separated by 'and')
        params = []
        
        # Check if we have parameters (not a newline or indent after 'do')
        if (self.current_token and 
            self.current_token.type not in [TokenType.NEWLINE, TokenType.INDENT, TokenType.EOF]):
            
            # Parse parameters separated by 'and'
            while True:
                if self.current_token.type == TokenType.IDENTIFIER or self._can_be_identifier(self.current_token):
                    param_name = self.current_token.lexeme
                    self.advance()
                    
                    # Optional type annotation (param_name as Type)
                    param_type = None
                    if self.current_token and self.current_token.type == TokenType.AS:
                        self.advance()  # Eat 'as'
                        param_type = self.parse_type()
                    
                    params.append(Parameter(param_name, param_type, line_number=line_number))
                    
                    # Check for more parameters
                    if self.current_token and self.current_token.type == TokenType.AND:
                        self.advance()  # Eat 'and'
                        continue
                    else:
                        break
                else:
                    break
        
        # Expect newline or indent after 'do' or after parameters
        while self.current_token and self.current_token.type == TokenType.NEWLINE:
            self.advance()
        
        # Check for INDENT (indentation-based syntax)
        if self.current_token and self.current_token.type == TokenType.INDENT:
            self.advance()  # Consume INDENT
            
            # Parse body until DEDENT
            body = []
            while (self.current_token and 
                   self.current_token.type != TokenType.EOF and
                   self.current_token.type != TokenType.DEDENT and
                   self.current_token.type != TokenType.END):
                statement = self.statement()
                if statement:
                    body.append(statement)
            
            # Consume DEDENT if present
            if self.current_token and self.current_token.type == TokenType.DEDENT:
                self.advance()
        else:
            # Fallback: Parse body with 'end' keyword (non-indented style)
            body = []
            while (self.current_token and 
                   self.current_token.type != TokenType.EOF and
                   self.current_token.type != TokenType.END):
                statement = self.statement()
                if statement:
                    body.append(statement)
        
        # Eat 'end'
        if self.current_token and self.current_token.type == TokenType.END:
            self.advance()
        else:
            self.error(f"Expected 'end' to close trailing block at line {line_number}")
        
        # Create and return lambda expression for the block
        return LambdaExpression(params, body, line_number)
        
    def repeat_n_times_loop(self):
        """Parse a repeat-n-times loop.
        
        Supports both indentation-based and end-keyword syntax:
            repeat N times ... DEDENT (indentation-based)
            repeat N times ... end (keyword-based)
            repeat N times ... end repeat (explicit)
        """
        line_number = self.current_token.line
        
        # Eat 'repeat'
        self.eat(TokenType.REPEAT)
        
        # Get the count - can be a number literal or variable (primary expression only)
        count = self.primary()  # Use primary() to avoid consuming 'times' as an operator
        
        # Eat 'times'
        self.eat(TokenType.TIMES)
        
        # Optional comma after "times"
        if self.current_token and self.current_token.type == TokenType.COMMA:
            self.advance()
        
        # Check for INDENT (indentation-based syntax)
        if self.current_token and self.current_token.type == TokenType.INDENT:
            self.advance()  # Consume INDENT
            
            # Parse body until DEDENT
            body = []
            while (self.current_token and 
                   self.current_token.type != TokenType.EOF and
                   self.current_token.type != TokenType.DEDENT):
                statement = self.statement()
                if statement:
                    body.append(statement)
            
            # Consume DEDENT
            if self.current_token and self.current_token.type == TokenType.DEDENT:
                self.advance()
        else:
            # Fallback: Parse body with 'end' keyword (old style)
            body = []
            while (self.current_token and self.current_token.type != TokenType.EOF and
                   self.current_token.type != TokenType.END):
                statement = self.statement()
                if statement:
                    body.append(statement)
                    
            # Eat 'end'
            if self.current_token and self.current_token.type == TokenType.END:
                self.advance()
                
                # Support for explicit "End repeat" or "End loop" syntax
                if self.current_token and self.current_token.type == TokenType.REPEAT:
                    self.advance()
                elif (self.current_token and self.current_token.type == TokenType.IDENTIFIER and 
                      self.current_token.lexeme.lower() == 'loop'):
                    self.advance()
                    
                # Optional period after end
                if (self.current_token and self.current_token.type == TokenType.DOT):
                    self.advance()
            
        return RepeatNTimesLoop(count, body, line_number)
    
    def repeat_while_loop(self):
        """Parse a repeat-while loop.
        
        Natural language while loop syntax:
            repeat while <condition> ... DEDENT (indentation-based)
            repeat while <condition> ... end (keyword-based)
            repeat while <condition> ... end repeat (explicit)
        """
        line_number = self.current_token.line
        
        # Eat 'repeat'
        self.eat(TokenType.REPEAT)
        
        # Eat 'while'
        self.eat(TokenType.WHILE)
        
        # Parse condition
        condition = self.expression()
        
        # Optional comma after condition
        if self.current_token and self.current_token.type == TokenType.COMMA:
            self.advance()
        
        # Check for INDENT (indentation-based syntax)
        if self.current_token and self.current_token.type == TokenType.INDENT:
            self.advance()  # Consume INDENT
            
            # Parse body until DEDENT
            body = []
            while (self.current_token and 
                   self.current_token.type != TokenType.EOF and
                   self.current_token.type != TokenType.DEDENT):
                statement = self.statement()
                if statement:
                    body.append(statement)
            
            # Consume DEDENT
            if self.current_token and self.current_token.type == TokenType.DEDENT:
                self.advance()
        else:
            # Fallback: Parse body with 'end' keyword (old style)
            body = []
            while (self.current_token and self.current_token.type != TokenType.EOF and
                   self.current_token.type != TokenType.END):
                statement = self.statement()
                if statement:
                    body.append(statement)
                    
            # Eat 'end'
            if self.current_token and self.current_token.type == TokenType.END:
                self.advance()
                
                # Support for explicit "End repeat" syntax
                if self.current_token and self.current_token.type == TokenType.REPEAT:
                    self.advance()
                elif (self.current_token and self.current_token.type == TokenType.IDENTIFIER and 
                      self.current_token.lexeme.lower() == 'loop'):
                    self.advance()
                    
                # Optional period after end
                if (self.current_token and self.current_token.type == TokenType.DOT):
                    self.advance()
        
        return RepeatWhileLoop(condition, body, line_number)
    
    def _parse_generic_type_argument(self):
        """
        Parse a single generic type argument which can be:
        - Simple: Integer, String, MyClass
        - Generic: List<Integer>, Dictionary<String, Integer>
        - Nested: List<List<Integer>>, Dictionary<String, List<Integer>>
        
        Returns the type as a string.
        """
        type_token_types = [
            TokenType.IDENTIFIER, TokenType.INTEGER, TokenType.STRING,
            TokenType.FLOAT, TokenType.BOOLEAN, TokenType.LIST,
            TokenType.DICTIONARY
        ]
        
        if self.current_token.type not in type_token_types:
            self.error("Expected type name")
            return "Any"
        
        # Get the base type name
        type_name = self.current_token.lexeme
        self.advance()
        
        # Check for generic parameters like List<Integer> or Dictionary<K, V>
        if self.current_token and self.current_token.type == TokenType.LESS_THAN:
            self.advance()  # Eat '<'
            
            # Recursively parse nested type arguments
            type_params = []
            type_params.append(self._parse_generic_type_argument())
            
            while self.current_token and self.current_token.type == TokenType.COMMA:
                self.advance()  # Eat ','
                type_params.append(self._parse_generic_type_argument())
            
            # Expect '>'
            if self.current_token and self.current_token.type == TokenType.GREATER_THAN:
                self.advance()  # Eat '>'
            elif self.current_token and self.current_token.type == TokenType.RIGHT_SHIFT:
                # Handle >> as > > for nested cases like List<List<Integer>>
                from ..parser.lexer import Token
                self.current_token = Token(TokenType.GREATER_THAN, '>', None,
                                          self.current_token.line, self.current_token.column + 1)
            else:
                self.error("Expected '>' to close generic type parameters")
            
            # Build the full generic type string
            type_name += f"<{', '.join(type_params)}>"
        
        return type_name
        
    def _parse_generic_type_arguments(self):
        """
        Parse generic type arguments in angle brackets: <Integer>, <T, U>, <List<Integer>>
        Returns a list of type names as strings.
        """
        if self.current_token.type != TokenType.LESS_THAN:
            return []
        
        self.advance()  # consume <
        type_args = []
        
        # Parse first type
        type_arg = self._parse_generic_type_argument()
        if type_arg:
            type_args.append(type_arg)
        
        # Parse additional types (comma-separated)
        while self.current_token and self.current_token.type == TokenType.COMMA:
            self.advance()  # consume ,
            type_arg = self._parse_generic_type_argument()
            if type_arg:
                type_args.append(type_arg)
        
        # Expect >
        if self.current_token and self.current_token.type == TokenType.GREATER_THAN:
            self.advance()  # consume >
        elif self.current_token and self.current_token.type == TokenType.RIGHT_SHIFT:
            # Handle >> as > > for nested cases
            from ..parser.lexer import Token
            self.current_token = Token(TokenType.GREATER_THAN, '>', None,
                                      self.current_token.line, self.current_token.column + 1)
        else:
            self.error("Expected '>' to close generic type arguments")
        
        return type_args
        
    def parse_generic_type_instantiation(self):
        """
        Parse generic type instantiation:
        - create list of Integer
        - create list of String with ["a", "b", "c"]
        - create list  (type inference)
        - create dict of String to Integer
        - create dict of String to List of Integer
        - create dictionary  (type inference)
        
        Returns a GenericTypeInstantiation AST node.
        """
        from ..parser.ast import GenericTypeInstantiation
        
        line_num = self.current_token.line if hasattr(self.current_token, 'line') else 0
        self.eat(TokenType.CREATE)  # consume 'create'
        
        # Expect type name (list, dict, set, tuple, queue, stack, etc.)
        # Note: Some collection names may be keywords (SET, STRUCT, etc.)
        # We allow them in this context as type names
        valid_types = [
            TokenType.LIST, TokenType.DICTIONARY, TokenType.IDENTIFIER,
            TokenType.SET,  # Allow SET keyword as collection type name
            TokenType.STRUCT, TokenType.ENUM, TokenType.UNION  # Allow struct/enum/union as type names
        ]
        
        if not self.current_token or self.current_token.type not in valid_types:
            self.error("Expected type name after 'create' (e.g., 'list', 'dict', 'set', 'tuple')")
        
        generic_name = self.current_token.lexeme.lower()  # "list", "dict", "set", "tuple", etc.
        self.advance()
        
        # Check for 'of' - now optional for type inference
        has_explicit_type = False
        if self.current_token and self.current_token.type == TokenType.OF:
            has_explicit_type = True
            self.advance()  # consume 'of'
        
        # Parse type arguments (only if explicit type provided)
        type_args = []
        
        if has_explicit_type:
            if generic_name == "dict" or generic_name == "dictionary":
                # Dictionary requires: create dict of KeyType to ValueType
                key_type = self._parse_generic_type_argument()
                type_args.append(key_type)
                
                # Expect 'to'
                if not self.current_token or self.current_token.type != TokenType.TO:
                    self.error("Expected 'to' between key and value types in dictionary creation")
                self.advance()  # consume 'to'
                
                value_type = self._parse_generic_type_argument()
                type_args.append(value_type)
            else:
                # List or other single-parameter generic: create list of ElementType
                element_type = self._parse_generic_type_argument()
                type_args.append(element_type)
        # If no explicit type, type_args remains empty - type inference will handle it
        
        # Check for optional initial value: with [...]
        initial_value = None
        if self.current_token and self.current_token.type == TokenType.WITH:
            self.advance()  # consume 'with'
            initial_value = self.expression()  # Parse the initial value expression
        
        return GenericTypeInstantiation(generic_name, type_args, initial_value, line_num)
    
    def parse_rc_type(self):
        """Parse reference counted smart pointer type: Rc of Type"""
        line_number = self.current_token.line
        self.eat(TokenType.RC)  # Consume 'rc'
        
        # Expect 'of' keyword
        if self.current_token.type == TokenType.OF:
            self.advance()
        else:
            self.error("Expected 'of' after 'rc'")
        
        # Parse the inner type (will return a string like "Integer" or "List of Integer")
        inner_type = self.parse_type()
        
        # Return formatted string like "Rc of Integer"
        return f"Rc of {inner_type}"
    
    def parse_weak_type(self):
        """Parse weak reference type: Weak of Type"""
        line_number = self.current_token.line
        self.eat(TokenType.WEAK)  # Consume 'weak'
        
        # Expect 'of' keyword
        if self.current_token.type == TokenType.OF:
            self.advance()
        else:
            self.error("Expected 'of' after 'weak'")
        
        # Parse the inner type
        inner_type = self.parse_type()
        
        # Return formatted string like "Weak of Integer"
        return f"Weak of {inner_type}"
    
    def parse_arc_type(self):
        """Parse atomic reference counted type: Arc of Type"""
        line_number = self.current_token.line
        self.eat(TokenType.ARC)  # Consume 'arc'
        
        # Expect 'of' keyword
        if self.current_token.type == TokenType.OF:
            self.advance()
        else:
            self.error("Expected 'of' after 'arc'")
        
        # Parse the inner type
        inner_type = self.parse_type()
        
        # Return formatted string like "Arc of Integer"
        return f"Arc of {inner_type}"
    
    def parse_rc_creation(self):
        """Parse Rc/Weak/Arc creation: 'Rc of Integer with 42'"""
        # Save which kind of smart pointer (RC, WEAK, or ARC)
        token = self.current_token
        if token.type == TokenType.RC:
            rc_kind = "rc"
        elif token.type == TokenType.WEAK:
            rc_kind = "weak"
        elif token.type == TokenType.ARC:
            rc_kind = "arc"
        else:
            self.error(f"Expected Rc, Weak, or Arc, got {token.type}")
        
        line_number = token.line
        self.advance()  # Move past RC/WEAK/ARC
        
        # Expect 'of'
        if self.current_token.type != TokenType.OF:
            self.error("Expected 'of' after Rc/Weak/Arc")
        self.advance()  # Move past 'of'
        
        # Parse the inner type
        inner_type = self.parse_type()
        
        # Expect 'with'
        if self.current_token.type != TokenType.WITH:
            self.error("Expected 'with' after type in Rc creation")
        self.advance()  # Move past 'with'
        
        # Parse the initial value expression
        value = self.expression()
        
        return RcCreation(rc_kind, inner_type, value, line_number)
    
    def _parse_lifetime_annotation(self):
        """Parse ``with lifetime <label>`` and return a :class:`LifetimeAnnotation`.

        Called when the caller already detected the WITH token followed by the
        LIFETIME token.  Consumes both tokens plus the following identifier and
        returns a :class:`~nlpl.parser.ast.LifetimeAnnotation` node.

        If the pattern does not match (no WITH/LIFETIME) returns ``None``
        without consuming any tokens.
        """
        if not (self.current_token and self.current_token.type == TokenType.WITH):
            return None
        # Peek ahead: only consume if the following token is LIFETIME
        if not (self.peek() and self.peek().type == TokenType.LIFETIME):
            return None
        line = self.current_token.line
        self.advance()  # consume 'with'
        self.advance()  # consume 'lifetime'
        if self.current_token and (self.current_token.type == TokenType.IDENTIFIER or
                                   self._can_be_identifier(self.current_token)):
            label = self.current_token.lexeme
            self.advance()  # consume the lifetime label identifier
            return LifetimeAnnotation(label, line_number=line)
        else:
            self.error("Expected a lifetime name (identifier) after 'lifetime'")

    def _try_parse_allocator_hint(self, base_type, line=None):
        """Optionally consume ``with allocator <name>`` after a collection type.

        Returns an :class:`AllocatorHint` node if the pattern is found,
        otherwise returns *base_type* unchanged.  Never consumes tokens that
        do not match the pattern.
        """
        if not (self.current_token and self.current_token.type == TokenType.WITH):
            return base_type
        # Only consume if the very next token is ALLOCATOR
        if not (self.peek() and self.peek().type == TokenType.ALLOCATOR):
            return base_type
        hint_line = self.current_token.line
        self.advance()  # consume 'with'
        self.advance()  # consume 'allocator'
        if self.current_token and (self.current_token.type == TokenType.IDENTIFIER or
                                   self._can_be_identifier(self.current_token)):
            alloc_name = self.current_token.lexeme
            self.advance()  # consume the allocator name identifier
            return AllocatorHint(base_type, alloc_name, line_number=hint_line)
        else:
            self.error("Expected an allocator name (identifier) after 'allocator'")

    def parse_type(self):
        """Parse a type annotation."""
        # Check for smart pointer types first: Rc, Weak, Arc
        if self.current_token.type == TokenType.RC:
            return self.parse_rc_type()
        elif self.current_token.type == TokenType.WEAK:
            return self.parse_weak_type()
        elif self.current_token.type == TokenType.ARC:
            return self.parse_arc_type()

        # Borrow type annotation: borrow [mutable] <type> [with lifetime <label>]
        # Used in parameter and return-type positions to indicate a borrowed value.
        #   x as borrow String
        #   x as borrow mutable String with lifetime outer
        if self.current_token and self.current_token.type == TokenType.BORROW:
            line = self.current_token.line
            self.advance()  # consume 'borrow'
            mutable = False
            if (self.current_token and self.current_token.type == TokenType.IDENTIFIER and
                    self.current_token.lexeme.lower() == "mutable"):
                mutable = True
                self.advance()  # consume 'mutable'
            # Parse the base type
            base_type = self.parse_type()
            # Optionally parse 'with lifetime <label>'
            lt = self._parse_lifetime_annotation()
            if lt is not None:
                # Return a ReturnTypeWithLifetime node so the lifetime checker can use it.
                return ReturnTypeWithLifetime(base_type, borrow_mutable=mutable, lifetime=lt,
                                             line_number=line)
            mut_prefix = "mutable " if mutable else ""
            return f"borrow {mut_prefix}{base_type}"
        
        # Accept both IDENTIFIER and built-in type keywords
        if self.current_token.type == TokenType.IDENTIFIER or self.current_token.type == TokenType.FUNCTION or self._can_be_identifier(self.current_token):
            if self.current_token.type == TokenType.FUNCTION:
                 type_name = "Function"
            else:
                 type_name = self.current_token.lexeme
            self.advance()
            
            # Check for generic type parameters: TypeName<T, K, V>
            if self.current_token and self.current_token.type == TokenType.LESS_THAN:
                self.advance()  # Eat '<'
                
                # Parse type arguments
                type_args = []
                type_args.append(self.parse_type())
                
                while self.current_token and self.current_token.type == TokenType.COMMA:
                    self.advance()  # Eat ','
                    type_args.append(self.parse_type())
                
                # Expect '>'
                if self.current_token and self.current_token.type == TokenType.GREATER_THAN:
                    self.advance()  # Eat '>'
                elif self.current_token and self.current_token.type == TokenType.RIGHT_SHIFT:
                    # Handle >> as > > for nested generics like List<List<T>>
                    # Replace >> with a single > for the next token
                    from ..parser.lexer import Token
                    self.current_token = Token(TokenType.GREATER_THAN, '>', None,
                                              self.current_token.line, self.current_token.column + 1)
                else:
                    self.error("Expected '>' to close generic type parameters")
                
                # Return formatted generic type string
                type_args_str = ", ".join(type_args)
                return f"{type_name}<{type_args_str}>"
            
            # Handle composite types like "List of Type" or "Dictionary of Type, Type"
            # This handles the case when List/Dictionary/Map are matched as contextual identifiers
            if type_name.lower() in ("list", "dictionary", "map"):
                # Check for 'of' keyword (TokenType.OF) or identifier with value "of"
                if (self.current_token and 
                    (self.current_token.type == TokenType.OF or 
                     (self.current_token.type == TokenType.IDENTIFIER and 
                      self.current_token.lexeme.lower() == "of"))):
                    self.advance()  # Eat "of"
                    
                    # Parse element type
                    element_type = self.parse_type()
                    
                    canonical_name = type_name.capitalize()
                    if canonical_name == "Map":
                        canonical_name = "Dictionary" # Normalize Map -> Dictionary
                    
                    if canonical_name == "List":
                        type_name = f"List of {element_type}"
                    else: # Dictionary
                        # Check for COMMA or TO
                        if self.current_token and self.current_token.type == TokenType.COMMA:
                            self.advance()
                            value_type = self.parse_type()
                            type_name = f"Dictionary of {element_type}, {value_type}"
                        elif self.current_token and self.current_token.type == TokenType.TO:
                            self.advance()
                            value_type = self.parse_type()
                            type_name = f"Dictionary of {element_type}, {value_type}"
                        else:
                             type_name = f"Dictionary of {element_type}"
                    
                    return self._try_parse_allocator_hint(type_name)
            
            return type_name
            
        elif self.current_token.type in (TokenType.INTEGER, TokenType.FLOAT, 
                                          TokenType.STRING, TokenType.BOOLEAN, 
                                          TokenType.NOTHING, TokenType.LIST, TokenType.DICTIONARY,
                                          TokenType.ARRAY, TokenType.POINTER):
            type_name = self.current_token.type.name.capitalize()
            self.advance()
            
            # Handle Pointer to Type syntax
            if type_name == "Pointer":
                if self.current_token and self.current_token.type == TokenType.TO:
                    self.advance()  # consume 'to'
                    base_type = self.parse_type()  # Recursively parse the base type
                    return f"Pointer to {base_type}"
                return type_name  # Just "Pointer" without base type
            
            # Handle Array of N bytes syntax (for fixed-size arrays)
            if type_name == "Array":
                # Check for 'of' keyword (TokenType.OF) or identifier with value "of"
                if (self.current_token and 
                    (self.current_token.type == TokenType.OF or
                     (self.current_token.type == TokenType.IDENTIFIER and 
                      self.current_token.lexeme.lower() == "of"))):
                    self.advance()  # Eat "of"
                    
                    # Get array size
                    if self.current_token and self.current_token.type == TokenType.INTEGER_LITERAL:
                        array_size = self.current_token.lexeme
                        self.advance()
                        
                        # Check for element type: "bytes" or a type name (e.g., "Point", "Integer")
                        if self.current_token and self.current_token.type == TokenType.IDENTIFIER:
                            element_type = self.current_token.lexeme
                            self.advance()
                            
                            # Special case: "bytes" means byte array
                            if element_type.lower() == "bytes":
                                return f"Array of {array_size} bytes"
                            else:
                                # Array of structured type: Array of 10 Point
                                return f"Array of {array_size} {element_type}"
                        
                        # No type specified, just size
                        return f"Array of {array_size}"
                    else:
                        self.error("Expected array size after 'of'")
                
                return type_name
            
            # Check for generic syntax: List<T> or Dictionary<K, V>
            if self.current_token and self.current_token.type == TokenType.LESS_THAN:
                self.advance()  # Eat '<'
                
                # Parse type arguments
                type_args = []
                type_args.append(self.parse_type())
                
                while self.current_token and self.current_token.type == TokenType.COMMA:
                    self.advance()  # Eat ','
                    type_args.append(self.parse_type())
                
                # Expect '>'
                if self.current_token and self.current_token.type == TokenType.GREATER_THAN:
                    self.advance()  # Eat '>'
                elif self.current_token and self.current_token.type == TokenType.RIGHT_SHIFT:
                    # Handle >> as > > for nested generics like List<List<T>>
                    # Replace >> with a single > for the next token
                    from ..parser.lexer import Token
                    self.current_token = Token(TokenType.GREATER_THAN, '>', None,
                                              self.current_token.line, self.current_token.column + 1)
                else:
                    self.error("Expected '>' to close generic type parameters")
                
                # Return formatted generic type string
                type_args_str = ", ".join(type_args)
                return f"{type_name}<{type_args_str}>"
            
            # Handle composite types like "List of Type" or "Dictionary of Type, Type"
            # This logic handles KEYWORDS (TokenType.LIST etc) that fell through
            if type_name in ("List", "Dictionary"):
                # Check for 'of' keyword (TokenType.OF) or identifier with value "of"
                if (self.current_token and 
                    (self.current_token.type == TokenType.OF or 
                     (self.current_token.type == TokenType.IDENTIFIER and 
                      self.current_token.lexeme.lower() == "of"))):
                    self.advance()  # Eat "of"
                    
                    # Parse element type (recursively to support nested types)
                    element_type = self.parse_type()
                    
                    if type_name == "List":
                        type_name = f"List of {element_type}"
                    else: # Dictionary
                        if self.current_token.type == TokenType.COMMA:
                            self.advance()
                            value_type = self.parse_type()
                            type_name = f"Dictionary of {element_type}, {value_type}"
                        elif self.current_token.type == TokenType.TO:
                             # Support Dictionary of K to V
                            self.advance()
                            value_type = self.parse_type()
                            type_name = f"Dictionary of {element_type}, {value_type}"
                        else:
                            type_name = f"Dictionary of {element_type}"
            
            return self._try_parse_allocator_hint(type_name)
        else:
            self.error("Expected a type name")
            
    def import_statement(self):
        """Parse an import statement."""
        # Syntax: Import <module_name> [as <alias>]
        # Also supports quoted paths: import "./mymodule" or import "../utils/helper"
        line_number = self.current_token.line
        
        # Eat 'import'
        self.eat(TokenType.IMPORT)
        
        # Get module name - accepts a quoted string path or a bare identifier
        if self.current_token.type == TokenType.STRING_LITERAL:
            # Quoted path, e.g. import "./mymodule" or import "../utils/helper"
            module_name = self.current_token.literal
            self.advance()
        elif self.current_token.type == TokenType.IDENTIFIER or self._can_be_identifier(self.current_token):
            module_name = self.current_token.lexeme
            self.advance()
            
            # Support dotted module names (e.g. core.result)
            while self.current_token and self.current_token.type == TokenType.DOT:
                self.advance() # Eat '.'
                module_name += "."
                if self.current_token.type == TokenType.IDENTIFIER or self._can_be_identifier(self.current_token):
                    module_name += self.current_token.lexeme
                    self.advance()
                else:
                    self.error("Expected module name after '.'")
        else:
            self.error("Expected a module name or a quoted path (e.g. \"./mymodule\")")
            
        # Check for optional alias
        alias = None
        if self.current_token and self.current_token.type == TokenType.AS:
            self.advance()  # Eat 'as'
            if self.current_token.type == TokenType.IDENTIFIER:
                alias = self.current_token.lexeme
                self.advance()
            else:
                self.error("Expected an alias name after 'as'")
                
        return ImportStatement(module_name, alias, line_number)
    
    def selective_import_statement(self):
        """Parse a selective import statement."""
        # Syntax: from <module_name> import <name1>, <name2>, ...
        line_number = self.current_token.line
        
        # Eat 'from'
        self.eat(TokenType.FROM)
        
        # Get module name - accepts a quoted string path or a bare identifier
        if self.current_token.type == TokenType.STRING_LITERAL:
            # Quoted path, e.g. from "./helpers" import format_date
            module_name = self.current_token.literal
            self.advance()
        elif self.current_token.type == TokenType.IDENTIFIER or self._can_be_identifier(self.current_token):
            module_name = self.current_token.lexeme
            self.advance()
            
            # Support dotted module names (e.g. test_modules.math_utils)
            while self.current_token and self.current_token.type == TokenType.DOT:
                self.advance()  # Eat '.'
                module_name += "."
                if self.current_token.type == TokenType.IDENTIFIER or self._can_be_identifier(self.current_token):
                    module_name += self.current_token.lexeme
                    self.advance()
                else:
                    self.error("Expected module name after '.'")
        else:
            self.error("Expected a module name or a quoted path after 'from' (e.g. \"./mymodule\")")
        
        # Eat 'import'
        self.eat(TokenType.IMPORT)
        
        # Parse imported names
        imported_names = []
        if self.current_token.type == TokenType.IDENTIFIER or self._can_be_identifier(self.current_token):
            imported_names.append(self.current_token.lexeme)
            self.advance()
            
            # Parse additional names separated by commas
            while self.current_token and self.current_token.type == TokenType.COMMA:
                self.advance()  # Eat ','
                if self.current_token.type == TokenType.IDENTIFIER or self._can_be_identifier(self.current_token):
                    imported_names.append(self.current_token.lexeme)
                    self.advance()
                else:
                    self.error("Expected name after ','")
        else:
            self.error("Expected at least one name to import")
        
        return SelectiveImport(module_name, imported_names, line_number)

    def private_declaration(self):
        """Parse a private declaration."""
        # Syntax: Define private function/class ...
        line_number = self.current_token.line
        
        # Eat 'define'
        self.eat(TokenType.DEFINE)
        
        # Eat 'private'
        self.eat(TokenType.PRIVATE)
        
        # Parse the declaration
        if self.current_token.type == TokenType.FUNCTION:
            declaration = self.function_definition()
        elif self.current_token.type == TokenType.CLASS:
            declaration = self.class_definition()
        else:
            self.error("Expected 'function' or 'class' after 'private'")
            
        return PrivateDeclaration(declaration, line_number)

    def interface_definition(self):
        """Parse an interface definition.
        
        Supports two syntaxes:
        1. interface Name ... end
        2. define an interface called Name ... end
        """
        line_number = self.current_token.line
        
        # Check for simpler syntax: interface Name
        if self.current_token.type == TokenType.INTERFACE:
            self.advance()  # consume 'interface'
            
            # Get the interface name
            if self.current_token.type == TokenType.IDENTIFIER:
                interface_name = self.current_token.lexeme
                self.advance()
            else:
                self.error("Expected an interface name")
            
            generic_parameters = []
            # No generic parameters in simple syntax for now
            
        else:
            # Full syntax: Define an interface called <identifier>
            # Eat 'define'
            self.eat(TokenType.DEFINE)
            
            # Skip optional 'an' or 'a'
            if self.current_token.type == TokenType.AN:
                self.advance()
            elif self.current_token.type == TokenType.A:
                self.advance()
            elif self.current_token.type == TokenType.IDENTIFIER and self.current_token.lexeme.lower() in ('an', 'a'):
                self.advance()
            
            # Eat 'interface'
            self.eat(TokenType.INTERFACE)
            
            # Eat 'called'
            self.eat(TokenType.CALLED)
            
            # Get the interface name
            if self.current_token.type == TokenType.IDENTIFIER:
                interface_name = self.current_token.lexeme
                self.advance()
            else:
                self.error("Expected an interface name")
            
            # Parse generic parameters if present
            generic_parameters = []
            if (self.current_token.type == TokenType.WITH and
                self.peek() and self.peek().type == TokenType.GENERIC and
                self.peek(2) and self.peek(2).type == TokenType.IDENTIFIER and
                self.peek(2).lexeme.lower() == 'parameters'):
                
                self.advance()  # Eat 'with'
                self.advance()  # Eat 'generic'
                self.advance()  # Eat 'parameters'
                
                # Parse parameter list
                if self.current_token.type == TokenType.IDENTIFIER:
                    generic_parameters.append(self.current_token.value)
                    self.advance()
                    
                    # Parse additional parameters
                    while (self.current_token.type == TokenType.COMMA):
                        self.advance()  # Eat comma
                        if self.current_token.type == TokenType.IDENTIFIER:
                            generic_parameters.append(self.current_token.value)
                            self.advance()
                        else:
                            self.error("Expected generic parameter name after comma")
        
        # Parse interface body (method signatures)
        methods = []
        
        # Consume INDENT if present
        if self.current_token and self.current_token.type == TokenType.INDENT:
            self.advance()
        
        while (self.current_token and self.current_token.type != TokenType.EOF and
               self.current_token.type != TokenType.END_INTERFACE and
               self.current_token.type != TokenType.DEDENT and
               not (self.current_token.type == TokenType.IDENTIFIER and 
                    self.current_token.lexeme.lower() == 'end')):
            
            # Simple syntax: [public/private] function name ... returns Type
            if (self.current_token.type == TokenType.FUNCTION or
                self.current_token.type in (TokenType.PUBLIC, TokenType.PRIVATE, TokenType.PROTECTED)):
                
                # Skip access modifier if present
                if self.current_token.type in (TokenType.PUBLIC, TokenType.PRIVATE, TokenType.PROTECTED):
                    self.advance()
                
                # Parse as function signature (no body)
                method_sig = self.interface_simple_method_signature()
                methods.append(method_sig)
            
            # Method signature (interface methods don't have implementations)
            # Syntax: "it has a method called <name> that returns <type>"
            elif (self.current_token.type == TokenType.IDENTIFIER and 
                self.current_token.lexeme.lower() == 'it' and
                self.peek() and self.peek().type == TokenType.HAS and
                self.peek(2) and self.peek(2).type in (TokenType.A, TokenType.AN, TokenType.IDENTIFIER) and
                self.peek(3) and self.peek(3).type in (TokenType.METHOD, TokenType.IDENTIFIER)):
                
                # Parse method signature (similar to method_definition but without body)
                method_sig = self.interface_method_signature()
                methods.append(method_sig)
            elif self.current_token.type == TokenType.INDENT:
                # Skip indentation
                self.advance()
            elif self.current_token.type == TokenType.NEWLINE:
                # Skip newlines
                self.advance()
            else:
                # Skip unknown tokens in interface body or break
                break
        
        # Eat 'end' - could be END_INTERFACE combined token, DEDENT, END token, or IDENTIFIER 'end'
        if self.current_token:
            if self.current_token.type == TokenType.DEDENT:
                self.advance()
            if self.current_token and self.current_token.type == TokenType.END_INTERFACE:
                self.advance()
            elif self.current_token and self.current_token.type == TokenType.END:
                self.advance()
                # Optionally consume "interface" after "end"
                if (self.current_token and self.current_token.type == TokenType.INTERFACE):
                    self.advance()
            elif self.current_token and self.current_token.type == TokenType.IDENTIFIER and self.current_token.lexeme.lower() == 'end':
                self.advance()
                
                # Support for explicit "End interface" syntax
                if (self.current_token and self.current_token.type == TokenType.INTERFACE):
                    self.advance()
            
            # Support for explicit "End the interface" syntax
            elif (self.current_token and self.current_token.type == TokenType.IDENTIFIER and 
                  self.current_token.lexeme.lower() == 'the' and self.peek() and 
                  self.peek().type == TokenType.IDENTIFIER and 
                  self.peek().lexeme.lower() == 'interface'):
                self.advance()  # Eat 'the'
                self.advance()  # Eat 'interface'
            
            # Optional period after end
            if (self.current_token and self.current_token.type == TokenType.DOT):
                self.advance()
        
        return InterfaceDefinition(interface_name, methods, generic_parameters, line_number)

    def interface_method_signature(self):
        """Parse an interface method signature without implementation."""
        # Syntax: It has a method called <identifier> that takes [parameters] [and returns <type>]
        line_number = self.current_token.line
        
        # Eat 'it' (it's an identifier)
        if self.current_token.type == TokenType.IDENTIFIER and self.current_token.lexeme.lower() == 'it':
            self.advance()
        else:
            self.error("Expected 'it' at start of method signature")
        
        # Eat 'has'
        self.eat(TokenType.HAS)
        
        # Skip optional 'a' or 'an'
        if self.current_token.type == TokenType.A:
            self.advance()
        elif self.current_token.type == TokenType.AN:
            self.advance()
        elif self.current_token.type == TokenType.IDENTIFIER and self.current_token.lexeme.lower() in ('a', 'an'):
            self.advance()
        
        # Eat 'method'
        if self.current_token.type == TokenType.METHOD:
            self.advance()
        elif self.current_token.type == TokenType.IDENTIFIER and self.current_token.lexeme.lower() == 'method':
            self.advance()
        else:
            self.error("Expected 'method' keyword")
        
        # Eat 'called'
        self.eat(TokenType.CALLED)
        
        # Get method name
        if self.current_token.type == TokenType.IDENTIFIER:
            method_name = self.current_token.lexeme
            self.advance()
        else:
            self.error("Expected method name")
        
        # Parse parameters
        parameters = []
        
        # Check for parameter list introduced by "that takes"
        if (self.current_token.type == TokenType.THAT and
            self.peek() and self.peek().type == TokenType.IDENTIFIER and
            self.peek().lexeme.lower() == 'takes'):
            
            self.advance()  # Eat 'that'
            self.advance()  # Eat 'takes'
            
            # Parse parameter list
            parameters, variadic = self.parameter_list()
        
        # Parse return type if present - "that returns <type>"
        return_type = None
        if (self.current_token.type == TokenType.THAT and
            self.peek() and self.peek().type == TokenType.RETURNS):
            self.advance()  # Eat 'that'
            self.advance()  # Eat 'returns'
            
            # Get return type
            if self.current_token.type == TokenType.IDENTIFIER:
                return_type = self.current_token.lexeme
                self.advance()
        
        # Create method signature node (AbstractMethodDefinition since it has no body)
        from ..parser.ast import AbstractMethodDefinition
        return AbstractMethodDefinition(method_name, parameters, return_type, line_number)

    def interface_simple_method_signature(self):
        """Parse simple function signature in interface: function name ... returns Type"""
        line_number = self.current_token.line
        
        # Eat 'function'
        self.eat(TokenType.FUNCTION)
        
        # Get function name (can be multi-word)
        function_name_parts = []
        while (self.current_token and 
               (self.current_token.type == TokenType.IDENTIFIER or self._can_be_identifier(self.current_token)) and
               self.current_token.type not in (TokenType.WITH, TokenType.RETURNS, TokenType.NEWLINE)):
            function_name_parts.append(self.current_token.lexeme)
            self.advance()
            if self.current_token and self.current_token.type in (TokenType.WITH, TokenType.RETURNS, TokenType.NEWLINE):
                break
        
        if not function_name_parts:
            self.error("Expected function name after 'function'")
        
        function_name = "_".join(function_name_parts)
        
        # Parse parameters if present
        parameters = []
        if self.current_token and self.current_token.type == TokenType.WITH:
            self.advance()  # consume 'with'
            parameters, _ = self.parameter_list()
        
        # Parse return type
        return_type = None
        if self.current_token and self.current_token.type == TokenType.RETURNS:
            self.advance()  # consume 'returns'
            return_type = self.parse_type()
        
        # Consume NEWLINE if present
        if self.current_token and self.current_token.type == TokenType.NEWLINE:
            self.advance()
        
        # Create method signature node
        from ..parser.ast import AbstractMethodDefinition
        return AbstractMethodDefinition(function_name, parameters, return_type, line_number)

    def abstract_class_short_syntax(self):
        """Parse abstract class with short syntax: abstract class Name"""
        line_number = self.current_token.line
        
        # Eat 'abstract' (IDENTIFIER)
        if self.current_token.type == TokenType.IDENTIFIER and self.current_token.lexeme.lower() == "abstract":
            self.advance()
        else:
            self.error("Expected 'abstract' keyword")
        
        # Eat 'class'
        self.eat(TokenType.CLASS)
        
        # Get class name
        if self.current_token.type == TokenType.IDENTIFIER or self._can_be_identifier(self.current_token):
            class_name = self.current_token.lexeme
            self.advance()
        else:
            self.error("Expected class name after 'abstract class'")
        
        # Check for inheritance
        parent_classes = []
        if self.current_token and self.current_token.type == TokenType.EXTENDS:
            self.advance()  # consume 'extends'
            if self.current_token.type == TokenType.IDENTIFIER:
                parent_classes.append(self.current_token.lexeme)
                self.advance()
        
        # Parse class body - same as regular class but track abstract methods
        properties = []
        methods = []
        abstract_methods = []
        concrete_methods = []
        
        # Consume INDENT if present
        if self.current_token and self.current_token.type == TokenType.INDENT:
            self.advance()
            
            # Parse class body
            while self.current_token and self.current_token.type != TokenType.DEDENT and self.current_token.type != TokenType.EOF:
                # Check for access modifiers
                access_modifier = 'public'
                if self.current_token.type in (TokenType.PRIVATE, TokenType.PUBLIC, TokenType.PROTECTED):
                    if self.current_token.type == TokenType.PRIVATE:
                        access_modifier = 'private'
                    elif self.current_token.type == TokenType.PUBLIC:
                        access_modifier = 'public'
                    elif self.current_token.type == TokenType.PROTECTED:
                        access_modifier = 'protected'
                    self.advance()
                
                # Check for abstract modifier
                is_abstract = False
                if self.current_token and self.current_token.type == TokenType.IDENTIFIER and self.current_token.lexeme.lower() == "abstract":
                    is_abstract = True
                    self.advance()  # consume 'abstract'
                
                # Parse member
                if self.current_token.type == TokenType.SET:
                    prop = self.set_statement_as_property()
                    prop.access_modifier = access_modifier
                    properties.append(prop)
                elif self.current_token.type == TokenType.FUNCTION:
                    if is_abstract:
                        # Abstract method - parse signature only
                        from ..parser.ast import AbstractMethodDefinition
                        line_num = self.current_token.line
                        self.advance()  # Eat 'function'
                        
                        # Get function name (multi-word support)
                        function_name_parts = []
                        while (self.current_token and 
                               (self.current_token.type == TokenType.IDENTIFIER or self._can_be_identifier(self.current_token)) and
                               self.current_token.type not in (TokenType.WITH, TokenType.RETURNS, TokenType.NEWLINE)):
                            function_name_parts.append(self.current_token.lexeme)
                            self.advance()
                            if self.current_token and self.current_token.type in (TokenType.WITH, TokenType.RETURNS, TokenType.NEWLINE):
                                break
                        
                        function_name = "_".join(function_name_parts) if function_name_parts else "unnamed"
                        
                        # Parse parameters
                        parameters = []
                        if self.current_token and self.current_token.type == TokenType.WITH:
                            self.advance()
                            parameters, _ = self.parameter_list()
                        
                        # Parse return type
                        return_type = None
                        if self.current_token and self.current_token.type == TokenType.RETURNS:
                            self.advance()
                            return_type = self.parse_type()
                        
                        if self.current_token and self.current_token.type == TokenType.NEWLINE:
                            self.advance()
                        
                        abstract_method = AbstractMethodDefinition(function_name, parameters, return_type, line_num)
                        abstract_method.access_modifier = access_modifier
                        abstract_methods.append(abstract_method)
                    else:
                        # Concrete method
                        from ..parser.ast import MethodDefinition
                        func = self.function_definition_short()
                        method = MethodDefinition(func.name, func.parameters, func.body, func.return_type, is_static=False, access_modifier=access_modifier, line_number=func.line_number)
                        concrete_methods.append(method)
                        methods.append(method)
                elif self.current_token.type == TokenType.NEWLINE:
                    self.advance()
                else:
                    break
            
            # Consume DEDENT
            if self.current_token and self.current_token.type == TokenType.DEDENT:
                self.advance()
        
        # Consume 'end' token if present
        if self.current_token and self.current_token.type == TokenType.END:
            self.advance()
        
        # Create AbstractClassDefinition
        from ..parser.ast import AbstractClassDefinition
        return AbstractClassDefinition(
            class_name,
            abstract_methods=abstract_methods,
            concrete_methods=concrete_methods,
            properties=properties,
            parent_classes=parent_classes,
            implemented_interfaces=[],
            generic_parameters=[],
            line_number=line_number
        )

    def abstract_class_definition(self):
        """Parse an abstract class definition."""
        # Syntax: Create an abstract class called <identifier> with:
        #           An abstract method called <identifier> that returns <type>.
        #           A concrete method called <identifier> that returns <type>.
        line_number = self.current_token.line
        
        # The first token could be "Create an abstract class called Shape with"
        if self.current_token.type == TokenType.IDENTIFIER:
            # Split the token text into lowercase parts for easy matching
            parts_lower = self.current_token.lexeme.lower().split()
            # Keep original parts for preserving case
            parts_original = self.current_token.lexeme.split()
            
            if "create" in parts_lower and "abstract" in parts_lower and "class" in parts_lower and "called" in parts_lower and "with" in parts_lower:
                # Extract the class name from the token (preserving original case)
                class_name = None
                try:
                    # The class name should be between "called" and "with"
                    called_index = parts_lower.index("called")
                    with_index = parts_lower.index("with")
                    if called_index < with_index and called_index + 1 < len(parts_original):
                        class_name = parts_original[called_index + 1]
                except ValueError:
                    self.error("Could not find class name in abstract class definition")
                
                # Advance past this token
                self.advance()
                
                # Check for colon (if any)
                if self.current_token.type == TokenType.COLON:
                    self.advance()
                    
            else:
                # Handling the case of separate tokens
                # Skip past 'create'
                self.advance()
                
                # Skip past 'an'
                if self.current_token.type == TokenType.IDENTIFIER and self.current_token.lexeme.lower() == "an":
                    self.advance()
                
                # Skip past 'abstract'
                if self.current_token.type == TokenType.IDENTIFIER and self.current_token.lexeme.lower() == "abstract":
                    self.advance()
                    
                # Skip past 'class'
                if self.current_token.type == TokenType.IDENTIFIER and self.current_token.lexeme.lower() == "class":
                    self.advance()
                    
                # Eat 'called'
                self.eat(TokenType.CALLED)
                
                # Get the class name (preserve original case)
                if self.current_token.type == TokenType.IDENTIFIER:
                    class_name = self.current_token.lexeme
                    self.advance()
                else:
                    self.error("Expected a class name")
                    
                # Eat 'with'
                self.eat(TokenType.WITH)
                
                # Eat optional colon
                if self.current_token.type == TokenType.COLON:
                    self.advance()
                    
        else:
            self.error("Expected abstract class definition to start with 'Create'")
        
        # Parse abstract and concrete methods
        abstract_methods = []
        concrete_methods = []
        
        while self.current_token and self.current_token.type != TokenType.EOF:
            # Handle method definitions which might be in a single token
            if self.current_token.type == TokenType.IDENTIFIER:
                # Split into lowercase for matching
                method_text_lower = self.current_token.lexeme.lower()
                # Keep original for preserving case
                method_text_original = self.current_token.lexeme
                
                is_abstract = False
                
                # Check if it's an abstract method
                if method_text_lower.startswith("an abstract method") or method_text_lower.startswith("abstract method"):
                    is_abstract = True
                
                # Extract method name and return type
                parts_lower = method_text_lower.split()
                parts_original = method_text_original.split()
                
                method_name = None
                return_type = None
                
                # Try to extract method name (after "called")
                try:
                    called_index = parts_lower.index("called")
                    if called_index + 1 < len(parts_original):
                        # Preserve original case
                        method_name = parts_original[called_index + 1]
                except ValueError:
                    self.error("Could not find method name in method definition")
                    
                # Try to extract return type (after "returns")
                try:
                    returns_index = parts_lower.index("returns")
                    if returns_index + 1 < len(parts_original):
                        # Get the return type and remove any trailing punctuation
                        return_type = parts_original[returns_index + 1].rstrip(".,;:")
                        
                        # Skip 'a' or 'an' article if present
                        if return_type.lower() in ['a', 'an'] and returns_index + 2 < len(parts_original):
                            return_type = parts_original[returns_index + 2].rstrip(".,;:")
                except ValueError:
                    self.error("Could not find return type in method definition")
                
                # Create the appropriate method definition
                if is_abstract:
                    # Use AbstractMethodDefinition for abstract methods
                    method = AbstractMethodDefinition(
                        name=method_name,
                        parameters=[],  # No parameters for simplicity
                        return_type=return_type,
                        line_number=self.current_token.line
                    )
                    abstract_methods.append(method)
                else:
                    # Use MethodDefinition for concrete methods
                    method = MethodDefinition(
                        name=method_name,
                        parameters=[],  # No parameters for simplicity
                        body=[],  # Empty body for concrete methods
                        return_type=return_type,
                        line_number=self.current_token.line
                    )
                    concrete_methods.append(method)
                    
                # Move past this token
                self.advance()
                
                # Skip period if present
                if self.current_token.type == TokenType.DOT:
                    self.advance()
                    
            # Check for end of class definition
            elif self.current_token.type == TokenType.IDENTIFIER and self.current_token.lexeme.lower() == "end":
                self.advance()
                if self.current_token.type == TokenType.IDENTIFIER and self.current_token.lexeme.lower() == "class":
                    self.advance()
                    break
            else:
                # Skip unknown tokens
                self.advance()
        
        # Return the abstract class definition
        return AbstractClassDefinition(
            name=class_name,
            abstract_methods=abstract_methods,
            concrete_methods=concrete_methods,
            line_number=line_number
        )

    def trait_definition(self):
        """Parse a trait definition."""
        # Syntax variations:
        #   1. Create a trait called <identifier> with:
        #   2. define a trait called <identifier>
        #         methods: ...
        line_number = self.current_token.line
        
        trait_name = None
        
        # Check if we're starting with DEFINE token
        if self.current_token.type == TokenType.DEFINE:
            # Eat 'define'
            self.eat(TokenType.DEFINE)
            
            # Skip optional 'a'
            if self.current_token.type == TokenType.A:
                self.advance()
            
            # Eat 'trait'
            self.eat(TokenType.TRAIT)
            
            # Eat 'called'
            self.eat(TokenType.CALLED)
            
            # Get the trait name
            if self.current_token.type == TokenType.IDENTIFIER:
                trait_name = self.current_token.lexeme
                self.advance()
            else:
                self.error("Expected a trait name")
        
        # Otherwise check for IDENTIFIER token with "Create a trait..."
        elif self.current_token.type == TokenType.IDENTIFIER:
            # Split the token text into lowercase parts for easy matching
            parts_lower = self.current_token.lexeme.lower().split()
            # Keep original parts for preserving case
            parts_original = self.current_token.lexeme.split()
            
            if "create" in parts_lower and "trait" in parts_lower and "called" in parts_lower and "with" in parts_lower:
                # Extract the trait name from the token (preserving original case)
                trait_name = None
                try:
                    # The trait name should be between "called" and "with"
                    called_index = parts_lower.index("called")
                    with_index = parts_lower.index("with")
                    if called_index < with_index and called_index + 1 < len(parts_original):
                        trait_name = parts_original[called_index + 1]
                except ValueError:
                    self.error("Could not find trait name in trait definition")
                
                # Advance past this token
                self.advance()
                
                # Check for colon (if any)
                if self.current_token.type == TokenType.COLON:
                    self.advance()
            else:
                # Handle multi-token case
                # Eat 'trait'
                self.eat(TokenType.IDENTIFIER)  # 'trait'
                
                # Eat 'called'
                self.eat(TokenType.CALLED)
                
                # Get the trait name
                if self.current_token.type == TokenType.IDENTIFIER:
                    trait_name = self.current_token.lexeme
                    self.advance()
                else:
                    self.error("Expected a trait name")
                    
                # Eat 'with'
                self.eat(TokenType.WITH)
                
                # Eat colon if present
                if self.current_token.type == TokenType.COLON:
                    self.advance()
        else:
            self.error("Expected trait definition to start with 'Create'")
        
        # Parse trait body - methods can be in single tokens
        required_methods = []
        provided_methods = []
        
        while self.current_token and self.current_token.type != TokenType.EOF:
            # Check for END_TRAIT token first
            if self.current_token.type == TokenType.END_TRAIT:
                self.advance()  # Consume 'end trait'
                break
            
            # Check for DEDENT (end of trait body)
            if self.current_token.type == TokenType.DEDENT:
                self.advance()
                continue
            
            # Handle THAT token (start of method requirement/provision)
            if self.current_token.type == TokenType.THAT:
                self.advance()  # Consume 'that'
                
                # Check if it's a required or provided method
                is_required = False
                is_provided = False
                
                if self.current_token.type == TokenType.IDENTIFIER:
                    if self.current_token.lexeme.lower() == 'requires':
                        is_required = True
                        self.advance()  # Consume 'requires'
                    elif self.current_token.lexeme.lower() == 'provides':
                        is_provided = True
                        self.advance()  # Consume 'provides'
                
                if is_required or is_provided:
                    # Expect: a method called <name> [with <param> [as <type>]] [returning <type>]
                    
                    # Skip 'a' if present
                    if self.current_token.type == TokenType.A:
                        self.advance()
                    
                    # Expect 'method'
                    if self.current_token.type == TokenType.METHOD:
                        self.advance()
                    else:
                        self.error("Expected 'method' after 'requires' or 'provides'")
                    
                    # Expect 'called'
                    if self.current_token.type == TokenType.CALLED:
                        self.advance()
                    else:
                        self.error("Expected 'called' after 'method'")
                    
                    # Get method name
                    if self.current_token.type == TokenType.IDENTIFIER:
                        method_name = self.current_token.lexeme
                        self.advance()
                    else:
                        self.error("Expected method name")
                    
                    # Parse parameters (optional)
                    parameters = []
                    if self.current_token.type == TokenType.WITH:
                        self.advance()  # Consume 'with'
                        
                        # Get parameter name
                        if self.current_token.type == TokenType.IDENTIFIER:
                            param_name = self.current_token.lexeme
                            self.advance()
                            
                            # Check for type annotation (as Type)
                            param_type = None
                            if self.current_token.type == TokenType.AS:
                                self.advance()  # Consume 'as'
                                param_type = self.parse_type()
                            
                            parameters.append(Parameter(param_name, param_type))
                    
                    # Parse return type (optional)
                    return_type = None
                    if self.current_token.type == TokenType.IDENTIFIER and self.current_token.lexeme.lower() == 'returning':
                        self.advance()  # Consume 'returning'
                        return_type = self.parse_type()
                    
                    # Create method definition
                    method = MethodDefinition(
                        name=method_name,
                        parameters=parameters,
                        body=[],  # Traits don't have method bodies (yet)
                        return_type=return_type,
                        line_number=line_number
                    )
                    
                    # Add to appropriate list
                    if is_required:
                        required_methods.append(method)
                    else:
                        provided_methods.append(method)
                else:
                    # Unknown pattern, skip token
                    self.advance()
            
            # Handle method definitions which might be in a single IDENTIFIER token (legacy support)
            elif self.current_token.type == TokenType.IDENTIFIER:
                # Split into lowercase for matching
                method_text_lower = self.current_token.lexeme.lower()
                # Keep original for preserving case
                method_text_original = self.current_token.lexeme
                
                is_required = False
                is_provided = False
                
                # Check if it's a required method
                if "required method" in method_text_lower or "a required method" in method_text_lower:
                    is_required = True
                # Check if it's a provided method
                elif "provided method" in method_text_lower or "a provided method" in method_text_lower:
                    is_provided = True
                
                if is_required or is_provided:
                    # Extract method name and return type
                    parts_lower = method_text_lower.split()
                    parts_original = method_text_original.split()
                    
                    method_name = None
                    param_name = None
                    return_type = None
                    
                    # Try to extract method name (after "called")
                    try:
                        called_index = parts_lower.index("called")
                        if called_index + 1 < len(parts_original):
                            # Preserve original case
                            method_name = parts_original[called_index + 1]
                    except ValueError:
                        self.error("Could not find method name in method definition")
                        
                    # Try to extract parameter (after "takes")
                    try:
                        takes_index = parts_lower.index("takes")
                        if takes_index + 1 < len(parts_original):
                            # Preserve original case
                            param_name = parts_original[takes_index + 1]
                    except ValueError:
                        pass  # Parameters might be optional
                        
                    # Try to extract return type (after "returns")
                    try:
                        returns_index = parts_lower.index("returns")
                        if returns_index + 1 < len(parts_original):
                            # Get the return type and remove any trailing punctuation
                            return_type = parts_original[returns_index + 1].rstrip(".,;:")
                            
                            # Skip 'a' or 'an' article if present
                            if return_type.lower() in ['a', 'an'] and returns_index + 2 < len(parts_original):
                                return_type = parts_original[returns_index + 2].rstrip(".,;:")
                    except ValueError:
                        self.error("Could not find return type in method definition")
                    
                    # Create parameters list (if any)
                    parameters = []
                    if param_name:
                        parameters.append(Parameter(param_name, None))
                    
                    # Create method
                    method = MethodDefinition(
                        name=method_name,
                        parameters=parameters,
                        body=[],  # Empty body
                        return_type=return_type,
                        line_number=self.current_token.line
                    )
                    
                    # Add to appropriate list
                    if is_required:
                        required_methods.append(method)
                    else:
                        provided_methods.append(method)
                    
                    # Move past this token
                    self.advance()
                    
                    # Skip period if present
                    if self.current_token and self.current_token.type == TokenType.DOT:
                        self.advance()
                else:
                    # Skip unknown tokens
                    self.advance()
                
            # Check for end of trait definition
            elif self.current_token.type == TokenType.IDENTIFIER and self.current_token.lexeme.lower() == "end":
                self.advance()  # Consume 'end'
                
                # Support for explicit "End trait" syntax
                if self.current_token.type == TokenType.IDENTIFIER and self.current_token.lexeme.lower() == "trait":
                    self.advance()  # Consume 'trait'
                    
                # Support for explicit "End the trait" syntax
                elif (self.current_token.type == TokenType.IDENTIFIER and 
                      self.current_token.lexeme.lower() == "the" and
                      self.peek() and self.peek().type == TokenType.IDENTIFIER and 
                      self.peek().lexeme.lower() == "trait"):
                    self.advance()  # Consume 'the'
                    self.advance()  # Consume 'trait'
                    
                # Skip period if present
                if self.current_token and self.current_token.type == TokenType.DOT:
                    self.advance()
                
                break
            else:
                # Skip unknown tokens
                self.advance()
        
        # Return the trait definition
        return TraitDefinition(
            name=trait_name,
            required_methods=required_methods,
            provided_methods=provided_methods,
            line_number=line_number
        )

    def parse_type_parameters(self):
        """Parse type parameters for generic types."""
        # Syntax: with generic parameters T, K, V
        parameters = []
        
        # Eat 'with'
        self.eat(TokenType.WITH)
        
        # Eat 'generic'
        self.eat(TokenType.GENERIC)
        
        # Eat 'parameters'
        self.eat(TokenType.IDENTIFIER)  # 'parameters'
        
        # Parse parameter list
        if self.current_token.type == TokenType.IDENTIFIER:
            param_name = self.current_token.value
            self.advance()
            
            # Check for constraints
            bounds = []
            if (self.current_token.type == TokenType.THAT and 
                self.peek() and self.peek().type == TokenType.EXTENDS):
                self.advance()  # Eat 'that'
                self.advance()  # Eat 'extends'
                
                # Parse bound type
                if self.current_token.type == TokenType.IDENTIFIER:
                    bounds.append(self.current_token.value)
                    self.advance()
                    
                    # Parse additional bounds
                    while (self.current_token.type == TokenType.AND):
                        self.advance()  # Eat 'and'
                        if self.current_token.type == TokenType.IDENTIFIER:
                            bounds.append(self.current_token.value)
                            self.advance()
                        else:
                            self.error("Expected bound type after 'and'")
            
            parameters.append(TypeParameter(param_name, bounds))
            
            # Parse additional parameters
            while (self.current_token.type == TokenType.COMMA):
                self.advance()  # Eat comma
                if self.current_token.type == TokenType.IDENTIFIER:
                    param_name = self.current_token.value
                    self.advance()
                    
                    # Check for constraints
                    bounds = []
                    if (self.current_token.type == TokenType.THAT and 
                        self.peek() and self.peek().type == TokenType.EXTENDS):
                        self.advance()  # Eat 'that'
                        self.advance()  # Eat 'extends'
                        
                        # Parse bound type
                        if self.current_token.type == TokenType.IDENTIFIER:
                            bounds.append(self.current_token.value)
                            self.advance()
                            
                            # Parse additional bounds
                            while (self.current_token.type == TokenType.AND):
                                self.advance()  # Eat 'and'
                                if self.current_token.type == TokenType.IDENTIFIER:
                                    bounds.append(self.current_token.value)
                                    self.advance()
                                else:
                                    self.error("Expected bound type after 'and'")
                    
                    parameters.append(TypeParameter(param_name, bounds))
                else:
                    self.error("Expected parameter name after comma")
        
        return parameters

    def parse_type_constraint(self):
        """Parse a type constraint."""
        # Syntax: that extends Type1 and Type2
        bounds = []
        
        # Eat 'that'
        self.eat(TokenType.THAT)
        
        # Eat 'extends'
        self.eat(TokenType.EXTENDS)
        
        # Parse bound type
        if self.current_token.type == TokenType.IDENTIFIER:
            bounds.append(self.current_token.value)
            self.advance()
            
            # Parse additional bounds
            while (self.current_token.type == TokenType.AND):
                self.advance()  # Eat 'and'
                if self.current_token.type == TokenType.IDENTIFIER:
                    bounds.append(self.current_token.value)
                    self.advance()
                else:
                    self.error("Expected bound type after 'and'")
        
        return TypeConstraint(bounds)

    # -----------------------------------------------------------------
    # Kind annotation parsing for Higher-Kinded Types (HKT)
    # Grammar:
    #   kindAnnotation ::= kindAtom ('->' kindAnnotation)?
    #   kindAtom       ::= '*' | '(' kindAnnotation ')'
    # -----------------------------------------------------------------

    def parse_kind_annotation(self):
        """Parse a kind annotation after ``::`` in a generic type parameter.

        Returns a :class:`StarKindAnnotation` or :class:`ArrowKindAnnotation`.
        """
        left = self._parse_kind_atom()

        # Check for arrow: * -> *
        if (self.current_token and
                self.current_token.type in (TokenType.ARROW, TokenType.ARROW_OP)):
            self.advance()  # Eat '->'
            right = self.parse_kind_annotation()  # right-associative
            return ArrowKindAnnotation(left, right,
                                       line_number=left.line_number)
        return left

    def _parse_kind_atom(self):
        """Parse a single kind atom: ``*`` or ``( kindAnnotation )``."""
        line = self.current_token.line if self.current_token else None

        # Parenthesized kind
        if self.current_token and self.current_token.type == TokenType.LEFT_PAREN:
            self.advance()  # Eat '('
            inner = self.parse_kind_annotation()
            if self.current_token and self.current_token.type == TokenType.RIGHT_PAREN:
                self.advance()  # Eat ')'
            else:
                self.error("Expected ')' to close kind annotation")
            return inner

        # Star kind: *
        if self.current_token and self.current_token.type == TokenType.TIMES:
            self.advance()  # Eat '*'
            return StarKindAnnotation(line_number=line)

        self.error("Expected '*' or '(' in kind annotation")

    def parse_type_guard(self):
        """Parse a type guard in an if statement."""
        # Syntax: if <expression> is a <type> then <statement>
        line_number = self.current_token.line
        
        # Eat 'if'
        self.eat(TokenType.IF)
        
        # Parse the condition expression
        condition = self.expression()
        
        # Eat 'is'
        self.eat(TokenType.IDENTIFIER)  # 'is'
        
        # Skip optional 'a'
        if self.current_token.type == TokenType.IDENTIFIER and self.current_token.lexeme.lower() == 'a':
            self.advance()
            
        # Get the type
        if self.current_token.type == TokenType.IDENTIFIER:
            type_name = self.current_token.lexeme
            self.advance()
        else:
            self.error("Expected a type")
            
        # Eat 'then'
        self.eat(TokenType.THEN)
        
        # Parse the body statement
        body = self.statement()
        
        return TypeGuard(
            condition=condition,
            type_name=type_name,
            body=body,
            line_number=line_number
        )

    def parse_parent_classes(self):
        """Parse parent class names."""
        parents = []
        while True:
            if self.match(TokenType.IDENTIFIER):
                parents.append(self.previous().lexeme)
                if not self.match(TokenType.COMMA):
                    break
            else:
                break
        return parents

    def parse_implemented_interfaces(self):
        """Parse implemented interface names."""
        interfaces = []
        while True:
            if self.match(TokenType.IDENTIFIER):
                interfaces.append(self.previous().lexeme)
                if not self.match(TokenType.COMMA):
                    break
            else:
                break
        return interfaces

    def parse_properties(self):
        """Parse class properties."""
        properties = []
        while not self.match(TokenType.METHODS, TokenType.END, TokenType.END_CLASS, TokenType.END_THE_CLASS):
            if self.match(TokenType.IDENTIFIER):
                name = self.previous()
                self.consume(TokenType.COLON, "Expected ':' after property name")
                type_annotation = self.parse_type_annotation()
                properties.append(PropertyDeclaration(name.lexeme, type_annotation))
            else:
                self.error(self.peek(), "Expected property name")
        return properties

    def parse_methods(self):
        """Parse class methods."""
        methods = []
        while not self.match(TokenType.END, TokenType.END_CLASS, TokenType.END_THE_CLASS):
            if self.match(TokenType.DEFINE):
                if self.match(TokenType.A, TokenType.AN):
                    if self.match(TokenType.METHOD):
                        methods.append(self.method_definition())
            else:
                self.error(self.peek(), "Expected method definition")
        return methods

    def method_definition_short(self):
        """Parse a method definition (short syntax without 'define' keyword)."""
        name = self.consume(TokenType.IDENTIFIER, "Expected method name")
        
        # Parse parameters
        parameters = []
        self.consume(TokenType.THAT, "Expected 'that' after method name")
        self.consume(TokenType.TAKES, "Expected 'takes' after 'that'")
        
        while not self.match(TokenType.RETURNS):
            if self.match(TokenType.IDENTIFIER):
                param_name = self.previous()
                self.consume(TokenType.COLON, "Expected ':' after parameter name")
                param_type = self.parse_type_annotation()
                parameters.append((param_name.lexeme, param_type))
            else:
                self.error(self.peek(), "Expected parameter name")
        
        # Parse return type
        return_type = self.parse_type_annotation()
        
        # Parse method body
        body = []
        while not self.match(TokenType.END, TokenType.END_METHOD, TokenType.END_THE_METHOD):
            body.append(self.statement())
        
        return MethodDefinition(
            name=name.lexeme,
            parameters=parameters,
            return_type=return_type,
            body=body
        )

    def parse_type_annotation(self):
        """Parse a type annotation."""
        if self.match(TokenType.IDENTIFIER):
            return self.previous().lexeme
        elif self.match(TokenType.LIST):
            self.consume(TokenType.LESS_THAN, "Expected '<' after 'List'")
            element_type = self.parse_type_annotation()
            self.consume(TokenType.GREATER_THAN, "Expected '>' after element type")
            return f"List<{element_type}>"
        elif self.match(TokenType.DICTIONARY):
            self.consume(TokenType.LESS_THAN, "Expected '<' after 'Dictionary'")
            key_type = self.parse_type_annotation()
            self.consume(TokenType.COMMA, "Expected ',' between key and value types")
            value_type = self.parse_type_annotation()
            self.consume(TokenType.GREATER_THAN, "Expected '>' after value type")
            return f"Dictionary<{key_type}, {value_type}>"
        else:
            self.error(self.peek(), "Expected type annotation")
            return "Any"

    def type_alias_definition(self):
        """Parse a type alias definition."""
        # Syntax: Create a type alias called <identifier> that is a <type>
        # Examples:
        # - Create a type alias called StringMap that is a dictionary with string keys and string values.
        # - Create a type alias called NumberList that is a list of integers.
        line_number = self.current_token.line
        
        # Handle the case where the entire phrase is in a single token
        if self.current_token.type == TokenType.IDENTIFIER:
            # Get the full text of the token and check if it contains the key parts
            full_text = self.current_token.lexeme
            parts = full_text.lower().split()
            
            # Check if this is a type alias definition
            if "create" in parts and "type" in parts and "alias" in parts and "called" in parts:
                # Extract the type alias name (after "called")
                alias_name = None
                target_type = None
                
                try:
                    # Extract the alias name (should be after "called")
                    called_index = parts.index("called")
                    if called_index + 1 < len(parts):
                        alias_name = full_text.split()[called_index + 1]
                        
                    # Extract the target type
                    if "is" in parts:
                        is_index = parts.index("is")
                        
                        # Check for dictionary type
                        if "dictionary" in parts and "with" in parts and "keys" in parts and "values" in parts:
                            # This is a dictionary type with key and value types
                            key_type = None
                            value_type = None
                            
                            try:
                                # Find key type (after "with")
                                with_index = parts.index("with")
                                if with_index + 1 < len(parts):
                                    key_type = full_text.split()[with_index + 1]  # should be "string"
                                    
                                # Find value type (before "values")
                                values_index = parts.index("values")
                                if values_index > 1:
                                    # Get the token before "values", which is usually "and"
                                    if parts[values_index - 1] == "and" and values_index - 2 >= 0:
                                        # Get the token before "and", which should be the value type
                                        value_type = full_text.split()[values_index - 2]
                                    else:
                                        # Handle the case where we don't have "and" before "values"
                                        value_type = "string"  # Default to string as a fallback
                                    
                                if key_type and value_type:
                                    target_type = f"dictionary<{key_type}, {value_type}>"
                            except (ValueError, IndexError):
                                pass
                        
                        # Check for list type
                        elif "list" in parts and "of" in parts:
                            try:
                                # Find element type (after "of")
                                of_index = parts.index("of")
                                if of_index + 1 < len(parts):
                                    element_type = full_text.split()[of_index + 1].rstrip(".,;")
                                    # Handle plural forms - convert to singular
                                    if element_type.lower() == "integers":
                                        element_type = "integer"
                                    target_type = f"list<{element_type}>"
                            except (ValueError, IndexError):
                                pass
                        
                        # For other simple types
                        elif is_index + 2 < len(parts) and parts[is_index + 1] in ["a", "an"]:
                            target_type = full_text.split()[is_index + 2]
                except (ValueError, IndexError):
                    pass
                
                # If we successfully extracted both name and type, we can create the TypeAliasDefinition
                if alias_name and target_type:
                    # Advance past this token
                    self.advance()
                    
                    # Skip period if present
                    if self.current_token and self.current_token.type == TokenType.DOT:
                        self.advance()
                        
                    return TypeAliasDefinition(
                        name=alias_name,
                        target_type=target_type,
                        line_number=line_number
                    )
                
        # Traditional token-by-token parsing as fallback
        # This part handles the case where the declaration spans multiple tokens
        
        # Eat 'alias'
        self.eat(TokenType.IDENTIFIER)  # 'alias'
        
        # Eat 'called'
        self.eat(TokenType.CALLED)
        
        # Get the alias name
        if self.current_token.type == TokenType.IDENTIFIER:
            alias_name = self.current_token.lexeme
            self.advance()
        else:
            self.error("Expected an alias name")
            
        # Eat 'that'
        self.eat(TokenType.THAT)
        
        # Eat 'is'
        self.eat(TokenType.IDENTIFIER)  # 'is'
        
        # Skip optional 'a'
        if self.current_token.type == TokenType.IDENTIFIER and self.current_token.lexeme.lower() in ['a', 'an']:
            self.advance()
            
        # Get the target type
        if self.current_token.type == TokenType.IDENTIFIER:
            target_type = self.current_token.lexeme
            self.advance()
            
            # Handle generic types (e.g., dictionary with string keys and string values)
            if target_type.lower() == 'dictionary':
                # Eat 'with'
                self.eat(TokenType.WITH)
                
                # Get key type
                if self.current_token.type == TokenType.IDENTIFIER:
                    key_type = self.current_token.lexeme
                    self.advance()
                    
                    # Eat 'keys'
                    self.eat(TokenType.IDENTIFIER)  # 'keys'
                    
                    # Eat 'and'
                    self.eat(TokenType.AND)
                    
                    # Get value type
                    if self.current_token.type == TokenType.IDENTIFIER:
                        value_type = self.current_token.lexeme
                        self.advance()
                        
                        # Eat 'values'
                        self.eat(TokenType.IDENTIFIER)  # 'values'
                        
                        target_type = f"dictionary<{key_type}, {value_type}>"
                        
            # Handle list types (e.g., list of integers)
            elif target_type.lower() == 'list':
                # Eat 'of'
                self.eat(TokenType.IDENTIFIER)  # 'of'
                
                # Get element type
                if self.current_token.type == TokenType.IDENTIFIER:
                    element_type = self.current_token.lexeme
                    # Handle plural forms - convert to singular
                    if element_type.lower() == "integers":
                        element_type = "integer"
                    self.advance()
                    
                    target_type = f"list<{element_type}>"
        else:
            self.error("Expected a type")
            
        # Optional period after type alias definition
        if self.current_token and self.current_token.type == TokenType.DOT:
            self.advance()
            
        return TypeAliasDefinition(
            name=alias_name,
            target_type=target_type,
            line_number=line_number
        )

    def return_statement(self):
        """Parse a return statement."""
        token = self.current_token
        # Accept both 'return' and 'returns'
        if self.current_token.type == TokenType.RETURN:
            self.eat(TokenType.RETURN)
        else:
            self.eat(TokenType.RETURNS)
        
        # Parse the return value expression
        value = self.expression()
            
        return ReturnStatement(value, token.line)
    
    def break_statement(self):
        """Parse a break statement.
        
        Supports:
            break           - break innermost loop
            break label     - break labeled loop
        """
        line_num = self.current_token.line if hasattr(self.current_token, 'line') else 0
        self.eat(TokenType.BREAK)
        
        # Check for optional label
        label = None
        if self.current_token and self.current_token.type == TokenType.IDENTIFIER:
            label = self.current_token.lexeme
            self.advance()
        
        return BreakStatement(line_num, label)
    
    def continue_statement(self):
        """Parse a continue statement.
        
        Supports:
            continue        - continue innermost loop
            continue label  - continue labeled loop
        """
        line_num = self.current_token.line if hasattr(self.current_token, 'line') else 0
        self.eat(TokenType.CONTINUE)
        
        # Check for optional label
        label = None
        if self.current_token and self.current_token.type == TokenType.IDENTIFIER:
            label = self.current_token.lexeme
            self.advance()
        
        return ContinueStatement(line_num, label)
    
    def fallthrough_statement(self):
        """Parse a fallthrough statement in switch cases.
        
        Syntax:
            fallthrough    - continue to next case in switch
        """
        line_num = self.current_token.line if hasattr(self.current_token, 'line') else 0
        self.eat(TokenType.FALLTHROUGH)
        from ..parser.ast import FallthroughStatement
        return FallthroughStatement(line_num)

    def generic_type_parameters(self):
        """Parse generic type parameters."""
        # Syntax: with <type> parameter <type> parameter ...
        parameters = []
        
        # Eat 'with'
        self.eat(TokenType.WITH)
        
        while True:
            # Get the parameter type
            if self.current_token.type == TokenType.IDENTIFIER:
                param_type = self.current_token.value
                self.advance()
                
                # Eat 'parameter'
                self.eat(TokenType.IDENTIFIER)  # 'parameter'
                
                parameters.append(param_type)
                
                # Check if there are more parameters
                if self.current_token.type == TokenType.IDENTIFIER:
                    continue
                else:
                    break
            else:
                self.error("Expected a type parameter")
                break
                
        return parameters

    def type_guards(self):
        """Parse type guards."""
        # Syntax: if <expression> is a <type> then <statement>
        line_number = self.current_token.line
        
        # Check if this is a complete sentence rather than an expression
        if self.current_token.type == TokenType.IDENTIFIER:
            # Process the natural language phrase
            full_text = self.current_token.lexeme
            parts = full_text.lower().split()
            
            # Check if this is a type guard pattern
            if "if" in parts and "is" in parts and "then" in parts:
                # Extract the condition variable (between 'if' and 'is')
                condition_var = None
                type_name = None
                
                try:
                    if_index = parts.index("if")
                    is_index = parts.index("is")
                    then_index = parts.index("then")
                    
                    if if_index + 1 < is_index:
                        # Get the variable name between 'if' and 'is'
                        condition_var = full_text.split()[if_index + 1]
                    
                    # Get the type name
                    # Check if there's an 'a' after 'is'
                    if is_index + 1 < then_index:
                        if parts[is_index + 1] == "a":
                            # Type is after 'a'
                            if is_index + 2 < then_index:
                                type_name = full_text.split()[is_index + 2]
                        else:
                            # Type directly after 'is'
                            type_name = full_text.split()[is_index + 1]
                except (ValueError, IndexError):
                    pass
                
                # If we successfully extracted the condition and type, create the TypeGuard
                if condition_var and type_name:
                    # Create the condition identifier
                    condition = Identifier(name=condition_var, line_number=line_number)
                    
                    # Advance past this token
                    self.advance()
                    
                    # Parse the body statements
                    body_statements = []
                    while self.current_token.type != TokenType.EOF:
                        if (self.current_token.type == TokenType.IDENTIFIER and 
                            "end if" in self.current_token.lexeme.lower()):
                            self.advance()  # Consume "End if"
                            
                            # Skip period if present
                            if self.current_token.type == TokenType.DOT:
                                self.advance()
                            break
                        
                        # Special handling for variable declarations in the body
                        if (self.current_token.type == TokenType.IDENTIFIER and
                            "create" in self.current_token.lexeme.lower() and
                            "called" in self.current_token.lexeme.lower()):
                            # Extract variable details
                            var_text = self.current_token.lexeme
                            var_parts = var_text.lower().split()
                            
                            var_name = None
                            var_type = None
                            
                            try:
                                # Get variable name (after "called")
                                called_index = var_parts.index("called")
                                if called_index + 1 < len(var_parts):
                                    var_name = var_text.split()[called_index + 1]
                                
                                # Get variable type (after "a" or "an")
                                if "integer" in var_parts:
                                    var_type = "integer"
                                elif "string" in var_parts:
                                    var_type = "string"
                                elif "boolean" in var_parts:
                                    var_type = "boolean"
                                elif "float" in var_parts:
                                    var_type = "float"
                            except (ValueError, IndexError):
                                pass
                            
                            # Advance past this token
                            self.advance()
                            
                        # Handle set clause if present
                        value = None
                        if (self.current_token.type == TokenType.IDENTIFIER and
                            "set" in self.current_token.lexeme.lower() and 
                            "to" in self.current_token.lexeme.lower()):
                            self.advance()
                            
                            # Parse the actual expression value
                            # Handle the expression until we hit a period or end marker
                            value = self.expression()
                            
                            # Skip period if present
                            if self.current_token.type == TokenType.DOT:
                                self.advance()                            # Create variable declaration
                            if var_name:
                                var_decl = VariableDeclaration(
                                    name=var_name,
                                    value=value,
                                    type_annotation=var_type,
                                    line_number=line_number
                                )
                                body_statements.append(var_decl)
                            continue
                        
                        # For other statements
                        try:
                            stmt = self.statement()
                            body_statements.append(stmt)
                        except Exception as e:
                            # Skip problematic tokens to avoid infinite loops
                            print(f"Error parsing statement: {e}")
                            self.advance()
                    
                    # Create a block for the body
                    body = Block(statements=body_statements, line_number=line_number)
                    
                    return TypeGuard(
                        condition=condition,
                        type_name=type_name,
                        body=body,
                        line_number=line_number
                    )
        
        # If we get here, something went wrong
        self.error("Expected a type guard statement")

    def error_recovery(self):
        """Attempt to recover from a syntax error by skipping tokens until a statement boundary is found."""
        # Skip tokens until we find a statement boundary
        while self.current_token and self.current_token.type != TokenType.EOF:
            # Check for potential statement boundaries
            if self.current_token.type in [
                TokenType.SET, TokenType.FUNCTION, TokenType.IF,
                TokenType.WHILE, TokenType.FOR, TokenType.TRY,
                TokenType.PRINT, TokenType.RETURNS, TokenType.CLASS,
                TokenType.INTERFACE, TokenType.TRAIT, TokenType.IMPORT,
                TokenType.ALLOCATE, TokenType.FREE, TokenType.DEFINE
            ]:
                return
                
            # Skip the current token
            self.advance()

    def parse_list_expression(self):
        """Parse a list expression or list comprehension."""
        # Syntax: [expr1, expr2, ...] or [expr for var in iterable if condition]
        line_number = self.current_token.line
        
        self.eat(TokenType.LEFT_BRACKET)
        
        # Skip any newlines and indentation after opening bracket
        self._skip_whitespace_tokens()
        
        # Empty list
        if self.current_token.type == TokenType.RIGHT_BRACKET:
            self.eat(TokenType.RIGHT_BRACKET)
            return ListExpression([], line_number)
        
        # Parse first expression
        first_expr = self.expression()
        
        # Skip whitespace after first expression
        self._skip_whitespace_tokens()
        
        # Check if it's a list comprehension (look for 'for' keyword)
        if self.current_token.type == TokenType.FOR:
            # It's a list comprehension: [expr for var in iterable if condition]
            self.eat(TokenType.FOR)
            
            # Target should be an identifier (or contextual keyword)
            if self.current_token.type == TokenType.IDENTIFIER or self._can_be_identifier(self.current_token):
                target = Identifier(self.current_token.lexeme, self.current_token.line)
                self.advance()
            else:
                self.error("Expected variable name after 'for' in list comprehension")
            
            self.eat(TokenType.IN)
            iterable = self.expression()
            
            condition = None
            if self.current_token.type == TokenType.IF:
                self.advance()
                condition = self.expression()
            
            # Skip whitespace before closing bracket
            self._skip_whitespace_tokens()
            self.eat(TokenType.RIGHT_BRACKET)
            return ListComprehension(first_expr, target, iterable, condition, line_number)
        else:
            # Regular list literal: [expr1, expr2, ...]
            elements = [first_expr]
            while self.current_token.type == TokenType.COMMA:
                self.advance()
                # Skip newlines and indentation after comma
                self._skip_whitespace_tokens()
                
                # Check for trailing comma before closing bracket
                if self.current_token.type == TokenType.RIGHT_BRACKET:
                    break
                    
                elements.append(self.expression())
                # Skip whitespace after element
                self._skip_whitespace_tokens()
            
            self.eat(TokenType.RIGHT_BRACKET)
            return ListExpression(elements, line_number)

    def parse_dict_expression(self):
        """Parse a dictionary expression or dict comprehension."""
        # Syntax: {key1: value1, key2: value2, ...}
        # or: {key: value for var in iterable if condition}
        line_number = self.current_token.line
        
        self.eat(TokenType.LEFT_BRACE)
        
        # Skip any newlines and indentation after opening brace
        self._skip_whitespace_tokens()
        
        # Check for empty dict
        if self.current_token.type == TokenType.RIGHT_BRACE:
            self.eat(TokenType.RIGHT_BRACE)
            return DictExpression([], line_number)
        
        # Parse first key
        key = self.expression()
        self._skip_whitespace_tokens()
        self.eat(TokenType.COLON)
        self._skip_whitespace_tokens()
        value = self.expression()
        self._skip_whitespace_tokens()
        
        # Check if this is a dict comprehension
        if self.current_token.type == TokenType.FOR:
            # It's a dict comprehension: {key: value for var in iterable}
            self.eat(TokenType.FOR)
            
            # Target should be an identifier (or contextual keyword)
            if self.current_token.type == TokenType.IDENTIFIER or self._can_be_identifier(self.current_token):
                target = Identifier(self.current_token.lexeme, self.current_token.line)
                self.advance()
            else:
                self.error("Expected variable name after 'for' in dict comprehension")
            
            self.eat(TokenType.IN)
            iterable = self.expression()
            
            condition = None
            if self.current_token.type == TokenType.IF:
                self.advance()
                condition = self.expression()
            
            # Skip whitespace before closing brace
            self._skip_whitespace_tokens()
            self.eat(TokenType.RIGHT_BRACE)
            return DictComprehension(key, value, target, iterable, condition, line_number)
        
        # Regular dict expression
        entries = [(key, value)]
        
        while self.current_token.type == TokenType.COMMA:
            self.advance()
            # Skip newlines and indentation after comma
            self._skip_whitespace_tokens()
            
            # Check for trailing comma before closing brace
            if self.current_token.type == TokenType.RIGHT_BRACE:
                break
                
            key = self.expression()
            self._skip_whitespace_tokens()
            self.eat(TokenType.COLON)
            self._skip_whitespace_tokens()
            value = self.expression()
            self._skip_whitespace_tokens()
            entries.append((key, value))
        
        self.eat(TokenType.RIGHT_BRACE)
        return DictExpression(entries, line_number)

    def parse_slice_expression(self):
        """Parse a slice expression."""
        # Syntax: expr[start:end:step]
        line_number = self.current_token.line
        
        expr = self.expression()
        self.eat(TokenType.LEFT_BRACKET)
        
        start = None
        if self.current_token.type != TokenType.COLON:
            start = self.expression()
        
        self.eat(TokenType.COLON)
        
        end = None
        if self.current_token.type != TokenType.COLON and self.current_token.type != TokenType.RIGHT_BRACKET:
            end = self.expression()
        
        step = None
        if self.current_token.type == TokenType.COLON:
            self.advance()
            if self.current_token.type != TokenType.RIGHT_BRACKET:
                step = self.expression()
        
        self.eat(TokenType.RIGHT_BRACKET)
        return SliceExpression(expr, start, end, step, line_number)

    def parse_comprehension(self):
        """Parse a list or dictionary comprehension."""
        # Syntax: [expr for var in iterable if condition]
        # or {key: value for var in iterable if condition}
        line_number = self.current_token.line
        
        is_dict = self.current_token.type == TokenType.LEFT_BRACE
        self.advance()  # Eat [ or {
        
        if is_dict:
            key = self.expression()
            self.eat(TokenType.COLON)
            value = self.expression()
        else:
            expr = self.expression()
        
        self.eat(TokenType.FOR)
        target = self.expression()
        self.eat(TokenType.IN)
        iterable = self.expression()
        
        condition = None
        if self.current_token.type == TokenType.IF:
            self.advance()
            condition = self.logical_or()  # Use logical_or() to get full condition but avoid assignment
        
        self.eat(TokenType.RIGHT_BRACKET if not is_dict else TokenType.RIGHT_BRACE)
        
        if is_dict:
            return DictComprehension(key, value, target, iterable, condition, line_number)
        else:
            return ListComprehension(expr, target, iterable, condition, line_number)

    def parse_ternary_expression(self):
        """Parse a ternary expression."""
        # Syntax: condition ? true_expr : false_expr
        line_number = self.current_token.line
        
        condition = self.expression()
        self.eat(TokenType.QUESTION)
        true_expr = self.expression()
        self.eat(TokenType.COLON)
        false_expr = self.expression()
        
        return TernaryExpression(condition, true_expr, false_expr, line_number)

    def parse_lambda_expression(self):
        """Parse a lambda expression.
        
        NLPL Syntax:
            lambda with a as Integer, b as Integer returns Integer
                return a plus b
            
            lambda with x as Integer returns Integer
                return x times 2
            
            lambda returns Integer
                return 42
        
        Also supports Python-like: lambda params: expr
        """
        line_number = self.current_token.line
        
        self.eat(TokenType.LAMBDA)
        
        # Check for NLPL style: "lambda with params returns type" or "lambda returns type"
        params = []
        return_type = None
        
        # Handle 'with' for parameters
        if self.current_token and self.current_token.type == TokenType.WITH:
            self.advance()  # Eat 'with'
            
            # Parse parameters (name as Type, separated by comma or 'and')
            while True:
                # Parse parameter name
                if self.current_token.type == TokenType.IDENTIFIER or self._can_be_identifier(self.current_token):
                    param_name = self.current_token.lexeme
                    self.advance()
                    
                    # Parse optional type annotation
                    param_type = None
                    if self.current_token and self.current_token.type == TokenType.AS:
                        self.advance()  # Eat 'as'
                        param_type = self.parse_type()
                    
                    params.append(Parameter(param_name, param_type))
                    
                    # Check for more parameters
                    if self.current_token and self.current_token.type == TokenType.COMMA:
                        self.advance()  # Eat ','
                        continue
                    elif self.current_token and self.current_token.type == TokenType.AND:
                        self.advance()  # Eat 'and'
                        continue
                    else:
                        break
                else:
                    break
        
        # Handle 'returns' for return type
        if self.current_token and self.current_token.type == TokenType.RETURNS:
            self.advance()  # Eat 'returns'
            return_type = self.parse_type()
        
        # Parse body - either indented block or single expression after colon
        body = None
        if self.current_token and self.current_token.type == TokenType.COLON:
            # Python-style: lambda x: expr
            self.advance()  # Eat ':'
            body = self.comparison()
        elif self.current_token and self.current_token.type == TokenType.NEWLINE:
            # NLPL-style: multi-line body with indentation (NEWLINE before INDENT)
            self.advance()  # Eat newline
            
            if self.current_token and self.current_token.type == TokenType.INDENT:
                self.advance()  # Eat indent
                
                # Parse statements until dedent
                body_statements = []
                while (self.current_token and 
                       self.current_token.type != TokenType.DEDENT and
                       self.current_token.type != TokenType.EOF):
                    stmt = self.statement()
                    if stmt:
                        body_statements.append(stmt)
                    # Skip newlines between statements
                    while self.current_token and self.current_token.type == TokenType.NEWLINE:
                        self.advance()
                
                # Consume dedent
                if self.current_token and self.current_token.type == TokenType.DEDENT:
                    self.advance()
                
                body = body_statements
            else:
                # Single statement on next line (no indent)
                body = self.statement()
        elif self.current_token and self.current_token.type == TokenType.INDENT:
            # NLPL-style: INDENT directly without NEWLINE (lexer optimization)
            self.advance()  # Eat indent
            
            # Parse statements until dedent
            body_statements = []
            while (self.current_token and 
                   self.current_token.type != TokenType.DEDENT and
                   self.current_token.type != TokenType.EOF):
                stmt = self.statement()
                if stmt:
                    body_statements.append(stmt)
                # Skip newlines between statements
                while self.current_token and self.current_token.type == TokenType.NEWLINE:
                    self.advance()
            
            # Consume dedent
            if self.current_token and self.current_token.type == TokenType.DEDENT:
                self.advance()
            
            body = body_statements
        else:
            # Inline expression
            body = self.comparison()
        
        return LambdaExpression(params, body, line_number, return_type)

    def parse_async_expression(self):
        """Parse an async expression."""
        # Syntax: async expr
        line_number = self.current_token.line
        
        self.eat(TokenType.ASYNC)
        expr = self.expression()
        
        return AsyncExpression(expr, line_number)

    def parse_await_expression(self):
        """Parse an await expression."""
        # Syntax: await expr
        line_number = self.current_token.line
        
        self.eat(TokenType.AWAIT)
        expr = self.expression()
        
        return AwaitExpression(expr, line_number)

    def parse_yield_expression(self):
        """Parse a yield expression."""
        # Syntax: yield [expr]
        line_number = self.current_token.line
        
        self.eat(TokenType.YIELD)
        value = None
        if self.current_token.type != TokenType.NEWLINE and self.current_token.type != TokenType.EOF:
            value = self.expression()
        
        return YieldExpression(value, line_number)

    def parse_generator_expression(self):
        """Parse a generator expression."""
        # Syntax: (expr for var in iterable if condition)
        line_number = self.current_token.line
        
        self.eat(TokenType.LEFT_PAREN)
        expr = self.expression()
        self.eat(TokenType.FOR)
        target = self.expression()
        self.eat(TokenType.IN)
        iterable = self.expression()
        
        condition = None
        if self.current_token.type == TokenType.IF:
            self.advance()
            condition = self.expression()
        
        self.eat(TokenType.RIGHT_PAREN)
        return GeneratorExpression(expr, target, iterable, condition, line_number)

    def extern_declaration(self):
        """Parse an external function, variable, or type declaration for FFI.
        
        Syntax:
            extern function <name> with <param> as <type> returns <type> from library "<lib>"
            extern function <name> with <param> as <type> with <param2> as <type2> returns <type> from library "<lib>"
            foreign function <name> ...
            extern variable <name> as <type> from library "<lib>"
            extern type <name> as <base_type>
            extern type <name> as opaque pointer
            extern type <name> as function with <params> returns <type>
        """
        from ..parser.ast import ExternFunctionDeclaration, ExternVariableDeclaration, ExternTypeDeclaration, Parameter
        
        line_number = self.current_token.line
        
        # Consume 'extern' or 'foreign'
        self.advance()
        
        # Check if it's a function, variable, or type
        if self.current_token.type == TokenType.TYPE:
            # extern type declaration
            self.advance()  # consume 'type'
            
            # Get type name - allow keywords as type names for FFI
            if self.current_token.type == TokenType.IDENTIFIER or self.current_token.lexeme in ['FILE', 'DIR', 'file', 'dir']:
                type_name = self.current_token.lexeme
                self.advance()
            else:
                self.error("Expected type name after 'extern type'")
            
            # Expect 'as'
            if self.current_token.type != TokenType.AS:
                self.error("Expected 'as' after type name in extern type declaration")
            self.advance()
            
            # Check for opaque qualifier
            is_opaque = False
            if self.current_token.type == TokenType.OPAQUE:
                is_opaque = True
                self.advance()
            
            # Check if it's a function pointer type
            if self.current_token.type == TokenType.FUNCTION:
                self.advance()  # consume 'function'
                
                # Parse function signature
                param_types = []
                if self.current_token.type == TokenType.WITH:
                    self.advance()
                    
                    # Parse parameter types
                    while True:
                        param_type = self.parse_type()
                        param_types.append(param_type)
                        
                        if self.current_token.type == TokenType.COMMA:
                            self.advance()
                            continue
                        else:
                            break
                
                # Parse return type
                return_type = "Void"
                if self.current_token.type == TokenType.RETURNS:
                    self.advance()
                    return_type = self.parse_type()
                
                function_signature = (param_types, return_type)
                return ExternTypeDeclaration(
                    name=type_name,
                    base_type="function",
                    is_opaque=False,
                    is_function_pointer=True,
                    function_signature=function_signature,
                    line_number=line_number
                )
            else:
                # Parse base type (pointer, struct, etc.)
                base_type = self.parse_type()
                
                return ExternTypeDeclaration(
                    name=type_name,
                    base_type=base_type,
                    is_opaque=is_opaque,
                    is_function_pointer=False,
                    function_signature=None,
                    line_number=line_number
                )
        
        elif self.current_token.type == TokenType.FUNCTION:
            self.advance()  # consume 'function'
            
            # Get function name - allow keywords as function names for FFI
            if self.current_token.type == TokenType.IDENTIFIER or self.current_token.lexeme in ['free', 'malloc', 'printf', 'sin', 'cos', 'pow', 'sqrt']:
                func_name = self.current_token.lexeme
                self.advance()
            else:
                self.error("Expected function name after 'extern function'")
            
            # Parse parameters (with <param> as <type>, <param2> as <type2> pattern)
            parameters = []
            variadic = False
            if self.current_token and self.current_token.type == TokenType.WITH:
                self.advance()  # consume 'with'
                
                # Parse parameter list (comma-separated)
                while True:
                    # Check for ellipsis (variadic)
                    if self.current_token.type == TokenType.ELLIPSIS:
                        variadic = True
                        self.advance()
                        break
                    
                    # Get parameter name
                    # Get parameter name
                    if self.current_token.type != TokenType.IDENTIFIER and not self._can_be_identifier(self.current_token):
                        self.error("Expected parameter name after 'with'")
                    param_name = self.current_token.lexeme
                    self.advance()
                    
                    # Expect 'as'
                    if self.current_token.type != TokenType.AS:
                        self.error(f"Expected 'as' after parameter name '{param_name}'")
                    self.advance()
                    
                    # Get parameter type
                    param_type = self.parse_type()
                    
                    parameters.append(Parameter(param_name, param_type, line_number))
                    
                    # Check for comma (more parameters)
                    if self.current_token and self.current_token.type == TokenType.COMMA:
                        self.advance()  # consume comma and continue
                    else:
                        break  # No more parameters
            
            # Parse return type
            return_type = "Void"
            if self.current_token and self.current_token.type == TokenType.RETURNS:
                self.advance()  # consume 'returns'
                return_type = self.parse_type()
            
            # Parse library specification
            library = None
            calling_convention = "cdecl"
            
            if self.current_token and self.current_token.type == TokenType.FROM:
                self.advance()  # consume 'from'
                
                # Expect 'library'
                if self.current_token.type == TokenType.LIBRARY:
                    self.advance()
                    
                    # Get library name (string literal)
                    if self.current_token.type == TokenType.STRING_LITERAL:
                        library = self.current_token.literal
                        self.advance()
                    else:
                        self.error("Expected library name as string literal")
                
                # Optional: calling convention
                if self.current_token and self.current_token.lexeme.lower() == "calling":
                    self.advance()  # consume 'calling'
                    
                    if self.current_token.lexeme.lower() == "convention":
                        self.advance()  # consume 'convention'
                        
                        if self.current_token.type in [TokenType.CDECL, TokenType.STDCALL]:
                            calling_convention = self.current_token.lexeme.lower()
                            self.advance()
                        elif self.current_token.type == TokenType.IDENTIFIER:
                            calling_convention = self.current_token.lexeme.lower()
                            self.advance()
            
            return ExternFunctionDeclaration(
                func_name,
                parameters,
                return_type,
                library,
                calling_convention,
                variadic,
                line_number
            )
        
        elif self.current_token.lexeme.lower() == "variable":
            self.advance()  # consume 'variable'
            
            # Get variable name
            if self.current_token.type != TokenType.IDENTIFIER:
                self.error("Expected variable name after 'extern variable'")
            var_name = self.current_token.lexeme
            self.advance()
            
            # Expect 'as'
            if self.current_token.type != TokenType.AS:
                self.error(f"Expected 'as' after variable name '{var_name}'")
            self.advance()
            
            # Get variable type
            var_type_token = self.current_token
            if var_type_token.type in [TokenType.IDENTIFIER, TokenType.INTEGER, TokenType.FLOAT,
                                       TokenType.STRING, TokenType.BOOLEAN, TokenType.POINTER]:
                var_type = var_type_token.lexeme
                self.advance()
            else:
                self.error(f"Expected type for variable '{var_name}'")
            
            # Parse library specification
            library = None
            if self.current_token and self.current_token.type == TokenType.FROM:
                self.advance()  # consume 'from'
                
                # Expect 'library'
                if self.current_token.type == TokenType.LIBRARY:
                    self.advance()
                    
                    # Get library name (string literal)
                    if self.current_token.type == TokenType.STRING_LITERAL:
                        library = self.current_token.literal
                        self.advance()
                    else:
                        self.error("Expected library name as string literal")
            
            return ExternVariableDeclaration(var_name, var_type, library, line_number)
        
        else:
            self.error("Expected 'function' or 'variable' after 'extern'/'foreign'")

    def parse_unsafe_block(self):
        """Parse an unsafe FFI block.

        Syntax:
            unsafe do
                <statements>
            end

        Inside an unsafe block, null-pointer guards, bounds checks, and
        ownership enforcement are suppressed so that raw FFI operations can
        be performed without runtime overhead.
        """
        from ..parser.ast import UnsafeBlock

        line_number = self.current_token.line
        self.advance()  # consume 'unsafe'

        # Optional 'do' keyword
        if self.current_token and self.current_token.type == TokenType.DO:
            self.advance()

        body = []
        while (self.current_token and
               self.current_token.type not in (TokenType.END, TokenType.EOF)):
            stmt = self.statement()
            if stmt is not None:
                body.append(stmt)

        if self.current_token and self.current_token.type == TokenType.END:
            self.advance()  # consume 'end'
        else:
            self.error("Expected 'end' to close 'unsafe' block")

        return UnsafeBlock(body=body, line_number=line_number)

    def parse_decorator(self):
        """Parse a decorator: @name, @name(arg1, arg2), or @name with arg1 value1"""
        self.eat(TokenType.AT)
        
        # Get decorator name
        if self.current_token.type != TokenType.IDENTIFIER:
            self.error("Expected decorator name after '@'")
        
        decorator_name = self.current_token.lexeme
        line_number = self.current_token.line
        self.advance()
        
        # Check for decorator arguments
        arguments = {}
        if self.current_token and self.current_token.type == TokenType.LEFT_PAREN:
            # Parenthesis-style args: @name(Arg1, Arg2, ...)
            self.advance()  # consume '('
            args_list = []
            while self.current_token and self.current_token.type not in (TokenType.RIGHT_PAREN, TokenType.EOF, TokenType.NEWLINE):
                if self.current_token.type == TokenType.IDENTIFIER or self._can_be_identifier(self.current_token):
                    args_list.append(self.current_token.lexeme)
                    self.advance()
                elif self.current_token.type == TokenType.COMMA:
                    self.advance()
                else:
                    break
            if self.current_token and self.current_token.type == TokenType.RIGHT_PAREN:
                self.advance()  # consume ')'
            arguments["_args"] = args_list
        elif self.current_token and self.current_token.type == TokenType.WITH:
            self.advance()  # consume 'with'
            
            # Parse arguments: arg1 value1, arg2 value2, ...
            while True:
                # Get argument name
                if self.current_token.type != TokenType.IDENTIFIER and not self._can_be_identifier(self.current_token):
                    break
                
                arg_name = self.current_token.lexeme
                self.advance()
                
                # Get argument value (expression)
                arg_value = self.expression()
                arguments[arg_name] = arg_value
                
                # Check for comma (more arguments)
                if self.current_token and self.current_token.type == TokenType.COMMA:
                    self.advance()
                else:
                    break
        
        return Decorator(decorator_name, arguments, line_number)
    
    def macro_definition(self):
        """Parse a macro definition: macro NAME [with params] ... end"""
        line_number = self.current_token.line
        self.eat(TokenType.MACRO)
        
        # Get macro name
        if self.current_token.type != TokenType.IDENTIFIER:
            self.error("Expected macro name after 'macro'")
        
        macro_name = self.current_token.lexeme
        self.advance()
        
        # Parse optional parameters
        parameters = []
        if self.current_token and self.current_token.type == TokenType.WITH:
            self.advance()  # consume 'with'
            
            # Parse parameter list: param1, param2, ...
            while True:
                if self.current_token.type == TokenType.IDENTIFIER or self._can_be_identifier(self.current_token):
                    parameters.append(self.current_token.lexeme)
                    self.advance()
                    
                    if self.current_token and self.current_token.type == TokenType.COMMA:
                        self.advance()
                    else:
                        break
                else:
                    break
        
        # Parse macro body (statements until 'end')
        body = []
        while self.current_token and self.current_token.type != TokenType.END:
            stmt = self.statement()
            if stmt:
                body.append(stmt)
        
        self.eat(TokenType.END)
        
        return MacroDefinition(macro_name, parameters, body, line_number)
    
    def macro_expansion(self):
        """Parse a macro expansion: expand NAME [with arg1 value1, arg2 value2]"""
        line_number = self.current_token.line
        self.eat(TokenType.EXPAND)
        
        # Get macro name
        if self.current_token.type != TokenType.IDENTIFIER:
            self.error("Expected macro name after 'expand'")
        
        macro_name = self.current_token.lexeme
        self.advance()
        
        # Parse optional arguments
        arguments = {}
        if self.current_token and self.current_token.type == TokenType.WITH:
            self.advance()  # consume 'with'
            
            # Parse arguments: arg1 value1, arg2 value2, ...
            while True:
                # Get argument name
                if self.current_token.type != TokenType.IDENTIFIER and not self._can_be_identifier(self.current_token):
                    break
                
                arg_name = self.current_token.lexeme
                self.advance()
                
                # Get argument value (expression)
                arg_value = self.expression()
                arguments[arg_name] = arg_value
                
                # Check for comma (more arguments)
                if self.current_token and self.current_token.type == TokenType.COMMA:
                    self.advance()
                else:
                    break
        
        return MacroExpansion(macro_name, arguments, line_number)

    def comptime_statement(self):
        """Parse a comptime statement.

        Supported forms:
            comptime eval EXPR            -- evaluate expression at load time
            comptime const NAME is EXPR   -- define immutable compile-time constant
            comptime assert COND          -- check condition at load time
            comptime assert COND message MSG
        """
        line_number = self.current_token.line
        self.eat(TokenType.COMPTIME)

        tok = self.current_token
        # Determine sub-form by inspecting the next identifier keyword
        sub = tok.lexeme if tok and tok.type == TokenType.IDENTIFIER else None

        if sub == "eval":
            self.advance()  # consume 'eval'
            expr = self.expression()
            return ComptimeExpression(expr, line_number)

        elif sub == "const":
            self.advance()  # consume 'const'
            # Expect: NAME is EXPR  (or NAME to EXPR)
            if not (self.current_token and (
                    self.current_token.type == TokenType.IDENTIFIER
                    or self._can_be_identifier(self.current_token))):
                self.error("Expected constant name after 'comptime const'")
            const_name = self.current_token.lexeme
            self.advance()
            # Consume 'is' or 'to'
            if self.current_token and self.current_token.type in (TokenType.IS, TokenType.TO):
                self.advance()
            elif self.current_token and self.current_token.type == TokenType.IDENTIFIER \
                    and self.current_token.lexeme in ("is", "to", "equals"):
                self.advance()
            expr = self.expression()
            return ComptimeConst(const_name, expr, line_number)

        elif sub == "assert":
            self.advance()  # consume 'assert'
            condition = self.expression()
            message_expr = None
            # Optional:  message EXPR  or  with message EXPR
            if self.current_token and self.current_token.type == TokenType.MESSAGE:
                self.advance()
                message_expr = self.expression()
            elif self.current_token and self.current_token.type == TokenType.WITH:
                self.advance()
                if self.current_token and self.current_token.type == TokenType.MESSAGE:
                    self.advance()
                    message_expr = self.expression()
                elif self.current_token and self.current_token.type == TokenType.IDENTIFIER \
                        and self.current_token.lexeme == "message":
                    self.advance()
                    message_expr = self.expression()
            return ComptimeAssert(condition, message_expr, line_number)

        else:
            # Default: treat bare expression as 'comptime eval EXPR'
            expr = self.expression()
            return ComptimeExpression(expr, line_number)

    def attribute_declaration(self):
        """Parse: attribute Name [with prop1 as Type1, prop2 as Type2, ...]

        Syntax::

            attribute Serializable
            attribute JsonProperty with key as String
            attribute Range with min as Integer, max as Integer
        """
        line_number = self.current_token.line
        self.eat(TokenType.ATTRIBUTE)

        # Structural tokens that can never be a name/type token in this context
        _non_name = {
            TokenType.EOF, TokenType.NEWLINE, TokenType.END,
            TokenType.COMMA, TokenType.DOT, TokenType.SEMICOLON,
            TokenType.WITH, TokenType.AS, TokenType.AND,
        }

        def _is_name_tok(tok):
            return tok is not None and tok.type not in _non_name and tok.lexeme

        # Get attribute name — accept any non-structural token (keywords included)
        if not _is_name_tok(self.current_token):
            self.error("Expected attribute name after 'attribute'")
        attr_name = self.current_token.lexeme
        self.advance()

        # Optional: with prop1 as Type1, prop2 as Type2
        properties = []
        if self.current_token and self.current_token.type == TokenType.WITH:
            self.advance()
            while _is_name_tok(self.current_token):
                prop_name = self.current_token.lexeme
                self.advance()
                prop_type = "Any"
                if self.current_token and self.current_token.type == TokenType.AS:
                    self.advance()
                    if _is_name_tok(self.current_token):
                        prop_type = self.current_token.lexeme
                        self.advance()
                properties.append((prop_name, prop_type))
                # Allow comma OR 'and' as property separators
                if self.current_token and self.current_token.type == TokenType.COMMA:
                    self.advance()
                elif self.current_token and self.current_token.type == TokenType.AND:
                    self.advance()
                else:
                    break

        return AttributeDeclaration(attr_name, properties, line_number)

    # ---------------------------------------------------------------------------
    # Native test framework parsing
    # ---------------------------------------------------------------------------

    def _parse_block_body(self, stop_types=None):
        """Parse a list of statements until END or EOF.

        Parameters
        ----------
        stop_types : collection of TokenType, optional
            Additional token types (besides END and EOF) that terminate the
            block.  Defaults to just (END, EOF).

        Returns
        -------
        list
            The collected statement nodes.
        """
        terminators = {TokenType.END, TokenType.EOF}
        if stop_types:
            terminators.update(stop_types)

        body = []
        while self.current_token and self.current_token.type not in terminators:
            stmt = self.statement()
            if stmt is not None:
                body.append(stmt)
        return body

    def parse_test_block(self):
        """Parse a test block.

        Syntax:
            test "name" do
                <statements>
            end

        Parameterized variant:
            test "name" with cases
                case (arg1, arg2, ...)
                case (arg1, arg2, ...)
            do
                <statements>
            end
        """
        line_number = self.current_token.line
        self.advance()  # consume 'test'

        # Test name - must be a string literal
        if not (self.current_token and
                self.current_token.type == TokenType.STRING_LITERAL):
            self.error("Expected a string literal test name after 'test'")

        name = self.current_token.literal
        self.advance()

        # Check for "with cases" (parameterized test)
        if (self.current_token and
                self.current_token.type == TokenType.WITH):
            peek = self.peek(1)
            if peek and peek.lexeme.lower() == "cases":
                return self._parse_parameterized_test(name, line_number)

        # Plain test block
        if self.current_token and self.current_token.type == TokenType.DO:
            self.advance()  # consume 'do'

        body = self._parse_block_body()

        if self.current_token and self.current_token.type == TokenType.END:
            self.advance()
        else:
            self.error("Expected 'end' to close 'test' block")

        return TestBlock(name=name, body=body, line_number=line_number)

    def _parse_parameterized_test(self, name, line_number):
        """Continue parsing a parameterized test after the name has been consumed.

        Syntax (resumed after name):
            with cases
                case (<params>) using (<param_names>)
                case (<args>)
                ...
            do
                <body>
            end
        """
        self.advance()  # consume 'with'
        # consume 'cases' identifier
        if (self.current_token and
                self.current_token.lexeme.lower() == "cases"):
            self.advance()
        else:
            self.error("Expected 'cases' after 'with' in parameterized test")

        # Optional parameter name declaration
        # "using (param1, param2, ...)" or just positional names in the body
        param_names = []
        if (self.current_token and
                self.current_token.type == TokenType.IDENTIFIER and
                self.current_token.lexeme.lower() == "using"):
            self.advance()  # consume 'using'
            if (self.current_token and
                    self.current_token.type == TokenType.LPAREN):
                self.advance()  # consume '('
                while (self.current_token and
                       self.current_token.type != TokenType.RPAREN and
                       self.current_token.type != TokenType.EOF):
                    if self.current_token.type == TokenType.IDENTIFIER:
                        param_names.append(self.current_token.lexeme)
                        self.advance()
                    if (self.current_token and
                            self.current_token.type == TokenType.COMMA):
                        self.advance()
                if self.current_token and self.current_token.type == TokenType.RPAREN:
                    self.advance()

        # Parse case rows
        cases = []
        while (self.current_token and
               self.current_token.type not in (TokenType.DO, TokenType.END,
                                               TokenType.EOF)):
            if (self.current_token.type == TokenType.IDENTIFIER and
                    self.current_token.lexeme.lower() == "case"):
                self.advance()  # consume 'case'
                # Parse a tuple / parenthesised list of arguments
                args = []
                if (self.current_token and
                        self.current_token.type == TokenType.LPAREN):
                    self.advance()  # consume '('
                    while (self.current_token and
                           self.current_token.type not in (TokenType.RPAREN,
                                                           TokenType.EOF)):
                        arg = self.expression()
                        if arg is not None:
                            args.append(arg)
                        if (self.current_token and
                                self.current_token.type == TokenType.COMMA):
                            self.advance()
                    if (self.current_token and
                            self.current_token.type == TokenType.RPAREN):
                        self.advance()
                else:
                    # Single bare expression as the case argument
                    arg = self.expression()
                    if arg is not None:
                        args.append(arg)
                cases.append(args)
            else:
                self.advance()  # skip unexpected tokens inside cases section

        if self.current_token and self.current_token.type == TokenType.DO:
            self.advance()

        body = self._parse_block_body()

        if self.current_token and self.current_token.type == TokenType.END:
            self.advance()
        else:
            self.error("Expected 'end' to close parameterized 'test' block")

        return ParameterizedTestBlock(
            name=name,
            params=param_names,
            cases=cases,
            body=body,
            line_number=line_number,
        )

    def parse_describe_block(self):
        """Parse a describe (test suite) block.

        Syntax:
            describe "SuiteName" do
                before each do ... end
                after each do ... end
                it "should ..." do ... end
                test "..." do ... end
            end
        """
        line_number = self.current_token.line
        self.advance()  # consume 'describe'

        if not (self.current_token and
                self.current_token.type == TokenType.STRING_LITERAL):
            self.error("Expected a string literal suite name after 'describe'")

        name = self.current_token.literal
        self.advance()

        if self.current_token and self.current_token.type == TokenType.DO:
            self.advance()

        body = self._parse_block_body()

        if self.current_token and self.current_token.type == TokenType.END:
            self.advance()
        else:
            self.error("Expected 'end' to close 'describe' block")

        return DescribeBlock(name=name, body=body, line_number=line_number)

    def parse_it_block(self):
        """Parse an 'it' specification block (BDD style).

        Syntax:
            it "should do something" do
                <statements>
            end
        """
        line_number = self.current_token.line
        self.advance()  # consume 'it'

        if not (self.current_token and
                self.current_token.type == TokenType.STRING_LITERAL):
            self.error("Expected a string literal spec name after 'it'")

        name = self.current_token.literal
        self.advance()

        if self.current_token and self.current_token.type == TokenType.DO:
            self.advance()

        body = self._parse_block_body()

        if self.current_token and self.current_token.type == TokenType.END:
            self.advance()
        else:
            self.error("Expected 'end' to close 'it' block")

        return ItBlock(name=name, body=body, line_number=line_number)

    def parse_before_each_block(self):
        """Parse a 'before each' setup block inside a describe suite.

        Syntax:
            before each do
                <statements>
            end
        """
        line_number = self.current_token.line
        self.advance()  # consume 'before each' (single token BEFORE_EACH)

        if self.current_token and self.current_token.type == TokenType.DO:
            self.advance()

        body = self._parse_block_body()

        if self.current_token and self.current_token.type == TokenType.END:
            self.advance()
        else:
            self.error("Expected 'end' to close 'before each' block")

        return BeforeEachBlock(body=body, line_number=line_number)

    def parse_after_each_block(self):
        """Parse an 'after each' teardown block inside a describe suite.

        Syntax:
            after each do
                <statements>
            end
        """
        line_number = self.current_token.line
        self.advance()  # consume 'after each' (single token AFTER_EACH)

        if self.current_token and self.current_token.type == TokenType.DO:
            self.advance()

        body = self._parse_block_body()

        if self.current_token and self.current_token.type == TokenType.END:
            self.advance()
        else:
            self.error("Expected 'end' to close 'after each' block")

        return AfterEachBlock(body=body, line_number=line_number)

    # ------------------------------------------------------------------
    # Assertion library
    # ------------------------------------------------------------------

    def parse_expect_statement(self):
        """Parse an expect assertion statement.

        Syntax (all forms):
            expect <actual> to equal <expected>
            expect <actual> to not equal <expected>
            expect <actual> to be greater than <expected>
            expect <actual> to be less than <expected>
            expect <actual> to be greater than or equal to <expected>
            expect <actual> to be less than or equal to <expected>
            expect <actual> to contain <expected>
            expect <actual> to be true
            expect <actual> to be false
            expect <actual> to be null
            expect <actual> to not be null
            expect <actual> to be approximately equal to <expected> within <tol>
            expect <actual> to be empty
            expect <actual> to have length <n>
            expect <actual> to have size <n>
            expect <actual> to start with <expected>
            expect <actual> to end with <expected>
            expect <actual> to be of type <typename>
            expect <actual> to be a <typename>
            expect <actual> to raise error
            expect <actual> to not raise error
        """
        line_number = self.current_token.line
        self.advance()  # consume EXPECT

        # Parse the actual expression (stops naturally at TO keyword)
        actual_expr = self.expression()

        # Consume TO
        if self.current_token and self.current_token.type == TokenType.TO:
            self.advance()
        else:
            self.error("Expected 'to' after expect expression")

        negated = False
        matcher = None
        expected_expr = None
        tolerance_expr = None

        # Check for optional NOT
        if self.current_token and self.current_token.type == TokenType.NOT:
            negated = True
            self.advance()

        # Determine the matcher
        tok = self.current_token
        if tok is None:
            self.error("Expected matcher after 'expect ... to'")

        # EQUAL_TO token ("equals" / "equal to")
        if tok.type == TokenType.EQUAL_TO:
            matcher = "equal"
            self.advance()
            expected_expr = self.expression()

        # IDENTIFIER "equal" (bare word)
        elif tok.type == TokenType.IDENTIFIER and tok.value in ("equal", "equals"):
            matcher = "equal"
            self.advance()
            expected_expr = self.expression()

        # CONTAINS token ("contains")
        elif tok.type == TokenType.CONTAINS:
            matcher = "contain"
            self.advance()
            expected_expr = self.expression()

        # IDENTIFIER "contain" / "contains"
        elif tok.type == TokenType.IDENTIFIER and tok.value in ("contain", "contains"):
            matcher = "contain"
            self.advance()
            expected_expr = self.expression()

        # IDENTIFIER "be" — disambiguate by the next token
        elif tok.type == TokenType.IDENTIFIER and tok.value == "be":
            self.advance()  # consume "be"
            tok2 = self.current_token

            if tok2 is None:
                self.error("Incomplete expect matcher after 'be'")

            if tok2.type == TokenType.GREATER_THAN:
                matcher = "greater_than"
                self.advance()
                expected_expr = self.expression()

            elif tok2.type == TokenType.LESS_THAN:
                matcher = "less_than"
                self.advance()
                expected_expr = self.expression()

            elif tok2.type == TokenType.GREATER_THAN_OR_EQUAL_TO:
                matcher = "greater_than_or_equal_to"
                self.advance()
                expected_expr = self.expression()

            elif tok2.type == TokenType.LESS_THAN_OR_EQUAL_TO:
                matcher = "less_than_or_equal_to"
                self.advance()
                expected_expr = self.expression()

            elif tok2.type == TokenType.TRUE:
                matcher = "be_true"
                self.advance()

            elif tok2.type == TokenType.FALSE:
                matcher = "be_false"
                self.advance()

            elif tok2.type == TokenType.NULL:
                matcher = "be_null"
                self.advance()

            # "approximately" equal to <expr> within <tol>
            elif tok2.type == TokenType.IDENTIFIER and tok2.value == "approximately":
                self.advance()  # consume "approximately"
                # expect EQUAL_TO next ("equal to")
                if self.current_token and self.current_token.type == TokenType.EQUAL_TO:
                    self.advance()
                matcher = "approximately_equal"
                expected_expr = self.expression()
                # Optional "within <tolerance>"
                if (self.current_token and self.current_token.type == TokenType.IDENTIFIER
                        and self.current_token.value == "within"):
                    self.advance()
                    tolerance_expr = self.expression()

            # "empty" — expect x to be empty
            elif tok2.type == TokenType.EMPTY:
                matcher = "be_empty"
                self.advance()

            # "of type <typename>" — expect x to be of type Integer
            elif tok2.type == TokenType.OF:
                self.advance()  # consume "of"
                # consume optional "type" keyword
                if self.current_token and self.current_token.type == TokenType.TYPE:
                    self.advance()
                matcher = "be_of_type"
                expected_expr = self.expression()

            # "a <typename>" — expect x to be a Integer
            elif tok2.type == TokenType.A:
                self.advance()  # consume "a"
                matcher = "be_of_type"
                expected_expr = self.expression()

            else:
                self.error(f"Unknown matcher after 'be': {tok2.value!r}")

        # "have length <n>" / "have size <n>"
        elif tok.type == TokenType.IDENTIFIER and tok.value == "have":
            self.advance()  # consume "have"
            # consume optional "length" (TokenType.LENGTH) / "size" / "count"
            if self.current_token and self.current_token.type == TokenType.LENGTH:
                self.advance()
            elif (self.current_token and self.current_token.type == TokenType.IDENTIFIER
                    and self.current_token.value in ("size", "count")):
                self.advance()
            matcher = "have_length"
            expected_expr = self.expression()

        # "start with <expected>" — string / collection starts-with assertion
        elif tok.type == TokenType.IDENTIFIER and tok.value == "start":
            self.advance()  # consume "start"
            if self.current_token and self.current_token.type == TokenType.WITH:
                self.advance()
            elif (self.current_token and self.current_token.type == TokenType.IDENTIFIER
                    and self.current_token.value == "with"):
                self.advance()
            matcher = "start_with"
            expected_expr = self.expression()

        # "end with <expected>" — "end" is TokenType.END in NLPL
        elif tok.type == TokenType.END:
            self.advance()  # consume "end"
            if self.current_token and self.current_token.type == TokenType.WITH:
                self.advance()
            elif (self.current_token and self.current_token.type == TokenType.IDENTIFIER
                    and self.current_token.value == "with"):
                self.advance()
            matcher = "end_with"
            expected_expr = self.expression()

        # "raise error" / "raise" / "raise an error" — exception assertion
        elif tok.type == TokenType.RAISE:
            self.advance()  # consume "raise"
            # consume optional "error" (TokenType.ERROR) or "an" + "error"
            if self.current_token and self.current_token.type == TokenType.ERROR:
                self.advance()  # consume "error"
            elif (self.current_token and self.current_token.type == TokenType.IDENTIFIER
                    and self.current_token.value == "an"):
                self.advance()  # consume "an"
                if self.current_token and self.current_token.type == TokenType.ERROR:
                    self.advance()  # consume "error"
            matcher = "raise_error"

        else:
            self.error(f"Unknown expect matcher: {tok.value!r}")

        return ExpectStatement(
            actual_expr=actual_expr,
            matcher=matcher,
            expected_expr=expected_expr,
            negated=negated,
            tolerance_expr=tolerance_expr,
            line_number=line_number,
        )

    # ------------------------------------------------------------------
    # Contract programming
    # ------------------------------------------------------------------

    def _parse_contract_body(self, keyword: str):
        """Parse condition and optional 'message <expr>' for contract stmts."""
        condition = self.expression()
        message_expr = None
        # 'message' may be tokenized as TokenType.MESSAGE or as an IDENTIFIER
        # depending on lexer version; handle both.
        tok = self.current_token
        is_message_token = tok is not None and (
            tok.type == TokenType.MESSAGE
            or (tok.type == TokenType.IDENTIFIER and tok.value == "message")
        )
        if is_message_token:
            self.advance()  # consume "message"
            message_expr = self.expression()
        return condition, message_expr

    def parse_require_statement(self):
        """Parse a 'require <condition>' contract precondition.

        Syntax:
            require <condition>
            require <condition> message "explanation"
        """
        line_number = self.current_token.line
        self.advance()  # consume REQUIRE
        condition, message_expr = self._parse_contract_body("require")
        return RequireStatement(condition=condition, message_expr=message_expr,
                                line_number=line_number)

    def parse_ensure_statement(self):
        """Parse an 'ensure <condition>' contract postcondition.

        Syntax:
            ensure <condition>
            ensure <condition> message "explanation"
        """
        line_number = self.current_token.line
        self.advance()  # consume ENSURE
        condition, message_expr = self._parse_contract_body("ensure")
        return EnsureStatement(condition=condition, message_expr=message_expr,
                               line_number=line_number)

    def parse_guarantee_statement(self):
        """Parse a 'guarantee <condition>' invariant assertion.

        Syntax:
            guarantee <condition>
            guarantee <condition> message "explanation"
        """
        line_number = self.current_token.line
        self.advance()  # consume GUARANTEE
        condition, message_expr = self._parse_contract_body("guarantee")
        return GuaranteeStatement(condition=condition, message_expr=message_expr,
                                  line_number=line_number)

    def parse_invariant_statement(self):
        """Parse an 'invariant <condition>' class/scope invariant.

        Syntax:
            invariant <condition>
            invariant <condition> message "explanation"

        Inside a class body the invariant is collected and checked after
        every method call.  In any other scope it fires immediately like
        ``guarantee``.
        """
        line_number = self.current_token.line
        self.advance()  # consume INVARIANT
        condition, message_expr = self._parse_contract_body("invariant")
        return InvariantStatement(condition=condition, message_expr=message_expr,
                                  line_number=line_number)

    def parse_spec_block(self):
        """Parse a formal ``spec`` block containing spec annotations.

        Syntax:
            spec
                requires  <cond>
                ensures   <cond>
                invariant <cond>
                decreases <expr>
            end spec

        Or with an optional name label::

            spec "label"
                requires  <cond>
            end spec

        Spec blocks are no-ops at runtime; they are consumed by the
        ``nlpl-verify`` static verification tool.
        """
        line_number = self.current_token.line
        self.advance()  # consume SPEC

        # Optional string label
        name = None
        if (self.current_token
                and self.current_token.type == TokenType.STRING_LITERAL):
            name = self.current_token.value
            self.advance()

        annotations = []

        # Skip trailing newline before INDENT
        while self.current_token and self.current_token.type == TokenType.NEWLINE:
            self.advance()

        if self.current_token and self.current_token.type == TokenType.INDENT:
            self.advance()  # consume INDENT

            while (self.current_token
                   and self.current_token.type not in (TokenType.DEDENT, TokenType.EOF)):

                tok = self.current_token

                if tok.type in (TokenType.NEWLINE,):
                    self.advance()
                    continue

                # "requires <cond>", "ensures <cond>", "invariant <cond>"
                # Accept both keyword tokens (require/ensure) and identifier
                # variants (requires/ensures) commonly used in spec blocks.
                _tok_val = getattr(tok, "value", "") or getattr(tok, "lexeme", "")
                if (tok.type == TokenType.REQUIRE
                        or (tok.type == TokenType.IDENTIFIER
                            and _tok_val.lower() in ("requires", "require"))):
                    ann_line = tok.line
                    self.advance()
                    cond, _ = self._parse_contract_body("requires")
                    annotations.append(SpecAnnotation("requires", cond, line_number=ann_line))
                elif (tok.type == TokenType.ENSURE
                        or (tok.type == TokenType.IDENTIFIER
                            and _tok_val.lower() in ("ensures", "ensure"))):
                    ann_line = tok.line
                    self.advance()
                    cond, _ = self._parse_contract_body("ensures")
                    annotations.append(SpecAnnotation("ensures", cond, line_number=ann_line))
                elif tok.type == TokenType.INVARIANT:
                    ann_line = tok.line
                    self.advance()
                    cond, _ = self._parse_contract_body("invariant")
                    annotations.append(SpecAnnotation("invariant", cond, line_number=ann_line))
                elif (tok.type == TokenType.IDENTIFIER
                      and tok.lexeme.lower() == "decreases"):
                    ann_line = tok.line
                    self.advance()
                    expr = self.expression()
                    annotations.append(SpecAnnotation("decreases", expr, line_number=ann_line))
                else:
                    # Skip unrecognised tokens gracefully
                    self.advance()

            if self.current_token and self.current_token.type == TokenType.DEDENT:
                self.advance()  # consume DEDENT

        # Consume optional "end spec" / "end"
        if self.current_token and self.current_token.type == TokenType.END:
            self.advance()  # consume END
            if (self.current_token and self.current_token.type == TokenType.SPEC):
                self.advance()  # consume SPEC (part of "end spec")

        return SpecBlock(name=name, annotations=annotations, line_number=line_number)
