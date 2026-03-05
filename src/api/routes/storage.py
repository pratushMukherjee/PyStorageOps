"""Storage management REST API routes."""

from fastapi import APIRouter, HTTPException

from ..models import (
    BlockReadResponse,
    BlockWriteRequest,
    VolumeCreate,
    VolumeList,
    VolumeResponse,
)

router = APIRouter(prefix="/api/v1/storage", tags=["storage"])


def _get_volume_response(vol_id: int, name: str, device) -> VolumeResponse:
    return VolumeResponse(
        id=vol_id,
        name=name,
        size_blocks=device.block_count,
        block_size=device.block_size,
        used_blocks=device.used_blocks,
        status="online",
    )


@router.post("/volumes", response_model=VolumeResponse, status_code=201)
async def create_volume(req: VolumeCreate):
    """Create a new storage volume."""
    from ..app import storage_manager

    try:
        vol_id, device = storage_manager.create_volume(
            req.name, req.size_blocks, req.block_size
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return _get_volume_response(vol_id, req.name, device)


@router.get("/volumes", response_model=VolumeList)
async def list_volumes():
    """List all storage volumes."""
    from ..app import storage_manager

    volumes = []
    for vol_id, (name, device) in storage_manager.volumes.items():
        volumes.append(_get_volume_response(vol_id, name, device))
    return VolumeList(volumes=volumes, total=len(volumes))


@router.get("/volumes/{volume_id}", response_model=VolumeResponse)
async def get_volume(volume_id: int):
    """Get details of a specific volume."""
    from ..app import storage_manager

    if volume_id not in storage_manager.volumes:
        raise HTTPException(status_code=404, detail="Volume not found")
    name, device = storage_manager.volumes[volume_id]
    return _get_volume_response(volume_id, name, device)


@router.delete("/volumes/{volume_id}", status_code=204)
async def delete_volume(volume_id: int):
    """Delete a storage volume."""
    from ..app import storage_manager

    if volume_id not in storage_manager.volumes:
        raise HTTPException(status_code=404, detail="Volume not found")
    storage_manager.delete_volume(volume_id)


@router.post("/volumes/{volume_id}/blocks", response_model=BlockReadResponse)
async def write_block(volume_id: int, req: BlockWriteRequest):
    """Write data to a block in a volume."""
    from ..app import storage_manager

    if volume_id not in storage_manager.volumes:
        raise HTTPException(status_code=404, detail="Volume not found")
    _, device = storage_manager.volumes[volume_id]

    try:
        data = bytes.fromhex(req.data_hex)
        device.write_block(req.block_index, data)
        from ...core.data_integrity import DataIntegrity
        stored = device.read_block(req.block_index)
        return BlockReadResponse(
            block_index=req.block_index,
            data_hex=stored.hex(),
            crc32=DataIntegrity.crc32(stored),
        )
    except (IndexError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/volumes/{volume_id}/blocks/{block_index}", response_model=BlockReadResponse)
async def read_block(volume_id: int, block_index: int):
    """Read a block from a volume."""
    from ..app import storage_manager

    if volume_id not in storage_manager.volumes:
        raise HTTPException(status_code=404, detail="Volume not found")
    _, device = storage_manager.volumes[volume_id]

    try:
        data = device.read_block(block_index)
        from ...core.data_integrity import DataIntegrity
        return BlockReadResponse(
            block_index=block_index,
            data_hex=data.hex(),
            crc32=DataIntegrity.crc32(data),
        )
    except IndexError as e:
        raise HTTPException(status_code=400, detail=str(e))
