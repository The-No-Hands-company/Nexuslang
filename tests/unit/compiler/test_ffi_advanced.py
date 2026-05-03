import pytest

llvmlite = pytest.importorskip("llvmlite")
ir = llvmlite.ir

from nexuslang.compiler.ffi_advanced import CallbackManager


def test_compiler_callback_registration_fails_fast_until_implemented():
    module = ir.Module(name="test_module")
    function = ir.Function(module, ir.FunctionType(ir.VoidType(), []), name="entry")
    block = function.append_basic_block(name="entry")
    builder = ir.IRBuilder(block)

    manager = CallbackManager(module, builder)

    with pytest.raises(NotImplementedError, match="callback trampolines"):
        manager.register_callback(
            name="sort_callback",
            param_types=["Integer", "Integer"],
            return_type="Integer",
            nxl_function="compare_values",
        )