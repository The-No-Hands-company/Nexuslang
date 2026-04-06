"""
Compiler round-trip integration tests: NexusLang source -> LLVM IR -> native binary -> execute.

Each test compiles a small NexusLang program all the way to a native executable (via the
LLVMIRGenerator + LLVM/clang tool chain), runs it, and checks stdout against the
expected output.

Requirements
------------
- LLVM tools (llc, opt) installed and on PATH
- clang installed and on PATH

Tests are automatically *skipped* when the required tools are absent so CI
environments without LLVM installed do not fail.
"""

import os
import subprocess
import sys
import tempfile

import pytest

# Ensure the src/ tree is importable regardless of how pytest is invoked.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))

from nexuslang.parser.lexer import Lexer
from nexuslang.parser.parser import Parser
from nexuslang.compiler.backends.llvm_ir_generator import LLVMIRGenerator


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

def _tools_available() -> bool:
    """Return True when llc, opt AND clang are all on PATH."""
    import shutil
    return all(shutil.which(t) for t in ("llc", "opt", "clang"))


skip_no_llvm = pytest.mark.skipif(
    not _tools_available(),
    reason="LLVM tools (llc, opt, clang) not available on PATH"
)


def compile_and_run(source: str) -> tuple[int, str, str]:
    """Compile *source* to a native binary and run it.

    Returns ``(returncode, stdout, stderr)``.

    Raises ``CompilationFailed`` if any compilation step returns a non-zero
    exit code.
    """
    tokens = Lexer(source).tokenize()
    ast = Parser(tokens).parse()

    gen = LLVMIRGenerator()
    gen.generate(ast, source_file="test.nxl")

    with tempfile.TemporaryDirectory() as tmpdir:
        exe = os.path.join(tmpdir, "test_prog")

        # LLVMIRGenerator.compile_to_executable() drives opt -> llc -> clang.
        # It prints progress banners; suppress them so test output is clean.
        import io
        saved = sys.stdout
        sys.stdout = io.StringIO()
        try:
            ok = gen.compile_to_executable(exe, opt_level=0)
        finally:
            sys.stdout = saved

        if not ok or not os.path.exists(exe):
            raise CompilationFailed("compile_to_executable() returned False")

        result = subprocess.run([exe], capture_output=True, text=True, timeout=15)
        return result.returncode, result.stdout, result.stderr


class CompilationFailed(Exception):
    pass


# ---------------------------------------------------------------------------
# Test cases
# ---------------------------------------------------------------------------

