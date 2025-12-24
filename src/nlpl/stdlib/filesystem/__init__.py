"""
File System Operations for NLPL.
Provides file and directory manipulation capabilities.
"""

import os
import shutil
from pathlib import Path
from typing import List, Optional, Any
from ...runtime.runtime import Runtime


def read_file(filepath: str, encoding: str = 'utf-8') -> str:
    """Read entire file contents as string."""
    with open(filepath, 'r', encoding=encoding) as f:
        return f.read()


def read_lines(filepath: str, encoding: str = 'utf-8') -> List[str]:
    """Read file as list of lines."""
    with open(filepath, 'r', encoding=encoding) as f:
        return f.readlines()


def read_bytes(filepath: str) -> bytes:
    """Read file as raw bytes."""
    with open(filepath, 'rb') as f:
        return f.read()


def write_file(filepath: str, content: str, encoding: str = 'utf-8') -> bool:
    """Write string content to file (overwrites)."""
    try:
        # Create parent directories if they don't exist
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding=encoding) as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Error writing file: {e}")
        return False


def append_file(filepath: str, content: str, encoding: str = 'utf-8') -> bool:
    """Append string content to file."""
    try:
        with open(filepath, 'a', encoding=encoding) as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Error appending to file: {e}")
        return False


def write_bytes(filepath: str, data: bytes) -> bool:
    """Write raw bytes to file."""
    try:
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'wb') as f:
            f.write(data)
        return True
    except Exception as e:
        print(f"Error writing bytes: {e}")
        return False


def file_exists(filepath: str) -> bool:
    """Check if file exists."""
    return os.path.isfile(filepath)


def dir_exists(dirpath: str) -> bool:
    """Check if directory exists."""
    return os.path.isdir(dirpath)


def path_exists(path: str) -> bool:
    """Check if path exists (file or directory)."""
    return os.path.exists(path)


def create_dir(dirpath: str, parents: bool = True) -> bool:
    """Create directory (and parents if needed)."""
    try:
        Path(dirpath).mkdir(parents=parents, exist_ok=True)
        return True
    except Exception as e:
        print(f"Error creating directory: {e}")
        return False


def delete_file(filepath: str) -> bool:
    """Delete a file."""
    try:
        os.remove(filepath)
        return True
    except Exception as e:
        print(f"Error deleting file: {e}")
        return False


def delete_dir(dirpath: str, recursive: bool = False) -> bool:
    """Delete a directory."""
    try:
        if recursive:
            shutil.rmtree(dirpath)
        else:
            os.rmdir(dirpath)
        return True
    except Exception as e:
        print(f"Error deleting directory: {e}")
        return False


def copy_file(src: str, dst: str) -> bool:
    """Copy a file."""
    try:
        shutil.copy2(src, dst)
        return True
    except Exception as e:
        print(f"Error copying file: {e}")
        return False


def move_file(src: str, dst: str) -> bool:
    """Move/rename a file."""
    try:
        shutil.move(src, dst)
        return True
    except Exception as e:
        print(f"Error moving file: {e}")
        return False


def list_dir(dirpath: str) -> List[str]:
    """List directory contents."""
    try:
        return os.listdir(dirpath)
    except Exception as e:
        print(f"Error listing directory: {e}")
        return []


def list_files(dirpath: str, pattern: str = "*") -> List[str]:
    """List files in directory matching pattern."""
    try:
        path = Path(dirpath)
        return [str(p) for p in path.glob(pattern) if p.is_file()]
    except Exception as e:
        print(f"Error listing files: {e}")
        return []


def list_dirs(dirpath: str) -> List[str]:
    """List subdirectories in directory."""
    try:
        path = Path(dirpath)
        return [str(p) for p in path.iterdir() if p.is_dir()]
    except Exception as e:
        print(f"Error listing directories: {e}")
        return []


def get_file_size(filepath: str) -> int:
    """Get file size in bytes."""
    try:
        return os.path.getsize(filepath)
    except Exception as e:
        print(f"Error getting file size: {e}")
        return -1


def get_file_info(filepath: str) -> dict:
    """Get file metadata."""
    try:
        stat = os.stat(filepath)
        return {
            'size': stat.st_size,
            'modified': stat.st_mtime,
            'accessed': stat.st_atime,
            'created': stat.st_ctime,
            'is_file': os.path.isfile(filepath),
            'is_dir': os.path.isdir(filepath),
            'is_link': os.path.islink(filepath),
        }
    except Exception as e:
        print(f"Error getting file info: {e}")
        return {}


def get_cwd() -> str:
    """Get current working directory."""
    return os.getcwd()


def change_dir(dirpath: str) -> bool:
    """Change current working directory."""
    try:
        os.chdir(dirpath)
        return True
    except Exception as e:
        print(f"Error changing directory: {e}")
        return False


def get_home_dir() -> str:
    """Get user's home directory."""
    return str(Path.home())


def get_temp_dir() -> str:
    """Get system temporary directory."""
    import tempfile
    return tempfile.gettempdir()


def join_path(*parts: str) -> str:
    """Join path components."""
    return os.path.join(*parts)


def split_path(filepath: str) -> tuple:
    """Split path into directory and filename."""
    return os.path.split(filepath)


def get_extension(filepath: str) -> str:
    """Get file extension."""
    return os.path.splitext(filepath)[1]


def get_basename(filepath: str) -> str:
    """Get filename without directory."""
    return os.path.basename(filepath)


def get_dirname(filepath: str) -> str:
    """Get directory name from path."""
    return os.path.dirname(filepath)


def absolute_path(filepath: str) -> str:
    """Get absolute path."""
    return os.path.abspath(filepath)


def register_filesystem_functions(runtime: Runtime) -> None:
    """Register file system functions with the runtime."""
    
    # File operations
    runtime.register_function("read_file", read_file)
    runtime.register_function("read_lines", read_lines)
    runtime.register_function("read_bytes", read_bytes)
    runtime.register_function("write_file", write_file)
    runtime.register_function("append_file", append_file)
    runtime.register_function("write_bytes", write_bytes)
    
    # File queries
    runtime.register_function("file_exists", file_exists)
    runtime.register_function("dir_exists", dir_exists)
    runtime.register_function("path_exists", path_exists)
    runtime.register_function("get_file_size", get_file_size)
    runtime.register_function("get_file_info", get_file_info)
    
    # Directory operations
    runtime.register_function("create_dir", create_dir)
    runtime.register_function("delete_file", delete_file)
    runtime.register_function("delete_dir", delete_dir)
    runtime.register_function("copy_file", copy_file)
    runtime.register_function("move_file", move_file)
    runtime.register_function("list_dir", list_dir)
    runtime.register_function("list_files", list_files)
    runtime.register_function("list_dirs", list_dirs)
    
    # Path operations
    runtime.register_function("get_cwd", get_cwd)
    runtime.register_function("change_dir", change_dir)
    runtime.register_function("get_home_dir", get_home_dir)
    runtime.register_function("get_temp_dir", get_temp_dir)
    runtime.register_function("join_path", join_path)
    runtime.register_function("split_path", split_path)
    runtime.register_function("get_extension", get_extension)
    runtime.register_function("get_basename", get_basename)
    runtime.register_function("get_dirname", get_dirname)
    runtime.register_function("absolute_path", absolute_path)
    
    # Short aliases
    runtime.register_function("read", read_file)
    runtime.register_function("write", write_file)
    runtime.register_function("exists", path_exists)
    runtime.register_function("mkdir", create_dir)
    runtime.register_function("ls", list_dir)
    runtime.register_function("pwd", get_cwd)
    runtime.register_function("cd", change_dir)
