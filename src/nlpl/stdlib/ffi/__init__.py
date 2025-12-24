"""
FFI (Foreign Function Interface) module for NLPL.
Allows calling functions from C libraries using ctypes.
"""

import ctypes
import ctypes.util
from typing import Dict, List, Any, Optional, Callable
from ...runtime.runtime import Runtime

class FFILibrary:
    """Wrapper for a loaded C library."""
    
    def __init__(self, library_name: str, handle: ctypes.CDLL):
        self.name = library_name
        self.handle = handle
        self.functions: Dict[str, Callable] = {}
    
    def get_function(self, name: str, argtypes: List[Any], restype: Any) -> Callable:
        """Get a function from the library with specified signature."""
        if name in self.functions:
            return self.functions[name]
        
        func = getattr(self.handle, name)
        func.argtypes = argtypes
        func.restype = restype
        self.functions[name] = func
        return func

class FFIManager:
    """Manages FFI libraries and function calls."""
    
    def __init__(self):
        self.libraries: Dict[str, FFILibrary] = {}
        self.type_map = {
            'int': ctypes.c_int,
            'long': ctypes.c_long,
            'float': ctypes.c_float,
            'double': ctypes.c_double,
            'char': ctypes.c_char,
            'char*': ctypes.c_char_p,
            'void*': ctypes.c_void_p,
            'size_t': ctypes.c_size_t,
            'uint8': ctypes.c_uint8,
            'uint16': ctypes.c_uint16,
            'uint32': ctypes.c_uint32,
            'uint64': ctypes.c_uint64,
            'int8': ctypes.c_int8,
            'int16': ctypes.c_int16,
            'int32': ctypes.c_int32,
            'int64': ctypes.c_int64,
        }
    
    def load_library(self, name: str, path: Optional[str] = None) -> FFILibrary:
        """Load a C library by name or path."""
        if name in self.libraries:
            return self.libraries[name]
        
        try:
            if path:
                handle = ctypes.CDLL(path)
            else:
                # Try to find library in system paths
                lib_path = ctypes.util.find_library(name)
                if not lib_path:
                    raise RuntimeError(f"Library '{name}' not found in system paths")
                handle = ctypes.CDLL(lib_path)
            
            library = FFILibrary(name, handle)
            self.libraries[name] = library
            return library
        except OSError as e:
            raise RuntimeError(f"Failed to load library '{name}': {e}")
    
    def map_type(self, type_name: str) -> Any:
        """Map NLPL/string type name to ctypes type."""
        if type_name in self.type_map:
            return self.type_map[type_name]
        elif type_name == 'void':
            return None
        else:
            raise ValueError(f"Unknown FFI type: {type_name}")
    
    def call_function(self, lib_name: str, func_name: str, 
                     arg_types: List[str], return_type: str, 
                     args: List[Any]) -> Any:
        """Call a C function from a loaded library."""
        if lib_name not in self.libraries:
            raise RuntimeError(f"Library '{lib_name}' not loaded")
        
        library = self.libraries[lib_name]
        
        # Map type names to ctypes
        c_arg_types = [self.map_type(t) for t in arg_types]
        c_return_type = self.map_type(return_type)
        
        # Get the function
        func = library.get_function(func_name, c_arg_types, c_return_type)
        
        # Convert arguments to appropriate ctypes
        c_args = []
        for arg, arg_type in zip(args, c_arg_types):
            if arg_type == ctypes.c_char_p and isinstance(arg, str):
                c_args.append(arg.encode('utf-8'))
            else:
                c_args.append(arg)
        
        # Call the function
        result = func(*c_args)
        
        # Convert result back to Python type
        if c_return_type == ctypes.c_char_p and result:
            return result.decode('utf-8')
        return result

def register_ffi_functions(runtime: Runtime) -> None:
    """Register FFI functions with the runtime."""
    ffi_manager = FFIManager()
    
    # Store FFI manager in runtime for access
    runtime.ffi_manager = ffi_manager
    
    # Register functions
    runtime.register_function("ffi_load_library", lambda name, path=None: ffi_manager.load_library(name, path))
    runtime.register_function("ffi_call", lambda lib, func, arg_types, return_type, *args: 
                            ffi_manager.call_function(lib, func, arg_types, return_type, list(args)))
    
    # Helper functions for common C library functions
    def c_strlen(s: str) -> int:
        """Call C strlen function."""
        try:
            ffi_manager.load_library("c")
            return ffi_manager.call_function("c", "strlen", ["char*"], "size_t", [s])
        except Exception as e:
            raise RuntimeError(f"Failed to call strlen: {e}")
    
    def c_malloc(size: int) -> int:
        """Call C malloc function."""
        try:
            ffi_manager.load_library("c")
            return ffi_manager.call_function("c", "malloc", ["size_t"], "void*", [size])
        except Exception as e:
            raise RuntimeError(f"Failed to call malloc: {e}")
    
    def c_free(ptr: int) -> None:
        """Call C free function."""
        try:
            ffi_manager.load_library("c")
            ffi_manager.call_function("c", "free", ["void*"], "void", [ptr])
        except Exception as e:
            raise RuntimeError(f"Failed to call free: {e}")
    
    runtime.register_function("c_strlen", c_strlen)
    runtime.register_function("c_malloc", c_malloc)
    runtime.register_function("c_free", c_free)
