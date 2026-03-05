"""Tests for the FastAPI REST API."""

import pytest
from fastapi.testclient import TestClient

from src.api.app import app, storage_manager


@pytest.fixture(autouse=True)
def reset_storage():
    """Reset storage manager between tests."""
    storage_manager.volumes.clear()
    storage_manager._next_id = 1
    yield


@pytest.fixture
def client():
    return TestClient(app)


class TestAPIRoot:
    def test_root(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["service"] == "PyStorageOps"


class TestStorageAPI:
    def test_create_volume(self, client):
        resp = client.post("/api/v1/storage/volumes", json={
            "name": "vol1",
            "size_blocks": 100,
            "block_size": 4096,
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "vol1"
        assert data["size_blocks"] == 100

    def test_list_volumes(self, client):
        client.post("/api/v1/storage/volumes", json={"name": "v1", "size_blocks": 50})
        client.post("/api/v1/storage/volumes", json={"name": "v2", "size_blocks": 50})
        resp = client.get("/api/v1/storage/volumes")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 2

    def test_get_volume(self, client):
        client.post("/api/v1/storage/volumes", json={"name": "vol1", "size_blocks": 100})
        resp = client.get("/api/v1/storage/volumes/1")
        assert resp.status_code == 200
        assert resp.json()["name"] == "vol1"

    def test_get_volume_not_found(self, client):
        resp = client.get("/api/v1/storage/volumes/999")
        assert resp.status_code == 404

    def test_delete_volume(self, client):
        client.post("/api/v1/storage/volumes", json={"name": "del", "size_blocks": 10})
        resp = client.delete("/api/v1/storage/volumes/1")
        assert resp.status_code == 204
        resp = client.get("/api/v1/storage/volumes/1")
        assert resp.status_code == 404

    def test_duplicate_volume_name(self, client):
        client.post("/api/v1/storage/volumes", json={"name": "dup", "size_blocks": 10})
        resp = client.post("/api/v1/storage/volumes", json={"name": "dup", "size_blocks": 10})
        assert resp.status_code == 400

    def test_write_and_read_block(self, client):
        client.post("/api/v1/storage/volumes", json={"name": "io", "size_blocks": 10})
        # Write
        resp = client.post("/api/v1/storage/volumes/1/blocks", json={
            "block_index": 0,
            "data_hex": "deadbeef" * 512,
        })
        assert resp.status_code == 200
        assert resp.json()["block_index"] == 0

        # Read
        resp = client.get("/api/v1/storage/volumes/1/blocks/0")
        assert resp.status_code == 200
        assert resp.json()["crc32"] > 0


class TestHealthAPI:
    def test_health_endpoint(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert "uptime_seconds" in data


class TestMetricsAPI:
    def test_metrics_endpoint(self, client):
        resp = client.get("/metrics")
        assert resp.status_code == 200
        assert "storage_volumes_total" in resp.text
