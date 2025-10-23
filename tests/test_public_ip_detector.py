"""Test per PublicIPDetector"""
import pytest
import responses
from ionos_ddns import PublicIPDetector


class TestPublicIPDetector:
    """Test suite per PublicIPDetector"""

    @responses.activate
    def test_get_public_ip_ipv4_first_service(self):
        """Test rilevamento IPv4 con primo servizio"""
        # Mock del primo servizio IPv4
        responses.add(
            responses.GET,
            "https://api.ipify.org",
            body="203.0.113.42",
            status=200
        )

        detector = PublicIPDetector()
        ip, record_type = detector.get_public_ip()

        assert ip == "203.0.113.42"
        assert record_type == "A"

    @responses.activate
    def test_get_public_ip_ipv4_fallback(self):
        """Test rilevamento IPv4 con fallback al secondo servizio"""
        # Primo servizio fallisce
        responses.add(
            responses.GET,
            "https://api.ipify.org",
            status=500
        )
        # Secondo servizio funziona
        responses.add(
            responses.GET,
            "https://ifconfig.me/ip",
            body="198.51.100.123",
            status=200
        )

        detector = PublicIPDetector()
        ip, record_type = detector.get_public_ip()

        assert ip == "198.51.100.123"
        assert record_type == "A"

    @responses.activate
    def test_get_public_ip_ipv6(self):
        """Test rilevamento IPv6"""
        # Tutti i servizi IPv4 falliscono
        for service in PublicIPDetector.IPV4_SERVICES:
            responses.add(responses.GET, service, status=500)

        # Primo servizio IPv6 funziona
        responses.add(
            responses.GET,
            "https://api64.ipify.org",
            body="2001:db8::1",
            status=200
        )

        detector = PublicIPDetector()
        ip, record_type = detector.get_public_ip()

        assert ip == "2001:db8::1"
        assert record_type == "AAAA"

    @responses.activate
    def test_get_public_ip_all_services_fail(self):
        """Test quando tutti i servizi falliscono"""
        # Tutti i servizi IPv4 falliscono
        for service in PublicIPDetector.IPV4_SERVICES:
            responses.add(responses.GET, service, status=500)

        # Tutti i servizi IPv6 falliscono
        for service in PublicIPDetector.IPV6_SERVICES:
            responses.add(responses.GET, service, status=500)

        detector = PublicIPDetector()

        with pytest.raises(RuntimeError, match="Impossibile rilevare l'indirizzo IP pubblico"):
            detector.get_public_ip()

    @responses.activate
    def test_get_public_ip_invalid_ipv4(self):
        """Test con risposta IPv4 non valida"""
        # Primo servizio ritorna IP non valido
        responses.add(
            responses.GET,
            "https://api.ipify.org",
            body="not-an-ip",
            status=200
        )
        # Secondo servizio ritorna IP valido
        responses.add(
            responses.GET,
            "https://ifconfig.me/ip",
            body="192.0.2.1",
            status=200
        )

        detector = PublicIPDetector()
        ip, record_type = detector.get_public_ip()

        assert ip == "192.0.2.1"
        assert record_type == "A"

    @responses.activate
    def test_get_public_ip_timeout(self):
        """Test gestione timeout"""
        # Simula timeout con un'eccezione di rete
        import requests
        responses.add(
            responses.GET,
            "https://api.ipify.org",
            body=requests.exceptions.Timeout("Connection timeout")
        )
        # Secondo servizio funziona
        responses.add(
            responses.GET,
            "https://ifconfig.me/ip",
            body="192.0.2.100",
            status=200
        )

        detector = PublicIPDetector()
        ip, record_type = detector.get_public_ip()

        assert ip == "192.0.2.100"
        assert record_type == "A"
