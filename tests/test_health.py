"""Tests for health check endpoint."""

from fastapi.testclient import TestClient

from fingerprint_check.main import app

client = TestClient(app)


def test_health_check() -> None:
    """Ensure GET /health returns 200 with status ok."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
