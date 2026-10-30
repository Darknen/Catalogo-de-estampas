"""Testes básicos sem inicializar portas ou banco de dados."""
import pytest
from fastapi.testclient import TestClient
from app.server.application import create_app
from app.shared.constants import APP_NAME, APP_VERSION, API_VERSION
from config.settings import Settings


def test_health():
    with TestClient(create_app()) as client:
        result = client.get("/health")
    assert result.status_code == 200
    assert result.json() == {"status": "online", "api_version": API_VERSION}


def test_info():
    with TestClient(create_app()) as client:
        result = client.get("/info")
    assert result.status_code == 200
    assert result.json()["name"] == APP_NAME
    assert result.json()["app_version"] == APP_VERSION
    assert result.json()["api_version"] == API_VERSION
    assert result.json()["started_at"]


def test_default_local_address():
    assert Settings().base_url == "http://127.0.0.1:8765"


def test_external_host_rejected():
    with pytest.raises(ValueError):
        Settings(host="0.0.0.0")


@pytest.mark.parametrize("port", [0, 65536])
def test_invalid_port(port):
    with pytest.raises(ValueError):
        Settings(port=port)


def test_timeout_validation():
    with pytest.raises(ValueError):
        Settings(timeout_seconds=0)
