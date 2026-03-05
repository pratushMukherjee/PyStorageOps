"""
Prometheus metrics collector for storage monitoring.

Collects and exposes IOPS, latency, throughput, and capacity metrics.
"""

from prometheus_client import Counter, Gauge, Histogram, CollectorRegistry

registry = CollectorRegistry()

# Capacity metrics
TOTAL_CAPACITY = Gauge(
    "storage_total_capacity_bytes",
    "Total storage capacity in bytes",
    registry=registry,
)
USED_CAPACITY = Gauge(
    "storage_used_capacity_bytes",
    "Used storage capacity in bytes",
    registry=registry,
)
VOLUME_COUNT = Gauge(
    "storage_volume_count",
    "Number of active storage volumes",
    registry=registry,
)

# I/O metrics
IO_OPS = Counter(
    "storage_io_operations_total",
    "Total I/O operations",
    ["operation", "volume"],
    registry=registry,
)
IO_BYTES = Counter(
    "storage_io_bytes_total",
    "Total bytes transferred",
    ["direction", "volume"],
    registry=registry,
)
IO_LATENCY = Histogram(
    "storage_io_latency_seconds",
    "I/O operation latency in seconds",
    ["operation"],
    buckets=[0.0001, 0.0005, 0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0],
    registry=registry,
)

# Health metrics
DEVICE_HEALTH = Gauge(
    "storage_device_health",
    "Device health status (1=healthy, 0=degraded)",
    ["device"],
    registry=registry,
)


class MetricsCollector:
    """Collects and updates storage metrics for Prometheus."""

    def record_read(self, volume_name: str, bytes_count: int, latency_s: float):
        IO_OPS.labels(operation="read", volume=volume_name).inc()
        IO_BYTES.labels(direction="read", volume=volume_name).inc(bytes_count)
        IO_LATENCY.labels(operation="read").observe(latency_s)

    def record_write(self, volume_name: str, bytes_count: int, latency_s: float):
        IO_OPS.labels(operation="write", volume=volume_name).inc()
        IO_BYTES.labels(direction="write", volume=volume_name).inc(bytes_count)
        IO_LATENCY.labels(operation="write").observe(latency_s)

    def update_capacity(self, total_bytes: int, used_bytes: int, volume_count: int):
        TOTAL_CAPACITY.set(total_bytes)
        USED_CAPACITY.set(used_bytes)
        VOLUME_COUNT.set(volume_count)

    def set_device_health(self, device_name: str, healthy: bool):
        DEVICE_HEALTH.labels(device=device_name).set(1 if healthy else 0)
