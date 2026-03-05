"""Tests for NVMe and SCSI storage drivers."""

import pytest

from src.core.block_device import BlockDevice
from src.drivers.nvme_driver import NVMeDriver
from src.drivers.scsi_driver import SCSIDriver
from src.drivers.base import DeviceStatus


@pytest.fixture
def nvme():
    device = BlockDevice("nvme-test", block_size=4096, block_count=100)
    return NVMeDriver(device)


@pytest.fixture
def scsi():
    device = BlockDevice("scsi-test", block_size=4096, block_count=100)
    return SCSIDriver(device)


class TestNVMeDriver:
    def test_identify(self, nvme):
        info = nvme.identify()
        assert info.vendor == "IBM"
        assert info.protocol == "NVMe"
        assert info.capacity_bytes == 4096 * 100

    def test_identify_namespace(self, nvme):
        ns = nvme.identify_namespace()
        assert ns.nsid == 1
        assert ns.size_blocks == 100
        assert ns.block_size == 4096

    def test_read_write(self, nvme):
        data = b"\xDE\xAD" * 2048
        blocks_written = nvme.write(0, data)
        assert blocks_written == 1
        result = nvme.read(0, 1)
        assert result[:4096] == data

    def test_flush(self, nvme):
        assert nvme.flush() is True

    def test_get_status(self, nvme):
        assert nvme.get_status() == DeviceStatus.READY

    def test_get_capacity(self, nvme):
        total, block_size = nvme.get_capacity()
        assert total == 100
        assert block_size == 4096

    def test_smart_log(self, nvme):
        nvme.write(0, b"\x00" * 4096)
        nvme.read(0, 1)
        smart = nvme.get_smart_log()
        assert smart.host_write_commands == 1
        assert smart.host_read_commands == 1
        assert smart.data_units_written >= 1

    def test_format_namespace(self, nvme):
        nvme.write(0, b"\xFF" * 4096)
        assert nvme.format_namespace() is True
        data = nvme.read(0, 1)
        assert data == b"\x00" * 4096


class TestSCSIDriver:
    def test_inquiry(self, scsi):
        inq = scsi.inquiry()
        assert inq.vendor_id == "IBM"
        assert inq.product_id == "DS8000-Sim"

    def test_identify(self, scsi):
        info = scsi.identify()
        assert info.protocol == "SCSI"
        assert info.vendor == "IBM"

    def test_read_capacity(self, scsi):
        cap = scsi.read_capacity()
        assert cap.last_lba == 99
        assert cap.block_size == 4096

    def test_test_unit_ready(self, scsi):
        assert scsi.test_unit_ready() is True

    def test_read_write(self, scsi):
        data = b"\xCA\xFE" * 2048
        blocks = scsi.write(0, data)
        assert blocks == 1
        result = scsi.read(0, 1)
        assert result[:4096] == data

    def test_flush(self, scsi):
        assert scsi.flush() is True

    def test_request_sense_empty(self, scsi):
        assert scsi.request_sense() == b""
