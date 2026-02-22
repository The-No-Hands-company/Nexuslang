"""
Device driver framework for NLPL.

Provides userspace-accessible primitives for interacting with device drivers
and hardware through the Linux kernel interfaces:

  Character devices  - /dev/XXX files (serial, tty, GPIO, custom drivers)
  Block devices      - /dev/sdX, /dev/nvme0n1 (sector-level I/O)
  PCI devices        - /sys/bus/pci enumeration and resource access
  I2C devices        - /dev/i2c-X bus communication
  SPI devices        - /dev/spidevX.Y bus communication
  GPIO               - /sys/class/gpio and character device GPIO
  Interrupt handling - Signal-based interrupt simulation + hardware IRQ info
  Device tree        - /proc/device-tree / /sys/firmware/devicetree parsing
  udev               - /sys/class/* device enumeration

All operations degrade gracefully on platforms that do not expose the
required kernel interfaces: a DriverError is raised rather than crashing.

Platform notes
--------------
Full support requires Linux with appropriate kernel drivers loaded and
sufficient privileges (root or appropriate group membership).
Most read operations work without root; write/ioctl usually require elevated
privileges or appropriate udev rules.
"""
from __future__ import annotations

import os
import sys
import stat
import mmap
import signal
import struct
import ctypes
import ctypes.util
import platform
import threading
import subprocess
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

_IS_LINUX = platform.system() == "Linux"
_IS_POSIX = os.name == "posix"


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------

class DriverError(Exception):
    """Raised when a driver operation fails."""


def _require_linux(op: str) -> None:
    if not _IS_LINUX:
        raise DriverError(f"drivers.{op}: operation requires Linux")


def _require_posix(op: str) -> None:
    if not _IS_POSIX:
        raise DriverError(f"drivers.{op}: operation requires POSIX")


# ---------------------------------------------------------------------------
# Character device
# ---------------------------------------------------------------------------

class CharDevice:
    """Represents an open character device node (e.g. /dev/ttyS0, /dev/zero)."""

    def __init__(self, path: str, flags: int = os.O_RDWR) -> None:
        self._path = path
        self._fd: Optional[int] = None
        self._flags = flags

    def open(self) -> None:
        """Open the device node."""
        if not os.path.exists(self._path):
            raise DriverError(f"Character device not found: {self._path}")
        try:
            self._fd = os.open(self._path, self._flags)
        except OSError as exc:
            raise DriverError(f"Cannot open {self._path}: {exc}") from exc

    def close(self) -> None:
        """Close the device node."""
        if self._fd is not None:
            try:
                os.close(self._fd)
            except OSError:
                pass
            self._fd = None

    def read(self, n: int) -> bytes:
        """Read up to *n* bytes from the device."""
        if self._fd is None:
            raise DriverError("Device not open")
        try:
            return os.read(self._fd, n)
        except OSError as exc:
            raise DriverError(f"Read from {self._path} failed: {exc}") from exc

    def write(self, data: bytes) -> int:
        """Write *data* to the device.  Returns number of bytes written."""
        if self._fd is None:
            raise DriverError("Device not open")
        try:
            return os.write(self._fd, data)
        except OSError as exc:
            raise DriverError(f"Write to {self._path} failed: {exc}") from exc

    def ioctl(self, request: int, arg: int = 0) -> int:
        """Perform an ioctl(2) call on the device file descriptor."""
        _require_linux("CharDevice.ioctl")
        if self._fd is None:
            raise DriverError("Device not open")
        import fcntl
        try:
            result = fcntl.ioctl(self._fd, request, arg)
            return result if isinstance(result, int) else 0
        except OSError as exc:
            raise DriverError(
                f"ioctl(fd={self._fd}, req=0x{request:x}) failed: {exc}"
            ) from exc

    def ioctl_buffer(self, request: int, buf: bytearray) -> bytearray:
        """Perform an ioctl that exchanges a mutable buffer."""
        _require_linux("CharDevice.ioctl_buffer")
        if self._fd is None:
            raise DriverError("Device not open")
        import fcntl
        try:
            result = fcntl.ioctl(self._fd, request, buf, True)
            return bytearray(result)
        except OSError as exc:
            raise DriverError(
                f"ioctl_buffer(fd={self._fd}, req=0x{request:x}) failed: {exc}"
            ) from exc

    @property
    def path(self) -> str:
        return self._path

    @property
    def fd(self) -> Optional[int]:
        return self._fd

    def is_open(self) -> bool:
        return self._fd is not None

    def __repr__(self) -> str:
        state = "open" if self.is_open() else "closed"
        return f"CharDevice({self._path!r}, {state})"

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, *_):
        self.close()


# ---------------------------------------------------------------------------
# Block device
# ---------------------------------------------------------------------------