@skip_no_llvm
class TestCompilerRoundtrip:
    """Each method compiles a specific NexusLang program and checks the native output."""

    # --- basic output -------------------------------------------------------

    def test_hello_world(self):
        src = """
function main returns Integer
    print text "hello world"
    return 0
end
"""
        rc, out, _ = compile_and_run(src)
        assert rc == 0
        assert out == "hello world\n"

    def test_print_integer(self):
        src = """
function main returns Integer
    print text 42
    return 0
end
"""
        rc, out, _ = compile_and_run(src)
        assert rc == 0
        assert out == "42\n"

    # --- arithmetic ---------------------------------------------------------

    def test_integer_multiplication(self):
        src = """
function main returns Integer
    set x to 6
    set y to 7
    set result to x times y
    print text result
    return 0
end
"""
        rc, out, _ = compile_and_run(src)
        assert rc == 0
        assert out == "42\n"

    def test_integer_addition(self):
        src = """
function main returns Integer
    set a to 100
    set b to 23
    print text a plus b
    return 0
end
"""
        rc, out, _ = compile_and_run(src)
        assert rc == 0
        assert out == "123\n"

    def test_integer_subtraction(self):
        src = """
function main returns Integer
    set x to 50
    set y to 8
    print text x minus y
    return 0
end
"""
        rc, out, _ = compile_and_run(src)
        assert rc == 0
        assert out == "42\n"

    # --- control flow -------------------------------------------------------

    def test_if_true_branch(self):
        src = """
function main returns Integer
    set x to 42
    if x is greater than 10
        print text "big"
    else
        print text "small"
    end
    return 0
end
"""
        rc, out, _ = compile_and_run(src)
        assert rc == 0
        assert out == "big\n"

    def test_if_false_branch(self):
        src = """
function main returns Integer
    set x to 5
    if x is greater than 10
        print text "big"
    else
        print text "small"
    end
    return 0
end
"""
        rc, out, _ = compile_and_run(src)
        assert rc == 0
        assert out == "small\n"

    def test_while_loop(self):
        src = """
function main returns Integer
    set i to 0
    set sum to 0
    while i is less than 5
        set sum to sum plus i
        set i to i plus 1
    end
    print text sum
    return 0
end
"""
        rc, out, _ = compile_and_run(src)
        assert rc == 0
        assert out == "10\n"

    # --- functions ----------------------------------------------------------

    def test_function_call_no_args(self):
        src = """
function greet returns Integer
    print text "hi"
    return 0
end

function main returns Integer
    call greet
    return 0
end
"""
        rc, out, _ = compile_and_run(src)
        assert rc == 0
        assert out == "hi\n"

    def test_function_with_argument(self):
        src = """
function double with n as Integer returns Integer
    return n times 2
end

function main returns Integer
    set result to double with 21
    print text result
    return 0
end
"""
        rc, out, _ = compile_and_run(src)
        assert rc == 0
        assert out == "42\n"

    def test_function_returns_value(self):
        src = """
function add with a as Integer and b as Integer returns Integer
    return a plus b
end

function main returns Integer
    print text add with 10 and 32
    return 0
end
"""
        rc, out, _ = compile_and_run(src)
        assert rc == 0
        assert out == "42\n"

    def test_recursive_fibonacci(self):
        """Recursive fibonacci: validates recursive function calls and proper
        binary-expression parsing for 'fib with n minus 1 plus fib with n minus 2'."""
        src = """
function fib with n as Integer returns Integer
    if n is less than or equal to 1
        return n
    end
    return fib with n minus 1 plus fib with n minus 2
end

function main returns Integer
    set result to fib with 10
    print text result
    return 0
end
"""
        rc, out, _ = compile_and_run(src)
        assert rc == 0
        assert out == "55\n"

    def test_iterative_fibonacci(self):
        src = """
function fib_iter with n as Integer returns Integer
    if n is less than or equal to 1
        return n
    end
    set a to 0
    set b to 1
    set i to 2
    while i is less than or equal to n
        set c to a plus b
        set a to b
        set b to c
        set i to i plus 1
    end
    return b
end

function main returns Integer
    print text fib_iter with 20
    return 0
end
"""
        rc, out, _ = compile_and_run(src)
        assert rc == 0
        assert out == "6765\n"

    # --- return code --------------------------------------------------------

    def test_return_code_zero(self):
        src = """
function main returns Integer
    return 0
end
"""
        rc, _, _ = compile_and_run(src)
        assert rc == 0

    def test_return_code_nonzero(self):
        src = """
function main returns Integer
    return 42
end
"""
        rc, _, _ = compile_and_run(src)
        assert rc == 42


@skip_no_llvm
class TestArithmeticOperations:
    """Extended arithmetic and comparison operations."""

    def test_integer_division(self):
        src = """
function main returns Integer
    set x to 100
    set y to x divided by 4
    print text y
    return 0
end
"""
        rc, out, _ = compile_and_run(src)
        assert rc == 0
        assert out == "25\n"

    def test_modulo(self):
        src = """
function main returns Integer
    set x to 17
    set y to x modulo 5
    print text y
    return 0
end
"""
        rc, out, _ = compile_and_run(src)
        assert rc == 0
        assert out == "2\n"

    def test_combined_arithmetic(self):
        """Tests operator precedence and multi-step arithmetic."""
        src = """
function main returns Integer
    set a to 10
    set b to 3
    set sum to a plus b
    set diff to a minus b
    set prod to a times b
    set quot to a divided by b
    print text sum
    print text diff
    print text prod
    print text quot
    return 0
end
"""
        rc, out, _ = compile_and_run(src)
        assert rc == 0
        assert out == "13\n7\n30\n3\n"

    def test_variable_reassignment(self):
        src = """
function main returns Integer
    set x to 1
    set x to x plus 10
    set x to x times 2
    print text x
    return 0
end
"""
        rc, out, _ = compile_and_run(src)
        assert rc == 0
        assert out == "22\n"


