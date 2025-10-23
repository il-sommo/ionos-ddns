"""Test per IONOSClient"""
import pytest
import responses
from ionos_ddns import IONOSClient


class TestIONOSClient:
    """Test suite per IONOSClient"""

    def setup_method(self):
        """Setup per ogni test"""
        self.client = IONOSClient("test_pub_key", "test_secret_key")
        self.base_url = "https://api.hosting.ionos.com"

    @responses.activate
    def test_get_zones_success(self):
        """Test recupero zone DNS con successo"""
        mock_zones = [
            {"name": "example.com", "id": "zone-123", "type": "NATIVE"},
            {"name": "test.com", "id": "zone-456", "type": "NATIVE"}
        ]

        responses.add(
            responses.GET,
            f"{self.base_url}/dns/v1/zones",
            json=mock_zones,
            status=200
        )

        zones = self.client.get_zones()
        assert len(zones) == 2
        assert zones[0]["name"] == "example.com"
        assert zones[1]["name"] == "test.com"

    @responses.activate
    def test_get_zones_authentication_header(self):
        """Test che l'header di autenticazione sia corretto"""
        responses.add(
            responses.GET,
            f"{self.base_url}/dns/v1/zones",
            json=[],
            status=200
        )

        self.client.get_zones()

        # Verifica che l'header X-API-Key sia nel formato corretto
        assert len(responses.calls) == 1
        request = responses.calls[0].request
        assert "X-API-Key" in request.headers
        assert request.headers["X-API-Key"] == "test_pub_key.test_secret_key"

    @responses.activate
    def test_get_zone_id_found(self):
        """Test recupero ID zona esistente"""
        mock_zones = [
            {"name": "example.com", "id": "zone-123", "type": "NATIVE"},
            {"name": "test.com", "id": "zone-456", "type": "NATIVE"}
        ]

        responses.add(
            responses.GET,
            f"{self.base_url}/dns/v1/zones",
            json=mock_zones,
            status=200
        )

        zone_id = self.client.get_zone_id("example.com")
        assert zone_id == "zone-123"

    @responses.activate
    def test_get_zone_id_not_found(self):
        """Test recupero ID zona inesistente"""
        mock_zones = [
            {"name": "example.com", "id": "zone-123", "type": "NATIVE"}
        ]

        responses.add(
            responses.GET,
            f"{self.base_url}/dns/v1/zones",
            json=mock_zones,
            status=200
        )

        zone_id = self.client.get_zone_id("notfound.com")
        assert zone_id is None

    @responses.activate
    def test_get_zone_success(self):
        """Test recupero dettagli zona con successo"""
        mock_zone = {
            "name": "example.com",
            "id": "zone-123",
            "type": "NATIVE",
            "records": [
                {
                    "name": "example.com",
                    "type": "A",
                    "content": "192.0.2.1",
                    "ttl": 3600
                }
            ]
        }

        responses.add(
            responses.GET,
            f"{self.base_url}/dns/v1/zones/zone-123",
            json=mock_zone,
            status=200
        )

        zone = self.client.get_zone("zone-123")
        assert zone["name"] == "example.com"
        assert len(zone["records"]) == 1

    @responses.activate
    def test_get_zone_not_found(self):
        """Test recupero zona inesistente"""
        responses.add(
            responses.GET,
            f"{self.base_url}/dns/v1/zones/zone-999",
            status=404
        )

        zone = self.client.get_zone("zone-999")
        assert zone is None

    @responses.activate
    def test_get_records(self):
        """Test recupero record DNS"""
        mock_zone = {
            "name": "example.com",
            "id": "zone-123",
            "records": [
                {"name": "www.example.com", "type": "A", "content": "192.0.2.1"},
                {"name": "mail.example.com", "type": "A", "content": "192.0.2.2"}
            ]
        }

        responses.add(
            responses.GET,
            f"{self.base_url}/dns/v1/zones/zone-123",
            json=mock_zone,
            status=200
        )

        records = self.client.get_records("zone-123")
        assert len(records) == 2
        assert records[0]["name"] == "www.example.com"

    @responses.activate
    def test_create_record_success(self):
        """Test creazione record DNS con successo"""
        # Mock get_zone_id
        responses.add(
            responses.GET,
            f"{self.base_url}/dns/v1/zones",
            json=[{"name": "example.com", "id": "zone-123", "type": "NATIVE"}],
            status=200
        )

        # Mock get_zone
        responses.add(
            responses.GET,
            f"{self.base_url}/dns/v1/zones/zone-123",
            json={
                "name": "example.com",
                "id": "zone-123",
                "records": []
            },
            status=200
        )

        # Mock POST per creazione record
        mock_response = [{
            "name": "test.example.com",
            "rootName": "example.com",
            "type": "A",
            "content": "192.0.2.10",
            "ttl": 3600,
            "id": "record-789"
        }]

        responses.add(
            responses.POST,
            f"{self.base_url}/dns/v1/zones/zone-123/records",
            json=mock_response,
            status=201
        )

        result = self.client.create_record(
            domain="example.com",
            name="test",
            record_type="A",
            content="192.0.2.10"
        )

        assert result[0]["name"] == "test.example.com"
        assert result[0]["content"] == "192.0.2.10"

    @responses.activate
    def test_create_record_domain_not_found(self):
        """Test creazione record per dominio inesistente"""
        responses.add(
            responses.GET,
            f"{self.base_url}/dns/v1/zones",
            json=[],
            status=200
        )

        with pytest.raises(ValueError, match="Dominio .* non trovato"):
            self.client.create_record(
                domain="notfound.com",
                name="test",
                record_type="A",
                content="192.0.2.10"
            )

    @responses.activate
    def test_update_record_success(self):
        """Test aggiornamento record DNS con successo"""
        # Mock get_zone_id
        responses.add(
            responses.GET,
            f"{self.base_url}/dns/v1/zones",
            json=[{"name": "example.com", "id": "zone-123", "type": "NATIVE"}],
            status=200
        )

        # Mock PUT per aggiornamento record
        mock_response = {
            "name": "test.example.com",
            "rootName": "example.com",
            "type": "A",
            "content": "192.0.2.20",
            "ttl": 3600,
            "id": "record-789"
        }

        responses.add(
            responses.PUT,
            f"{self.base_url}/dns/v1/zones/zone-123/records/record-789",
            json=mock_response,
            status=200
        )

        result = self.client.update_record(
            domain="example.com",
            name="test",
            record_type="A",
            new_content="192.0.2.20",
            record_id="record-789"
        )

        assert result["content"] == "192.0.2.20"

    @responses.activate
    def test_update_record_domain_not_found(self):
        """Test aggiornamento record per dominio inesistente"""
        responses.add(
            responses.GET,
            f"{self.base_url}/dns/v1/zones",
            json=[],
            status=200
        )

        with pytest.raises(ValueError, match="Dominio .* non trovato"):
            self.client.update_record(
                domain="notfound.com",
                name="test",
                record_type="A",
                new_content="192.0.2.20",
                record_id="record-789"
            )
