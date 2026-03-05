"""
RAID implementations: RAID 0 (striping), RAID 1 (mirroring), RAID 5 (striped parity).

Each RAID level manages a set of underlying BlockDevice instances and provides
a unified read/write interface with the reliability characteristics of its level.
"""

from .block_device import BlockDevice


class RAID0:
    """RAID 0 — Striping across N devices for maximum throughput.

    Data is interleaved across all devices at the block level.
    No redundancy: any single device failure loses all data.
    """

    def __init__(self, devices: list[BlockDevice]):
        if len(devices) < 2:
            raise ValueError("RAID 0 requires at least 2 devices")
        block_size = devices[0].block_size
        if any(d.block_size != block_size for d in devices):
            raise ValueError("All devices must have the same block size")

        self.devices = devices
        self.block_size = block_size
        self.stripe_count = len(devices)
        self.total_blocks = sum(d.block_count for d in devices)

    def _map_block(self, virtual_block: int) -> tuple[int, int]:
        """Map a virtual block index to (device_index, local_block_index)."""
        device_idx = virtual_block % self.stripe_count
        local_block = virtual_block // self.stripe_count
        return device_idx, local_block

    def read_block(self, virtual_block: int) -> bytes:
        device_idx, local_block = self._map_block(virtual_block)
        return self.devices[device_idx].read_block(local_block)

    def write_block(self, virtual_block: int, data: bytes) -> None:
        device_idx, local_block = self._map_block(virtual_block)
        self.devices[device_idx].write_block(local_block, data)


class RAID1:
    """RAID 1 — Mirroring across N devices for redundancy.

    All writes go to every device. Reads come from the primary (first) device.
    Can tolerate N-1 device failures.
    """

    def __init__(self, devices: list[BlockDevice]):
        if len(devices) < 2:
            raise ValueError("RAID 1 requires at least 2 devices")
        block_size = devices[0].block_size
        block_count = devices[0].block_count
        if any(d.block_size != block_size or d.block_count != block_count for d in devices):
            raise ValueError("All devices must have the same block size and count")

        self.devices = devices
        self.block_size = block_size
        self.block_count = block_count

    def read_block(self, block_index: int) -> bytes:
        """Read from the primary device."""
        return self.devices[0].read_block(block_index)

    def read_block_from(self, block_index: int, device_index: int) -> bytes:
        """Read a block from a specific mirror."""
        return self.devices[device_index].read_block(block_index)

    def write_block(self, block_index: int, data: bytes) -> None:
        """Write to all mirrors."""
        for device in self.devices:
            device.write_block(block_index, data)

    def verify_mirrors(self, block_index: int) -> bool:
        """Check that all mirrors have identical data for a block."""
        reference = self.devices[0].read_block(block_index)
        return all(d.read_block(block_index) == reference for d in self.devices[1:])

    def rebuild_device(self, failed_index: int, new_device: BlockDevice) -> None:
        """Rebuild a failed device from a healthy mirror."""
        source_idx = 0 if failed_index != 0 else 1
        source = self.devices[source_idx]
        for block in range(self.block_count):
            data = source.read_block(block)
            new_device.write_block(block, data)
        self.devices[failed_index] = new_device


class RAID5:
    """RAID 5 — Striping with distributed parity.

    Data and parity are distributed across all devices.
    Can tolerate exactly 1 device failure with full data recovery.
    Uses XOR-based parity for simplicity and efficiency.
    """

    def __init__(self, devices: list[BlockDevice]):
        if len(devices) < 3:
            raise ValueError("RAID 5 requires at least 3 devices")
        block_size = devices[0].block_size
        block_count = devices[0].block_count
        if any(d.block_size != block_size or d.block_count != block_count for d in devices):
            raise ValueError("All devices must have the same block size and count")

        self.devices = devices
        self.block_size = block_size
        self.num_devices = len(devices)
        # Usable capacity: (N-1) data blocks per stripe row
        self.data_devices = self.num_devices - 1
        self.rows_per_device = devices[0].block_count
        self.total_data_blocks = self.data_devices * self.rows_per_device

    @staticmethod
    def _xor_blocks(*blocks: bytes) -> bytes:
        """XOR multiple byte strings together for parity."""
        result = bytearray(len(blocks[0]))
        for block in blocks:
            for i, b in enumerate(block):
                result[i] ^= b
        return bytes(result)

    def _parity_device(self, stripe_row: int) -> int:
        """Determine which device holds parity for a given stripe row (rotating)."""
        return stripe_row % self.num_devices

    def _map_block(self, virtual_block: int) -> tuple[int, int]:
        """Map virtual data block -> (device_index, local_block_index)."""
        stripe_row = virtual_block // self.data_devices
        offset_in_row = virtual_block % self.data_devices
        parity_dev = self._parity_device(stripe_row)

        # Data devices are all devices except the parity device for this row
        device_idx = offset_in_row
        if device_idx >= parity_dev:
            device_idx += 1

        return device_idx, stripe_row

    def read_block(self, virtual_block: int) -> bytes:
        if virtual_block < 0 or virtual_block >= self.total_data_blocks:
            raise IndexError(f"Virtual block {virtual_block} out of range")
        device_idx, local_block = self._map_block(virtual_block)
        return self.devices[device_idx].read_block(local_block)

    def write_block(self, virtual_block: int, data: bytes) -> None:
        if virtual_block < 0 or virtual_block >= self.total_data_blocks:
            raise IndexError(f"Virtual block {virtual_block} out of range")

        device_idx, stripe_row = self._map_block(virtual_block)
        parity_dev = self._parity_device(stripe_row)

        # Write data to the target device
        self.devices[device_idx].write_block(stripe_row, data)

        # Recompute parity for the entire stripe row
        data_blocks = []
        for d in range(self.num_devices):
            if d != parity_dev:
                data_blocks.append(self.devices[d].read_block(stripe_row))

        parity = self._xor_blocks(*data_blocks)
        self.devices[parity_dev].write_block(stripe_row, parity)

    def rebuild_device(self, failed_index: int, new_device: BlockDevice) -> None:
        """Rebuild a failed device using XOR of all remaining devices."""
        for row in range(self.rows_per_device):
            surviving = [
                self.devices[d].read_block(row)
                for d in range(self.num_devices)
                if d != failed_index
            ]
            rebuilt = self._xor_blocks(*surviving)
            new_device.write_block(row, rebuilt)
        self.devices[failed_index] = new_device

    def verify_parity(self, stripe_row: int) -> bool:
        """Verify parity is consistent for a given stripe row."""
        all_blocks = [self.devices[d].read_block(stripe_row) for d in range(self.num_devices)]
        xored = self._xor_blocks(*all_blocks)
        return xored == b"\x00" * self.block_size