@skip_no_llvm
class TestComparisonOperators:
    """All six comparison operators compiled to native code."""

    def test_less_than_or_equal(self):
        src = """
function main returns Integer
    set x to 10
    if x is less than or equal to 10
        print text "yes"
    else
        print text "no"
    end
    return 0
end
"""
        rc, out, _ = compile_and_run(src)
        assert rc == 0
        assert out == "yes\n"

    def test_greater_than_or_equal(self):
        src = """
function main returns Integer
    set x to 10
    if x is greater than or equal to 10
        print text "yes"
    else
        print text "no"
    end
    return 0
end
"""
        rc, out, _ = compile_and_run(src)
        assert rc == 0
        assert out == "yes\n"

    def test_not_equal(self):
        src = """
function main returns Integer
    set x to 10
    if x is not equal to 5
        print text "different"
    else
        print text "same"
    end
    return 0
end
"""
        rc, out, _ = compile_and_run(src)
        assert rc == 0
        assert out == "different\n"

    def test_equal_to(self):
        src = """
function main returns Integer
    set x to 42
    if x is equal to 42
        print text "match"
    else
        print text "no match"
    end
    return 0
end
"""
        rc, out, _ = compile_and_run(src)
        assert rc == 0
        assert out == "match\n"

    def test_string_equality(self):
        src = """
function main returns Integer
    set name to "alice"
    if name is equal to "alice"
        print text "found"
    else
        print text "not found"
    end
    return 0
end
"""
        rc, out, _ = compile_and_run(src)
        assert rc == 0
        assert out == "found\n"


@skip_no_llvm
class TestControlFlow:
    """Extended control flow: nested if/else, boolean operators, match."""

    def test_nested_if_else(self):
        src = """
function main returns Integer
    set x to 15
    if x is greater than 20
        print text "big"
    else if x is greater than 10
        print text "medium"
    else
        print text "small"
    end
    return 0
end
"""
        rc, out, _ = compile_and_run(src)
        assert rc == 0
        assert out == "medium\n"

    def test_logical_and(self):
        src = """
function main returns Integer
    set x to 10
    if x is greater than 5 and x is less than 20
        print text "in range"
    else
        print text "out of range"
    end
    return 0
end
"""
        rc, out, _ = compile_and_run(src)
        assert rc == 0
        assert out == "in range\n"

    def test_logical_or(self):
        src = """
function main returns Integer
    set x to 0
    if x is equal to 5 or x is equal to 0
        print text "found"
    else
        print text "nope"
    end
    return 0
end
"""
        rc, out, _ = compile_and_run(src)
        assert rc == 0
        assert out == "found\n"

    def test_match_integer(self):
        src = """
function main returns Integer
    set x to 2
    match x with
        case 1
            print text "one"
        case 2
            print text "two"
        case 3
            print text "three"
    end
    return 0
end
"""
        rc, out, _ = compile_and_run(src)
        assert rc == 0
        assert out == "two\n"


@skip_no_llvm
class TestLoops:
    """Extended loop constructs: break, continue, nested loops."""

    def test_break_in_while(self):
        src = """
function main returns Integer
    set i to 0
    while i is less than 100
        if i is equal to 5
            break
        end
        set i to i plus 1
    end
    print text i
    return 0
end
"""
        rc, out, _ = compile_and_run(src)
        assert rc == 0
        assert out == "5\n"

    def test_continue_in_while(self):
        """Sum 1..10 skipping 3 and 7: 1+2+4+5+6+8+9+10 = 45."""
        src = """
function main returns Integer
    set sum to 0
    set i to 0
    while i is less than 10
        set i to i plus 1
        if i is equal to 3
            continue
        end
        if i is equal to 7
            continue
        end
        set sum to sum plus i
    end
    print text sum
    return 0
end
"""
        rc, out, _ = compile_and_run(src)
        assert rc == 0
        assert out == "45\n"

    def test_nested_loops(self):
        """5x5 nested loop counting iterations."""
        src = """
function main returns Integer
    set count to 0
    set i to 0
    while i is less than 5
        set j to 0
        while j is less than 5
            set count to count plus 1
            set j to j plus 1
        end
        set i to i plus 1
    end
    print text count
    return 0
end
"""
        rc, out, _ = compile_and_run(src)
        assert rc == 0
        assert out == "25\n"

    def test_loop_accumulator(self):
        """Sum of 1+2+...+100 = 5050."""
        src = """
function main returns Integer
    set sum to 0
    set i to 1
    while i is less than or equal to 100
        set sum to sum plus i
        set i to i plus 1
    end
    print text sum
    return 0
end
"""
        rc, out, _ = compile_and_run(src)
        assert rc == 0
        assert out == "5050\n"


