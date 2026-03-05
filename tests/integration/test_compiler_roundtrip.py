"""
Compiler round-trip integration tests: NLPL source -> LLVM IR -> native binary -> execute.

Each test compiles a small NLPL program all the way to a native executable (via the
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

from nlpl.parser.lexer import Lexer
from nlpl.parser.parser import Parser
from nlpl.compiler.backends.llvm_ir_generator import LLVMIRGenerator


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
    gen.generate(ast, source_file="test.nlpl")

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
    """Each method compiles a specific NLPL program and checks the native output."""

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
