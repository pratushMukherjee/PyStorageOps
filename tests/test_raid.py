"""Tests for RAID 0, 1, and 5 implementations."""

import pytest

from src.core.block_device import BlockDevice
from src.core.raid import RAID0, RAID1, RAID5


class TestRAID0:
    def test_requires_two_devices(self):
        with pytest.raises(ValueError):
            RAID0([BlockDevice("solo", block_size=512, block_count=10)])

    def test_stripe_write_read(self, raid_devices):
        raid = RAID0(raid_devices)
        data = b"\xAA" * 4096
        raid.write_block(0, data)
        assert raid.read_block(0) == data

    def test_data_distributed_across_devices(self, raid_devices):
        raid = RAID0(raid_devices)
        for i in range(8):
            raid.write_block(i, bytes([i]) * 4096)

        # Block 0 -> device 0, block 1 -> device 1, etc.
        assert raid_devices[0].read_block(0) == b"\x00" * 4096
        assert raid_devices[1].read_block(0) == b"\x01" * 4096
        assert raid_devices[2].read_block(0) == b"\x02" * 4096
        assert raid_devices[3].read_block(0) == b"\x03" * 4096

    def test_mismatched_block_size_rejected(self):
        devices = [
            BlockDevice("a", block_size=512, block_count=10),
            BlockDevice("b", block_size=1024, block_count=10),
        ]
        with pytest.raises(ValueError):
            RAID0(devices)


class TestRAID1:
    def test_requires_two_devices(self):
        with pytest.raises(ValueError):
            RAID1([BlockDevice("solo", block_size=512, block_count=10)])

    def test_mirror_write_read(self, raid_devices):
        raid = RAID1(raid_devices[:2])
        data = b"\xBB" * 4096
        raid.write_block(0, data)
        assert raid.read_block(0) == data

    def test_all_mirrors_have_data(self, raid_devices):
        raid = RAID1(raid_devices[:2])
        data = b"\xCC" * 4096
        raid.write_block(5, data)
        assert raid.read_block_from(5, 0) == data
        assert raid.read_block_from(5, 1) == data

    def test_verify_mirrors(self, raid_devices):
        raid = RAID1(raid_devices[:2])
        raid.write_block(0, b"\xDD" * 4096)
        assert raid.verify_mirrors(0) is True

        # Corrupt one mirror
        raid_devices[1]._blocks[0] = b"\xFF" * 4096
        assert raid.verify_mirrors(0) is False

    def test_rebuild_device(self, raid_devices):
        raid = RAID1(raid_devices[:2])
        raid.write_block(0, b"\xEE" * 4096)
        raid.write_block(1, b"\xFF" * 4096)

        new_device = BlockDevice("replacement", block_size=4096, block_count=64)
        raid.rebuild_device(1, new_device)

        assert raid.read_block_from(0, 1) == b"\xEE" * 4096
        assert raid.read_block_from(1, 1) == b"\xFF" * 4096


class TestRAID5:
    def test_requires_three_devices(self):
        devices = [BlockDevice(f"d{i}", block_size=512, block_count=10) for i in range(2)]
        with pytest.raises(ValueError):
            RAID5(devices)

    def test_write_and_read(self, raid_devices):
        raid = RAID5(raid_devices)
        data = b"\x42" * 4096
        raid.write_block(0, data)
        assert raid.read_block(0) == data

    def test_multiple_blocks(self, raid_devices):
        raid = RAID5(raid_devices)
        for i in range(6):
            raid.write_block(i, bytes([i + 1]) * 4096)
        for i in range(6):
            assert raid.read_block(i) == bytes([i + 1]) * 4096

    def test_parity_valid_after_write(self, raid_devices):
        raid = RAID5(raid_devices)
        raid.write_block(0, b"\xAA" * 4096)
        raid.write_block(1, b"\xBB" * 4096)
        raid.write_block(2, b"\xCC" * 4096)
        assert raid.verify_parity(0) is True

    def test_rebuild_after_failure(self, raid_devices):
        raid = RAID5(raid_devices)

        # Write data
        for i in range(6):
            raid.write_block(i, bytes([i + 10]) * 4096)

        # "Fail" device 1 and rebuild
        new_device = BlockDevice("replacement", block_size=4096, block_count=64)
        raid.rebuild_device(1, new_device)

        # Verify all data is still readable
        for i in range(6):
            assert raid.read_block(i) == bytes([i + 10]) * 4096

    def test_out_of_range(self, raid_devices):
        raid = RAID5(raid_devices)
        with pytest.raises(IndexError):
            raid.read_block(raid.total_data_blocks + 1)
