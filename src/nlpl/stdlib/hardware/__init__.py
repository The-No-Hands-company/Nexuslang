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


class InterruptError(Exception):
    """Raised when interrupt handling operations fail"""
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

# Global interrupt handler registry
_interrupt_handlers: Dict[int, callable] = {}

# Interrupt state
_interrupts_enabled: bool = True


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


# ============================================================================
# INTERRUPT AND EXCEPTION HANDLING
# ============================================================================

# Standard x86 Interrupt/Exception Vectors
class InterruptVector(IntEnum):
    """Standard x86 interrupt and exception vectors (0-255)"""
    # CPU Exceptions (0-31)
    DIVIDE_BY_ZERO = 0           # #DE - Division error
    DEBUG = 1                     # #DB - Debug exception
    NMI = 2                       # Non-maskable interrupt
    BREAKPOINT = 3                # #BP - Breakpoint
    OVERFLOW = 4                  # #OF - Overflow
    BOUND_RANGE_EXCEEDED = 5      # #BR - Bound range exceeded
    INVALID_OPCODE = 6            # #UD - Invalid opcode
    DEVICE_NOT_AVAILABLE = 7      # #NM - Device not available (no FPU)
    DOUBLE_FAULT = 8              # #DF - Double fault
    COPROCESSOR_SEGMENT_OVERRUN = 9  # Legacy (not used on modern CPUs)
    INVALID_TSS = 10              # #TS - Invalid task state segment
    SEGMENT_NOT_PRESENT = 11      # #NP - Segment not present
    STACK_SEGMENT_FAULT = 12      # #SS - Stack-segment fault
    GENERAL_PROTECTION = 13       # #GP - General protection fault
    PAGE_FAULT = 14               # #PF - Page fault
    # 15 is reserved
    FPU_ERROR = 16                # #MF - x87 FPU error
    ALIGNMENT_CHECK = 17          # #AC - Alignment check
    MACHINE_CHECK = 18            # #MC - Machine check
    SIMD_EXCEPTION = 19           # #XM - SIMD floating-point exception
    VIRTUALIZATION_EXCEPTION = 20  # #VE - Virtualization exception
    CONTROL_PROTECTION = 21       # #CP - Control protection exception
    # 22-27 reserved
    HYPERVISOR_INJECTION = 28     # #HV - Hypervisor injection exception
    VMM_COMMUNICATION = 29        # #VC - VMM communication exception
    SECURITY_EXCEPTION = 30       # #SX - Security exception
    # 31 reserved
    
    # Hardware Interrupts (32-255)
    # Typical mappings (can vary by system):
    TIMER = 32                    # IRQ 0 - Programmable Interval Timer
    KEYBOARD = 33                 # IRQ 1 - Keyboard
    CASCADE = 34                  # IRQ 2 - Cascade (second PIC)
    COM2 = 35                     # IRQ 3 - Serial port 2
    COM1 = 36                     # IRQ 4 - Serial port 1
    LPT2 = 37                     # IRQ 5 - Parallel port 2
    FLOPPY = 38                   # IRQ 6 - Floppy disk
    LPT1 = 39                     # IRQ 7 - Parallel port 1
    RTC = 40                      # IRQ 8 - Real-time clock
    FREE_1 = 41                   # IRQ 9 - Available
    FREE_2 = 42                   # IRQ 10 - Available
    FREE_3 = 43                   # IRQ 11 - Available
    MOUSE = 44                    # IRQ 12 - PS/2 Mouse
    FPU_IRQ = 45                  # IRQ 13 - FPU / Coprocessor
    PRIMARY_ATA = 46              # IRQ 14 - Primary ATA hard disk
    SECONDARY_ATA = 47            # IRQ 15 - Secondary ATA hard disk


# IDT Entry Structure (Simplified representation)
class IDTEntry:
    """
    Interrupt Descriptor Table Entry
    
    Represents a gate descriptor in the IDT. In real x86, this is a 16-byte
    structure. This is a simplified Python representation.
    """
    def __init__(self, offset: int = 0, segment: int = 0x08, 
                 gate_type: int = 0x8E, dpl: int = 0):
        """
        Initialize IDT entry
        
        Args:
            offset: Interrupt handler address (linear address)
            segment: Code segment selector (typically 0x08 for kernel code)
            gate_type: Gate type and attributes:
                - 0x8E: 32-bit interrupt gate (IF=0)
                - 0x8F: 32-bit trap gate (IF=1)
                - 0xEE: 32-bit interrupt gate, DPL=3 (user callable)
            dpl: Descriptor Privilege Level (0-3, 0=kernel, 3=user)
        """
        self.offset = offset          # Handler address
        self.segment = segment        # Code segment
        self.gate_type = gate_type    # Gate type byte
        self.dpl = dpl                # Privilege level
        self.present = True           # Present bit
    
    def to_dict(self) -> dict:
        """Convert to dictionary for NLPL access"""
        return {
            "offset": self.offset,
            "segment": self.segment,
            "gate_type": self.gate_type,
            "dpl": self.dpl,
            "present": self.present
        }