class BlockDevice:
    """Represents an open block device (e.g. /dev/sda, /dev/nvme0n1)."""

    # Standard Linux sector size
    SECTOR_SIZE = 512

    def __init__(self, path: str) -> None:
        self._path = path
        self._fd: Optional[int] = None

    def open(self, read_only: bool = True) -> None:
        """Open the block device.

        Defaults to read-only; pass *read_only=False* for write access
        (requires appropriate privileges).
        """
        if not os.path.exists(self._path):
            raise DriverError(f"Block device not found: {self._path}")
        flags = os.O_RDONLY if read_only else os.O_RDWR
        try:
            self._fd = os.open(self._path, flags)
        except OSError as exc:
            raise DriverError(f"Cannot open {self._path}: {exc}") from exc

    def close(self) -> None:
        if self._fd is not None:
            try:
                os.close(self._fd)
            except OSError:
                pass
            self._fd = None

    def read_sector(self, lba: int) -> bytes:
        """Read one 512-byte sector at logical block address *lba*."""
        if self._fd is None:
            raise DriverError("Device not open")
        offset = lba * self.SECTOR_SIZE
        try:
            os.lseek(self._fd, offset, os.SEEK_SET)
            data = os.read(self._fd, self.SECTOR_SIZE)
        except OSError as exc:
            raise DriverError(
                f"read_sector(lba={lba}) on {self._path} failed: {exc}"
            ) from exc
        return data

    def write_sector(self, lba: int, data: bytes) -> None:
        """Write exactly one sector at *lba*.  Data must be SECTOR_SIZE bytes."""
        if self._fd is None:
            raise DriverError("Device not open")
        if len(data) != self.SECTOR_SIZE:
            raise DriverError(
                f"write_sector requires exactly {self.SECTOR_SIZE} bytes, "
                f"got {len(data)}"
            )
        offset = lba * self.SECTOR_SIZE
        try:
            os.lseek(self._fd, offset, os.SEEK_SET)
            os.write(self._fd, data)
        except OSError as exc:
            raise DriverError(
                f"write_sector(lba={lba}) on {self._path} failed: {exc}"
            ) from exc

    def get_size(self) -> int:
        """Return device size in bytes using BLKGETSIZE64 ioctl (Linux only)."""
        _require_linux("BlockDevice.get_size")
        if self._fd is None:
            raise DriverError("Device not open")
        import fcntl
        BLKGETSIZE64 = 0x80081272
        buf = bytearray(8)
        try:
            fcntl.ioctl(self._fd, BLKGETSIZE64, buf, True)
        except OSError as exc:
            raise DriverError(f"BLKGETSIZE64 failed: {exc}") from exc
        return struct.unpack_from("<Q", buf)[0]

    def get_logical_block_size(self) -> int:
        """Return reported logical block size via BLKSSZGET ioctl."""
        _require_linux("BlockDevice.get_logical_block_size")
        if self._fd is None:
            raise DriverError("Device not open")
        import fcntl
        BLKSSZGET = 0x1268
        buf = bytearray(4)
        try:
            fcntl.ioctl(self._fd, BLKSSZGET, buf, True)
        except OSError as exc:
            raise DriverError(f"BLKSSZGET failed: {exc}") from exc
        return struct.unpack_from("<I", buf)[0]

    def is_open(self) -> bool:
        return self._fd is not None

    def __repr__(self) -> str:
        state = "open" if self._fd is not None else "closed"
        return f"BlockDevice({self._path!r}, {state})"

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, *_):
        self.close()


# ---------------------------------------------------------------------------
# PCI device enumeration
# ---------------------------------------------------------------------------

def _read_sysfs(path: str) -> str:
    """Read a sysfs file as stripped text, returning '' on error."""
    try:
        with open(path, "r", errors="replace") as fh:
            return fh.read().strip()
    except OSError:
        return ""


def _read_sysfs_hex(path: str) -> int:
    """Read a sysfs file as a hex integer, returning -1 on error."""
    raw = _read_sysfs(path)
    raw = raw.lstrip("0x").strip()
    if not raw:
        return -1
    try:
        return int(raw, 16)
    except ValueError:
        return -1


