#!/usr/bin/env python3
"""
Script per aggiornare DNS dinamico su IONOS
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple
import ipaddress
import requests


class PublicIPDetector:
    """Rileva l'indirizzo IP pubblico della macchina"""

    # Servizi per rilevare IPv4
    IPV4_SERVICES = [
        "https://api.ipify.org",
        "https://ifconfig.me/ip",
        "https://icanhazip.com",
    ]

    # Servizi per rilevare IPv6
    IPV6_SERVICES = [
        "https://api64.ipify.org",
        "https://ifconfig.me/ip",
    ]

    @staticmethod
    def get_public_ip() -> Tuple[str, str]:
        """
        Rileva l'IP pubblico e determina se è IPv4 o IPv6

        Returns:
            Tuple[str, str]: (indirizzo_ip, tipo) dove tipo è 'A' per IPv4 o 'AAAA' per IPv6
        """
        # Prova prima con IPv4
        for service in PublicIPDetector.IPV4_SERVICES:
            try:
                response = requests.get(service, timeout=5)
                if response.status_code == 200:
                    ip = response.text.strip()
                    # Verifica che sia un IPv4 valido
                    ipaddress.IPv4Address(ip)
                    return ip, 'A'
            except (requests.exceptions.RequestException, ValueError, ipaddress.AddressValueError):
                # Ignora errori di rete o IP non validi e prova il prossimo servizio
                continue

        # Se IPv4 fallisce, prova con IPv6
        for service in PublicIPDetector.IPV6_SERVICES:
            try:
                response = requests.get(service, timeout=5)
                if response.status_code == 200:
                    ip = response.text.strip()
                    # Verifica che sia un IPv6 valido
                    ipaddress.IPv6Address(ip)
                    return ip, 'AAAA'
            except (requests.exceptions.RequestException, ValueError, ipaddress.AddressValueError):
                # Ignora errori di rete o IP non validi e prova il prossimo servizio
                continue

        raise RuntimeError("Impossibile rilevare l'indirizzo IP pubblico")


