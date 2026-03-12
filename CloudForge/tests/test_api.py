"""Integration tests for the Go API server.

These tests verify the API contract using httpx against a running server.
For CI, the server is started in docker-compose.
For local testing, start the server first: cd server && go run .
"""

import os

import httpx
import pytest

API_URL = os.getenv("CLOUDFORGE_API_URL", "http://localhost:8080")


def api_available():
    """Check if the API server is running."""
    try:
        r = httpx.get(f"{API_URL}/health", timeout=2)
        return r.status_code == 200
    except (httpx.ConnectError, httpx.TimeoutException):
        return False


@pytest.mark.skipif(not api_available(), reason="API server not running")
class TestAPIIntegration:
    def test_health(self):
        r = httpx.get(f"{API_URL}/health")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "healthy"
        assert data["service"] == "CloudForge API"

    def test_create_and_list_apps(self):
        # Create
        r = httpx.post(f"{API_URL}/api/v1/apps", json={"name": "test-integration", "language": "python"})
        assert r.status_code == 201
        app_id = r.json()["app"]["id"]

        # List
        r = httpx.get(f"{API_URL}/api/v1/apps")
        assert r.status_code == 200
        names = [a["name"] for a in r.json()["apps"]]
        assert "test-integration" in names

        # Cleanup
        httpx.delete(f"{API_URL}/api/v1/apps/{app_id}")

    def test_deploy_and_rollback(self):
        # Create app
        r = httpx.post(f"{API_URL}/api/v1/apps", json={"name": "test-deploy", "language": "go"})
        app_id = r.json()["app"]["id"]

        # Deploy v1
        r = httpx.post(f"{API_URL}/api/v1/apps/{app_id}/deploy")
        assert r.status_code == 202
        assert r.json()["deployment"]["version"] == 1

        # Deploy v2
        import time
        time.sleep(2)
        r = httpx.post(f"{API_URL}/api/v1/apps/{app_id}/deploy")
        assert r.json()["deployment"]["version"] == 2

        # Rollback
        time.sleep(2)
        r = httpx.post(f"{API_URL}/api/v1/apps/{app_id}/rollback")
        assert r.status_code == 200

        # Cleanup
        httpx.delete(f"{API_URL}/api/v1/apps/{app_id}")

    def test_env_vars(self):
        r = httpx.post(f"{API_URL}/api/v1/apps", json={"name": "test-env", "language": "node"})
        app_id = r.json()["app"]["id"]

        # Set env var
        r = httpx.post(f"{API_URL}/api/v1/apps/{app_id}/env", json={"key": "DB_HOST", "value": "localhost"})
        assert r.status_code == 200

        # Get env vars
        r = httpx.get(f"{API_URL}/api/v1/apps/{app_id}/env")
        assert r.status_code == 200
        keys = [v["key"] for v in r.json()["env_vars"]]
        assert "DB_HOST" in keys

        # Cleanup
        httpx.delete(f"{API_URL}/api/v1/apps/{app_id}")
