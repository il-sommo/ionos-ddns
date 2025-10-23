"""Configurazione pytest"""
import pytest


@pytest.fixture
def mock_dns_config():
    """Fixture per configurazione DNS di test"""
    return {
        "pub": "test_public_key",
        "secret": "test_secret_key"
    }


@pytest.fixture
def mock_zone_data():
    """Fixture per dati zona DNS di test"""
    return {
        "name": "example.com",
        "id": "zone-123",
        "type": "NATIVE",
        "records": [
            {
                "name": "example.com",
                "rootName": "example.com",
                "type": "A",
                "content": "192.0.2.1",
                "ttl": 3600,
                "disabled": False,
                "id": "record-001"
            },
            {
                "name": "www.example.com",
                "rootName": "example.com",
                "type": "A",
                "content": "192.0.2.2",
                "ttl": 3600,
                "disabled": False,
                "id": "record-002"
            }
        ]
    }


@pytest.fixture
def mock_zones_list():
    """Fixture per lista zone DNS di test"""
    return [
        {"name": "example.com", "id": "zone-123", "type": "NATIVE"},
        {"name": "test.com", "id": "zone-456", "type": "NATIVE"}
    ]