class PciDevice:
    """Represents a PCI device discovered via sysfs."""

    def __init__(self, sysfs_path: str) -> None:
        self._path = sysfs_path

    @property
    def address(self) -> str:
        """BDF address: 0000:00:1f.0"""
        return os.path.basename(self._path)

    @property
    def vendor_id(self) -> int:
        return _read_sysfs_hex(os.path.join(self._path, "vendor"))

    @property
    def device_id(self) -> int:
        return _read_sysfs_hex(os.path.join(self._path, "device"))

    @property
    def class_code(self) -> int:
        return _read_sysfs_hex(os.path.join(self._path, "class"))

    @property
    def subsystem_vendor(self) -> int:
        return _read_sysfs_hex(os.path.join(self._path, "subsystem_vendor"))

    @property
    def subsystem_device(self) -> int:
        return _read_sysfs_hex(os.path.join(self._path, "subsystem_device"))

    @property
    def driver(self) -> str:
        """Name of the currently bound kernel driver, or '' if none."""
        driver_link = os.path.join(self._path, "driver")
        if os.path.islink(driver_link):
            return os.path.basename(os.readlink(driver_link))
        return ""

    @property
    def enabled(self) -> bool:
        return _read_sysfs(os.path.join(self._path, "enable")) == "1"

    def read_config_byte(self, offset: int) -> int:
        """Read one byte from PCI configuration space (offset in bytes)."""
        _require_linux("PciDevice.read_config_byte")
        config_path = os.path.join(self._path, "config")
        try:
            with open(config_path, "rb") as fh:
                fh.seek(offset)
                raw = fh.read(1)
                return raw[0] if raw else -1
        except OSError as exc:
            raise DriverError(
                f"PCI config read at 0x{offset:x} failed: {exc}"
            ) from exc

    def read_config_word(self, offset: int) -> int:
        """Read two bytes (little-endian) from PCI config space."""
        _require_linux("PciDevice.read_config_word")
        config_path = os.path.join(self._path, "config")
        try:
            with open(config_path, "rb") as fh:
                fh.seek(offset)
                raw = fh.read(2)
                return struct.unpack_from("<H", raw)[0] if len(raw) == 2 else -1
        except OSError as exc:
            raise DriverError(
                f"PCI config read at 0x{offset:x} failed: {exc}"
            ) from exc

    def to_dict(self) -> Dict[str, Any]:
        return {
            "address": self.address,
            "vendor_id": f"0x{self.vendor_id:04x}",
            "device_id": f"0x{self.device_id:04x}",
            "class_code": f"0x{self.class_code:06x}",
            "driver": self.driver,
            "enabled": self.enabled,
        }

    def __repr__(self) -> str:
        return (f"PciDevice({self.address}, "
                f"vendor=0x{self.vendor_id:04x}, "
                f"device=0x{self.device_id:04x})")


def enumerate_pci_devices(
    vendor_id: Optional[int] = None,
    device_id: Optional[int] = None,
    class_code: Optional[int] = None,
) -> List[PciDevice]:
    """Return all PCI devices visible in sysfs, optionally filtered.

    Filters are applied as exact integer matches.  Pass *None* to match
    any value for that field.
    """
    _require_linux("enumerate_pci_devices")
    base = Path("/sys/bus/pci/devices")
    if not base.exists():
        raise DriverError("PCI sysfs not available: /sys/bus/pci/devices missing")
    devices = []
    for entry in sorted(base.iterdir()):
        dev = PciDevice(str(entry))
        if vendor_id is not None and dev.vendor_id != vendor_id:
            continue
        if device_id is not None and dev.device_id != device_id:
            continue
        if class_code is not None and dev.class_code != class_code:
            continue
        devices.append(dev)
    return devices


# ---------------------------------------------------------------------------
# I2C device
# ---------------------------------------------------------------------------

# Linux I2C ioctl numbers
_I2C_SLAVE = 0x0703
_I2C_SLAVE_FORCE = 0x0706
_I2C_RDWR = 0x0707
_I2C_SMBUS = 0x0720
_I2C_FUNCS = 0x0705

