"""
IO module for the NLPL standard library.
This module provides input/output functions for file operations.
"""

import os
import json
import shutil
from ...runtime.runtime import Runtime

def register_io_functions(runtime: Runtime) -> None:
    """Register IO functions with the runtime."""
    # File operations
    runtime.register_function("read_file", read_file)
    runtime.register_function("write_file", write_file)
    runtime.register_function("append_file", append_file)
    runtime.register_function("file_exists", file_exists)
    runtime.register_function("delete_file", delete_file)
    runtime.register_function("copy_file", copy_file)
    runtime.register_function("move_file", move_file)
    runtime.register_function("get_file_size", get_file_size)
    runtime.register_function("read_lines", read_lines)
    runtime.register_function("write_lines", write_lines)
    runtime.register_function("read_bytes", read_bytes)
    runtime.register_function("write_bytes", write_bytes)
    
    # Directory operations
    runtime.register_function("list_directory", list_directory)
    runtime.register_function("create_directory", create_directory)
    runtime.register_function("directory_exists", directory_exists)
    runtime.register_function("delete_directory", delete_directory)
    runtime.register_function("walk_directory", walk_directory)
    
    # Path operations
    runtime.register_function("join_path", join_path)
    runtime.register_function("get_basename", get_basename)
    runtime.register_function("get_dirname", get_dirname)
    runtime.register_function("get_extension", get_extension)
    runtime.register_function("absolute_path", absolute_path)
    runtime.register_function("normalize_path", normalize_path)
    
    # JSON operations
    runtime.register_function("parse_json", parse_json)
    runtime.register_function("stringify_json", stringify_json)
    
    # Console operations
    runtime.register_function("print", print_to_console)
    runtime.register_function("println", print_to_console)  # Alias
    runtime.register_function("input", get_input)
    runtime.register_function("read_input", get_input)  # Alias

# File operations
def read_file(path, encoding="utf-8"):
    """Read the contents of a file."""
    if not os.path.isfile(path):
        raise FileNotFoundError(f"File not found: {path}")
    
    with open(path, "r", encoding=encoding) as f:
        return f.read()

def write_file(path, content, encoding="utf-8"):
    """Write content to a file, overwriting any existing content."""
    with open(path, "w", encoding=encoding) as f:
        f.write(content)
    return True

def append_file(path, content, encoding="utf-8"):
    """Append content to a file."""
    with open(path, "a", encoding=encoding) as f:
        f.write(content)
    return True

def file_exists(path):
    """Check if a file exists."""
    return os.path.isfile(path)

def delete_file(path):
    """Delete a file."""
    if not os.path.isfile(path):
        raise FileNotFoundError(f"File not found: {path}")
    
    os.remove(path)
    return True

# Directory operations
def list_directory(path="."):
    """List the contents of a directory."""
    if not os.path.isdir(path):
        raise NotADirectoryError(f"Not a directory: {path}")
    
    return os.listdir(path)

def create_directory(path, exist_ok=True):
    """Create a directory."""
    os.makedirs(path, exist_ok=exist_ok)
    return True

def directory_exists(path):
    """Check if a directory exists."""
    return os.path.isdir(path)

def delete_directory(path, recursive=True):
    """Delete a directory."""
    if not os.path.isdir(path):
        raise NotADirectoryError(f"Not a directory: {path}")
    
    if recursive:
        shutil.rmtree(path)
    else:
        os.rmdir(path)
    
    return True

# Path operations
def join_path(*paths):
    """Join path components."""
    return os.path.join(*paths)

def get_basename(path):
    """Get the base name of a path."""
    return os.path.basename(path)

def get_dirname(path):
    """Get the directory name of a path."""
    return os.path.dirname(path)

def get_extension(path):
    """Get the file extension of a path."""
    return os.path.splitext(path)[1]

# JSON operations
def parse_json(json_str):
    """Parse a JSON string into an object."""
    return json.loads(json_str)

def stringify_json(obj, indent=None):
    """Convert an object to a JSON string."""
    return json.dumps(obj, indent=indent)

# Console operations
def print_to_console(*args, sep=" ", end="\n"):
    """Print to the console."""
    print(*args, sep=sep, end=end)
    return None

def get_input(prompt=""):
    """Get input from the user."""
    return input(prompt)

# Additional file operations

def copy_file(source, destination):
    """Copy a file from source to destination."""
    try:
        shutil.copy2(source, destination)
        return True
    except Exception as e:
        raise RuntimeError(f"Error copying file from '{source}' to '{destination}': {str(e)}")

def move_file(source, destination):
    """Move/rename a file from source to destination."""
    try:
        shutil.move(source, destination)
        return True
    except Exception as e:
        raise RuntimeError(f"Error moving file from '{source}' to '{destination}': {str(e)}")

def get_file_size(file_path):
    """Get the size of a file in bytes."""
    try:
        return os.path.getsize(file_path)
    except Exception as e:
        raise RuntimeError(f"Error getting file size for '{file_path}': {str(e)}")

def read_lines(file_path, encoding="utf-8"):
    """Read file contents as a list of lines."""
    try:
        with open(file_path, "r", encoding=encoding) as file:
            return file.readlines()
    except Exception as e:
        raise RuntimeError(f"Error reading lines from '{file_path}': {str(e)}")

def write_lines(file_path, lines, encoding="utf-8"):
    """Write a list of lines to a file."""
    try:
        with open(file_path, "w", encoding=encoding) as file:
            file.writelines(lines)
        return True
    except Exception as e:
        raise RuntimeError(f"Error writing lines to '{file_path}': {str(e)}")

def read_bytes(file_path):
    """Read file contents as bytes."""
    try:
        with open(file_path, "rb") as file:
            return file.read()
    except Exception as e:
        raise RuntimeError(f"Error reading bytes from '{file_path}': {str(e)}")

def write_bytes(file_path, data):
    """Write bytes to a file."""
    try:
        with open(file_path, "wb") as file:
            file.write(data)
        return True
    except Exception as e:
        raise RuntimeError(f"Error writing bytes to '{file_path}': {str(e)}")

def walk_directory(directory_path):
    """Walk through directory tree, returning (dirpath, dirnames, filenames) tuples."""
    try:
        results = []
        for dirpath, dirnames, filenames in os.walk(directory_path):
            results.append({
                "path": dirpath,
                "directories": dirnames,
                "files": filenames
            })
        return results
    except Exception as e:
        raise RuntimeError(f"Error walking directory '{directory_path}': {str(e)}")

def absolute_path(path):
    """Get the absolute path of a file or directory."""
    return os.path.abspath(path)

def normalize_path(path):
    """Normalize a path (resolve .. and . components)."""
    return os.path.normpath(path)
