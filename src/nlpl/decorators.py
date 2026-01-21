"""
Built-in decorators for NLPL.
Provides common decorator implementations like @memoize, @deprecated, @async.
"""

import functools
import warnings
from typing import Callable, Any, Dict

def memoize(func: Callable) -> Callable:
 """Memoization decorator - caches function results.
 
 Example:
 @memoize
 function fibonacci with n as Integer returns Integer
 if n is less than 2
 return n
 return fibonacci(n minus 1) plus fibonacci(n minus 2)
 """
 cache: Dict[tuple, Any] = {}
 
 @functools.wraps(func)
 def wrapper(*args, **kwargs):
 # Create cache key from arguments
 key = (args, tuple(sorted(kwargs.items())))
 
 if key not in cache:
 cache[key] = func(*args, **kwargs)
 return cache[key]
 
 # Attach cache for inspection
 wrapper.cache = cache
 wrapper.cache_clear = cache.clear
 return wrapper

def deprecated(message: str = None):
 """Deprecation warning decorator.
 
 Example:
 @deprecated with message "Use new_function instead"
 function old_function
 print text "Old implementation"
 """
 def decorator(func: Callable) -> Callable:
 @functools.wraps(func)
 def wrapper(*args, **kwargs):
 warning_msg = f"Function '{func.__name__}' is deprecated"
 if message:
 warning_msg += f": {message}"
 warnings.warn(warning_msg, DeprecationWarning, stacklevel=2)
 return func(*args, **kwargs)
 return wrapper
 
 # If called without arguments, message will be the function
 if callable(message):
 func = message
 return deprecated(None)(func)
 
 return decorator

def trace(func: Callable) -> Callable:
 """Trace decorator - prints function calls and returns.
 
 Example:
 @trace
 function calculate with x as Integer returns Integer
 return x times 2
 """
 @functools.wraps(func)
 def wrapper(*args, **kwargs):
 args_str = ", ".join(repr(arg) for arg in args)
 kwargs_str = ", ".join(f"{k}={v!r}" for k, v in kwargs.items())
 all_args = ", ".join(filter(None, [args_str, kwargs_str]))
 
 print(f" Calling {func.__name__}({all_args})")
 result = func(*args, **kwargs)
 print(f" {func.__name__} returned {result!r}")
 return result
 
 return wrapper

def timer(func: Callable) -> Callable:
 """Timer decorator - measures execution time.
 
 Example:
 @timer
 function slow_operation
 # ... expensive computation
 """
 import time
 
 @functools.wraps(func)
 def wrapper(*args, **kwargs):
 start_time = time.perf_counter()
 result = func(*args, **kwargs)
 end_time = time.perf_counter()
 execution_time = (end_time - start_time) * 1000 # Convert to ms
 print(f" {func.__name__} executed in {execution_time:.2f}ms")
 return result
 
 return wrapper

def retry(max_attempts: int = 3):
 """Retry decorator - retries function on exception.
 
 Example:
 @retry with max_attempts 5
 function unreliable_operation
 # ... may fail
 """
 def decorator(func: Callable) -> Callable:
 @functools.wraps(func)
 def wrapper(*args, **kwargs):
 for attempt in range(max_attempts):
 try:
 return func(*args, **kwargs)
 except Exception as e:
 if attempt == max_attempts - 1:
 raise
 print(f" Attempt {attempt + 1}/{max_attempts} failed: {e}")
 return None
 return wrapper
 return decorator

def validate_args(**validators):
 """Argument validation decorator.
 
 Example:
 @validate_args with x "positive", y "non_zero"
 function divide with x, y
 return x divided by y
 """
 def decorator(func: Callable) -> Callable:
 @functools.wraps(func)
 def wrapper(*args, **kwargs):
 # Simple validation logic
 for arg_name, validator in validators.items():
 if arg_name in kwargs:
 value = kwargs[arg_name]
 if validator == "positive" and value <= 0:
 raise ValueError(f"{arg_name} must be positive")
 elif validator == "non_zero" and value == 0:
 raise ValueError(f"{arg_name} must not be zero")
 return func(*args, **kwargs)
 return wrapper
 return decorator

# Decorator registry for NLPL interpreter
BUILTIN_DECORATORS = {
 "memoize": memoize,
 "deprecated": deprecated,
 "trace": trace,
 "timer": timer,
 "retry": retry,
 "validate_args": validate_args,
}

def apply_decorator(func: Callable, decorator_name: str, arguments: list) -> Callable:
 """Apply a decorator to a function.
 
 Args:
 func: The function to decorate
 decorator_name: Name of the decorator
 arguments: List of (key, value) tuples for decorator arguments
 
 Returns:
 The decorated function
 """
 if decorator_name not in BUILTIN_DECORATORS:
 raise ValueError(f"Unknown decorator: @{decorator_name}")
 
 decorator = BUILTIN_DECORATORS[decorator_name]
 
 # Handle decorators with arguments
 if arguments and decorator_name in ("deprecated", "retry", "validate_args"):
 # Extract arguments
 if decorator_name == "deprecated":
 message = next((v for k, v in arguments if k == "message"), None)
 return decorator(message)(func)
 elif decorator_name == "retry":
 max_attempts = next((v for k, v in arguments if k == "max_attempts"), 3)
 return decorator(max_attempts)(func)
 elif decorator_name == "validate_args":
 validators = {k: v for k, v in arguments}
 return decorator(**validators)(func)
 
 # Decorators without arguments
 return decorator(func)