class I2cDevice:
    """Userspace I2C device client via /dev/i2c-X."""

    def __init__(self, bus: int, address: int) -> None:
        self._bus_path = f"/dev/i2c-{bus}"
        self._address = address
        self._fd: Optional[int] = None

    @property
    def bus(self) -> int:
        return int(self._bus_path.split("-")[-1])

    @property
    def address(self) -> int:
        return self._address

    def open(self) -> None:
        _require_linux("I2cDevice.open")
        if not os.path.exists(self._bus_path):
            raise DriverError(f"I2C bus not found: {self._bus_path}")
        try:
            self._fd = os.open(self._bus_path, os.O_RDWR)
        except OSError as exc:
            raise DriverError(f"Cannot open {self._bus_path}: {exc}") from exc
        import fcntl
        try:
            fcntl.ioctl(self._fd, _I2C_SLAVE, self._address)
        except OSError as exc:
            os.close(self._fd)
            self._fd = None
            raise DriverError(
                f"Cannot set I2C slave address 0x{self._address:02x}: {exc}"
            ) from exc

    def close(self) -> None:
        if self._fd is not None:
            try:
                os.close(self._fd)
            except OSError:
                pass
            self._fd = None

    def is_open(self) -> bool:
        return self._fd is not None

    def read(self, n: int) -> bytes:
        """Read *n* bytes from the I2C device."""
        if self._fd is None:
            raise DriverError("I2C device not open")
        try:
            return os.read(self._fd, n)
        except OSError as exc:
            raise DriverError(f"I2C read failed: {exc}") from exc

    def write(self, data: bytes) -> int:
        """Write *data* to the I2C device."""
        if self._fd is None:
            raise DriverError("I2C device not open")
        try:
            return os.write(self._fd, data)
        except OSError as exc:
            raise DriverError(f"I2C write failed: {exc}") from exc

    def write_byte_data(self, register: int, value: int) -> None:
        """Write a single byte to a register (SMBus write-byte-data)."""
        self.write(bytes([register & 0xFF, value & 0xFF]))

    def read_byte_data(self, register: int) -> int:
        """Write register address then read back one byte."""
        self.write(bytes([register & 0xFF]))
        return self.read(1)[0]

    def read_word_data(self, register: int) -> int:
        """Read two bytes starting at *register*, returned as little-endian u16."""
        self.write(bytes([register & 0xFF]))
        data = self.read(2)
        return struct.unpack_from("<H", data)[0]

    def __repr__(self) -> str:
        return (f"I2cDevice(bus={self._bus_path!r}, "
                f"addr=0x{self._address:02x})")


# ---------------------------------------------------------------------------
# SPI device
# ---------------------------------------------------------------------------

# Linux SPI ioctl numbers
_SPI_IOC_MAGIC = ord("k")


def _SPI_IOC_MESSAGE(n: int) -> int:
    # _IOW macro equivalent: (direction=1<<30) | (size<<16) | (magic<<8) | nr
    # struct spi_ioc_transfer is 36 bytes each
    size = n * 36
    return (1 << 30) | (size << 16) | (_SPI_IOC_MAGIC << 8) | 0


class SpiDevice:
    """Userspace SPI device client via /dev/spidevX.Y."""

    MODE_0 = 0x00
    MODE_1 = 0x01
    MODE_2 = 0x02
    MODE_3 = 0x03

    def __init__(self, bus: int, cs: int) -> None:
        self._bus = bus
        self._cs = cs
        self._path = f"/dev/spidev{bus}.{cs}"
        self._fd: Optional[int] = None

    @property
    def bus(self) -> int:
        return self._bus

    @property
    def cs(self) -> int:
        return self._cs

    def open(self) -> None:
        _require_linux("SpiDevice.open")
        if not os.path.exists(self._path):
            raise DriverError(f"SPI device not found: {self._path}")
        try:
            self._fd = os.open(self._path, os.O_RDWR)
        except OSError as exc:
            raise DriverError(f"Cannot open {self._path}: {exc}") from exc

    def close(self) -> None:
        if self._fd is not None:
            try:
                os.close(self._fd)
            except OSError:
                pass
            self._fd = None

    def is_open(self) -> bool:
        return self._fd is not None

    def transfer(self, tx_data: bytes, speed_hz: int = 500000) -> bytes:
        """Full-duplex SPI transfer using spi_ioc_transfer ioctl.

        Returns received bytes of the same length as *tx_data*.
        """
        _require_linux("SpiDevice.transfer")
        if self._fd is None:
            raise DriverError("SPI device not open")
        import fcntl, ctypes
        n = len(tx_data)
        rx_buf = (ctypes.c_uint8 * n)()
        tx_buf = (ctypes.c_uint8 * n)(*tx_data)
        # struct spi_ioc_transfer layout (36 bytes):
        # u64 tx_buf, u64 rx_buf, u32 len, u32 speed_hz, u16 delay_usecs,
        # u8 bits_per_word, u8 cs_change, u8 tx_nbits, u8 rx_nbits, u16 pad
        msg = struct.pack(
            "=QQIIHBBBBH",
            ctypes.addressof(tx_buf),
            ctypes.addressof(rx_buf),
            n,
            speed_hz,
            0,   # delay_usecs
            8,   # bits_per_word
            0,   # cs_change
            0,   # tx_nbits
            0,   # rx_nbits
            0,   # pad
        )
        buf = bytearray(msg)
        try:
            fcntl.ioctl(self._fd, _SPI_IOC_MESSAGE(1), buf)
        except OSError as exc:
            raise DriverError(f"SPI transfer failed: {exc}") from exc
        return bytes(rx_buf)

    def __repr__(self) -> str:
        return f"SpiDevice({self._path!r})"


# ---------------------------------------------------------------------------
# GPIO (sysfs interface)
# ---------------------------------------------------------------------------

