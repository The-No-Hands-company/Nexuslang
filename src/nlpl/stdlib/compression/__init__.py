"""
Compression and archiving for NLPL.
Supports gzip, zlib, bz2, and tar archives.
"""

import gzip
import zlib
import bz2
import tarfile
import zipfile
import io
from pathlib import Path
from typing import List, Optional
from ...runtime.runtime import Runtime


# GZIP compression
def gzip_compress(data: str, encoding: str = 'utf-8') -> bytes:
    """Compress string with gzip."""
    return gzip.compress(data.encode(encoding))


def gzip_decompress(data: bytes, encoding: str = 'utf-8') -> str:
    """Decompress gzip data to string."""
    return gzip.decompress(data).decode(encoding)


def gzip_compress_file(input_path: str, output_path: Optional[str] = None) -> str:
    """Compress file with gzip. Returns output path."""
    if output_path is None:
        output_path = input_path + '.gz'
    
    with open(input_path, 'rb') as f_in:
        with gzip.open(output_path, 'wb') as f_out:
            f_out.write(f_in.read())
    
    return output_path


def gzip_decompress_file(input_path: str, output_path: str) -> bool:
    """Decompress gzip file."""
    try:
        with gzip.open(input_path, 'rb') as f_in:
            with open(output_path, 'wb') as f_out:
                f_out.write(f_in.read())
        return True
    except Exception as e:
        print(f"Decompression failed: {e}")
        return False


# ZLIB compression
def zlib_compress(data: str, level: int = 6, encoding: str = 'utf-8') -> bytes:
    """Compress string with zlib."""
    return zlib.compress(data.encode(encoding), level=level)


def zlib_decompress(data: bytes, encoding: str = 'utf-8') -> str:
    """Decompress zlib data to string."""
    return zlib.decompress(data).decode(encoding)


# BZ2 compression
def bz2_compress(data: str, level: int = 9, encoding: str = 'utf-8') -> bytes:
    """Compress string with bz2."""
    return bz2.compress(data.encode(encoding), compresslevel=level)


def bz2_decompress(data: bytes, encoding: str = 'utf-8') -> str:
    """Decompress bz2 data to string."""
    return bz2.decompress(data).decode(encoding)


def bz2_compress_file(input_path: str, output_path: Optional[str] = None) -> str:
    """Compress file with bz2. Returns output path."""
    if output_path is None:
        output_path = input_path + '.bz2'
    
    with open(input_path, 'rb') as f_in:
        with bz2.open(output_path, 'wb') as f_out:
            f_out.write(f_in.read())
    
    return output_path


def bz2_decompress_file(input_path: str, output_path: str) -> bool:
    """Decompress bz2 file."""
    try:
        with bz2.open(input_path, 'rb') as f_in:
            with open(output_path, 'wb') as f_out:
                f_out.write(f_in.read())
        return True
    except Exception as e:
        print(f"Decompression failed: {e}")
        return False


# ZIP archives
def zip_create(archive_path: str, files: List[str]) -> bool:
    """Create zip archive from list of files."""
    try:
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for filepath in files:
                zf.write(filepath, Path(filepath).name)
        return True
    except Exception as e:
        print(f"Zip creation failed: {e}")
        return False


def zip_extract(archive_path: str, extract_to: str = '.') -> bool:
    """Extract zip archive."""
    try:
        with zipfile.ZipFile(archive_path, 'r') as zf:
            zf.extractall(extract_to)
        return True
    except Exception as e:
        print(f"Zip extraction failed: {e}")
        return False


def zip_list(archive_path: str) -> List[str]:
    """List files in zip archive."""
    try:
        with zipfile.ZipFile(archive_path, 'r') as zf:
            return zf.namelist()
    except Exception as e:
        print(f"Zip listing failed: {e}")
        return []


def zip_add(archive_path: str, filepath: str) -> bool:
    """Add file to existing zip archive."""
    try:
        with zipfile.ZipFile(archive_path, 'a', zipfile.ZIP_DEFLATED) as zf:
            zf.write(filepath, Path(filepath).name)
        return True
    except Exception as e:
        print(f"Zip add failed: {e}")
        return False


# TAR archives
def tar_create(archive_path: str, files: List[str], compression: Optional[str] = None) -> bool:
    """
    Create tar archive from list of files.
    compression: None, 'gz', 'bz2', 'xz'
    """
    try:
        mode = 'w'
        if compression == 'gz':
            mode = 'w:gz'
        elif compression == 'bz2':
            mode = 'w:bz2'
        elif compression == 'xz':
            mode = 'w:xz'
        
        with tarfile.open(archive_path, mode) as tf:
            for filepath in files:
                tf.add(filepath, Path(filepath).name)
        return True
    except Exception as e:
        print(f"Tar creation failed: {e}")
        return False


def tar_extract(archive_path: str, extract_to: str = '.') -> bool:
    """Extract tar archive (auto-detects compression)."""
    try:
        with tarfile.open(archive_path, 'r:*') as tf:
            tf.extractall(extract_to)
        return True
    except Exception as e:
        print(f"Tar extraction failed: {e}")
        return False


def tar_list(archive_path: str) -> List[str]:
    """List files in tar archive."""
    try:
        with tarfile.open(archive_path, 'r:*') as tf:
            return tf.getnames()
    except Exception as e:
        print(f"Tar listing failed: {e}")
        return []


def tar_add(archive_path: str, filepath: str) -> bool:
    """Add file to existing tar archive."""
    try:
        with tarfile.open(archive_path, 'a') as tf:
            tf.add(filepath, Path(filepath).name)
        return True
    except Exception as e:
        print(f"Tar add failed: {e}")
        return False


def register_compression_functions(runtime: Runtime) -> None:
    """Register compression functions with the runtime."""
    
    # GZIP
    runtime.register_function("gzip_compress", gzip_compress)
    runtime.register_function("gzip_decompress", gzip_decompress)
    runtime.register_function("gzip_compress_file", gzip_compress_file)
    runtime.register_function("gzip_decompress_file", gzip_decompress_file)
    
    # ZLIB
    runtime.register_function("zlib_compress", zlib_compress)
    runtime.register_function("zlib_decompress", zlib_decompress)
    
    # BZ2
    runtime.register_function("bz2_compress", bz2_compress)
    runtime.register_function("bz2_decompress", bz2_decompress)
    runtime.register_function("bz2_compress_file", bz2_compress_file)
    runtime.register_function("bz2_decompress_file", bz2_decompress_file)
    
    # ZIP
    runtime.register_function("zip_create", zip_create)
    runtime.register_function("zip_extract", zip_extract)
    runtime.register_function("zip_list", zip_list)
    runtime.register_function("zip_add", zip_add)
    
    # TAR
    runtime.register_function("tar_create", tar_create)
    runtime.register_function("tar_extract", tar_extract)
    runtime.register_function("tar_list", tar_list)
    runtime.register_function("tar_add", tar_add)
    
    # Aliases
    runtime.register_function("compress", gzip_compress)
    runtime.register_function("decompress", gzip_decompress)
