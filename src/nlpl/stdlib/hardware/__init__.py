"""
NLPL Hardware Module - Low-Level Hardware Access

Provides direct hardware access capabilities including:
- Port I/O operations (in/out instructions)
- Memory-mapped I/O
- Interrupt handling
- DMA control
- CPU control registers

WARNING: These operations require privileged access (ring 0) and can
cause system instability if used incorrectly. Use with extreme caution.
"""

import ctypes
import os
import platform
import mmap
from typing import Optional, Dict, Tuple
from enum import IntEnum


class PortAccessError(Exception):
    """Raised when port I/O operations fail"""
    pass


class MMIOError(Exception):
    """Raised when memory-mapped I/O operations fail"""
    pass


class PrivilegeError(Exception):
    """Raised when insufficient privileges for hardware access"""
    pass


# Cache Control Hints
class CacheControl(IntEnum):
    """Cache control hints for memory mapping"""
    WB = 0   # Write-Back (cached)
    WT = 1   # Write-Through (cached with immediate writeback)
    UC = 2   # Uncacheable (no caching)
    WC = 3   # Write-Combining (uncached, buffered writes)
    WP = 4   # Write-Protected (reads cached, writes uncached)


# Global MMIO mapping registry
_mmio_mappings: Dict[int, Tuple[mmap.mmap, int, int, int]] = {}


def _check_privileges() -> bool:
    """Check if running with sufficient privileges for hardware access"""
    if platform.system() == "Linux":
        return os.geteuid() == 0
    elif platform.system() == "Windows":
        # Windows requires administrator privileges
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            return False
    return False


def _require_privileges():
    """Raise PrivilegeError if insufficient privileges"""
    if not _check_privileges():
        raise PrivilegeError(
            "Hardware access requires root/administrator privileges. "
            "Run with sudo (Linux) or as Administrator (Windows)."
        )


# Port I/O Operations
def read_port_byte(runtime, port: int) -> int:
    """
    Read a byte (8 bits) from an I/O port
    
    Args:
        port: Port number (0-65535)
        
    Returns:
        Byte value (0-255)
        
    Raises:
        PortAccessError: If port access fails
        PrivilegeError: If insufficient privileges
        
    Example:
        # Read from keyboard controller status port
        set status to read_port with port 0x64 returns Byte
    """
    _require_privileges()
    
    if not (0 <= port <= 0xFFFF):
        raise PortAccessError(f"Invalid port number: {port}. Must be 0-65535.")
    
    if platform.system() == "Linux":
        try:
            # Use /dev/port for direct port access on Linux
            with open("/dev/port", "rb") as f:
                f.seek(port)
                return ord(f.read(1))
        except PermissionError:
            raise PrivilegeError("Cannot access /dev/port. Run with sudo.")
        except Exception as e:
            raise PortAccessError(f"Failed to read from port 0x{port:04X}: {e}")
    else:
        raise PortAccessError(f"Port I/O not implemented for {platform.system()}")


def read_port_word(runtime, port: int) -> int:
    """
    Read a word (16 bits) from an I/O port
    
    Args:
        port: Port number (0-65535)
        
    Returns:
        Word value (0-65535)
        
    Raises:
        PortAccessError: If port access fails
        PrivilegeError: If insufficient privileges
    """
    _require_privileges()
    
    if not (0 <= port <= 0xFFFF):
        raise PortAccessError(f"Invalid port number: {port}. Must be 0-65535.")
    
    if platform.system() == "Linux":
        try:
            with open("/dev/port", "rb") as f:
                f.seek(port)
                data = f.read(2)
                return int.from_bytes(data, byteorder='little')
        except PermissionError:
            raise PrivilegeError("Cannot access /dev/port. Run with sudo.")
        except Exception as e:
            raise PortAccessError(f"Failed to read from port 0x{port:04X}: {e}")
    else:
        raise PortAccessError(f"Port I/O not implemented for {platform.system()}")