class GpioPin:
    """Controls a single GPIO pin via the Linux sysfs GPIO interface.

    Usage::

        pin = GpioPin(18)
        pin.export()
        pin.set_direction("out")
        pin.write(1)
        pin.unexport()

    The character-device GPIO interface (/dev/gpiochipX) is preferred on
    newer kernels but not all boards expose it; the sysfs interface is used
    here for maximum portability.
    """

    # Direction constants
    IN = "in"
    OUT = "out"
    OUT_HIGH = "high"
    OUT_LOW = "low"

    @property
    def pin(self) -> int:
        return self._pin

    def __init__(self, pin: int) -> None:
        self._pin = pin
        self._base = Path(f"/sys/class/gpio/gpio{pin}")

    def export(self) -> None:
        """Export the GPIO pin to userspace via sysfs."""
        _require_linux("GpioPin.export")
        if self._base.exists():
            return  # Already exported
        try:
            with open("/sys/class/gpio/export", "w") as fh:
                fh.write(str(self._pin))
        except OSError as exc:
            raise DriverError(f"GPIO export pin {self._pin} failed: {exc}") from exc

    def unexport(self) -> None:
        """Unexport the GPIO pin."""
        _require_linux("GpioPin.unexport")
        try:
            with open("/sys/class/gpio/unexport", "w") as fh:
                fh.write(str(self._pin))
        except OSError as exc:
            raise DriverError(f"GPIO unexport pin {self._pin} failed: {exc}") from exc

    def set_direction(self, direction: str) -> None:
        """Set pin direction: "in", "out", "high", or "low"."""
        _require_linux("GpioPin.set_direction")
        direction_file = self._base / "direction"
        try:
            with open(direction_file, "w") as fh:
                fh.write(direction)
        except OSError as exc:
            raise DriverError(
                f"GPIO set_direction({direction}) for pin {self._pin} failed: {exc}"
            ) from exc

    def get_direction(self) -> str:
        """Return current pin direction."""
        _require_linux("GpioPin.get_direction")
        raw = _read_sysfs(str(self._base / "direction"))
        if not raw:
            raise DriverError(f"Cannot read direction for GPIO pin {self._pin}")
        return raw

    def read(self) -> int:
        """Read pin value (0 or 1)."""
        _require_linux("GpioPin.read")
        raw = _read_sysfs(str(self._base / "value"))
        if not raw:
            raise DriverError(f"Cannot read value for GPIO pin {self._pin}")
        return int(raw)

    def write(self, value: int) -> None:
        """Write pin value (0 or 1)."""
        _require_linux("GpioPin.write")
        try:
            with open(self._base / "value", "w") as fh:
                fh.write("1" if value else "0")
        except OSError as exc:
            raise DriverError(
                f"GPIO write({value}) for pin {self._pin} failed: {exc}"
            ) from exc

    def set_active_low(self, active_low: bool) -> None:
        """Configure active-low polarity."""
        _require_linux("GpioPin.set_active_low")
        try:
            with open(self._base / "active_low", "w") as fh:
                fh.write("1" if active_low else "0")
        except OSError as exc:
            raise DriverError(f"GPIO set_active_low failed: {exc}") from exc

    @property
    def pin_number(self) -> int:
        return self._pin

    def __repr__(self) -> str:
        return f"GpioPin({self._pin})"


def list_gpio_chips() -> List[str]:
    """Return a list of available GPIO chip names (e.g. ['gpiochip0'])."""
    _require_linux("list_gpio_chips")
    base = Path("/sys/class/gpio")
    if not base.exists():
        return []
    return [
        e.name for e in base.iterdir()
        if e.name.startswith("gpiochip")
    ]


# ---------------------------------------------------------------------------
# Interrupt / IRQ information
# ---------------------------------------------------------------------------

def list_irqs() -> List[Dict[str, Any]]:
    """Return a list of active IRQ entries from /proc/interrupts.

    Each entry is a dict with keys: 'irq', 'count', 'type', 'name'.
    Returns an empty list if /proc/interrupts is unavailable.
    """
    _require_linux("list_irqs")
    result: List[Dict[str, Any]] = []
    try:
        with open("/proc/interrupts", "r") as fh:
            lines = fh.read().splitlines()
    except OSError:
        return result
    for line in lines[1:]:  # skip header CPU0 ... CPUn
        parts = line.split()
        if not parts:
            continue
        irq_str = parts[0].rstrip(":")
        # Sum counts across all CPUs
        counts = []
        idx = 1
        while idx < len(parts) and parts[idx].isdigit():
            counts.append(int(parts[idx]))
            idx += 1
        irq_type = parts[idx] if idx < len(parts) else ""
        idx += 1
        name = " ".join(parts[idx:]) if idx < len(parts) else ""
        result.append({
            "irq": irq_str,
            "count": sum(counts),
            "type": irq_type,
            "name": name,
        })
    return result


