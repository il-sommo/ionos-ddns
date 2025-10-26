# IONOS Dynamic DNS Updater

Script Python per aggiornare automaticamente i record DNS su IONOS con l'indirizzo IP pubblico corrente.

## Requisiti

### Per l'installazione tramite pacchetto .deb
- Ubuntu 24.04 (Noble Numbat) o compatibile
- Python 3.9 o superiore (installato di default)
- Connessione internet

### Per lo sviluppo
- Python 3.9 o superiore
- [uv](https://github.com/astral-sh/uv) package manager

## Installazione

### Metodo 1: Installazione rapida dal pacchetto .deb (Raccomandato)

Se hai già un pacchetto `.deb` pre-costruito:

```bash
# Installa il pacchetto
sudo dpkg -i ionos-ddns_0.1.0-1_all.deb

# Installa eventuali dipendenze mancanti
sudo apt-get install -f -y
```

Il pacchetto installerà automaticamente:
- Script principale: `/usr/bin/ionos-ddns`
- Helper cron: `/usr/bin/ionos-ddns-setup-cron`
- File esempio: `/etc/ionos-ddns/dns.json.example`

### Metodo 2: Build e installazione dal sorgente

1. **IMPORTANTE**: Se riscontri problemi di connettività (timeout porta 80), configura HTTPS prima:

```bash
sudo sed -i 's|http://archive.ubuntu.com|https://archive.ubuntu.com|g' /etc/apt/sources.list
sudo apt-get update
```

2. Installa le dipendenze per la build:

```bash
sudo apt-get install -y debhelper
```

3. Costruisci il pacchetto .deb:

```bash
make build
```

4. Installa il pacchetto:

```bash
make install
# oppure manualmente:
sudo dpkg -i ../ionos-ddns_0.1.0-1_all.deb
sudo apt-get install -f -y
```

Per maggiori dettagli sulla build, consulta [BUILDING.md](BUILDING.md).

### Installazione manuale (sviluppo)

1. Clona o copia i file del progetto
2. Installa le dipendenze con uv:

```bash
uv pip install -e .
```

## Configurazione

### Dopo l'installazione del pacchetto .deb

1. Crea il file di configurazione con le tue credenziali IONOS:

```bash
sudo cp /etc/ionos-ddns/dns.json.example /etc/ionos-ddns/dns.json
sudo nano /etc/ionos-ddns/dns.json
```

2. Inserisci le tue credenziali API IONOS nel file:

```json
{
  "pub": "your-public-key",
  "secret": "your-secret-key"
}
```

3. Testa lo script manualmente:

```bash
ionos-ddns your-hostname.your-domain.com --config /etc/ionos-ddns/dns.json
```

4. Configura l'aggiornamento automatico ogni 5 minuti usando lo script helper:

```bash
sudo ionos-ddns-setup-cron
```

Lo script ti guiderà nella configurazione del cron job.

### Configurazione manuale (sviluppo)

1. Crea un file `dns.json` nella stessa directory dello script:

```bash
cp dns.json.example dns.json
```

2. Modifica `dns.json` inserendo la tua API key di IONOS:

```json
{
  "pub": "your-public-key",
  "secret": "your-secret-key"
}
```

Per ottenere le API key:
- Accedi al [Developer Portal di IONOS](https://developer.hosting.ionos.it/)
- Vai nella sezione API Keys
- Genera una nuova API key con permessi per gestire DNS

## Utilizzo

### Con il pacchetto .deb installato

```bash
sudo ionos-ddns hostname.dominio.com --config /etc/ionos-ddns/dns.json
```

Esempio:
```bash
sudo ionos-ddns dev01.cauware.com --config /etc/ionos-ddns/dns.json
```

**Nota**: È necessario usare `sudo` perché il file di configurazione `/etc/ionos-ddns/dns.json` ha permessi 600 (root only) per proteggere le credenziali API.

### In modalità sviluppo

```bash
python ionos_ddns.py hostname.dominio.com
```

Esempio:
```bash
python ionos_ddns.py dev01.cauware.com
```

### Opzioni

- `--config PATH`: Specifica un percorso alternativo per il file di configurazione (default: `dns.json`)

Esempi:
```bash
# Con pacchetto installato
sudo ionos-ddns dev01.cauware.com --config /etc/ionos-ddns/dns.json

# In sviluppo
python ionos_ddns.py dev01.cauware.com --config /path/to/dns.json
```

## Funzionalità

Lo script:

1. **Rileva automaticamente l'IP pubblico** utilizzando servizi esterni (ipify, ifconfig.me, icanhazip.com)
2. **Supporta sia IPv4 che IPv6** creando record di tipo A o AAAA appropriati
3. **Verifica se il dominio è gestito da IONOS** tramite le API
4. **Controlla se l'hostname esiste già**:
   - Se esiste e l'IP è diverso, aggiorna il record
   - Se esiste e l'IP è uguale, non fa nulla
   - Se non esiste, crea un nuovo record DNS
5. **Gestisce errori** con messaggi chiari

## Automazione

### Con il pacchetto .deb installato

Usa lo script helper per configurare il cron job:

```bash
sudo ionos-ddns-setup-cron
```

### Configurazione manuale del cron

Per automatizzare l'aggiornamento, puoi configurare un cron job manualmente:

```bash
# Aggiorna ogni 5 minuti
*/5 * * * * /usr/bin/python3 /path/to/ionos_ddns.py dev01.cauware.com
```

## Monitoraggio Log

Se hai configurato il cron job, puoi monitorare i log:

```bash
# Visualizza gli ultimi log
sudo tail -f /var/log/ionos-ddns.log

# Visualizza tutte le esecuzioni
sudo cat /var/log/ionos-ddns.log
```

## Disinstallazione

Per rimuovere il pacchetto:

```bash
sudo apt remove ionos-ddns
```

Per rimuovere anche i file di configurazione:

```bash
sudo apt purge ionos-ddns
```

## Note

- Assicurati che il dominio sia già configurato su IONOS
- La API key deve avere permessi di lettura e scrittura per le zone DNS
- Il TTL predefinito per i nuovi record è 3600 secondi (1 ora)

## Test

Il progetto include una suite completa di test:

```bash
# Installa dipendenze di test
uv pip install pytest pytest-mock responses

# Esegui tutti i test
pytest

# Con output verboso
pytest -v

# Con coverage
pytest --cov=ionos_ddns
```

**28 test totali** che coprono:
- Rilevamento IP pubblico (IPv4/IPv6)
- Client API IONOS (autenticazione, CRUD record)
- Logica aggiornamento DNS
- Test di integrazione end-to-end

Vedi [tests/README.md](tests/README.md) per dettagli completi.

## Troubleshooting

### "Dominio non gestito da IONOS"
Verifica che il dominio sia effettivamente configurato nel tuo account IONOS.

### "Impossibile rilevare l'indirizzo IP pubblico"
Verifica la connessione internet e che i servizi esterni siano raggiungibili.

### Errori di autenticazione
Controlla che le chiavi `pub` e `secret` nel file `dns.json` siano corrette e valide.

### Eseguire lo script
Per eseguire lo script, usa:
```bash
python3 ionos_ddns.py hostname.dominio.com
```

**NON** usare `uv ionos_ddns.py` - `uv` è un package manager, non un interprete Python.
