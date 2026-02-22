"""Tests for the device driver framework (stdlib/drivers)."""
import pytest
import sys
import os
import platform

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from nlpl.stdlib.drivers import (
    CharDevice,
    BlockDevice,
    GpioPin,
    I2cDevice,
    SpiDevice,
    InterruptHandler,
    DriverError,
    register_driver_functions,
    list_irqs,
    read_device_tree_string,
    list_devices_by_class,
)
from nlpl.runtime.runtime import Runtime
from nlpl.stdlib import register_stdlib


IS_LINUX = platform.system().lower() == "linux"


# ---------------------------------------------------------------------------
# CharDevice
# ---------------------------------------------------------------------------

class TestCharDevice:
    def test_not_open_initially(self):
        dev = CharDevice("/dev/zero")
        assert dev.is_open() is False

    def test_open_and_close_dev_zero(self):
        if not IS_LINUX:
            pytest.skip("Linux-only: /dev/zero")
        dev = CharDevice("/dev/zero")
        dev.open()
        assert dev.is_open() is True
        dev.close()
        assert dev.is_open() is False

    def test_read_dev_zero_returns_bytes(self):
        if not IS_LINUX:
            pytest.skip("Linux-only: /dev/zero")
        dev = CharDevice("/dev/zero")
        dev.open()
        data = dev.read(8)
        dev.close()
        assert len(data) == 8
        assert all(b == 0 for b in data)

    def test_read_dev_null_returns_empty(self):
        if not IS_LINUX:
            pytest.skip("Linux-only: /dev/null")
        dev = CharDevice("/dev/null")
        dev.open()
        data = dev.read(8)
        dev.close()
        assert len(data) == 0

    def test_write_dev_null_succeeds(self):
        if not IS_LINUX:
            pytest.skip("Linux-only: /dev/null")
        dev = CharDevice("/dev/null", flags=os.O_WRONLY)
        dev.open()
        written = dev.write(b"hello world")
        dev.close()
        assert written >= 0

    def test_open_nonexistent_raises(self):
        dev = CharDevice("/dev/no_such_device_xyzzy_12345")
        with pytest.raises((DriverError, OSError)):
            dev.open()

    def test_read_without_open_raises(self):
        dev = CharDevice("/dev/zero")
        with pytest.raises((DriverError, OSError)):
            dev.read(4)

    def test_context_manager(self):
        if not IS_LINUX:
            pytest.skip("Linux-only: /dev/zero")
        with CharDevice("/dev/zero") as dev:
            data = dev.read(4)
        assert not dev.is_open()
        assert len(data) == 4


# ---------------------------------------------------------------------------
# BlockDevice
# ---------------------------------------------------------------------------

class TestBlockDevice:
    def test_not_open_initially(self):
        bd = BlockDevice("/dev/sda")
        assert bd.is_open() is False

    def test_sector_size_constant(self):
        assert BlockDevice.SECTOR_SIZE == 512

    def test_open_nonexistent_raises(self):
        bd = BlockDevice("/dev/no_such_block_device_xyzzy")
        with pytest.raises((DriverError, OSError, FileNotFoundError)):
            bd.open()


# ---------------------------------------------------------------------------
# GpioPin
# ---------------------------------------------------------------------------

class TestGpioPin:
    def test_construction(self):
        pin = GpioPin(17)
        assert pin.pin == 17

    def test_export_requires_linux(self):
        if not IS_LINUX:
            with pytest.raises(DriverError):
                GpioPin(0).export()
        else:
            # On Linux we can't actually toggle real GPIO without root;
            # just confirm the DriverError message is sensible if sysfs missing
            pin = GpioPin(9999)
            try:
                pin.export()
            except (DriverError, OSError, PermissionError):
                pass  # expected without root / real hardware

    def test_read_requires_export_first(self):
        if not IS_LINUX:
            pytest.skip("Linux-only")
        pin = GpioPin(9999)
        with pytest.raises((DriverError, OSError, FileNotFoundError)):
            pin.read()


# ---------------------------------------------------------------------------
# I2cDevice
# ---------------------------------------------------------------------------

class TestI2cDevice:
    def test_construction(self):
        dev = I2cDevice(bus=1, address=0x68)
        assert dev.bus == 1
        assert dev.address == 0x68

    def test_not_open_initially(self):
        dev = I2cDevice(1, 0x68)
        assert dev.is_open() is False

    def test_requires_linux(self):
        if not IS_LINUX:
            dev = I2cDevice(1, 0x68)
            with pytest.raises(DriverError):
                dev.open()

    def test_open_nonexistent_bus_raises(self):
        if not IS_LINUX:
            pytest.skip("Linux-only")
        dev = I2cDevice(bus=9999, address=0x01)
        with pytest.raises((DriverError, OSError, FileNotFoundError)):
            dev.open()


# ---------------------------------------------------------------------------
# SpiDevice
# ---------------------------------------------------------------------------

