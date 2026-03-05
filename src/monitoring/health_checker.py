"""
Storage health monitoring with configurable thresholds.

Monitors device utilization, I/O error rates, and integrity status.
"""

from dataclasses import dataclass
from enum import Enum

from ..core.block_device import BlockDevice


class HealthStatus(Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class HealthReport:
    device_name: str
    status: HealthStatus
    utilization_pct: float
    checks: dict[str, bool]
    message: str


class HealthChecker:
    """Monitors storage device health against configurable thresholds."""

    def __init__(
        self,
        utilization_warn: float = 0.80,
        utilization_crit: float = 0.95,
    ):
        self.utilization_warn = utilization_warn
        self.utilization_crit = utilization_crit

    def check_device(self, device: BlockDevice) -> HealthReport:
        """Run all health checks on a block device."""
        checks = {}
        utilization = device.utilization

        checks["utilization_ok"] = utilization < self.utilization_warn
        checks["capacity_available"] = device.free_blocks > 0
        checks["io_functional"] = self._test_io(device)

        if utilization >= self.utilization_crit:
            status = HealthStatus.CRITICAL
            message = f"Critical: {utilization:.1%} utilization"
        elif utilization >= self.utilization_warn:
            status = HealthStatus.WARNING
            message = f"Warning: {utilization:.1%} utilization"
        elif not all(checks.values()):
            status = HealthStatus.WARNING
            failed = [k for k, v in checks.items() if not v]
            message = f"Warning: failed checks: {', '.join(failed)}"
        else:
            status = HealthStatus.HEALTHY
            message = "All checks passed"

        return HealthReport(
            device_name=device.name,
            status=status,
            utilization_pct=utilization * 100,
            checks=checks,
            message=message,
        )

    def _test_io(self, device: BlockDevice) -> bool:
        """Verify basic I/O works by writing and reading a test pattern."""
        test_block = device.block_count - 1
        test_data = b"\xAA" * device.block_size
        try:
            original = device.read_block(test_block)
            device.write_block(test_block, test_data)
            readback = device.read_block(test_block)
            device.write_block(test_block, original)  # Restore
            return readback == test_data
        except Exception:
            return False
