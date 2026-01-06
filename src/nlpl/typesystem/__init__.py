"""
Type system for the NLPL language.
This package provides type checking and type inference functionality.
"""

from ..typesystem.types import (
    Type, PrimitiveType, ListType, DictionaryType, ClassType, 
    FunctionType, UnionType, AnyType, GenericType, GenericParameter,
    INTEGER_TYPE, FLOAT_TYPE, STRING_TYPE, BOOLEAN_TYPE, NULL_TYPE, ANY_TYPE,
    get_type_by_name, infer_type
)
from ..typesystem.typechecker import TypeChecker, TypeEnvironment, TypeCheckError
from ..typesystem.type_inference import TypeInferenceEngine
from ..typesystem.generic_types import GenericTypeRegistry, GenericTypeContext
from ..typesystem.user_types import TypeRegistry
from ..typesystem.integration_enhanced import IntegratedTypeSystem, get_type_system, reset_type_system

__all__ = [
    # Core types
    'Type', 'PrimitiveType', 'ListType', 'DictionaryType', 'ClassType',
    'FunctionType', 'UnionType', 'AnyType', 'GenericType', 'GenericParameter',
    # Built-in type instances
    'INTEGER_TYPE', 'FLOAT_TYPE', 'STRING_TYPE', 'BOOLEAN_TYPE', 'NULL_TYPE', 'ANY_TYPE',
    # Type utilities
    'get_type_by_name', 'infer_type',
    # Type checking
    'TypeChecker', 'TypeEnvironment', 'TypeCheckError',
    # Type inference
    'TypeInferenceEngine',
    # Generic types
    'GenericTypeRegistry', 'GenericTypeContext',
    # User-defined types
    'TypeRegistry',
    # Integrated system
    'IntegratedTypeSystem', 'get_type_system', 'reset_type_system',
] 