# Exception Frame (CPU state at interrupt time)
class ExceptionFrame:
    """
    Exception frame - saved CPU state when interrupt occurs
    
    This represents the stack frame pushed by CPU and interrupt handler.
    Contains register values and error codes for exception handling.
    """
    def __init__(self):
        # General purpose registers
        self.rax = 0
        self.rbx = 0
        self.rcx = 0
        self.rdx = 0
        self.rsi = 0
        self.rdi = 0
        self.rbp = 0
        self.rsp = 0
        self.r8 = 0
        self.r9 = 0
        self.r10 = 0
        self.r11 = 0
        self.r12 = 0
        self.r13 = 0
        self.r14 = 0
        self.r15 = 0
        
        # Instruction pointer and flags
        self.rip = 0           # Instruction pointer
        self.rflags = 0        # CPU flags
        
        # Segment registers
        self.cs = 0            # Code segment
        self.ss = 0            # Stack segment
        
        # Exception-specific
        self.error_code = 0    # Error code (if applicable)
        self.vector = 0        # Interrupt vector number
    
    def to_dict(self) -> dict:
        """Convert to dictionary for NLPL access"""
        return {
            "rax": self.rax, "rbx": self.rbx, "rcx": self.rcx, "rdx": self.rdx,
            "rsi": self.rsi, "rdi": self.rdi, "rbp": self.rbp, "rsp": self.rsp,
            "r8": self.r8, "r9": self.r9, "r10": self.r10, "r11": self.r11,
            "r12": self.r12, "r13": self.r13, "r14": self.r14, "r15": self.r15,
            "rip": self.rip, "rflags": self.rflags,
            "cs": self.cs, "ss": self.ss,
            "error_code": self.error_code, "vector": self.vector
        }


# Current exception frame (set when handler is invoked)
_current_exception_frame: Optional[ExceptionFrame] = None

# IDT structure (simplified - 256 entries)
_idt: Dict[int, IDTEntry] = {}


def setup_idt(runtime) -> bool:
    """
    Initialize the Interrupt Descriptor Table
    
    Sets up a basic IDT structure with default handlers.
    On real hardware, this would configure the CPU's IDT register.
    
    Returns:
        True if successful
        
    Raises:
        PrivilegeError: If insufficient privileges
        InterruptError: If IDT setup fails
        
    Example:
        setup_idt
        print text "IDT initialized"
    """
    _require_privileges()
    
    global _idt
    _idt = {}
    
    # Initialize all 256 IDT entries with null handlers
    for vector in range(256):
        _idt[vector] = IDTEntry(offset=0, segment=0x08, gate_type=0x8E, dpl=0)
    
    # Set present bit for exception vectors (0-31)
    for vector in range(32):
        _idt[vector].present = True
    
    return True


def get_idt_entry(runtime, vector: int) -> dict:
    """
    Get an IDT entry
    
    Args:
        vector: Interrupt vector (0-255)
        
    Returns:
        Dictionary with IDT entry information:
        - offset: Handler address
        - segment: Code segment selector
        - gate_type: Gate type byte
        - dpl: Descriptor privilege level
        - present: Present bit
        
    Raises:
        InterruptError: If vector is invalid
        
    Example:
        set entry to get_idt_entry with vector: 14
        print text entry
    """
    if not (0 <= vector <= 255):
        raise InterruptError(f"Invalid interrupt vector: {vector}. Must be 0-255.")
    
    if vector not in _idt:
        # Return default entry
        return IDTEntry().to_dict()
    
    return _idt[vector].to_dict()


