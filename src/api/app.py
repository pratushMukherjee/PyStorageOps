"""
FastAPI application for PyStorageOps REST API.

Provides storage volume management, health checks, and Prometheus metrics.
"""

from fastapi import FastAPI

from ..core.block_device import BlockDevice
from .routes import health, metrics, storage


class StorageManager:
    """Manages storage volumes and their lifecycle."""

    def __init__(self):
        self.volumes: dict[int, tuple[str, BlockDevice]] = {}
        self._next_id = 1

    def create_volume(self, name: str, size_blocks: int, block_size: int = 4096) -> tuple[int, BlockDevice]:
        for _, (existing_name, _) in self.volumes.items():
            if existing_name == name:
                raise ValueError(f"Volume '{name}' already exists")

        device = BlockDevice(name=name, block_size=block_size, block_count=size_blocks)
        vol_id = self._next_id
        self._next_id += 1
        self.volumes[vol_id] = (name, device)
        return vol_id, device

    def delete_volume(self, volume_id: int) -> None:
        self.volumes.pop(volume_id, None)

    def get_volume(self, volume_id: int) -> tuple[str, BlockDevice] | None:
        return self.volumes.get(volume_id)


storage_manager = StorageManager()

app = FastAPI(
    title="PyStorageOps API",
    description="Storage management, monitoring, and automation toolkit",
    version="1.0.0",
)

app.include_router(storage.router)
app.include_router(health.router)
app.include_router(metrics.router)


@app.get("/")
async def root():
    return {
        "service": "PyStorageOps",
        "version": "1.0.0",
        "docs": "/docs",
    }