def get_irq_affinity(irq: int) -> Optional[str]:
    """Read the CPU affinity mask for *irq* from /proc/irq/<irq>/smp_affinity.

    Returns the hex affinity mask string, or None if unavailable.
    """
    _require_linux("get_irq_affinity")
    path = f"/proc/irq/{irq}/smp_affinity"
    raw = _read_sysfs(path)
    return raw if raw else None


def set_irq_affinity(irq: int, affinity_hex: str) -> None:
    """Write a CPU affinity mask for *irq* to /proc/irq/<irq>/smp_affinity.

    Requires root privileges.
    """
    _require_linux("set_irq_affinity")
    path = f"/proc/irq/{irq}/smp_affinity"
    try:
        with open(path, "w") as fh:
            fh.write(affinity_hex.strip())
    except OSError as exc:
        raise DriverError(f"set_irq_affinity({irq}, {affinity_hex!r}): {exc}") from exc


# ---------------------------------------------------------------------------
# Software interrupt / signal simulation
# ---------------------------------------------------------------------------

class InterruptHandler:
    """Register Python callables as handlers for POSIX signals.

    Useful for testing interrupt-driven logic in userspace without real
    hardware IRQs.

    Usage::

        handler = InterruptHandler()
        handler.register(signal.SIGUSR1, lambda: print("IRQ received"))
        handler.activate()
        # ... send SIGUSR1 via os.kill(os.getpid(), signal.SIGUSR1)
        handler.deactivate()
    """

    def __init__(self) -> None:
        self._handlers: Dict[signal.Signals, Callable] = {}
        self._original: Dict[signal.Signals, Any] = {}
        self._lock = threading.Lock()

    def register(self, sig: int, callback: Callable) -> None:
        """Register *callback* for signal number *sig*."""
        _require_posix("InterruptHandler.register")
        with self._lock:
            self._handlers[signal.Signals(sig)] = callback

    def activate(self) -> None:
        """Install registered signal handlers."""
        _require_posix("InterruptHandler.activate")
        with self._lock:
            for sig, cb in self._handlers.items():
                prev = signal.signal(sig, lambda signum, frame, _cb=cb: _cb())
                self._original[sig] = prev

    def deactivate(self) -> None:
        """Restore original signal handlers."""
        _require_posix("InterruptHandler.deactivate")
        with self._lock:
            for sig, prev in self._original.items():
                try:
                    signal.signal(sig, prev)
                except (OSError, ValueError):
                    pass
            self._original.clear()

    def trigger(self, sig: int) -> None:
        """Send *sig* to the current process, invoking the registered handler.

        If no handler has been registered for *sig*, this method returns
        immediately (no-op) so that callers never accidentally deliver a
        signal whose default action would terminate the process.
        """
        _require_posix("InterruptHandler.trigger")
        sig_obj = signal.Signals(sig)
        with self._lock:
            if sig_obj not in self._handlers:
                return
        os.kill(os.getpid(), sig)


# ---------------------------------------------------------------------------
# Device tree (simplified read interface)
# ---------------------------------------------------------------------------

def read_device_tree_property(node_path: str, prop: str) -> Optional[bytes]:
    """Read a property file from the device tree.

    *node_path* is a path relative to /proc/device-tree (or absolute).
    Returns raw bytes or None if unavailable.

    Example::

        read_device_tree_property("chosen", "bootargs")
    """
    _require_linux("read_device_tree_property")
    if not node_path.startswith("/"):
        node_path = f"/proc/device-tree/{node_path}"
    full = os.path.join(node_path, prop)
    try:
        with open(full, "rb") as fh:
            return fh.read()
    except OSError:
        return None


def read_device_tree_string(node_path: str, prop: str) -> str:
    """Read a device-tree property as a null-terminated UTF-8 string."""
    data = read_device_tree_property(node_path, prop)
    if data is None:
        return ""
    return data.rstrip(b"\x00").decode("utf-8", errors="replace")


def list_device_tree_children(node_path: str) -> List[str]:
    """List child nodes of a device-tree node directory."""
    _require_linux("list_device_tree_children")
    if not node_path.startswith("/"):
        node_path = f"/proc/device-tree/{node_path}"
    try:
        return [
            e for e in os.listdir(node_path)
            if os.path.isdir(os.path.join(node_path, e))
        ]
    except OSError:
        return []


# ---------------------------------------------------------------------------
# udev / sysfs device enumeration helpers
# ---------------------------------------------------------------------------