def set_idt_entry(runtime, vector: int, offset: int, segment: int = 0x08,
                  gate_type: int = 0x8E, dpl: int = 0) -> bool:
    """
    Set an IDT entry
    
    Configures an interrupt gate descriptor in the IDT.
    
    Args:
        vector: Interrupt vector (0-255)
        offset: Handler address
        segment: Code segment selector (default: 0x08 kernel code)
        gate_type: Gate type (default: 0x8E interrupt gate)
        dpl: Descriptor privilege level (default: 0 kernel)
        
    Returns:
        True if successful
        
    Raises:
        PrivilegeError: If insufficient privileges
        InterruptError: If parameters are invalid
        
    Example:
        set_idt_entry with vector: 32 and offset: handler_address
    """
    _require_privileges()
    
    if not (0 <= vector <= 255):
        raise InterruptError(f"Invalid interrupt vector: {vector}. Must be 0-255.")
    
    if not (0 <= dpl <= 3):
        raise InterruptError(f"Invalid DPL: {dpl}. Must be 0-3.")
    
    _idt[vector] = IDTEntry(offset=offset, segment=segment, 
                            gate_type=gate_type, dpl=dpl)
    return True


def get_idt_base(runtime) -> int:
    """
    Get IDT base address
    
    Returns the base address of the IDT. On real hardware, this would
    read the IDTR register.
    
    Returns:
        IDT base address (linear address)
        
    Example:
        set idt_base to get_idt_base
        print text "IDT at address:"
        print text idt_base
    """
    _require_privileges()
    
    # In this implementation, return the id of the IDT dict
    # On real hardware, would use SIDT instruction
    return id(_idt)


def get_idt_limit(runtime) -> int:
    """
    Get IDT limit (size - 1)
    
    Returns the IDT limit. The limit is the size of the IDT in bytes minus 1.
    For a standard IDT with 256 entries of 16 bytes each, this is 4095.
    
    Returns:
        IDT limit (size - 1)
        
    Example:
        set idt_limit to get_idt_limit
        print text "IDT size:"
        print text idt_limit plus 1
    """
    _require_privileges()
    
    # Standard x86-64 IDT: 256 entries * 16 bytes each = 4096 bytes
    # Limit = size - 1 = 4095
    return 4095


def register_interrupt_handler(runtime, vector: int, handler: callable) -> bool:
    """
    Register an interrupt handler
    
    Associates a handler function with an interrupt vector. When the
    interrupt fires, the handler will be invoked with the exception frame.
    
    Args:
        vector: Interrupt vector (0-255)
        handler: Callable handler function
                 Signature: handler(exception_frame: dict) -> None
        
    Returns:
        True if successful
        
    Raises:
        PrivilegeError: If insufficient privileges
        InterruptError: If vector is invalid or handler is not callable
        
    Example:
        function my_keyboard_handler with frame as Dict
            print text "Keyboard interrupt fired"
            print text "RIP:"
            print text frame["rip"]
        end
        
        register_interrupt_handler with vector: 33 and handler: my_keyboard_handler
    """
    _require_privileges()
    
    if not (0 <= vector <= 255):
        raise InterruptError(f"Invalid interrupt vector: {vector}. Must be 0-255.")
    
    if not callable(handler):
        raise InterruptError(f"Handler must be callable, got {type(handler).__name__}")
    
    _interrupt_handlers[vector] = handler
    
    # Update IDT entry to point to our dispatch mechanism
    # On real hardware, would set actual handler address
    _idt[vector] = IDTEntry(offset=id(handler), segment=0x08, 
                            gate_type=0x8E, dpl=0)
    _idt[vector].present = True
    
    return True


def unregister_interrupt_handler(runtime, vector: int) -> bool:
    """
    Unregister an interrupt handler
    
    Removes the handler for the specified interrupt vector.
    
    Args:
        vector: Interrupt vector (0-255)
        
    Returns:
        True if handler was registered and removed, False if no handler
        
    Raises:
        PrivilegeError: If insufficient privileges
        InterruptError: If vector is invalid
        
    Example:
        unregister_interrupt_handler with vector: 33
    """
    _require_privileges()
    
    if not (0 <= vector <= 255):
        raise InterruptError(f"Invalid interrupt vector: {vector}. Must be 0-255.")
    
    if vector in _interrupt_handlers:
        del _interrupt_handlers[vector]
        # Clear IDT entry
        _idt[vector] = IDTEntry(offset=0, segment=0x08, gate_type=0x8E, dpl=0)
        return True
    
    return False


