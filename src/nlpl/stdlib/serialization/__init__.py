"""
Serialization utilities for NLPL.

Provides:
- Pickle serialization (Python objects)
- JSON serialization (already in json_utils)
- MessagePack serialization (binary JSON)
- YAML serialization
- TOML serialization
- Protocol Buffers serialization (google.protobuf Struct encoding)
"""

import pickle
import json
from typing import Any
import os

# Optional imports with fallbacks
try:
    import msgpack
    HAS_MSGPACK = True
except ImportError:
    HAS_MSGPACK = False

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

try:
    import toml
    HAS_TOML = True
except ImportError:
    HAS_TOML = False

try:
    from google.protobuf.struct_pb2 import Struct as _PbStruct
    from google.protobuf.json_format import MessageToDict as _pb_to_dict, ParseDict as _pb_parse_dict
    HAS_PROTOBUF = True
except ImportError:
    HAS_PROTOBUF = False


def pickle_dumps(obj: Any) -> bytes:
    """Serialize object to bytes using pickle.
    
    Args:
        obj: Object to serialize
        
    Returns:
        Serialized bytes
    """
    return pickle.dumps(obj)


def pickle_loads(data: bytes) -> Any:
    """Deserialize object from bytes using pickle.
    
    Args:
        data: Serialized bytes
        
    Returns:
        Deserialized object
    """
    return pickle.loads(data)


