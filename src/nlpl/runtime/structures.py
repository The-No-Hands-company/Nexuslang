"""
Runtime support for low-level Structs and Unions in NLPL.

This module implements:
- Memory layout calculation (size, alignment, padding)
- Byte-array backed storage for Structs and Unions
- Type conversion to/from bytes using Python's `struct` module
"""

import struct
from typing import Dict, List, Any, Tuple, Optional
from enum import Enum

class PrimitiveType(Enum):
    INTEGER = 'q'  # 8 bytes (int64)
    FLOAT = 'd'    # 8 bytes (double)
    BOOLEAN = '?'  # 1 byte
    BYTE = 'b'     # 1 byte
    CHAR = 'c'     # 1 byte
    POINTER = 'Q'  # 8 bytes (unsigned int64 for IDs/addresses)

    @property
    def size(self) -> int:
        return struct.calcsize(self.value)

class Field:
    def __init__(self, name: str, type_code: str, offset: int, size: int):
        self.name = name
        self.type_code = type_code
        self.offset = offset
        self.size = size

class StructureDefinition:
    """Base class for Struct and Union definitions."""
    def __init__(self, name: str, fields: List[Tuple[str, str]]):
        self.name = name
        self.fields: Dict[str, Field] = {}
        self.size = 0
        self.alignment = 1
        self._calculate_layout(fields)

    def _get_type_info(self, type_name: str) -> Tuple[str, int, int]:
        """Returns (struct_format_char, size, alignment) for a given type name."""
        type_name = type_name.lower()
        if type_name in ('integer', 'int'):
            return PrimitiveType.INTEGER.value, 8, 8
        elif type_name in ('float', 'double'):
            return PrimitiveType.FLOAT.value, 8, 8
        elif type_name in ('boolean', 'bool'):
            return PrimitiveType.BOOLEAN.value, 1, 1
        elif type_name == 'byte':
            return PrimitiveType.BYTE.value, 1, 1
        elif type_name == 'char':
            return PrimitiveType.CHAR.value, 1, 1
        else:
            # Treat everything else as a pointer/reference (Object ID)
            return PrimitiveType.POINTER.value, 8, 8

    def _calculate_layout(self, fields: List[Tuple[str, str]]):
        raise NotImplementedError

class StructDefinition(StructureDefinition):
    """
    Defines a C-style struct layout including padding.
    """
    def _calculate_layout(self, fields: List[Tuple[str, str]]):
        current_offset = 0
        max_alignment = 1

        for name, type_name in fields:
            fmt, size, align = self._get_type_info(type_name)
            
            # Add padding for alignment
            padding = (align - (current_offset % align)) % align
            current_offset += padding
            
            self.fields[name] = Field(name, fmt, current_offset, size)
            current_offset += size
            
            max_alignment = max(max_alignment, align)

        # Structure end padding
        padding = (max_alignment - (current_offset % max_alignment)) % max_alignment
        self.size = current_offset + padding
        self.alignment = max_alignment

class UnionDefinition(StructureDefinition):
    """
    Defines a C-style union layout (all fields at offset 0).
    """
    def _calculate_layout(self, fields: List[Tuple[str, str]]):
        max_size = 0
        max_alignment = 1

        for name, type_name in fields:
            fmt, size, align = self._get_type_info(type_name)
            # All fields at offset 0
            self.fields[name] = Field(name, fmt, 0, size)
            
            max_size = max(max_size, size)
            max_alignment = max(max_alignment, align)

        # Union size is size of largest member, aligned
        padding = (max_alignment - (max_size % max_alignment)) % max_alignment
        self.size = max_size + padding
        self.alignment = max_alignment

class StructureInstance:
    """Instance of a Struct or Union, backed by a bytearray."""
    def __init__(self, definition: StructureDefinition):
        self.definition = definition
        self.memory = bytearray(definition.size)

    def get_field(self, name: str) -> Any:
        field = self.definition.fields.get(name)
        if not field:
            raise AttributeError(f"'{self.definition.name}' has no field '{name}'")
        
        # Unpack from memory
        try:
            val = struct.unpack_from(field.type_code, self.memory, field.offset)[0]
            
            # Convert bytes to char if needed (struct returns byte string for 'c')
            if field.type_code == 'c':
                return val.decode('ascii')
            return val
        except struct.error as e:
            raise RuntimeError(f"Memory corruption reading field '{name}': {e}")

    def set_field(self, name: str, value: Any) -> None:
        field = self.definition.fields.get(name)
        if not field:
            raise AttributeError(f"'{self.definition.name}' has no field '{name}'")
        
        # Pack to memory
        try:
            # Handle char encoding
            if field.type_code == 'c' and isinstance(value, str):
                value = value.encode('ascii')
                
            struct.pack_into(field.type_code, self.memory, field.offset, value)
        except struct.error as e:
            raise TypeError(f"Invalid value for field '{name}' (type {field.type_code}): {e}")

    def __repr__(self):
        fields_str = ", ".join(f"{name}={self.get_field(name)}" for name in self.definition.fields)
        return f"{self.definition.name}({fields_str})"
