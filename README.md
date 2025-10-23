# IONOS Dynamic DNS Updater

Script Python per aggiornare automaticamente i record DNS su IONOS con l'indirizzo IP pubblico corrente.

## Requisiti

- Python 3.9 o superiore
- [uv](https://github.com/astral-sh/uv) package manager

## Installazione

1. Clona o copia i file del progetto
2. Installa le dipendenze con uv:

```bash
uv pip install -e .
```

## Configurazione

1. Crea un file `dns.json` nella stessa directory dello script:

```bash
cp dns.json.example dns.json
```

2. Modifica `dns.json` inserendo la tua API key di IONOS:

```json
{
  "api_key": "your-actual-ionos-api-key"
}
```

Per ottenere la API key:
- Accedi al [Developer Portal di IONOS](https://developer.hosting.ionos.it/)
- Vai nella sezione API Keys
- Genera una nuova API key con permessi per gestire DNS

## Utilizzo

```bash
python ionos_ddns.py hostname.dominio.com
```

Esempio:
```bash
python ionos_ddns.py dev01.cauware.com
```

### Opzioni

- `--config PATH`: Specifica un percorso alternativo per il file di configurazione (default: `dns.json`)

Esempio:
```bash
python ionos_ddns.py dev01.cauware.com --config /etc/ionos/dns.json
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

Per automatizzare l'aggiornamento, puoi configurare un cron job:

```bash
# Aggiorna ogni 5 minuti
*/5 * * * * /usr/bin/python3 /path/to/ionos_ddns.py dev01.cauware.com
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
