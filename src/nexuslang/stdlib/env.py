"""
Environment variables module for the NexusLang standard library.
Provides functions for reading, writing, and querying environment variables.
"""

import os
from ..runtime.runtime import Runtime


def register_env_functions(runtime: Runtime) -> None:
    """Register environment variable functions with the runtime."""
    runtime.register_function("env_get", env_get)
    runtime.register_function("env_set", env_set)
    runtime.register_function("env_unset", env_unset)
    runtime.register_function("env_has", env_has)
    runtime.register_function("env_all", env_all)
    runtime.register_function("env_expand", env_expand)


def env_get(name, default=None):
    """Return the value of environment variable *name*, or *default* if unset."""
    return os.environ.get(str(name), default)


def env_set(name, value):
    """Set environment variable *name* to *value*."""
    os.environ[str(name)] = str(value)
    return True


def env_unset(name):
    """Remove environment variable *name* if it exists."""
    os.environ.pop(str(name), None)
    return True


def env_has(name):
    """Return True if environment variable *name* is set."""
    return str(name) in os.environ


def env_all():
    """Return a copy of the current environment as a plain dictionary."""
    return dict(os.environ)


def env_expand(template):
    """Expand environment variable references (``$VAR`` / ``${VAR}``) in *template*."""
    return os.path.expandvars(str(template))
