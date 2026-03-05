"""Pydantic models for API request/response validation."""

from pydantic import BaseModel, Field


class VolumeCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=64)
    size_blocks: int = Field(..., gt=0, le=1_000_000)
    block_size: int = Field(default=4096, gt=0)


class VolumeResponse(BaseModel):
    id: int
    name: str
    size_blocks: int
    block_size: int
    used_blocks: int
    status: str


class VolumeList(BaseModel):
    volumes: list[VolumeResponse]
    total: int


class BlockWriteRequest(BaseModel):
    block_index: int = Field(..., ge=0)
    data_hex: str = Field(..., description="Hex-encoded block data")


class BlockReadResponse(BaseModel):
    block_index: int
    data_hex: str
    crc32: int


class HealthResponse(BaseModel):
    status: str
    volumes_count: int
    total_capacity_bytes: int
    used_capacity_bytes: int
    uptime_seconds: float


class ErrorResponse(BaseModel):
    detail: str