class TestSpiDevice:
    def test_construction(self):
        dev = SpiDevice(bus=0, cs=0)
        assert dev.bus == 0
        assert dev.cs == 0

    def test_not_open_initially(self):
        dev = SpiDevice(0, 0)
        assert dev.is_open() is False

    def test_mode_constants(self):
        assert SpiDevice.MODE_0 == 0
        assert SpiDevice.MODE_1 == 1
        assert SpiDevice.MODE_2 == 2
        assert SpiDevice.MODE_3 == 3

    def test_requires_linux(self):
        if not IS_LINUX:
            dev = SpiDevice(0, 0)
            with pytest.raises(DriverError):
                dev.open()

    def test_open_nonexistent_device_raises(self):
        if not IS_LINUX:
            pytest.skip("Linux-only")
        dev = SpiDevice(bus=9999, cs=9999)
        with pytest.raises((DriverError, OSError, FileNotFoundError)):
            dev.open()


# ---------------------------------------------------------------------------
# InterruptHandler
# ---------------------------------------------------------------------------

class TestInterruptHandler:
    def test_construction(self):
        handler = InterruptHandler()
        assert handler is not None

    def test_register_and_trigger(self):
        if not IS_LINUX:
            pytest.skip("Linux-only: POSIX signals")
        import signal
        received = []

        handler = InterruptHandler()
        # Callbacks are invoked with zero arguments by the driver; record the
        # signal number explicitly in the closure.
        handler.register(signal.SIGUSR1, lambda: received.append(signal.SIGUSR1))
        handler.activate()
        handler.trigger(signal.SIGUSR1)

        import time
        time.sleep(0.05)
        handler.deactivate()

        assert len(received) > 0
        assert received[0] == signal.SIGUSR1

    def test_deactivate_without_activate_is_safe(self):
        handler = InterruptHandler()
        handler.deactivate()  # should not raise

    def test_trigger_without_registered_handler_is_safe(self):
        if not IS_LINUX:
            pytest.skip("Linux-only")
        import signal
        handler = InterruptHandler()
        handler.activate()
        try:
            handler.trigger(signal.SIGUSR2)
        except Exception:
            pass
        handler.deactivate()


# ---------------------------------------------------------------------------
# IRQ utilities
# ---------------------------------------------------------------------------

class TestIrqInfo:
    def test_list_irqs_returns_list(self):
        if not IS_LINUX:
            pytest.skip("Linux-only: /proc/interrupts")
        irqs = list_irqs()
        assert isinstance(irqs, list)

    def test_list_irqs_dicts_have_irq_field(self):
        if not IS_LINUX:
            pytest.skip("Linux-only: /proc/interrupts")
        irqs = list_irqs()
        if irqs:
            first = irqs[0]
            assert "irq" in first


# ---------------------------------------------------------------------------
# Device tree access
# ---------------------------------------------------------------------------

class TestDeviceTreeAccess:
    def test_missing_node_returns_none_or_raises_gracefully(self):
        result = read_device_tree_string(
            "node/that/does/not/exist_xyzzy_12345", "compatible"
        )
        # Should return None or empty string, not crash
        assert result is None or isinstance(result, str)


# ---------------------------------------------------------------------------
# Sysfs device listing
# ---------------------------------------------------------------------------

class TestSysfsDeviceListing:
    def test_list_devices_by_class_net(self):
        if not IS_LINUX:
            pytest.skip("Linux-only: /sys/class/net")
        devices = list_devices_by_class("net")
        assert isinstance(devices, list)

    def test_list_devices_unknown_class_returns_empty(self):
        devices = list_devices_by_class("no_such_class_xyzzy_12345")
        assert isinstance(devices, list)
        assert len(devices) == 0


# ---------------------------------------------------------------------------
# register_driver_functions
# ---------------------------------------------------------------------------

class TestDriverRegistration:
    EXPECTED_FUNCTIONS = [
        "open_char_device",
        "close_char_device",
        "read_char_device",
        "write_char_device",
        "char_device_is_open",
        "open_block_device",
        "close_block_device",
        "read_sector",
        "block_device_size",
        "enumerate_pci",
        "open_i2c_device",
        "close_i2c_device",
        "i2c_read",
        "i2c_write",
        "open_spi_device",
        "close_spi_device",
        "spi_transfer",
        "gpio_export",
        "gpio_unexport",
        "gpio_set_direction",
        "gpio_read",
        "gpio_write",
        "list_gpio_chips",
        "list_irqs",
        "get_irq_affinity",
        "set_irq_affinity",
        "create_interrupt_handler",
        "register_interrupt",
        "activate_interrupts",
        "deactivate_interrupts",
        "trigger_interrupt",
        "read_device_tree_property",
        "read_device_tree_string",
        "list_device_tree_children",
        "list_devices_by_class",
        "find_device_by_attr",
        "get_device_attribute",
    ]

    def test_all_expected_functions_registered(self):
        runtime = Runtime()
        register_driver_functions(runtime)
        registered = set(runtime.functions.keys())
        for fn_name in self.EXPECTED_FUNCTIONS:
            assert fn_name in registered, f"Missing: {fn_name}"

    def test_registration_via_register_stdlib(self):
        runtime = Runtime()
        register_stdlib(runtime)
        registered = set(runtime.functions.keys())
        assert "open_char_device" in registered
        assert "gpio_read" in registered
        assert "enumerate_pci" in registered

    def test_double_registration_is_safe(self):
        runtime = Runtime()
        register_driver_functions(runtime)
        register_driver_functions(runtime)  # should not raise
        assert "open_char_device" in runtime.functions
