"""
NLPL Security Module

This package provides comprehensive security features for NLPL including:
- Permission system (Deno-inspired)
- Path validation and sanitization
- Safe subprocess execution
- Input validation utilities
- Output sanitization
- Memory safety checks

The security model is deny-by-default: all dangerous operations require
explicit permission grants via command-line flags or runtime API.
"""

from nlpl.security.permissions import (
    PermissionType,
    Permission,
    PermissionManager,
    PermissionDeniedError,
    parse_permission_flags,
    get_permission_manager,
    set_permission_manager,
)

from nlpl.security.utils import (
    SecurityError,
    PathTraversalError,
    CommandInjectionError,
    ValidationError,
    normalize_path,
    validate_path,
    is_safe_path,
    get_safe_filename,
    safe_execute,
    validate_email,
    validate_url,
    validate_integer,
    sanitize_sql_identifier,
    escape_html,
    escape_shell_arg,
    is_safe_regex,
    check_rate_limit,
)

__all__ = [
    # Permission system
    'PermissionType',
    'Permission',
    'PermissionManager',
    'PermissionDeniedError',
    'parse_permission_flags',
    'get_permission_manager',
    'set_permission_manager',
    
    # Security utilities
    'SecurityError',
    'PathTraversalError',
    'CommandInjectionError',
    'ValidationError',
    'normalize_path',
    'validate_path',
    'is_safe_path',
    'get_safe_filename',
    'safe_execute',
    'validate_email',
    'validate_url',
    'validate_integer',
    'sanitize_sql_identifier',
    'escape_html',
    'escape_shell_arg',
    'is_safe_regex',
    'check_rate_limit',
]

__version__ = '1.0.0'
