"""
SCSI storage driver simulation.

Simulates SCSI primary command set including INQUIRY, READ CAPACITY,
READ(10), WRITE(10), and TEST UNIT READY.
"""

from dataclasses import dataclass

from ..core.block_device import BlockDevice
from .base import DeviceInfo, DeviceStatus, StorageDriver


@dataclass
class SCSIInquiryData:
    """SCSI INQUIRY response data."""
    peripheral_type: int = 0x00  # Direct access block device
    vendor_id: str = "IBM"
    product_id: str = "DS8000-Sim"
    product_rev: str = "1.0"
    serial_number: str = ""


@dataclass
class SCSIReadCapacity:
    """SCSI READ CAPACITY(10) response."""
    last_lba: int = 0
    block_size: int = 0


class SCSIDriver(StorageDriver):
    """Simulates a SCSI block device."""

    def __init__(self, device: BlockDevice, vendor: str = "IBM", product: str = "DS8000-Sim"):
        self._device = device
        self._vendor = vendor
        self._product = product
        self._serial = f"SCSI-{id(device):08X}"
        self._status = DeviceStatus.READY
        self._sense_data: bytes = b""

    def inquiry(self) -> SCSIInquiryData:
        """SCSI INQUIRY command."""
        return SCSIInquiryData(
            vendor_id=self._vendor,
            product_id=self._product,
            serial_number=self._serial,
        )

    def identify(self) -> DeviceInfo:
        """Identify via SCSI INQUIRY."""
        inq = self.inquiry()
        return DeviceInfo(
            vendor=inq.vendor_id,
            model=inq.product_id,
            serial=inq.serial_number,
            firmware_rev=inq.product_rev,
            capacity_bytes=self._device.total_capacity,
            block_size=self._device.block_size,
            protocol="SCSI",
        )

    def read_capacity(self) -> SCSIReadCapacity:
        """SCSI READ CAPACITY(10) command."""
        return SCSIReadCapacity(
            last_lba=self._device.block_count - 1,
            block_size=self._device.block_size,
        )

    def test_unit_ready(self) -> bool:
        """SCSI TEST UNIT READY command."""
        return self._status == DeviceStatus.READY

    def read(self, lba: int, block_count: int) -> bytes:
        """SCSI READ(10) command."""
        if not self.test_unit_ready():
            raise IOError("Unit not ready")
        return self._device.read_blocks(lba, block_count)

    def write(self, lba: int, data: bytes) -> int:
        """SCSI WRITE(10) command."""
        if not self.test_unit_ready():
            raise IOError("Unit not ready")
        self._device.write_blocks(lba, data)
        return (len(data) + self._device.block_size - 1) // self._device.block_size

    def flush(self) -> bool:
        """SCSI SYNCHRONIZE CACHE command."""
        return self.test_unit_ready()

    def get_status(self) -> DeviceStatus:
        return self._status

    def get_capacity(self) -> tuple[int, int]:
        return self._device.block_count, self._device.block_size

    def request_sense(self) -> bytes:
        """SCSI REQUEST SENSE command — returns sense data from last error."""
        return self._sense_data
