"""Test di integrazione end-to-end"""
import pytest
import responses
from ionos_ddns import DNSUpdater


class TestIntegration:
    """Test di integrazione completi"""

    @responses.activate
    def test_complete_flow_create_record(self):
        """Test flusso completo: rilevamento IP e creazione record"""
        # Mock rilevamento IP
        responses.add(
            responses.GET,
            "https://api.ipify.org",
            body="203.0.113.42",
            status=200
        )

        # Mock get zones
        responses.add(
            responses.GET,
            "https://api.hosting.ionos.com/dns/v1/zones",
            json=[{"name": "example.com", "id": "zone-123", "type": "NATIVE"}],
            status=200
        )

        # Mock get zone details (chiamato 2 volte: per get_zone_id e per update_dns)
        responses.add(
            responses.GET,
            "https://api.hosting.ionos.com/dns/v1/zones/zone-123",
            json={
                "name": "example.com",
                "id": "zone-123",
                "records": []
            },
            status=200
        )

        responses.add(
            responses.GET,
            "https://api.hosting.ionos.com/dns/v1/zones/zone-123",
            json={
                "name": "example.com",
                "id": "zone-123",
                "records": []
            },
            status=200
        )

        # Mock create record
        responses.add(
            responses.POST,
            "https://api.hosting.ionos.com/dns/v1/zones/zone-123/records",
            json=[{
                "name": "test.example.com",
                "rootName": "example.com",
                "type": "A",
                "content": "203.0.113.42",
                "id": "record-789"
            }],
            status=201
        )

        # Esegui flusso completo
        updater = DNSUpdater("test_pub", "test_secret")
        updater.update_dns("test.example.com")

        # Verifica che tutte le chiamate siano state effettuate
        # 1. get IP, 2. get zones, 3-4. get zone details (2x), 5. create record
        assert len(responses.calls) == 5

    @responses.activate
    def test_complete_flow_update_record(self):
        """Test flusso completo: rilevamento IP e aggiornamento record"""
        # Mock rilevamento IP
        responses.add(
            responses.GET,
            "https://api.ipify.org",
            body="203.0.113.50",
            status=200
        )

        # Mock get zones
        responses.add(
            responses.GET,
            "https://api.hosting.ionos.com/dns/v1/zones",
            json=[{"name": "example.com", "id": "zone-123", "type": "NATIVE"}],
            status=200
        )

        # Mock get zone details con record esistente (chiamato 2 volte)
        zone_data = {
            "name": "example.com",
            "id": "zone-123",
            "records": [
                {
                    "name": "test.example.com",
                    "rootName": "example.com",
                    "type": "A",
                    "content": "192.0.2.1",  # IP vecchio
                    "id": "record-789"
                }
            ]
        }

        responses.add(
            responses.GET,
            "https://api.hosting.ionos.com/dns/v1/zones/zone-123",
            json=zone_data,
            status=200
        )

        responses.add(
            responses.GET,
            "https://api.hosting.ionos.com/dns/v1/zones/zone-123",
            json=zone_data,
            status=200
        )

        # Mock update record
        responses.add(
            responses.PUT,
            "https://api.hosting.ionos.com/dns/v1/zones/zone-123/records/record-789",
            json={
                "name": "test.example.com",
                "rootName": "example.com",
                "type": "A",
                "content": "203.0.113.50",
                "id": "record-789"
            },
            status=200
        )

        # Esegui flusso completo
        updater = DNSUpdater("test_pub", "test_secret")
        updater.update_dns("test.example.com")

        # Verifica che tutte le chiamate siano state effettuate
        # 1. get IP, 2. get zones, 3-4. get zone details (2x), 5. update record
        assert len(responses.calls) == 5

    @responses.activate
    def test_complete_flow_ipv6(self):
        """Test flusso completo con IPv6"""
        # Mock rilevamento IPv4 fallisce
        for service in ["https://api.ipify.org", "https://ifconfig.me/ip", "https://icanhazip.com"]:
            responses.add(responses.GET, service, status=500)

        # Mock rilevamento IPv6
        responses.add(
            responses.GET,
            "https://api64.ipify.org",
            body="2001:db8::42",
            status=200
        )

        # Mock get zones
        responses.add(
            responses.GET,
            "https://api.hosting.ionos.com/dns/v1/zones",
            json=[{"name": "example.com", "id": "zone-123", "type": "NATIVE"}],
            status=200
        )

        # Mock get zone details
        responses.add(
            responses.GET,
            "https://api.hosting.ionos.com/dns/v1/zones/zone-123",
            json={
                "name": "example.com",
                "id": "zone-123",
                "records": []
            },
            status=200
        )

        # Mock create record AAAA
        responses.add(
            responses.POST,
            "https://api.hosting.ionos.com/dns/v1/zones/zone-123/records",
            json=[{
                "name": "test.example.com",
                "rootName": "example.com",
                "type": "AAAA",
                "content": "2001:db8::42",
                "id": "record-789"
            }],
            status=201
        )

        # Esegui flusso completo
        updater = DNSUpdater("test_pub", "test_secret")
        updater.update_dns("test.example.com")

        # Verifica che sia stato creato un record AAAA
        create_call = responses.calls[-1]
        assert "AAAA" in str(create_call.request.body)