def list_devices_by_class(device_class: str) -> List[Dict[str, str]]:
    """Enumerate devices in /sys/class/<device_class>.

    Returns a list of dicts with 'name' and common attribute keys found in
    the uevent file (DEVTYPE, DEVNAME, DRIVER, etc.).

    Example device_class values: 'net', 'block', 'input', 'tty', 'video4linux'
    """
    _require_linux("list_devices_by_class")
    base = Path(f"/sys/class/{device_class}")
    if not base.exists():
        return []
    result = []
    for entry in sorted(base.iterdir()):
        info: Dict[str, str] = {"name": entry.name}
        uevent_path = entry / "uevent"
        if uevent_path.exists():
            try:
                with open(uevent_path, "r") as fh:
                    for line in fh:
                        if "=" in line:
                            k, _, v = line.strip().partition("=")
                            info[k.lower()] = v
            except OSError:
                pass
        result.append(info)
    return result


def find_device_by_attr(
    device_class: str,
    attr: str,
    value: str,
) -> Optional[str]:
    """Find the first device name in *device_class* where *attr* equals *value*.

    Returns the device name string or None.
    """
    _require_linux("find_device_by_attr")
    base = Path(f"/sys/class/{device_class}")
    if not base.exists():
        return None
    for entry in sorted(base.iterdir()):
        attr_path = entry / attr
        if attr_path.exists():
            raw = _read_sysfs(str(attr_path))
            if raw == value.strip():
                return entry.name
    return None


def get_device_attribute(device_class: str, name: str, attr: str) -> str:
    """Read a single sysfs attribute for a named device.

    Example::

        get_device_attribute("net", "eth0", "speed")
    """
    _require_linux("get_device_attribute")
    path = f"/sys/class/{device_class}/{name}/{attr}"
    return _read_sysfs(path)


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

