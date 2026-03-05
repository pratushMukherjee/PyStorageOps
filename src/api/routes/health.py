"""Health check and system status endpoints."""

import time

from fastapi import APIRouter

from ..models import HealthResponse

router = APIRouter(tags=["health"])

_start_time = time.time()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """System health check endpoint."""
    from ..app import storage_manager

    total_capacity = 0
    used_capacity = 0
    for _, (_, device) in storage_manager.volumes.items():
        total_capacity += device.total_capacity
        used_capacity += device.used_blocks * device.block_size

    return HealthResponse(
        status="healthy",
        volumes_count=len(storage_manager.volumes),
        total_capacity_bytes=total_capacity,
        used_capacity_bytes=used_capacity,
        uptime_seconds=time.time() - _start_time,
    )