@skip_no_llvm
class TestFunctions:
    """Extended function tests: multiple args, mutual recursion, chaining."""

    def test_multiple_arguments(self):
        src = """
function add with a as Integer and b as Integer returns Integer
    return a plus b
end

function main returns Integer
    print text add with 10 and 32
    return 0
end
"""
        rc, out, _ = compile_and_run(src)
        assert rc == 0
        assert out == "42\n"

    def test_chained_calls(self):
        src = """
function increment with n as Integer returns Integer
    return n plus 1
end

function double with n as Integer returns Integer
    return n times 2
end

function main returns Integer
    set a to increment with 4
    set b to double with a
    print text b
    return 0
end
"""
        rc, out, _ = compile_and_run(src)
        assert rc == 0
        assert out == "10\n"

    def test_nested_function_calls(self):
        """Nested call: add_one(square(5)) = 26."""
        src = """
function square with n as Integer returns Integer
    return n times n
end

function add_one with n as Integer returns Integer
    return n plus 1
end

function main returns Integer
    set result to add_one with square with 5
    print text result
    return 0
end
"""
        rc, out, _ = compile_and_run(src)
        assert rc == 0
        assert out == "26\n"

    def test_mutual_recursion(self):
        """is_even/is_odd via mutual recursion."""
        src = """
function is_even with n as Integer returns Integer
    if n is equal to 0
        return 1
    end
    return is_odd with n minus 1
end

function is_odd with n as Integer returns Integer
    if n is equal to 0
        return 0
    end
    return is_even with n minus 1
end

function main returns Integer
    print text is_even with 10
    print text is_odd with 10
    print text is_even with 7
    print text is_odd with 7
    return 0
end
"""
        rc, out, _ = compile_and_run(src)
        assert rc == 0
        assert out == "1\n0\n0\n1\n"

    def test_multiple_return_paths(self):
        """Function with early returns from different branches."""
        src = """
function classify with n as Integer returns Integer
    if n is greater than 100
        return 3
    end
    if n is greater than 10
        return 2
    end
    return 1
end

function main returns Integer
    print text classify with 5
    print text classify with 50
    print text classify with 500
    return 0
end
"""
        rc, out, _ = compile_and_run(src)
        assert rc == 0
        assert out == "1\n2\n3\n"


@skip_no_llvm
class TestStrings:
    """String operations in compiled output."""

    def test_string_concatenation(self):
        src = """
function main returns Integer
    set greeting to "hello" plus " world"
    print text greeting
    return 0
end
"""
        rc, out, _ = compile_and_run(src)
        assert rc == 0
        assert out == "hello world\n"

    def test_multiple_print_statements(self):
        src = """
function main returns Integer
    print text "a"
    print text "b"
    print text "c"
    return 0
end
"""
        rc, out, _ = compile_and_run(src)
        assert rc == 0
        assert out == "a\nb\nc\n"


@skip_no_llvm
class TestArrays:
    """Array creation, indexing, and iteration."""

    def test_array_literal_indexing(self):
        src = """
function main returns Integer
    set arr to [10, 20, 30, 40, 50]
    print text arr[0]
    print text arr[2]
    print text arr[4]
    return 0
end
"""
        rc, out, _ = compile_and_run(src)
        assert rc == 0
        assert out == "10\n30\n50\n"

    def test_array_sum_loop(self):
        """Iterate over array by index and sum elements."""
        src = """
function main returns Integer
    set arr to [10, 20, 30, 40, 50]
    set sum to 0
    set i to 0
    while i is less than 5
        set sum to sum plus arr[i]
        set i to i plus 1
    end
    print text sum
    return 0
end
"""
        rc, out, _ = compile_and_run(src)
        assert rc == 0
        assert out == "150\n"


