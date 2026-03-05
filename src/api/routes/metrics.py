"""Prometheus metrics endpoint."""

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

router = APIRouter(tags=["metrics"])


@router.get("/metrics", response_class=PlainTextResponse)
async def prometheus_metrics():
    """Expose Prometheus-compatible metrics."""
    from ..app import storage_manager

    lines = []
    lines.append("# HELP storage_volumes_total Total number of volumes")
    lines.append("# TYPE storage_volumes_total gauge")
    lines.append(f"storage_volumes_total {len(storage_manager.volumes)}")

    total_capacity = 0
    used_capacity = 0
    total_reads = 0
    total_writes = 0

    for vol_id, (name, device) in storage_manager.volumes.items():
        total_capacity += device.total_capacity
        used_capacity += device.used_blocks * device.block_size
        total_reads += device.stats.reads
        total_writes += device.stats.writes

        lines.append(f'# HELP storage_volume_used_blocks Used blocks per volume')
        lines.append(f'# TYPE storage_volume_used_blocks gauge')
        lines.append(
            f'storage_volume_used_blocks{{volume="{name}",id="{vol_id}"}} {device.used_blocks}'
        )

    lines.append("# HELP storage_capacity_bytes_total Total storage capacity in bytes")
    lines.append("# TYPE storage_capacity_bytes_total gauge")
    lines.append(f"storage_capacity_bytes_total {total_capacity}")

    lines.append("# HELP storage_used_bytes_total Total used storage in bytes")
    lines.append("# TYPE storage_used_bytes_total gauge")
    lines.append(f"storage_used_bytes_total {used_capacity}")

    lines.append("# HELP storage_reads_total Total read operations")
    lines.append("# TYPE storage_reads_total counter")
    lines.append(f"storage_reads_total {total_reads}")

    lines.append("# HELP storage_writes_total Total write operations")
    lines.append("# TYPE storage_writes_total counter")
    lines.append(f"storage_writes_total {total_writes}")

    return "\n".join(lines) + "\n"