def register_driver_functions(runtime: Any) -> None:
    """Register all driver framework functions with the NLPL runtime."""

    # ---- CharDevice lifecycle ----
    runtime.register_function(
        "open_char_device",
        lambda rt, path, flags=os.O_RDWR: _open_char_device(path, int(flags)),
    )
    runtime.register_function(
        "close_char_device",
        lambda rt, dev: dev.close(),
    )
    runtime.register_function(
        "read_char_device",
        lambda rt, dev, n: dev.read(int(n)),
    )
    runtime.register_function(
        "write_char_device",
        lambda rt, dev, data: dev.write(
            data if isinstance(data, (bytes, bytearray)) else str(data).encode()
        ),
    )
    runtime.register_function(
        "ioctl_char_device",
        lambda rt, dev, request, arg=0: dev.ioctl(int(request), int(arg)),
    )
    runtime.register_function(
        "char_device_is_open",
        lambda rt, dev: dev.is_open(),
    )

    # ---- BlockDevice lifecycle ----
    runtime.register_function(
        "open_block_device",
        lambda rt, path, read_only=True: _open_block_device(path, bool(read_only)),
    )
    runtime.register_function(
        "close_block_device",
        lambda rt, dev: dev.close(),
    )
    runtime.register_function(
        "read_sector",
        lambda rt, dev, lba: dev.read_sector(int(lba)),
    )
    runtime.register_function(
        "write_sector",
        lambda rt, dev, lba, data: dev.write_sector(int(lba), bytes(data)),
    )
    runtime.register_function(
        "block_device_size",
        lambda rt, dev: dev.get_size(),
    )
    runtime.register_function(
        "block_device_sector_size",
        lambda rt, dev: dev.get_logical_block_size(),
    )

    # ---- PCI ----
    runtime.register_function(
        "enumerate_pci",
        lambda rt: [d.to_dict() for d in enumerate_pci_devices()],
    )
    runtime.register_function(
        "find_pci_device",
        lambda rt, vendor, device: _find_pci(int(vendor, 16) if isinstance(vendor, str) else int(vendor),
                                             int(device, 16) if isinstance(device, str) else int(device)),
    )
    runtime.register_function(
        "pci_device_info",
        lambda rt, dev: dev.to_dict() if isinstance(dev, PciDevice) else {},
    )

    # ---- I2C ----
    runtime.register_function(
        "open_i2c_device",
        lambda rt, bus, addr: _open_i2c(int(bus), int(addr)),
    )
    runtime.register_function(
        "close_i2c_device",
        lambda rt, dev: dev.close(),
    )
    runtime.register_function(
        "i2c_read",
        lambda rt, dev, n: dev.read(int(n)),
    )
    runtime.register_function(
        "i2c_write",
        lambda rt, dev, data: dev.write(
            data if isinstance(data, (bytes, bytearray)) else bytes([int(data)])
        ),
    )
    runtime.register_function(
        "i2c_write_byte",
        lambda rt, dev, reg, val: dev.write_byte_data(int(reg), int(val)),
    )
    runtime.register_function(
        "i2c_read_byte",
        lambda rt, dev, reg: dev.read_byte_data(int(reg)),
    )
    runtime.register_function(
        "i2c_read_word",
        lambda rt, dev, reg: dev.read_word_data(int(reg)),
    )

    # ---- SPI ----
    runtime.register_function(
        "open_spi_device",
        lambda rt, bus, cs: _open_spi(int(bus), int(cs)),
    )
    runtime.register_function(
        "close_spi_device",
        lambda rt, dev: dev.close(),
    )
    runtime.register_function(
        "spi_transfer",
        lambda rt, dev, data, speed=500000: dev.transfer(
            data if isinstance(data, (bytes, bytearray)) else bytes(data),
            int(speed),
        ),
    )

    # ---- GPIO ----
    runtime.register_function(
        "gpio_export",
        lambda rt, pin: _gpio_export(int(pin)),
    )
    runtime.register_function(
        "gpio_unexport",
        lambda rt, pin: GpioPin(int(pin)).unexport(),
    )
    runtime.register_function(
        "gpio_set_direction",
        lambda rt, pin, direction: _gpio_set_direction(int(pin), str(direction)),
    )
    runtime.register_function(
        "gpio_read",
        lambda rt, pin: GpioPin(int(pin)).read(),
    )
    runtime.register_function(
        "gpio_write",
        lambda rt, pin, value: _gpio_write(int(pin), int(value)),
    )
    runtime.register_function(
        "list_gpio_chips",
        lambda rt: list_gpio_chips(),
    )

    # ---- IRQ information ----
    runtime.register_function(
        "list_irqs",
        lambda rt: list_irqs(),
    )
    runtime.register_function(
        "get_irq_affinity",
        lambda rt, irq: get_irq_affinity(int(irq)),
    )
    runtime.register_function(
        "set_irq_affinity",
        lambda rt, irq, mask: set_irq_affinity(int(irq), str(mask)),
    )

    # ---- Interrupt handler (software simulation) ----
    runtime.register_function(
        "create_interrupt_handler",
        lambda rt: InterruptHandler(),
    )
    runtime.register_function(
        "register_interrupt",
        lambda rt, handler, sig, cb: handler.register(int(sig), cb),
    )
    runtime.register_function(
        "activate_interrupts",
        lambda rt, handler: handler.activate(),
    )
    runtime.register_function(
        "deactivate_interrupts",
        lambda rt, handler: handler.deactivate(),
    )
    runtime.register_function(
        "trigger_interrupt",
        lambda rt, handler, sig: handler.trigger(int(sig)),
    )

    # ---- Device tree ----
    runtime.register_function(
        "read_device_tree_property",
        lambda rt, node, prop: read_device_tree_property(str(node), str(prop)),
    )
    runtime.register_function(
        "read_device_tree_string",
        lambda rt, node, prop: read_device_tree_string(str(node), str(prop)),
    )
    runtime.register_function(
        "list_device_tree_children",
        lambda rt, node: list_device_tree_children(str(node)),
    )

    # ---- udev / sysfs ----
    runtime.register_function(
        "list_devices_by_class",
        lambda rt, cls: list_devices_by_class(str(cls)),
    )
    runtime.register_function(
        "find_device_by_attr",
        lambda rt, cls, attr, val: find_device_by_attr(str(cls), str(attr), str(val)),
    )
    runtime.register_function(
        "get_device_attribute",
        lambda rt, cls, name, attr: get_device_attribute(str(cls), str(name), str(attr)),
    )


# ---------------------------------------------------------------------------
# Private helpers used by lambda registrations
# ---------------------------------------------------------------------------

def _open_char_device(path: str, flags: int) -> CharDevice:
    dev = CharDevice(path, flags)
    dev.open()
    return dev


def _open_block_device(path: str, read_only: bool) -> BlockDevice:
    dev = BlockDevice(path)
    dev.open(read_only=read_only)
    return dev


def _open_i2c(bus: int, addr: int) -> I2cDevice:
    dev = I2cDevice(bus, addr)
    dev.open()
    return dev


def _open_spi(bus: int, cs: int) -> SpiDevice:
    dev = SpiDevice(bus, cs)
    dev.open()
    return dev


def _find_pci(
    vendor_id: int,
    device_id: int,
) -> Optional[Dict[str, Any]]:
    try:
        devices = enumerate_pci_devices(vendor_id=vendor_id, device_id=device_id)
        return devices[0].to_dict() if devices else None
    except DriverError:
        return None


def _gpio_export(pin: int) -> None:
    GpioPin(pin).export()


def _gpio_set_direction(pin: int, direction: str) -> None:
    GpioPin(pin).set_direction(direction)


def _gpio_write(pin: int, value: int) -> None:
    GpioPin(pin).write(value)
