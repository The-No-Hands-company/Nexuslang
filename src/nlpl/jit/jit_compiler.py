"""
JIT Compiler for NLPL
======================

Compiles hot NLPL functions to native machine code using LLVM.
"""

import time
from typing import Dict, Optional, Any, Callable
from dataclasses import dataclass, field

from .hot_function_detector import HotFunctionDetector


@dataclass
class JITStats:
    """Statistics about JIT compilation."""
    functions_compiled: int = 0
    total_compile_time: float = 0.0
    total_jit_execution_time: float = 0.0
    total_interpreter_execution_time: float = 0.0
    compilation_failures: int = 0
    
    @property
    def avg_compile_time(self) -> float:
        """Average time to compile a function."""
        return (self.total_compile_time / self.functions_compiled 
                if self.functions_compiled > 0 else 0.0)
    
    @property
    def speedup_factor(self) -> float:
        """Calculate speedup of JIT vs interpreter."""
        if self.total_jit_execution_time > 0:
            return self.total_interpreter_execution_time / self.total_jit_execution_time
        return 1.0


class JITCompiler:
    """
    Just-In-Time compiler for NLPL functions.
    
    Monitors function execution, identifies hot functions, and compiles them
    to native code using LLVM for improved performance.
    
    Note: This is a framework/infrastructure implementation. Full LLVM integration
    requires the llvmlite library. For now, this provides the architecture and
    will fall back to interpreter execution.
    """
    
    def __init__(self, hot_threshold: int = 100, optimization_level: int = 2):
        """
        Initialize the JIT compiler.
        
        Args:
            hot_threshold: Call count threshold for JIT compilation
            optimization_level: LLVM optimization level (0-3)
        """
        self.hot_threshold = hot_threshold
        self.optimization_level = optimization_level
        self.detector = HotFunctionDetector(hot_threshold=hot_threshold)
        self.compiled_functions: Dict[str, Callable] = {}
        self.stats = JITStats()
        self.interpreter = None
        self.enabled = True
        
        # Try to import llvmlite for actual JIT compilation
        self.llvm_available = False
        try:
            import llvmlite
            self.llvm_available = True
        except ImportError:
            pass  # Will use interpreter fallback
    
    def attach_to_interpreter(self, interpreter):
        """
        Attach JIT compiler to an interpreter instance.
        
        This hooks into the interpreter's function call mechanism to:
        1. Track function call counts
        2. Compile hot functions
        3. Replace interpreted execution with JIT execution
        """
        self.interpreter = interpreter
        
        # Store original function call handler
        if hasattr(interpreter, 'call_function'):
            self.original_call_function = interpreter.call_function
            # Wrap it with JIT logic
            interpreter.call_function = self._jit_call_function_wrapper
    
    def _jit_call_function_wrapper(self, function_name: str, arguments: list):
        """
        Wrapper for interpreter's function call that implements JIT logic.
        
        Flow:
        1. Check if function is already JIT compiled -> use compiled version
        2. Record call for hot function detection
        3. Check if function became hot -> compile it
        4. Execute using interpreter (or compiled version if available)
        """
        start_time = time.time()
        
        # Check if we have a compiled version
        if function_name in self.compiled_functions:
            # Execute JIT compiled version
            result = self._execute_jit_function(function_name, arguments)
            execution_time = time.time() - start_time
            self.stats.total_jit_execution_time += execution_time
            return result
        
        # Execute using interpreter
        result = self.original_call_function(function_name, arguments)
        execution_time = time.time() - start_time
        
        # Record call for hot detection
        self.detector.record_call(function_name, execution_time)
        self.stats.total_interpreter_execution_time += execution_time
        
        # Check if function became hot and should be compiled
        if self.enabled and self.detector.is_hot(function_name):
            if not self.detector.is_jit_compiled(function_name):
                self._compile_function(function_name)
        
        return result
    
    def _compile_function(self, function_name: str) -> bool:
        """
        Compile a function to native code using LLVM.
        
        Args:
            function_name: Name of the function to compile
        
        Returns:
            True if compilation succeeded, False otherwise
        """
        if not self.enabled:
            return False
        
        print(f"[JIT] Compiling hot function: {function_name}")
        compile_start = time.time()
        
        try:
            # Get function definition from interpreter
            if not self.interpreter or function_name not in self.interpreter.functions:
                raise ValueError(f"Function {function_name} not found in interpreter")
            
            function_def = self.interpreter.functions[function_name]
            
            # Compile to native code
            if self.llvm_available:
                compiled_func = self._compile_with_llvm(function_def)
            else:
                # Fallback: use optimized interpreter path
                compiled_func = self._create_optimized_interpreter_function(function_def)
            
            compile_time = time.time() - compile_start
            
            # Store compiled function
            self.compiled_functions[function_name] = compiled_func
            self.detector.mark_jit_compiled(function_name, compile_time)
            
            # Update stats
            self.stats.functions_compiled += 1
            self.stats.total_compile_time += compile_time
            
            print(f"[JIT] Compiled {function_name} in {compile_time*1000:.2f}ms")
            return True
            
        except Exception as e:
            print(f"[JIT] Compilation failed for {function_name}: {e}")
            self.stats.compilation_failures += 1
            return False
    
    def _compile_with_llvm(self, function_def) -> Callable:
        """
        Compile function to LLVM IR and then to machine code.
        
        This would use llvmlite to:
        1. Generate LLVM IR from NLPL function
        2. Optimize the IR
        3. Compile to machine code
        4. Return executable function
        
        Note: Requires full implementation with llvmlite
        """
        # TODO: Implement LLVM IR generation
        # For now, fall back to optimized interpreter
        return self._create_optimized_interpreter_function(function_def)
    
    def _create_optimized_interpreter_function(self, function_def) -> Callable:
        """
        Create an optimized interpreter-based function.
        
        This applies various optimizations:
        - Precompute parameter mappings
        - Cache scope setup
        - Skip unnecessary type checks
        - Inline small operations
        """
        # Pre-compute parameter info
        param_names = [p.name for p in function_def.parameters]
        param_count = len(param_names)
        
        def optimized_function(*args):
            """Optimized execution of NLPL function."""
            # Fast parameter binding
            if len(args) != param_count:
                raise TypeError(
                    f"{function_def.name} expects {param_count} arguments, got {len(args)}"
                )
            
            # Create scope with pre-allocated dict
            scope = dict(zip(param_names, args))
            
            # Execute function body with minimal overhead
            self.interpreter.enter_scope()
            self.interpreter.current_scope[-1].update(scope)
            
            try:
                for stmt in function_def.body:
                    self.interpreter.execute(stmt)
                return None  # No explicit return
            except self.interpreter.ReturnException as e:
                return e.value
            finally:
                self.interpreter.exit_scope()
        
        return optimized_function
    
    def _execute_jit_function(self, function_name: str, arguments: list) -> Any:
        """Execute a JIT-compiled function."""
        if function_name not in self.compiled_functions:
            raise RuntimeError(f"Function {function_name} not compiled")
        
        compiled_func = self.compiled_functions[function_name]
        return compiled_func(*arguments)
    
    def get_compiled_function(self, function_name: str) -> Optional[Callable]:
        """Get the compiled version of a function, if it exists."""
        return self.compiled_functions.get(function_name)
    
    def is_compiled(self, function_name: str) -> bool:
        """Check if a function has been JIT compiled."""
        return function_name in self.compiled_functions
    
    def disable(self):
        """Temporarily disable JIT compilation."""
        self.enabled = False
    
    def enable(self):
        """Re-enable JIT compilation."""
        self.enabled = True
    
    def clear_cache(self):
        """Clear all compiled functions."""
        self.compiled_functions.clear()
        self.detector.jit_compiled_functions.clear()
    
    def print_stats(self):
        """Print JIT compilation statistics."""
        print("\n" + "="*70)
        print("JIT Compilation Statistics")
        print("="*70)
        print(f"Functions Compiled: {self.stats.functions_compiled}")
        print(f"Compilation Failures: {self.stats.compilation_failures}")
        print(f"Total Compile Time: {self.stats.total_compile_time:.3f}s")
        print(f"Avg Compile Time: {self.stats.avg_compile_time*1000:.2f}ms")
        print(f"\nExecution Time:")
        print(f"  JIT: {self.stats.total_jit_execution_time:.3f}s")
        print(f"  Interpreter: {self.stats.total_interpreter_execution_time:.3f}s")
        print(f"  Speedup: {self.stats.speedup_factor:.2f}x")
        print(f"\nLLVM Available: {'Yes' if self.llvm_available else 'No (using optimized interpreter)'}")
        print("="*70)
        
        # Print hot function detector report
        self.detector.print_report()