class IONOSClient:
    """Client per le API IONOS"""

    BASE_URL = "https://api.hosting.ionos.com"
    REQUEST_TIMEOUT = 30  # Timeout in secondi per le richieste HTTP

    def __init__(self, pub_key: str, secret_key: str):
        self.pub_key = pub_key
        self.secret_key = secret_key
        self.headers = {
            "X-API-Key": f"{pub_key}.{secret_key}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    def get_zones(self) -> list:
        """Recupera tutte le zone DNS gestite"""
        url = f"{self.BASE_URL}/dns/v1/zones"
        response = requests.get(url, headers=self.headers, timeout=self.REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()

    def get_zone_id(self, domain: str) -> Optional[str]:
        """
        Trova l'ID della zona per un dominio specifico

        Args:
            domain: Nome del dominio (es. cauware.com)

        Returns:
            ID della zona o None se non trovata
        """
        zones = self.get_zones()
        for zone in zones:
            if zone['name'] == domain:
                return zone['id']
        return None

    def get_zone(self, zone_id: str) -> Optional[Dict]:
        """
        Recupera i dettagli di una zona DNS tramite ID

        Args:
            zone_id: ID della zona

        Returns:
            Dict con i dettagli della zona o None se non trovata
        """
        url = f"{self.BASE_URL}/dns/v1/zones/{zone_id}"
        try:
            response = requests.get(url, headers=self.headers, timeout=self.REQUEST_TIMEOUT)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise

    def get_records(self, zone_id: str) -> list:
        """Recupera tutti i record DNS per una zona"""
        zone = self.get_zone(zone_id)
        if not zone:
            return []
        return zone.get('records', [])

    def create_record(self, domain: str, name: str, record_type: str, content: str, ttl: int = 3600):
        """
        Crea un nuovo record DNS

        Args:
            domain: Dominio base (es. cauware.com)
            name: Nome del record (es. dev01 per dev01.cauware.com)
            record_type: Tipo di record ('A' o 'AAAA')
            content: Indirizzo IP
            ttl: Time to live in secondi
        """
        # Trova l'ID della zona
        zone_id = self.get_zone_id(domain)
        if not zone_id:
            raise ValueError(f"Dominio {domain} non trovato")

        url = f"{self.BASE_URL}/dns/v1/zones/{zone_id}/records"

        # Il nome completo deve includere il dominio
        full_name = f"{name}.{domain}" if name else domain

        new_record = {
            "name": full_name,
            "rootName": domain,
            "type": record_type,
            "content": content,
            "ttl": ttl,
            "disabled": False
        }

        # Crea il record usando POST
        response = requests.post(url, headers=self.headers, json=[new_record], timeout=self.REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()

    def update_record(self, domain: str, name: str, record_type: str, new_content: str, record_id: str):
        """
        Aggiorna un record DNS esistente

        Args:
            domain: Dominio base
            name: Nome del record
            record_type: Tipo di record
            new_content: Nuovo indirizzo IP
            record_id: ID del record da aggiornare
        """
        # Trova l'ID della zona
        zone_id = self.get_zone_id(domain)
        if not zone_id:
            raise ValueError(f"Dominio {domain} non trovato")

        url = f"{self.BASE_URL}/dns/v1/zones/{zone_id}/records/{record_id}"

        # Il nome completo deve includere il dominio
        full_name = f"{name}.{domain}" if name else domain

        updated_record = {
            "name": full_name,
            "rootName": domain,
            "type": record_type,
            "content": new_content,
            "disabled": False
        }

        # Aggiorna il record usando PUT
        response = requests.put(url, headers=self.headers, json=updated_record, timeout=self.REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()


class DNSUpdater:
    """Gestisce l'aggiornamento del DNS dinamico"""

    def __init__(self, pub_key: str, secret_key: str):
        self.client = IONOSClient(pub_key, secret_key)
        self.ip_detector = PublicIPDetector()

    def update_dns(self, hostname: str) -> None:
        """
        Aggiorna o crea il record DNS per l'hostname specificato

        Args:
            hostname: Hostname completo (es. dev01.cauware.com)
        """
        # Parse hostname
        parts = hostname.split('.')
        if len(parts) < 2:
            raise ValueError(f"Hostname non valido: {hostname}. Deve essere completo di dominio (es. dev01.cauware.com)")

        # Estrae nome e dominio
        record_name = parts[0]
        domain = '.'.join(parts[1:])

        print(f"Hostname: {hostname}")
        print(f"Record: {record_name}")
        print(f"Dominio: {domain}")
        print()

        # Rileva IP pubblico
        print("Rilevamento IP pubblico...")
        current_ip, record_type = self.ip_detector.get_public_ip()
        print(f"IP pubblico rilevato: {current_ip} (tipo: {record_type})")
        print()

        # Verifica se il dominio è gestito da IONOS
        print(f"Verifica dominio {domain} su IONOS...")
        zone_id = self.client.get_zone_id(domain)

        if not zone_id:
            print(f"ERRORE: Il dominio {domain} non è gestito da IONOS")
            sys.exit(1)

        print(f"Dominio {domain} trovato su IONOS (ID: {zone_id})")
        print()

        # Recupera la zona e i record
        zone = self.client.get_zone(zone_id)
        if not zone:
            print(f"ERRORE: Impossibile recuperare i dettagli della zona")
            sys.exit(1)

        # Cerca il record esistente
        records = zone.get('records', [])
        existing_record = None

        # Il nome nel record include il dominio completo
        full_hostname = f"{record_name}.{domain}"

        for record in records:
            if record['name'] == full_hostname and record['type'] == record_type:
                existing_record = record
                break

        # Aggiorna o crea il record
        if existing_record:
            existing_ip = existing_record['content']
            record_id = existing_record['id']
            print(f"Record {hostname} esistente trovato con IP: {existing_ip}")

            if existing_ip == current_ip:
                print("L'IP è già aggiornato. Nessuna modifica necessaria.")
            else:
                print(f"Aggiornamento IP da {existing_ip} a {current_ip}...")
                self.client.update_record(domain, record_name, record_type, current_ip, record_id)
                print("Record aggiornato con successo!")
        else:
            print(f"Record {hostname} non trovato. Creazione nuovo record...")
            self.client.create_record(domain, record_name, record_type, current_ip)
            print(f"Record {record_type} creato con successo per {hostname} -> {current_ip}")


def load_config(config_path: Path) -> Dict:
    """Carica la configurazione dal file dns.json"""
    if not config_path.exists():
        print(f"ERRORE: File di configurazione {config_path} non trovato")
        print("Crea il file dns.json con il seguente formato:")
        print(json.dumps({"pub": "your-public-key", "secret": "your-secret-key"}, indent=2))
        sys.exit(1)

    with open(config_path, 'r') as f:
        config = json.load(f)

    if 'pub' not in config or 'secret' not in config:
        print("ERRORE: Chiavi 'pub' e 'secret' non trovate nel file dns.json")
        sys.exit(1)

    return config


def main():
    """Funzione principale"""
    parser = argparse.ArgumentParser(
        description="Aggiorna DNS dinamico su IONOS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Esempi:
  %(prog)s dev01.cauware.com
  %(prog)s server.example.com --config /path/to/dns.json
        """
    )
    parser.add_argument(
        'hostname',
        help='Hostname completo da aggiornare (es. dev01.cauware.com)'
    )
    parser.add_argument(
        '--config',
        default='dns.json',
        help='Percorso del file di configurazione (default: dns.json)'
    )

    args = parser.parse_args()

    # Carica configurazione
    config_path = Path(args.config)
    config = load_config(config_path)

    try:
        # Esegue l'aggiornamento
        updater = DNSUpdater(config['pub'], config['secret'])
        updater.update_dns(args.hostname)
    except Exception as e:
        print(f"ERRORE: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