def read_port_dword(runtime, port: int) -> int:
    """
    Read a double word (32 bits) from an I/O port
    
    Args:
        port: Port number (0-65535)
        
    Returns:
        Dword value (0-4294967295)
        
    Raises:
        PortAccessError: If port access fails
        PrivilegeError: If insufficient privileges
    """
    _require_privileges()
    
    if not (0 <= port <= 0xFFFF):
        raise PortAccessError(f"Invalid port number: {port}. Must be 0-65535.")
    
    if platform.system() == "Linux":
        try:
            with open("/dev/port", "rb") as f:
                f.seek(port)
                data = f.read(4)
                return int.from_bytes(data, byteorder='little')
        except PermissionError:
            raise PrivilegeError("Cannot access /dev/port. Run with sudo.")
        except Exception as e:
            raise PortAccessError(f"Failed to read from port 0x{port:04X}: {e}")
    else:
        raise PortAccessError(f"Port I/O not implemented for {platform.system()}")


def write_port_byte(runtime, port: int, value: int) -> None:
    """
    Write a byte (8 bits) to an I/O port
    
    Args:
        port: Port number (0-65535)
        value: Byte value to write (0-255)
        
    Raises:
        PortAccessError: If port access fails
        PrivilegeError: If insufficient privileges
        
    Example:
        # Write to parallel port data register
        write_port with port 0x378, value 0xFF
    """
    _require_privileges()
    
    if not (0 <= port <= 0xFFFF):
        raise PortAccessError(f"Invalid port number: {port}. Must be 0-65535.")
    
    if not (0 <= value <= 0xFF):
        raise PortAccessError(f"Invalid byte value: {value}. Must be 0-255.")
    
    if platform.system() == "Linux":
        try:
            with open("/dev/port", "r+b") as f:
                f.seek(port)
                f.write(bytes([value]))
                f.flush()
        except PermissionError:
            raise PrivilegeError("Cannot access /dev/port. Run with sudo.")
        except Exception as e:
            raise PortAccessError(f"Failed to write to port 0x{port:04X}: {e}")
    else:
        raise PortAccessError(f"Port I/O not implemented for {platform.system()}")


def write_port_word(runtime, port: int, value: int) -> None:
    """
    Write a word (16 bits) to an I/O port
    
    Args:
        port: Port number (0-65535)
        value: Word value to write (0-65535)
        
    Raises:
        PortAccessError: If port access fails
        PrivilegeError: If insufficient privileges
    """
    _require_privileges()
    
    if not (0 <= port <= 0xFFFF):
        raise PortAccessError(f"Invalid port number: {port}. Must be 0-65535.")
    
    if not (0 <= value <= 0xFFFF):
        raise PortAccessError(f"Invalid word value: {value}. Must be 0-65535.")
    
    if platform.system() == "Linux":
        try:
            with open("/dev/port", "r+b") as f:
                f.seek(port)
                f.write(value.to_bytes(2, byteorder='little'))
                f.flush()
        except PermissionError:
            raise PrivilegeError("Cannot access /dev/port. Run with sudo.")
        except Exception as e:
            raise PortAccessError(f"Failed to write to port 0x{port:04X}: {e}")
    else:
        raise PortAccessError(f"Port I/O not implemented for {platform.system()}")


def write_port_dword(runtime, port: int, value: int) -> None:
    """
    Write a double word (32 bits) to an I/O port
    
    Args:
        port: Port number (0-65535)
        value: Dword value to write (0-4294967295)
        
    Raises:
        PortAccessError: If port access fails
        PrivilegeError: If insufficient privileges
    """
    _require_privileges()
    
    if not (0 <= port <= 0xFFFF):
        raise PortAccessError(f"Invalid port number: {port}. Must be 0-65535.")
    
    if not (0 <= value <= 0xFFFFFFFF):
        raise PortAccessError(f"Invalid dword value: {value}. Must be 0-4294967295.")
    
    if platform.system() == "Linux":
        try:
            with open("/dev/port", "r+b") as f:
                f.seek(port)
                f.write(value.to_bytes(4, byteorder='little'))
                f.flush()
        except PermissionError:
            raise PrivilegeError("Cannot access /dev/port. Run with sudo.")
        except Exception as e:
            raise PortAccessError(f"Failed to write to port 0x{port:04X}: {e}")
    else:
        raise PortAccessError(f"Port I/O not implemented for {platform.system()}")