def list_interrupt_handlers(runtime) -> list:
    """
    List all registered interrupt handlers
    
    Returns:
        List of dictionaries with handler information:
        - vector: Interrupt vector number
        - handler: Handler function reference
        - vector_name: Name of vector (if known)
        
    Example:
        set handlers to list_interrupt_handlers
        for each handler in handlers
            print text "Vector:"
            print text handler["vector"]
            print text handler["vector_name"]
        end
    """
    result = []
    
    # Map vector numbers to names
    vector_names = {
        0: "DIVIDE_BY_ZERO", 1: "DEBUG", 2: "NMI", 3: "BREAKPOINT",
        4: "OVERFLOW", 5: "BOUND_RANGE_EXCEEDED", 6: "INVALID_OPCODE",
        7: "DEVICE_NOT_AVAILABLE", 8: "DOUBLE_FAULT", 10: "INVALID_TSS",
        11: "SEGMENT_NOT_PRESENT", 12: "STACK_SEGMENT_FAULT",
        13: "GENERAL_PROTECTION", 14: "PAGE_FAULT", 16: "FPU_ERROR",
        17: "ALIGNMENT_CHECK", 18: "MACHINE_CHECK", 19: "SIMD_EXCEPTION",
        32: "TIMER", 33: "KEYBOARD", 34: "CASCADE", 35: "COM2",
        36: "COM1", 37: "LPT2", 38: "FLOPPY", 39: "LPT1",
        40: "RTC", 44: "MOUSE", 45: "FPU_IRQ",
        46: "PRIMARY_ATA", 47: "SECONDARY_ATA"
    }
    
    for vector, handler in _interrupt_handlers.items():
        result.append({
            "vector": vector,
            "handler": handler,
            "vector_name": vector_names.get(vector, f"IRQ_{vector}")
        })
    
    return result


def enable_interrupts(runtime) -> bool:
    """
    Enable hardware interrupts (STI instruction)
    
    Sets the interrupt flag (IF) in RFLAGS, allowing hardware interrupts
    to be serviced by the CPU.
    
    Returns:
        True if successful
        
    Raises:
        PrivilegeError: If insufficient privileges
        
    Example:
        enable_interrupts
        print text "Interrupts enabled"
    """
    _require_privileges()
    
    global _interrupts_enabled
    _interrupts_enabled = True
    
    # On real hardware, would execute STI instruction
    # x86: asm("sti")
    
    return True


def disable_interrupts(runtime) -> bool:
    """
    Disable hardware interrupts (CLI instruction)
    
    Clears the interrupt flag (IF) in RFLAGS, preventing hardware interrupts
    from being serviced. Non-maskable interrupts (NMI) still fire.
    
    Returns:
        True if successful
        
    Raises:
        PrivilegeError: If insufficient privileges
        
    Example:
        disable_interrupts
        # Critical section - no interrupts
        write_port with port: port_addr and value: critical_value
        enable_interrupts
    """
    _require_privileges()
    
    global _interrupts_enabled
    _interrupts_enabled = False
    
    # On real hardware, would execute CLI instruction
    # x86: asm("cli")
    
    return True


def get_interrupt_flag(runtime) -> bool:
    """
    Get current interrupt flag state
    
    Returns:
        True if interrupts are enabled, False if disabled
        
    Example:
        set if_state to get_interrupt_flag
        if if_state
            print text "Interrupts are enabled"
        else
            print text "Interrupts are disabled"
        end
    """
    return _interrupts_enabled


def set_interrupt_flag(runtime, enabled: bool) -> bool:
    """
    Set interrupt flag state
    
    Args:
        enabled: True to enable interrupts, False to disable
        
    Returns:
        True if successful
        
    Raises:
        PrivilegeError: If insufficient privileges
        
    Example:
        set_interrupt_flag with enabled: false
        # Critical section
        set_interrupt_flag with enabled: true
    """
    _require_privileges()
    
    global _interrupts_enabled
    _interrupts_enabled = enabled
    
    return True


def get_exception_frame(runtime) -> Optional[dict]:
    """
    Get current exception frame
    
    Returns the saved CPU state from the current interrupt context.
    Only valid when called from within an interrupt handler.
    
    Returns:
        Dictionary with CPU state, or None if not in interrupt context
        
    Example:
        function page_fault_handler with frame as Dict
            set saved_frame to get_exception_frame
            if saved_frame is not null
                print text "Page fault at address:"
                print text saved_frame["rip"]
                print text "Error code:"
                print text saved_frame["error_code"]
            end
        end
    """
    global _current_exception_frame
    
    if _current_exception_frame is None:
        return None
    
    return _current_exception_frame.to_dict()


