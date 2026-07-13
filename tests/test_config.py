"""Tests for the optional API key and configuration surface."""
from fastapi.testclient import TestClient

import config
from main import app

client = TestClient(app)


def test_api_open_by_default():
    assert client.get("/api/conditions").status_code == 200


def test_api_key_enforced_when_configured(monkeypatch):
    monkeypatch.setattr(config, "API_KEY", "s3cret")
    assert client.get("/api/conditions").status_code == 401
    assert client.get("/api/conditions", headers={"X-API-Key": "wrong"}).status_code == 401
    assert client.get("/api/conditions", headers={"X-API-Key": "s3cret"}).status_code == 200
    assert client.get(
        "/api/conditions", headers={"Authorization": "Bearer s3cret"}
    ).status_code == 200


def test_health_stays_open_with_api_key(monkeypatch):
    monkeypatch.setattr(config, "API_KEY", "s3cret")
    assert client.get("/health").status_code == 200
