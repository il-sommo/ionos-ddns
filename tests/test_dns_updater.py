"""Test per DNSUpdater"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from ionos_ddns import DNSUpdater


class TestDNSUpdater:
    """Test suite per DNSUpdater"""

    def setup_method(self):
        """Setup per ogni test"""
        self.updater = DNSUpdater("test_pub", "test_secret")

    def test_update_dns_create_new_record(self, mocker):
        """Test creazione nuovo record quando non esiste"""
        # Mock IP detector
        mock_get_ip = mocker.patch.object(
            self.updater.ip_detector,
            'get_public_ip',
            return_value=("203.0.113.1", "A")
        )

        # Mock IONOS client
        mock_get_zone_id = mocker.patch.object(
            self.updater.client,
            'get_zone_id',
            return_value="zone-123"
        )

        mock_get_zone = mocker.patch.object(
            self.updater.client,
            'get_zone',
            return_value={
                "name": "example.com",
                "id": "zone-123",
                "records": [
                    {
                        "name": "other.example.com",
                        "type": "A",
                        "content": "192.0.2.1",
                        "id": "record-999"
                    }
                ]
            }
        )

        mock_create = mocker.patch.object(
            self.updater.client,
            'create_record',
            return_value=[{"id": "record-123"}]
        )

        # Esegui update
        self.updater.update_dns("test.example.com")

        # Verifica chiamate
        mock_get_ip.assert_called_once()
        mock_get_zone_id.assert_called_once_with("example.com")
        mock_get_zone.assert_called_once_with("zone-123")
        mock_create.assert_called_once_with("example.com", "test", "A", "203.0.113.1")

    def test_update_dns_update_existing_record(self, mocker):
        """Test aggiornamento record esistente con IP diverso"""
        # Mock IP detector
        mock_get_ip = mocker.patch.object(
            self.updater.ip_detector,
            'get_public_ip',
            return_value=("203.0.113.10", "A")
        )

        # Mock IONOS client
        mock_get_zone_id = mocker.patch.object(
            self.updater.client,
            'get_zone_id',
            return_value="zone-123"
        )

        mock_get_zone = mocker.patch.object(
            self.updater.client,
            'get_zone',
            return_value={
                "name": "example.com",
                "id": "zone-123",
                "records": [
                    {
                        "name": "test.example.com",
                        "type": "A",
                        "content": "192.0.2.1",  # IP vecchio
                        "id": "record-456"
                    }
                ]
            }
        )

        mock_update = mocker.patch.object(
            self.updater.client,
            'update_record',
            return_value={"id": "record-456"}
        )

        # Esegui update
        self.updater.update_dns("test.example.com")

        # Verifica chiamate
        mock_get_ip.assert_called_once()
        mock_get_zone_id.assert_called_once_with("example.com")
        mock_get_zone.assert_called_once_with("zone-123")
        mock_update.assert_called_once_with(
            "example.com", "test", "A", "203.0.113.10", "record-456"
        )

    def test_update_dns_no_update_needed(self, mocker, capsys):
        """Test quando IP è già aggiornato"""
        # Mock IP detector
        mock_get_ip = mocker.patch.object(
            self.updater.ip_detector,
            'get_public_ip',
            return_value=("203.0.113.1", "A")
        )

        # Mock IONOS client
        mock_get_zone_id = mocker.patch.object(
            self.updater.client,
            'get_zone_id',
            return_value="zone-123"
        )

        mock_get_zone = mocker.patch.object(
            self.updater.client,
            'get_zone',
            return_value={
                "name": "example.com",
                "id": "zone-123",
                "records": [
                    {
                        "name": "test.example.com",
                        "type": "A",
                        "content": "203.0.113.1",  # Stesso IP
                        "id": "record-456"
                    }
                ]
            }
        )

        mock_update = mocker.patch.object(
            self.updater.client,
            'update_record'
        )

        mock_create = mocker.patch.object(
            self.updater.client,
            'create_record'
        )

        # Esegui update
        self.updater.update_dns("test.example.com")

        # Verifica che non ci siano stati aggiornamenti
        mock_update.assert_not_called()
        mock_create.assert_not_called()

        # Verifica output
        captured = capsys.readouterr()
        assert "L'IP è già aggiornato" in captured.out

    def test_update_dns_domain_not_found(self, mocker):
        """Test quando il dominio non è gestito da IONOS"""
        # Mock IP detector
        mocker.patch.object(
            self.updater.ip_detector,
            'get_public_ip',
            return_value=("203.0.113.1", "A")
        )

        # Mock IONOS client - dominio non trovato
        mocker.patch.object(
            self.updater.client,
            'get_zone_id',
            return_value=None
        )

        # Esegui update e verifica che faccia sys.exit(1)
        with pytest.raises(SystemExit) as exc_info:
            self.updater.update_dns("test.notfound.com")

        assert exc_info.value.code == 1

    def test_update_dns_invalid_hostname(self, mocker):
        """Test con hostname non valido"""
        # Mock IP detector
        mocker.patch.object(
            self.updater.ip_detector,
            'get_public_ip',
            return_value=("203.0.113.1", "A")
        )

        # Hostname senza dominio
        with pytest.raises(ValueError, match="Hostname non valido"):
            self.updater.update_dns("invalid")

    def test_update_dns_ipv6(self, mocker):
        """Test aggiornamento con IPv6"""
        # Mock IP detector per IPv6
        mock_get_ip = mocker.patch.object(
            self.updater.ip_detector,
            'get_public_ip',
            return_value=("2001:db8::1", "AAAA")
        )

        # Mock IONOS client
        mock_get_zone_id = mocker.patch.object(
            self.updater.client,
            'get_zone_id',
            return_value="zone-123"
        )

        mock_get_zone = mocker.patch.object(
            self.updater.client,
            'get_zone',
            return_value={
                "name": "example.com",
                "id": "zone-123",
                "records": []
            }
        )

        mock_create = mocker.patch.object(
            self.updater.client,
            'create_record',
            return_value=[{"id": "record-123"}]
        )

        # Esegui update
        self.updater.update_dns("test.example.com")

        # Verifica che sia stato creato un record AAAA
        mock_create.assert_called_once_with("example.com", "test", "AAAA", "2001:db8::1")

    def test_update_dns_subdomain_parsing(self, mocker):
        """Test parsing corretto di sottodomini complessi"""
        # Mock IP detector
        mocker.patch.object(
            self.updater.ip_detector,
            'get_public_ip',
            return_value=("203.0.113.1", "A")
        )

        # Mock IONOS client
        mock_get_zone_id = mocker.patch.object(
            self.updater.client,
            'get_zone_id',
            return_value="zone-123"
        )

        mock_get_zone = mocker.patch.object(
            self.updater.client,
            'get_zone',
            return_value={
                "name": "example.com",
                "id": "zone-123",
                "records": []
            }
        )

        mock_create = mocker.patch.object(
            self.updater.client,
            'create_record',
            return_value=[{"id": "record-123"}]
        )

        # Test con sottodominio multi-livello
        self.updater.update_dns("dev.api.example.com")

        # Verifica che il parsing sia corretto
        # dev.api deve essere il record, example.com il dominio
        mock_get_zone_id.assert_called_once_with("api.example.com")

    def test_update_dns_zone_retrieval_fails(self, mocker):
        """Test quando il recupero della zona fallisce"""
        # Mock IP detector
        mocker.patch.object(
            self.updater.ip_detector,
            'get_public_ip',
            return_value=("203.0.113.1", "A")
        )

        # Mock IONOS client
        mocker.patch.object(
            self.updater.client,
            'get_zone_id',
            return_value="zone-123"
        )

        # get_zone ritorna None
        mocker.patch.object(
            self.updater.client,
            'get_zone',
            return_value=None
        )

        # Esegui update e verifica che faccia sys.exit(1)
        with pytest.raises(SystemExit) as exc_info:
            self.updater.update_dns("test.example.com")

        assert exc_info.value.code == 1
