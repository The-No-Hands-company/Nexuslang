"""
Built-in decorators for NLPL.
Provides common decorator implementations like @memoize, @deprecated, @async.
"""

import functools
import warnings
from typing import Callable, Any, Dict


def memoize(func: Callable) -> Callable:
    """Memoization decorator - caches function results."""
    cache: Dict[tuple, Any] = {}
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        key = (args, tuple(sorted(kwargs.items())))
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    
    wrapper.cache = cache
    wrapper.cache_clear = cache.clear
    return wrapper


def deprecated(message: str = None):
    """Deprecation warning decorator."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            warning_msg = f"Function '{func.__name__}' is deprecated"
            if message:
                warning_msg += f": {message}"
            warnings.warn(warning_msg, DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)
        return wrapper
    
    if callable(message):
        func = message
        return deprecated(None)(func)
    
    return decorator


def trace(func: Callable) -> Callable:
    """Trace decorator - prints function calls and returns."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        args_str = ", ".join(repr(arg) for arg in args)
        kwargs_str = ", ".join(f"{k}={v!r}" for k, v in kwargs.items())
        all_args = ", ".join(filter(None, [args_str, kwargs_str]))
        
        print(f"Calling {func.__name__}({all_args})")
        result = func(*args, **kwargs)
        print(f"{func.__name__} returned {result!r}")
        return result
    
    return wrapper


def timer(func: Callable) -> Callable:
    """Timer decorator - measures execution time."""
    import time
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        execution_time = (end_time - start_time) * 1000
        print(f"{func.__name__} executed in {execution_time:.2f}ms")
        return result
    
    return wrapper


def retry(max_attempts: int = 3):
    """Retry decorator - retries function on exception."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    print(f"Attempt {attempt + 1}/{max_attempts} failed: {e}")
            return None
        return wrapper
    return decorator


def validate_args(**validators):
    """Argument validation decorator."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
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


BUILTIN_DECORATORS = {
    "memoize": memoize,
    "deprecated": deprecated,
    "trace": trace,
    "timer": timer,
    "retry": retry,
    "validate_args": validate_args,
}


def get_decorator(decorator_name: str):
    """Get a decorator function by name."""
    return BUILTIN_DECORATORS.get(decorator_name)
