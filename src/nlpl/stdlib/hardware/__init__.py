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
from typing import Optional


class PortAccessError(Exception):
    """Raised when port I/O operations fail"""
    pass


class PrivilegeError(Exception):
    """Raised when insufficient privileges for hardware access"""
    pass


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
def map_memory(runtime, physical_address: int, size: int) -> int:
    """
    Map physical memory to virtual address space for MMIO
    
    Args:
        physical_address: Physical memory address to map
        size: Size in bytes to map
        
    Returns:
        Virtual address pointer to mapped memory
        
    Raises:
        PortAccessError: If memory mapping fails
        PrivilegeError: If insufficient privileges
        
    Example:
        # Map VGA framebuffer at 0xB8000
        set vga_buffer to map_memory with physical_address 0xB8000, size 4000
    """
    _require_privileges()
    
    if physical_address < 0:
        raise PortAccessError(f"Invalid physical address: {physical_address}")
    
    if size <= 0:
        raise PortAccessError(f"Invalid size: {size}")
    
    if platform.system() == "Linux":
        try:
            # Use /dev/mem for physical memory access
            import mmap
            fd = os.open("/dev/mem", os.O_RDWR | os.O_SYNC)
            
            # Calculate page-aligned address
            page_size = os.sysconf("SC_PAGE_SIZE")
            offset = physical_address % page_size
            aligned_address = physical_address - offset
            aligned_size = size + offset
            
            # Map memory
            mem = mmap.mmap(
                fd,
                aligned_size,
                mmap.MAP_SHARED,
                mmap.PROT_READ | mmap.PROT_WRITE,
                offset=aligned_address
            )
            os.close(fd)
            
            # Return virtual address (Python memoryview address)
            return id(mem) + offset
        except PermissionError:
            raise PrivilegeError("Cannot access /dev/mem. Run with sudo.")
        except Exception as e:
            raise PortAccessError(f"Failed to map memory at 0x{physical_address:08X}: {e}")
    else:
        raise PortAccessError(f"Memory mapping not implemented for {platform.system()}")


def unmap_memory(runtime, address: int) -> None:
    """
    Unmap memory-mapped I/O region
    
    Args:
        address: Virtual address returned by map_memory
        
    Raises:
        PortAccessError: If unmapping fails
    """
    # Note: In Python, memory is managed automatically
    # This is a placeholder for proper cleanup in compiled version
    pass


def read_mmio_byte(runtime, address: int) -> int:
    """
    Read a byte from memory-mapped I/O address (volatile read)
    
    Args:
        address: Virtual memory address
        
    Returns:
        Byte value (0-255)
    """
    _require_privileges()
    # Implementation would use ctypes for volatile memory access
    raise NotImplementedError("MMIO read operations require compiled code")


def write_mmio_byte(runtime, address: int, value: int) -> None:
    """
    Write a byte to memory-mapped I/O address (volatile write)
    
    Args:
        address: Virtual memory address
        value: Byte value (0-255)
    """
    _require_privileges()
    # Implementation would use ctypes for volatile memory access
    raise NotImplementedError("MMIO write operations require compiled code")


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
    
    # Memory-mapped I/O
    runtime.register_function("map_memory", map_memory)
    runtime.register_function("unmap_memory", unmap_memory)
    runtime.register_function("read_mmio_byte", read_mmio_byte)
    runtime.register_function("write_mmio_byte", write_mmio_byte)
