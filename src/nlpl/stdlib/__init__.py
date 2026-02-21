"""
Standard library for the Natural Language Programming Language (NLPL).
This package contains built-in functions and modules for NLPL programs.
"""

from ..runtime.runtime import Runtime
from ..stdlib.option_result import register_option_result_functions
from ..stdlib.math import register_math_functions
from ..stdlib.string import register_string_functions
from ..stdlib.stringbuilder import register_stringbuilder_functions
from ..stdlib.io import register_io_functions
from ..stdlib.system import register_system_functions
from ..stdlib.collections import register_collections_functions
from ..stdlib.network import register_network_functions
from ..stdlib.types import register_type_functions
from ..stdlib.asyncio_utils import register_async_functions
from ..stdlib.iterators import register_iterator_functions
from ..stdlib.ffi import register_ffi_functions
from ..stdlib.asm import register_asm_functions
from ..stdlib.testing import register_testing_functions
from ..stdlib.graphics import register_graphics_functions
from ..stdlib.modules import register_module_functions
from ..stdlib.filesystem import register_filesystem_functions
from ..stdlib.json_utils import register_json_functions
from ..stdlib.regex import register_regex_functions
from ..stdlib.datetime_utils import register_datetime_functions
from ..stdlib.http import register_http_functions
from ..stdlib.crypto import register_crypto_functions
from ..stdlib.uuid_utils import register_uuid_functions
from ..stdlib.random_utils import register_random_functions
from ..stdlib.compression import register_compression_functions
from ..stdlib.env import register_env_functions
from ..stdlib.subprocess_utils import register_subprocess_functions
from ..stdlib.math3d import register_math3d_functions
from ..stdlib.camera import register_camera_functions
from ..stdlib.shaders import register_shader_functions
from ..stdlib.mesh_loader import register_mesh_functions
from ..stdlib.scene import register_scene_functions
from ..stdlib.logging_utils import register_logging_functions
from ..stdlib.csv_utils import register_csv_functions
from ..stdlib.path_utils import register_path_functions
from ..stdlib.signal_utils import register_signal_functions
from ..stdlib.argparse_utils import register_argparse_functions
from ..stdlib.config import register_config_functions
from ..stdlib.file_io import register_file_io_functions
from ..stdlib.sqlite import register_sqlite_functions
from ..stdlib.xml_utils import register_xml_functions
from ..stdlib.email_utils import register_email_functions
from ..stdlib.templates import register_template_functions
from ..stdlib.threading_utils import register_threading_functions
from ..stdlib.serialization import register_serialization_functions
from ..stdlib.websocket_utils import register_websocket_functions
from ..stdlib.databases import register_database_functions
from ..stdlib.pdf_utils import register_pdf_functions
from ..stdlib.image_utils import register_image_functions
from ..stdlib.validation import register_validation_functions
from ..stdlib.cache import register_cache_functions
from ..stdlib.statistics import register_statistics_functions
from ..stdlib.bit_ops import register_bit_ops_functions
from ..stdlib.ctype import register_ctype_functions
from ..stdlib.limits import register_limits_functions
from ..stdlib.algorithms import register_algorithms_functions
from ..stdlib.errno import register_errno_functions
from ..stdlib.simd import register_simd_functions
from ..stdlib.interrupts import register_interrupt_functions
from ..stdlib.type_traits import register_type_trait_functions
from ..stdlib.hardware import register_stdlib as register_hardware_functions
from ..stdlib.atomics import register_stdlib as register_atomics_functions
from ..stdlib.allocators import register_stdlib as register_allocator_functions
from ..stdlib.smart_pointers import register_stdlib as register_smart_pointer_functions
from ..stdlib.threading import register_stdlib as register_native_threading_functions
from ..stdlib.sync import register_stdlib as register_sync_functions
from ..stdlib.business import register_business_functions
from ..stdlib.data import register_data_functions
from ..stdlib.scientific import register_scientific_functions
from ..stdlib.parallel import register_parallel_functions
from ..stdlib.kernel import register_kernel_functions