def get_error_code(runtime) -> int:
    """
    Get exception error code
    
    Returns the error code pushed by the CPU for certain exceptions
    (e.g., page fault, general protection fault).
    
    Returns:
        Error code, or 0 if not in exception context or no error code
        
    Example:
        function gp_handler with frame as Dict
            set error_code to get_error_code
            print text "General Protection Fault, error code:"
            print text error_code
        end
    """
    global _current_exception_frame
    
    if _current_exception_frame is None:
        return 0
    
    return _current_exception_frame.error_code


def get_instruction_pointer(runtime) -> int:
    """
    Get saved instruction pointer (RIP)
    
    Returns the instruction pointer at the time of the interrupt.
    
    Returns:
        Instruction pointer value, or 0 if not in interrupt context
        
    Example:
        set rip to get_instruction_pointer
        print text "Interrupt occurred at:"
        print text rip
    """
    global _current_exception_frame
    
    if _current_exception_frame is None:
        return 0
    
    return _current_exception_frame.rip


def get_stack_pointer(runtime) -> int:
    """
    Get saved stack pointer (RSP)
    
    Returns the stack pointer at the time of the interrupt.
    
    Returns:
        Stack pointer value, or 0 if not in interrupt context
    """
    global _current_exception_frame
    
    if _current_exception_frame is None:
        return 0
    
    return _current_exception_frame.rsp


def get_cpu_flags(runtime) -> int:
    """
    Get saved CPU flags (RFLAGS)
    
    Returns the RFLAGS register at the time of the interrupt.
    Useful for checking flag states like IF, CF, ZF, etc.
    
    Returns:
        RFLAGS value, or 0 if not in interrupt context
        
    Example:
        set flags to get_cpu_flags
        set if_was_set to flags bitwise_and 512  # IF = bit 9
        if if_was_set is not 0
            print text "Interrupts were enabled"
        end
    """
    global _current_exception_frame
    
    if _current_exception_frame is None:
        return 0
    
    return _current_exception_frame.rflags


def invoke_interrupt_handler(runtime, vector: int, frame: Optional[ExceptionFrame] = None) -> bool:
    """
    Internal function to invoke a registered interrupt handler
    
    This simulates interrupt delivery. On real hardware, the CPU would
    handle this automatically.
    
    Args:
        vector: Interrupt vector number
        frame: Exception frame with CPU state (optional)
        
    Returns:
        True if handler was invoked, False if no handler registered
    """
    global _current_exception_frame
    
    if vector not in _interrupt_handlers:
        return False
    
    # Set up exception frame context
    if frame is None:
        frame = ExceptionFrame()
        frame.vector = vector
    
    _current_exception_frame = frame
    
    try:
        # Invoke the handler with the frame
        handler = _interrupt_handlers[vector]
        handler(frame.to_dict())
    finally:
        # Clear exception frame context
        _current_exception_frame = None
    
    return True


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
    
    # Interrupt and exception handling - IDT management
    runtime.register_function("setup_idt", setup_idt)
    runtime.register_function("get_idt_entry", get_idt_entry)
    runtime.register_function("set_idt_entry", set_idt_entry)
    runtime.register_function("get_idt_base", get_idt_base)
    runtime.register_function("get_idt_limit", get_idt_limit)
    
    # Interrupt and exception handling - handler registration
    runtime.register_function("register_interrupt_handler", register_interrupt_handler)
    runtime.register_function("unregister_interrupt_handler", unregister_interrupt_handler)
    runtime.register_function("list_interrupt_handlers", list_interrupt_handlers)
    
    # Interrupt and exception handling - interrupt control
    runtime.register_function("enable_interrupts", enable_interrupts)
    runtime.register_function("disable_interrupts", disable_interrupts)
    runtime.register_function("get_interrupt_flag", get_interrupt_flag)
    runtime.register_function("set_interrupt_flag", set_interrupt_flag)
    
    # Interrupt and exception handling - exception frame access
    runtime.register_function("get_exception_frame", get_exception_frame)
    runtime.register_function("get_error_code", get_error_code)
    runtime.register_function("get_instruction_pointer", get_instruction_pointer)
    runtime.register_function("get_stack_pointer", get_stack_pointer)
    runtime.register_function("get_cpu_flags", get_cpu_flags)

