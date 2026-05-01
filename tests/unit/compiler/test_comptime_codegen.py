"""Compiler backend coverage for comptime lowering."""

import os
import sys


sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from nexuslang.compiler.backends.c_generator import CCodeGenerator
from nexuslang.compiler.backends.llvm_ir_generator import LLVMIRGenerator
from nexuslang.parser.lexer import Lexer
from nexuslang.parser.parser import Parser


def _parse(code: str):
    lexer = Lexer(code)
    tokens = lexer.scan_tokens()
    parser = Parser(tokens)
    return parser.parse()


def test_llvm_comptime_const_is_collected_as_global_and_initialized_before_main():
    ast = _parse(
        """
comptime const BASE is 10
function add_limit with n as Integer returns Integer
    return n plus BASE
end

function main returns Integer
    print text add_limit with 5
    return 0
end
"""
    )

    llvm_ir = LLVMIRGenerator().generate(ast)

    assert "@BASE = global i64 0" in llvm_ir
    assert "store i64 10, i64* @BASE" in llvm_ir
    assert "invoke i64 @nxl_main()" in llvm_ir
    assert llvm_ir.index("store i64 10, i64* @BASE") < llvm_ir.index("invoke i64 @nxl_main()")


def test_llvm_comptime_assert_constant_true_emits_no_runtime_panic():
    ast = _parse(
        """
comptime assert 2 times 3 is equal to 6
function main returns Integer
    return 0
end
"""
    )

    llvm_ir = LLVMIRGenerator().generate(ast)

    assert "Compile-time assertion failed" not in llvm_ir


def test_c_comptime_const_uses_top_level_init_and_static_storage():
    ast = _parse(
        """
comptime const BASE is 10
function add_limit with n as Integer returns Integer
    return n plus BASE
end

function main returns Integer
    print text add_limit with 5
    return 0
end
"""
    )

    c_code = CCodeGenerator(target="c").generate(ast)

    assert "static void __nxl_top_level_init(void);" in c_code
    assert "static int BASE;" in c_code
    assert "__nxl_top_level_init();" in c_code
    assert "static void __nxl_top_level_init(void) {" in c_code
    assert "BASE = 10;" in c_code


def test_c_comptime_assert_lowers_to_guard():
    ast = _parse(
        """
function main returns Integer
    set value to 5
    comptime assert value is greater than 0 message "value must be positive"
    return 0
end
"""
    )

    c_code = CCodeGenerator(target="c").generate(ast)

    assert "value must be positive" in c_code
    assert "fprintf(stderr" in c_code
    assert "exit(1);" in c_code