def register_stdlib(runtime: Runtime) -> None:
    """Register all standard library functions with the runtime."""
    # Register math functions
    register_math_functions(runtime)
    
    # Register string functions
    register_string_functions(runtime)
    
    # Register IO functions
    register_io_functions(runtime)
    
    # Register system functions
    register_system_functions(runtime)
    
    # Register collections functions
    register_collections_functions(runtime)
    
    # Register network functions
    register_network_functions(runtime)
    
    # Register stringbuilder functions
    register_stringbuilder_functions(runtime)
    
    # Register iterator functions
    register_iterator_functions(runtime)
    
    # Register Option and Result types
    register_option_result_functions(runtime)
    
    # Register type utilities (Optional, Result)
    register_type_functions(runtime)
    
    # Register async utilities (Promise)
    register_async_functions(runtime)
    
    # Register FFI (Foreign Function Interface)
    register_ffi_functions(runtime)
    
    # Register graphics (OpenGL/GLFW wrapper)
    try:
        register_graphics_functions(runtime)
    except Exception as e:
        # Graphics module is optional (requires GLFW and PyOpenGL)
        pass
    
    # Register inline assembly support
    register_asm_functions(runtime)
    
    # Register testing framework
    register_testing_functions(runtime)
    
    # Register module system
    register_module_functions(runtime)
    
    # Register file system operations
    register_filesystem_functions(runtime)
    
    # Register 3D math library (Vector3, Matrix4, Quaternion)
    register_math3d_functions(runtime)
    
    # Register JSON utilities
    register_json_functions(runtime)
    
    # Register regular expressions
    register_regex_functions(runtime)
    
    # Register datetime operations
    register_datetime_functions(runtime)
    
    # Register HTTP client
    register_http_functions(runtime)
    
    # Register cryptography
    register_crypto_functions(runtime)
    
    # Register UUID utilities
    register_uuid_functions(runtime)
    
    # Register random utilities
    register_random_functions(runtime)
    
    # Register compression utilities
    register_compression_functions(runtime)
    
    # Register environment utilities
    register_env_functions(runtime)
    
    # Register subprocess utilities
    register_subprocess_functions(runtime)
    
    # Register 3D math library
    register_math3d_functions(runtime)
    
    # Register camera system
    register_camera_functions(runtime)
    
    # Register shader presets
    register_shader_functions(runtime)
    
    # Register mesh loading
    register_mesh_functions(runtime)
    
    # Register scene graph
    register_scene_functions(runtime)
    
    # Register logging utilities
    register_logging_functions(runtime)
    
    # Register CSV utilities
    register_csv_functions(runtime)
    
    # Register path utilities
    register_path_functions(runtime)
    
    # Register signal handling
    register_signal_functions(runtime)
    
    # Register argument parsing
    register_argparse_functions(runtime)
    
    # Register configuration handling
    register_config_functions(runtime)
    
    # Register file I/O
    register_file_io_functions(runtime)
    
    # Register SQLite database
    register_sqlite_functions(runtime)
    
    # Register XML parsing
    register_xml_functions(runtime)
    
    # Register email/SMTP
    register_email_functions(runtime)
    
    # Register templates
    register_template_functions(runtime)
    
    # Register threading and multiprocessing
    register_threading_functions(runtime)
    
    # Register serialization (pickle, msgpack, yaml, toml)
    register_serialization_functions(runtime)
    
    # Register WebSocket support
    register_websocket_functions(runtime)
    
    # Register database connectors (PostgreSQL, MySQL, MongoDB)
    register_database_functions(runtime)
    
    # Register PDF utilities (reportlab, PyPDF2)
    register_pdf_functions(runtime)
    
    # Register image processing (PIL/Pillow)
    register_image_functions(runtime)
    
    # Register validation and sanitization
    register_validation_functions(runtime)
    
    # Register caching utilities
    register_cache_functions(runtime)
    
    # Register statistics and data analysis
    register_statistics_functions(runtime)
    
    # Register business logic and financial calculations
    register_business_functions(runtime)
    
    # Register data processing and analytics
    register_data_functions(runtime)
    
    # Register scientific computing and physics
    register_scientific_functions(runtime)
    
    # Register bit manipulation operations (ASM/C essential)
    register_bit_ops_functions(runtime)
    
    # Register character classification (ctype.h equivalent)
    register_ctype_functions(runtime)
    
    # Register numeric limits (limits.h/float.h equivalent)
    register_limits_functions(runtime)
    
    # Register algorithms (C++ STL <algorithm> equivalent)
    register_algorithms_functions(runtime)
    
    # Register error numbers (errno.h equivalent)
    register_errno_functions(runtime)
    
    # Register SIMD vector operations (MMX, SSE, AVX)
    register_simd_functions(runtime)
    
    # Register interrupt handling (x86 interrupts)
    register_interrupt_functions(runtime)
    
    # Register type traits (C++ <type_traits> equivalent)
    register_type_trait_functions(runtime)
    
    # Register hardware access (port I/O, MMIO, interrupts)
    register_hardware_functions(runtime)
    
    # Register atomic operations and memory ordering
    register_atomics_functions(runtime)

    # Register custom allocator control
    register_allocator_functions(runtime)

    # Register smart pointer functions (Rc, Arc, Weak, Box, RefCell, Mutex<T>, RwLock<T>)
    register_smart_pointer_functions(runtime)

    # Register native threading API
    register_native_threading_functions(runtime)
    
    # Register synchronization primitives
    register_sync_functions(runtime)

    # Register parallel computing functions
    register_parallel_functions(runtime)

    # Register OS kernel primitives
    register_kernel_functions(runtime)
    
    # Register module names for importing
    runtime.register_module("math")
    runtime.register_module("string")
    runtime.register_module("io")
    runtime.register_module("system")
    runtime.register_module("collections")
    runtime.register_module("network")
    runtime.register_module("types")
    runtime.register_module("asyncio")
    runtime.register_module("ffi")
    runtime.register_module("asm")
    runtime.register_module("testing")
    runtime.register_module("modules")
    runtime.register_module("filesystem")
    runtime.register_module("json")
    runtime.register_module("regex")
    runtime.register_module("datetime")
    runtime.register_module("http")
    runtime.register_module("crypto")
    runtime.register_module("uuid")
    runtime.register_module("random")
    runtime.register_module("compression")
    runtime.register_module("env")
    runtime.register_module("subprocess")
    runtime.register_module("math3d")
    runtime.register_module("camera")
    runtime.register_module("shaders")
    runtime.register_module("mesh")
    runtime.register_module("scene")
    runtime.register_module("logging")
    runtime.register_module("csv")
    runtime.register_module("path")
    runtime.register_module("signal")
    runtime.register_module("argparse")
    runtime.register_module("config")
    runtime.register_module("file_io")
    runtime.register_module("files")
    runtime.register_module("sqlite")
    runtime.register_module("database")
    runtime.register_module("xml")
    runtime.register_module("email")
    runtime.register_module("smtp")
    runtime.register_module("templates")
    runtime.register_module("testing")
    runtime.register_module("hardware")
    runtime.register_module("port_io")
    runtime.register_module("atomics")
    runtime.register_module("atomic")
    runtime.register_module("allocators")
    runtime.register_module("allocator")
    runtime.register_module("smart_pointers")
    runtime.register_module("smart_pointer")
    runtime.register_module("threading")
    runtime.register_module("threads")
    runtime.register_module("sync")
    runtime.register_module("synchronization")
    runtime.register_module("business")
    runtime.register_module("data")
    runtime.register_module("scientific") 