def pickle_dump_file(obj: Any, filepath: str) -> bool:
    """Serialize object to file using pickle.
    
    Args:
        obj: Object to serialize
        filepath: Path to output file
        
    Returns:
        True if successful
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        
        with open(filepath, 'wb') as f:
            pickle.dump(obj, f)
        return True
    except Exception:
        return False


def pickle_load_file(filepath: str) -> Any:
    """Deserialize object from file using pickle.
    
    Args:
        filepath: Path to input file
        
    Returns:
        Deserialized object
    """
    with open(filepath, 'rb') as f:
        return pickle.load(f)


def msgpack_dumps(obj: Any) -> bytes:
    """Serialize object to bytes using MessagePack.
    
    Args:
        obj: Object to serialize
        
    Returns:
        Serialized bytes
    """
    if not HAS_MSGPACK:
        raise ImportError("msgpack is not installed. Install with: pip install msgpack")
    
    return msgpack.packb(obj, use_bin_type=True)


def msgpack_loads(data: bytes) -> Any:
    """Deserialize object from bytes using MessagePack.
    
    Args:
        data: Serialized bytes
        
    Returns:
        Deserialized object
    """
    if not HAS_MSGPACK:
        raise ImportError("msgpack is not installed. Install with: pip install msgpack")
    
    return msgpack.unpackb(data, raw=False)


def msgpack_dump_file(obj: Any, filepath: str) -> bool:
    """Serialize object to file using MessagePack.
    
    Args:
        obj: Object to serialize
        filepath: Path to output file
        
    Returns:
        True if successful
    """
    if not HAS_MSGPACK:
        raise ImportError("msgpack is not installed. Install with: pip install msgpack")
    
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        
        with open(filepath, 'wb') as f:
            msgpack.pack(obj, f, use_bin_type=True)
        return True
    except Exception:
        return False


def msgpack_load_file(filepath: str) -> Any:
    """Deserialize object from file using MessagePack.
    
    Args:
        filepath: Path to input file
        
    Returns:
        Deserialized object
    """
    if not HAS_MSGPACK:
        raise ImportError("msgpack is not installed. Install with: pip install msgpack")
    
    with open(filepath, 'rb') as f:
        return msgpack.unpack(f, raw=False)


def yaml_dumps(obj: Any) -> str:
    """Serialize object to YAML string.
    
    Args:
        obj: Object to serialize
        
    Returns:
        YAML string
    """
    if not HAS_YAML:
        raise ImportError("PyYAML is not installed. Install with: pip install pyyaml")
    
    return yaml.dump(obj, default_flow_style=False)


def yaml_loads(data: str) -> Any:
    """Deserialize object from YAML string.
    
    Args:
        data: YAML string
        
    Returns:
        Deserialized object
    """
    if not HAS_YAML:
        raise ImportError("PyYAML is not installed. Install with: pip install pyyaml")
    
    return yaml.safe_load(data)


def yaml_dump_file(obj: Any, filepath: str) -> bool:
    """Serialize object to YAML file.
    
    Args:
        obj: Object to serialize
        filepath: Path to output file
        
    Returns:
        True if successful
    """
    if not HAS_YAML:
        raise ImportError("PyYAML is not installed. Install with: pip install pyyaml")
    
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        
        with open(filepath, 'w') as f:
            yaml.dump(obj, f, default_flow_style=False)
        return True
    except Exception:
        return False


def yaml_load_file(filepath: str) -> Any:
    """Deserialize object from YAML file.
    
    Args:
        filepath: Path to input file
        
    Returns:
        Deserialized object
    """
    if not HAS_YAML:
        raise ImportError("PyYAML is not installed. Install with: pip install pyyaml")
    
    with open(filepath, 'r') as f:
        return yaml.safe_load(f)


def toml_dumps(obj: dict) -> str:
    """Serialize dictionary to TOML string.
    
    Args:
        obj: Dictionary to serialize
        
    Returns:
        TOML string
    """
    if not HAS_TOML:
        raise ImportError("toml is not installed. Install with: pip install toml")
    
    return toml.dumps(obj)


def toml_loads(data: str) -> dict:
    """Deserialize dictionary from TOML string.
    
    Args:
        data: TOML string
        
    Returns:
        Deserialized dictionary
    """
    if not HAS_TOML:
        raise ImportError("toml is not installed. Install with: pip install toml")
    
    return toml.loads(data)


def toml_dump_file(obj: dict, filepath: str) -> bool:
    """Serialize dictionary to TOML file.
    
    Args:
        obj: Dictionary to serialize
        filepath: Path to output file
        
    Returns:
        True if successful
    """
    if not HAS_TOML:
        raise ImportError("toml is not installed. Install with: pip install toml")
    
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        
        with open(filepath, 'w') as f:
            toml.dump(obj, f)
        return True
    except Exception:
        return False


def toml_load_file(filepath: str) -> dict:
    """Deserialize dictionary from TOML file.
    
    Args:
        filepath: Path to input file
        
    Returns:
        Deserialized dictionary
    """
    if not HAS_TOML:
        raise ImportError("toml is not installed. Install with: pip install toml")
    
    with open(filepath, 'r') as f:
        return toml.load(f)


def protobuf_dumps(obj: dict) -> bytes:
    """Serialize dictionary to Protocol Buffers bytes using Struct encoding.

    Args:
        obj: Dictionary to serialize (values must be JSON-compatible types)

    Returns:
        Serialized bytes
    """
    if not HAS_PROTOBUF:
        raise ImportError("protobuf is not installed. Install with: pip install protobuf")
    s = _PbStruct()
    _pb_parse_dict(obj, s)
    return s.SerializeToString()


def protobuf_loads(data: bytes) -> dict:
    """Deserialize dictionary from Protocol Buffers bytes.

    Args:
        data: Serialized bytes produced by protobuf_dumps

    Returns:
        Deserialized dictionary
    """
    if not HAS_PROTOBUF:
        raise ImportError("protobuf is not installed. Install with: pip install protobuf")
    s = _PbStruct()
    s.ParseFromString(data)
    return _pb_to_dict(s)


def protobuf_dump_file(obj: dict, filepath: str) -> bool:
    """Serialize dictionary to Protocol Buffers binary file.

    Args:
        obj: Dictionary to serialize
        filepath: Path to output file

    Returns:
        True on success, False on failure
    """
    if not HAS_PROTOBUF:
        raise ImportError("protobuf is not installed. Install with: pip install protobuf")
    try:
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with open(filepath, 'wb') as f:
            f.write(protobuf_dumps(obj))
        return True
    except Exception:
        return False


def protobuf_load_file(filepath: str) -> dict:
    """Deserialize dictionary from Protocol Buffers binary file.

    Args:
        filepath: Path to input file

    Returns:
        Deserialized dictionary
    """
    if not HAS_PROTOBUF:
        raise ImportError("protobuf is not installed. Install with: pip install protobuf")
    with open(filepath, 'rb') as f:
        return protobuf_loads(f.read())


def register_serialization_functions(runtime):
    """Register serialization functions with the NLPL runtime."""
    # Pickle serialization
    runtime.register_function("pickle_dumps", pickle_dumps)
    runtime.register_function("pickle_loads", pickle_loads)
    runtime.register_function("pickle_dump_file", pickle_dump_file)
    runtime.register_function("pickle_load_file", pickle_load_file)

    # MessagePack serialization (if available)
    if HAS_MSGPACK:
        runtime.register_function("msgpack_dumps", msgpack_dumps)
        runtime.register_function("msgpack_loads", msgpack_loads)
        runtime.register_function("msgpack_dump_file", msgpack_dump_file)
        runtime.register_function("msgpack_load_file", msgpack_load_file)

    # YAML serialization (if available)
    if HAS_YAML:
        runtime.register_function("yaml_dumps", yaml_dumps)
        runtime.register_function("yaml_loads", yaml_loads)
        runtime.register_function("yaml_dump_file", yaml_dump_file)
        runtime.register_function("yaml_load_file", yaml_load_file)

    # TOML serialization (if available)
    if HAS_TOML:
        runtime.register_function("toml_dumps", toml_dumps)
        runtime.register_function("toml_loads", toml_loads)
        runtime.register_function("toml_dump_file", toml_dump_file)
        runtime.register_function("toml_load_file", toml_load_file)

    # Protocol Buffers serialization (if available)
    if HAS_PROTOBUF:
        runtime.register_function("protobuf_dumps", protobuf_dumps)
        runtime.register_function("protobuf_loads", protobuf_loads)
        runtime.register_function("protobuf_dump_file", protobuf_dump_file)
        runtime.register_function("protobuf_load_file", protobuf_load_file)