@skip_no_llvm
class TestAlgorithms:
    """Real-world algorithms compiled end-to-end."""

    def test_gcd_euclidean(self):
        """Greatest common divisor using Euclidean algorithm."""
        src = """
function gcd with a as Integer and b as Integer returns Integer
    while b is not equal to 0
        set temp to b
        set b to a modulo b
        set a to temp
    end
    return a
end

function main returns Integer
    print text gcd with 48 and 18
    print text gcd with 100 and 75
    return 0
end
"""
        rc, out, _ = compile_and_run(src)
        assert rc == 0
        assert out == "6\n25\n"

    def test_factorial_iterative(self):
        """Iterative factorial: 10! = 3628800."""
        src = """
function factorial with n as Integer returns Integer
    set result to 1
    set i to 2
    while i is less than or equal to n
        set result to result times i
        set i to i plus 1
    end
    return result
end

function main returns Integer
    print text factorial with 10
    return 0
end
"""
        rc, out, _ = compile_and_run(src)
        assert rc == 0
        assert out == "3628800\n"

    def test_power_function(self):
        """Iterative exponentiation: 2^10 = 1024."""
        src = """
function int_pow with base as Integer and exp as Integer returns Integer
    set result to 1
    set i to 0
    while i is less than exp
        set result to result times base
        set i to i plus 1
    end
    return result
end

function main returns Integer
    print text int_pow with 2 and 10
    print text int_pow with 3 and 5
    return 0
end
"""
        rc, out, _ = compile_and_run(src)
        assert rc == 0
        assert out == "1024\n243\n"

    def test_collatz_steps(self):
        """Count Collatz steps from 27 to 1 (should be 111)."""
        src = """
function collatz_steps with n as Integer returns Integer
    set steps to 0
    while n is not equal to 1
        if n modulo 2 is equal to 0
            set n to n divided by 2
        else
            set n to n times 3 plus 1
        end
        set steps to steps plus 1
    end
    return steps
end

function main returns Integer
    print text collatz_steps with 27
    return 0
end
"""
        rc, out, _ = compile_and_run(src)
        assert rc == 0
        assert out == "111\n"


@skip_no_llvm
class TestOptimizationLevels:
    """Verify that -O3 produces correct output (not just that it compiles)."""

    def test_fibonacci_O3_correctness(self):
        """Fibonacci at -O3 must produce the same result as -O0."""
        src = """
function fib with n as Integer returns Integer
    if n is less than or equal to 1
        return n
    end
    set a to 0
    set b to 1
    set i to 2
    while i is less than or equal to n
        set c to a plus b
        set a to b
        set b to c
        set i to i plus 1
    end
    return b
end

function main returns Integer
    print text fib with 30
    return 0
end
"""
        tokens = Lexer(src).tokenize()
        ast = Parser(tokens).parse()

        gen_o0 = LLVMIRGenerator()
        gen_o0.generate(ast, source_file="test.nxl")

        gen_o3 = LLVMIRGenerator()
        gen_o3.generate(ast, source_file="test.nxl")

        import tempfile, io
        with tempfile.TemporaryDirectory() as d:
            # Compile at O0
            exe_o0 = os.path.join(d, "test_o0")
            old = sys.stdout; sys.stdout = io.StringIO()
            try:
                ok0 = gen_o0.compile_to_executable(exe_o0, opt_level=0)
            finally:
                sys.stdout = old
            assert ok0

            # Compile at O3
            exe_o3 = os.path.join(d, "test_o3")
            sys.stdout = io.StringIO()
            try:
                ok3 = gen_o3.compile_to_executable(exe_o3, opt_level=3)
            finally:
                sys.stdout = old

            assert ok3

            r0 = subprocess.run([exe_o0], capture_output=True, text=True, timeout=15)
            r3 = subprocess.run([exe_o3], capture_output=True, text=True, timeout=15)

            assert r0.stdout == r3.stdout == "832040\n"
