"""
NLPL JIT Compiler
=================

Just-In-Time compilation for hot functions using LLVM.

Key Features:
- Hot function detection based on call count thresholds
- LLVM IR generation for NLPL functions
- JIT compilation to native machine code
- Hybrid interpreter/JIT execution mode
- Transparent fallback to interpreter on JIT failure

Usage:
    from nlpl.jit import JITCompiler, enable_jit
    
    # Enable JIT for an interpreter
    jit = enable_jit(interpreter, hot_threshold=100)
    
    # Or create manually
    jit = JITCompiler(hot_threshold=100)
    jit.attach_to_interpreter(interpreter)
"""

from .jit_compiler import JITCompiler, JITStats
from .hot_function_detector import HotFunctionDetector

def enable_jit(interpreter, hot_threshold=100, optimization_level=2):
    """
    Enable JIT compilation for an interpreter instance.
    
    Args:
        interpreter: The Interpreter instance to attach JIT to
        hot_threshold: Number of calls before function is considered "hot"
        optimization_level: LLVM optimization level (0-3)
    
    Returns:
        JITCompiler instance
    """
    jit = JITCompiler(
        hot_threshold=hot_threshold,
        optimization_level=optimization_level
    )
    jit.attach_to_interpreter(interpreter)
    return jit

__all__ = [
    'JITCompiler',
    'JITStats',
    'HotFunctionDetector',
    'enable_jit'
]