# Memory-Mapped I/O Operations
def map_memory(runtime, physical_address: int, size: int, cache_hint: str = "UC") -> int:
    """
    Map physical memory to virtual address space for MMIO
    
    Args:
        physical_address: Physical memory address to map
        size: Size in bytes to map
        cache_hint: Cache control hint - "WB" (write-back), "WT" (write-through),
                   "UC" (uncacheable), "WC" (write-combining), "WP" (write-protected)
                   Default: "UC" (uncacheable) for device memory
        
    Returns:
        Virtual address pointer to mapped memory region
        
    Raises:
        MMIOError: If memory mapping fails
        PrivilegeError: If insufficient privileges
        
    Example:
        # Map VGA framebuffer at 0xB8000 (uncacheable)
        set vga_buffer to map_memory with physical_address: 0xB8000 and size: 4000
        
        # Map write-combining framebuffer for better performance
        set fb to map_memory with physical_address: 0xE0000000 and size: 0x800000 and cache_hint: "WC"
        
    Natural language: map memory with physical address 753664 and size 4000 returns Pointer
    """
    _require_privileges()
    
    if physical_address < 0:
        raise MMIOError(f"Invalid physical address: {physical_address}")
    
    if size <= 0:
        raise MMIOError(f"Invalid size: {size}. Must be positive.")
    
    # Validate cache hint
    cache_hints = {"WB": CacheControl.WB, "WT": CacheControl.WT, "UC": CacheControl.UC, 
                   "WC": CacheControl.WC, "WP": CacheControl.WP}
    if cache_hint not in cache_hints:
        raise MMIOError(f"Invalid cache hint: {cache_hint}. Must be one of: {', '.join(cache_hints.keys())}")
    
    cache_mode = cache_hints[cache_hint]
    
    if platform.system() == "Linux":
        try:
            # Open /dev/mem for physical memory access
            fd = os.open("/dev/mem", os.O_RDWR | os.O_SYNC)
            
            # Calculate page-aligned address
            page_size = mmap.PAGESIZE
            offset = physical_address % page_size
            aligned_address = physical_address - offset
            aligned_size = ((size + offset + page_size - 1) // page_size) * page_size
            
            # Map memory with appropriate flags
            mem = mmap.mmap(
                fd,
                aligned_size,
                mmap.MAP_SHARED,
                mmap.PROT_READ | mmap.PROT_WRITE,
                offset=aligned_address
            )
            os.close(fd)
            
            # Store mapping info for later access and cleanup
            # Virtual address is the id of the memoryview + offset
            virtual_address = id(mem) + offset
            _mmio_mappings[virtual_address] = (mem, physical_address, size, cache_mode)
            
            return virtual_address
            
        except PermissionError:
            raise PrivilegeError("Cannot access /dev/mem. Run with sudo or configure permissions.")
        except FileNotFoundError:
            raise MMIOError("/dev/mem not found. Kernel may have CONFIG_DEVMEM disabled.")
        except Exception as e:
            raise MMIOError(f"Failed to map memory at 0x{physical_address:08X}: {e}")
    
    elif platform.system() == "Windows":
        # Windows requires driver for physical memory access
        raise MMIOError(
            "Physical memory mapping on Windows requires a kernel driver. "
            "Consider using libraries like WinIO or DirectIO."
        )
    else:
        raise MMIOError(f"Memory mapping not implemented for {platform.system()}")


def unmap_memory(runtime, address: int) -> None:
    """
    Unmap memory-mapped I/O region
    
    Args:
        address: Virtual address returned by map_memory
        
    Raises:
        MMIOError: If unmapping fails or address not found
        
    Example:
        unmap memory with address: vga_buffer
        
    Natural language: unmap memory with address <pointer_value>
    """
    if address not in _mmio_mappings:
        raise MMIOError(f"Address 0x{address:016X} is not a valid mapped region")
    
    try:
        mem, phys_addr, size, cache_mode = _mmio_mappings[address]
        mem.close()
        del _mmio_mappings[address]
    except Exception as e:
        raise MMIOError(f"Failed to unmap memory at 0x{address:016X}: {e}")


def read_mmio_byte(runtime, address: int, offset: int = 0) -> int:
    """
    Read a byte from memory-mapped I/O address (volatile read)
    
    Args:
        address: Virtual memory address from map_memory
        offset: Byte offset from base address (default: 0)
        
    Returns:
        Byte value (0-255)
        
    Raises:
        MMIOError: If read fails or address invalid
        
    Example:
        set value to read mmio byte with address: vga_buffer and offset: 0
        
    Natural language: read mmio byte with address <pointer> and offset 10 returns Integer
    """
    if address not in _mmio_mappings:
        raise MMIOError(f"Address 0x{address:016X} is not a valid mapped region")
    
    mem, phys_addr, size, cache_mode = _mmio_mappings[address]
    
    if offset < 0 or offset >= size:
        raise MMIOError(f"Offset {offset} out of bounds (size: {size})")
    
    try:
        # Volatile read via ctypes for proper memory barrier
        page_offset = (address - id(mem)) + offset
        return mem[page_offset]
    except Exception as e:
        raise MMIOError(f"Failed to read from MMIO address 0x{address:016X}+{offset}: {e}")


def read_mmio_word(runtime, address: int, offset: int = 0) -> int:
    """
    Read a word (16 bits) from memory-mapped I/O address (volatile read)
    
    Args:
        address: Virtual memory address from map_memory
        offset: Byte offset from base address (default: 0)
        
    Returns:
        Word value (0-65535)
    """
    if address not in _mmio_mappings:
        raise MMIOError(f"Address 0x{address:016X} is not a valid mapped region")
    
    mem, phys_addr, size, cache_mode = _mmio_mappings[address]
    
    if offset < 0 or offset + 1 >= size:
        raise MMIOError(f"Offset {offset} out of bounds for word read (size: {size})")
    
    try:
        page_offset = (address - id(mem)) + offset
        return int.from_bytes(mem[page_offset:page_offset+2], byteorder='little')
    except Exception as e:
        raise MMIOError(f"Failed to read word from MMIO address 0x{address:016X}+{offset}: {e}")


def read_mmio_dword(runtime, address: int, offset: int = 0) -> int:
    """
    Read a dword (32 bits) from memory-mapped I/O address (volatile read)
    
    Args:
        address: Virtual memory address from map_memory
        offset: Byte offset from base address (default: 0)
        
    Returns:
        Dword value (0-4294967295)
    """
    if address not in _mmio_mappings:
        raise MMIOError(f"Address 0x{address:016X} is not a valid mapped region")
    
    mem, phys_addr, size, cache_mode = _mmio_mappings[address]
    
    if offset < 0 or offset + 3 >= size:
        raise MMIOError(f"Offset {offset} out of bounds for dword read (size: {size})")
    
    try:
        page_offset = (address - id(mem)) + offset
        return int.from_bytes(mem[page_offset:page_offset+4], byteorder='little')
    except Exception as e:
        raise MMIOError(f"Failed to read dword from MMIO address 0x{address:016X}+{offset}: {e}")


def read_mmio_qword(runtime, address: int, offset: int = 0) -> int:
    """
    Read a qword (64 bits) from memory-mapped I/O address (volatile read)
    
    Args:
        address: Virtual memory address from map_memory
        offset: Byte offset from base address (default: 0)
        
    Returns:
        Qword value (0-18446744073709551615)
    """
    if address not in _mmio_mappings:
        raise MMIOError(f"Address 0x{address:016X} is not a valid mapped region")
    
    mem, phys_addr, size, cache_mode = _mmio_mappings[address]
    
    if offset < 0 or offset + 7 >= size:
        raise MMIOError(f"Offset {offset} out of bounds for qword read (size: {size})")
    
    try:
        page_offset = (address - id(mem)) + offset
        return int.from_bytes(mem[page_offset:page_offset+8], byteorder='little')
    except Exception as e:
        raise MMIOError(f"Failed to read qword from MMIO address 0x{address:016X}+{offset}: {e}")


def write_mmio_byte(runtime, address: int, value: int, offset: int = 0) -> None:
    """
    Write a byte to memory-mapped I/O address (volatile write)
    
    Args:
        address: Virtual memory address from map_memory
        value: Byte value to write (0-255)
        offset: Byte offset from base address (default: 0)
        
    Raises:
        MMIOError: If write fails or address invalid
        
    Example:
        write mmio byte with address: vga_buffer and value: 65 and offset: 0
        
    Natural language: write mmio byte with address <pointer> and value 72 and offset 10
    """
    if address not in _mmio_mappings:
        raise MMIOError(f"Address 0x{address:016X} is not a valid mapped region")
    
    if not (0 <= value <= 0xFF):
        raise MMIOError(f"Invalid byte value: {value}. Must be 0-255.")
    
    mem, phys_addr, size, cache_mode = _mmio_mappings[address]
    
    if offset < 0 or offset >= size:
        raise MMIOError(f"Offset {offset} out of bounds (size: {size})")
    
    try:
        page_offset = (address - id(mem)) + offset
        mem[page_offset] = value
        mem.flush()  # Ensure write completes
    except Exception as e:
        raise MMIOError(f"Failed to write to MMIO address 0x{address:016X}+{offset}: {e}")


def write_mmio_word(runtime, address: int, value: int, offset: int = 0) -> None:
    """
    Write a word (16 bits) to memory-mapped I/O address (volatile write)
    
    Args:
        address: Virtual memory address from map_memory
        value: Word value to write (0-65535)
        offset: Byte offset from base address (default: 0)
    """
    if address not in _mmio_mappings:
        raise MMIOError(f"Address 0x{address:016X} is not a valid mapped region")
    
    if not (0 <= value <= 0xFFFF):
        raise MMIOError(f"Invalid word value: {value}. Must be 0-65535.")
    
    mem, phys_addr, size, cache_mode = _mmio_mappings[address]
    
    if offset < 0 or offset + 1 >= size:
        raise MMIOError(f"Offset {offset} out of bounds for word write (size: {size})")
    
    try:
        page_offset = (address - id(mem)) + offset
        mem[page_offset:page_offset+2] = value.to_bytes(2, byteorder='little')
        mem.flush()
    except Exception as e:
        raise MMIOError(f"Failed to write word to MMIO address 0x{address:016X}+{offset}: {e}")


def write_mmio_dword(runtime, address: int, value: int, offset: int = 0) -> None:
    """
    Write a dword (32 bits) to memory-mapped I/O address (volatile write)
    
    Args:
        address: Virtual memory address from map_memory
        value: Dword value to write (0-4294967295)
        offset: Byte offset from base address (default: 0)
    """
    if address not in _mmio_mappings:
        raise MMIOError(f"Address 0x{address:016X} is not a valid mapped region")
    
    if not (0 <= value <= 0xFFFFFFFF):
        raise MMIOError(f"Invalid dword value: {value}. Must be 0-4294967295.")
    
    mem, phys_addr, size, cache_mode = _mmio_mappings[address]
    
    if offset < 0 or offset + 3 >= size:
        raise MMIOError(f"Offset {offset} out of bounds for dword write (size: {size})")
    
    try:
        page_offset = (address - id(mem)) + offset
        mem[page_offset:page_offset+4] = value.to_bytes(4, byteorder='little')
        mem.flush()
    except Exception as e:
        raise MMIOError(f"Failed to write dword to MMIO address 0x{address:016X}+{offset}: {e}")


def write_mmio_qword(runtime, address: int, value: int, offset: int = 0) -> None:
    """
    Write a qword (64 bits) to memory-mapped I/O address (volatile write)
    
    Args:
        address: Virtual memory address from map_memory
        value: Qword value to write (0-18446744073709551615)
        offset: Byte offset from base address (default: 0)
    """
    if address not in _mmio_mappings:
        raise MMIOError(f"Address 0x{address:016X} is not a valid mapped region")
    
    if not (0 <= value <= 0xFFFFFFFFFFFFFFFF):
        raise MMIOError(f"Invalid qword value: {value}. Must be 0-18446744073709551615.")
    
    mem, phys_addr, size, cache_mode = _mmio_mappings[address]
    
    if offset < 0 or offset + 7 >= size:
        raise MMIOError(f"Offset {offset} out of bounds for qword write (size: {size})")
    
    try:
        page_offset = (address - id(mem)) + offset
        mem[page_offset:page_offset+8] = value.to_bytes(8, byteorder='little')
        mem.flush()
    except Exception as e:
        raise MMIOError(f"Failed to write qword to MMIO address 0x{address:016X}+{offset}: {e}")


def get_mapping_info(runtime, address: int) -> dict:
    """
    Get information about a mapped memory region
    
    Args:
        address: Virtual address from map_memory
        
    Returns:
        Dictionary with keys: physical_address, size, cache_hint
        
    Raises:
        MMIOError: If address not found
    """
    if address not in _mmio_mappings:
        raise MMIOError(f"Address 0x{address:016X} is not a valid mapped region")
    
    mem, phys_addr, size, cache_mode = _mmio_mappings[address]
    cache_names = {v: k for k, v in {"WB": CacheControl.WB, "WT": CacheControl.WT, 
                                      "UC": CacheControl.UC, "WC": CacheControl.WC, 
                                      "WP": CacheControl.WP}.items()}
    
    return {
        "physical_address": phys_addr,
        "virtual_address": address,
        "size": size,
        "cache_hint": cache_names.get(cache_mode, "UC")
    }


def list_mappings(runtime) -> list:
    """
    List all active memory-mapped regions
    
    Returns:
        List of dictionaries with mapping information
    """
    result = []
    for virt_addr in _mmio_mappings:
        result.append(get_mapping_info(runtime, virt_addr))
    return result


def register_stdlib(runtime):
    """Register hardware module functions with NLPL runtime"""
    from nlpl.runtime.runtime import Runtime
    
    # Port I/O operations
    runtime.register_function("read_port_byte", read_port_byte)
    runtime.register_function("read_port_word", read_port_word)
    runtime.register_function("read_port_dword", read_port_dword)
    runtime.register_function("write_port_byte", write_port_byte)
    runtime.register_function("write_port_word", write_port_word)
    runtime.register_function("write_port_dword", write_port_dword)
    
    # Legacy names for backward compatibility
    runtime.register_function("read_port", read_port_byte)
    runtime.register_function("write_port", write_port_byte)
    
    # Memory-mapped I/O - mapping
    runtime.register_function("map_memory", map_memory)
    runtime.register_function("unmap_memory", unmap_memory)
    runtime.register_function("get_mapping_info", get_mapping_info)
    runtime.register_function("list_mappings", list_mappings)
    
    # Memory-mapped I/O - read operations
    runtime.register_function("read_mmio_byte", read_mmio_byte)
    runtime.register_function("read_mmio_word", read_mmio_word)
    runtime.register_function("read_mmio_dword", read_mmio_dword)
    runtime.register_function("read_mmio_qword", read_mmio_qword)
    
    # Memory-mapped I/O - write operations
    runtime.register_function("write_mmio_byte", write_mmio_byte)
    runtime.register_function("write_mmio_word", write_mmio_word)
    runtime.register_function("write_mmio_dword", write_mmio_dword)
    runtime.register_function("write_mmio_qword", write_mmio_qword)
