"""
Type system for the NLPL language.
This package provides type checking and type inference functionality.
"""

from ..typesystem.types import (
    Type, PrimitiveType, ListType, DictionaryType, ClassType, 
    FunctionType, UnionType, AnyType,
    INTEGER_TYPE, FLOAT_TYPE, STRING_TYPE, BOOLEAN_TYPE, NULL_TYPE, ANY_TYPE,
    get_type_by_name, infer_type
)
from ..typesystem.typechecker import TypeChecker, TypeEnvironment, TypeCheckError 