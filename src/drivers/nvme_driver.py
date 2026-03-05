"""
NVMe storage driver simulation.

Simulates the NVMe command set including Identify, Read, Write, Flush,
and namespace management. Operates on a backing BlockDevice.
"""

import time
from dataclasses import dataclass, field

from ..core.block_device import BlockDevice
from .base import DeviceInfo, DeviceStatus, StorageDriver


@dataclass
class NVMeNamespace:
    nsid: int
    size_blocks: int
    block_size: int
    utilization: float = 0.0


@dataclass
class NVMeSmartLog:
    """SMART / Health Information (NVMe spec)."""
    critical_warning: int = 0
    temperature_kelvin: int = 310
    available_spare_pct: int = 100
    data_units_read: int = 0
    data_units_written: int = 0
    host_read_commands: int = 0
    host_write_commands: int = 0
    power_on_hours: int = 0


class NVMeDriver(StorageDriver):
    """Simulates an NVMe storage device with command set."""

    def __init__(self, device: BlockDevice, vendor: str = "IBM", model: str = "FlashSystem-Sim"):
        self._device = device
        self._vendor = vendor
        self._model = model
        self._serial = f"NVM-{id(device):08X}"
        self._firmware = "1.0.0"
        self._status = DeviceStatus.READY
        self._smart = NVMeSmartLog()
        self._start_time = time.time()

    def identify(self) -> DeviceInfo:
        """NVMe Identify Controller command."""
        return DeviceInfo(
            vendor=self._vendor,
            model=self._model,
            serial=self._serial,
            firmware_rev=self._firmware,
            capacity_bytes=self._device.total_capacity,
            block_size=self._device.block_size,
            protocol="NVMe",
        )

    def identify_namespace(self, nsid: int = 1) -> NVMeNamespace:
        """NVMe Identify Namespace command."""
        return NVMeNamespace(
            nsid=nsid,
            size_blocks=self._device.block_count,
            block_size=self._device.block_size,
            utilization=self._device.utilization,
        )

    def read(self, lba: int, block_count: int) -> bytes:
        """NVMe Read command."""
        if self._status != DeviceStatus.READY:
            raise IOError(f"Device not ready: {self._status.value}")

        data = self._device.read_blocks(lba, block_count)
        self._smart.host_read_commands += 1
        self._smart.data_units_read += block_count
        return data

    def write(self, lba: int, data: bytes) -> int:
        """NVMe Write command. Returns number of blocks written."""
        if self._status != DeviceStatus.READY:
            raise IOError(f"Device not ready: {self._status.value}")

        self._device.write_blocks(lba, data)
        blocks_written = (len(data) + self._device.block_size - 1) // self._device.block_size
        self._smart.host_write_commands += 1
        self._smart.data_units_written += blocks_written
        return blocks_written

    def flush(self) -> bool:
        """NVMe Flush command — ensures data is persisted."""
        if self._status != DeviceStatus.READY:
            return False
        return True

    def get_status(self) -> DeviceStatus:
        return self._status

    def get_capacity(self) -> tuple[int, int]:
        return self._device.block_count, self._device.block_size

    def get_smart_log(self) -> NVMeSmartLog:
        """NVMe Get Log Page — SMART/Health."""
        elapsed = time.time() - self._start_time
        self._smart.power_on_hours = int(elapsed / 3600)
        return self._smart

    def format_namespace(self, nsid: int = 1) -> bool:
        """NVMe Format NVM command — secure erase."""
        self._device.zero_all()
        return True
