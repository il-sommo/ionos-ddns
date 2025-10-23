# Test Suite - IONOS Dynamic DNS Updater

Suite completa di test per lo script di aggiornamento DNS dinamico IONOS.

## Struttura Test

```
tests/
├── __init__.py
├── conftest.py              # Configurazione pytest e fixtures
├── test_public_ip_detector.py   # Test rilevamento IP pubblico
├── test_ionos_client.py     # Test client API IONOS
├── test_dns_updater.py      # Test logica aggiornamento DNS
└── test_integration.py      # Test di integrazione end-to-end
```

## Statistiche Coverage

- **28 test totali**
- **100% test passati**
- Copertura completa di tutti i componenti principali

## Test Suites

### 1. PublicIPDetector (7 test)
- ✅ Rilevamento IPv4 con primo servizio
- ✅ Fallback a servizi alternativi
- ✅ Rilevamento IPv6
- ✅ Gestione fallimento tutti i servizi
- ✅ Validazione IP non validi
- ✅ Gestione timeout
- ✅ Retry automatico

### 2. IONOSClient (11 test)
- ✅ Recupero zone DNS
- ✅ Autenticazione corretta (header X-API-Key)
- ✅ Ricerca ID zona per dominio
- ✅ Gestione zona non trovata
- ✅ Recupero dettagli zona
- ✅ Recupero record DNS
- ✅ Creazione record (POST)
- ✅ Aggiornamento record (PUT)
- ✅ Gestione errori dominio non trovato
- ✅ Validazione parametri
- ✅ Formato payload corretto

### 3. DNSUpdater (8 test)
- ✅ Creazione nuovo record quando non esiste
- ✅ Aggiornamento record esistente con IP diverso
- ✅ Nessun aggiornamento quando IP già corretto
- ✅ Gestione dominio non trovato
- ✅ Validazione hostname
- ✅ Supporto IPv6 (record AAAA)
- ✅ Parsing corretto sottodomini
- ✅ Gestione errori recupero zona

### 4. Integration Tests (3 test)
- ✅ Flusso completo creazione record
- ✅ Flusso completo aggiornamento record
- ✅ Flusso completo con IPv6

## Eseguire i Test

### Tutti i test
```bash
pytest
```

### Con output verboso
```bash
pytest -v
```

### Solo test specifici
```bash
# Test singolo file
pytest tests/test_public_ip_detector.py

# Test singola classe
pytest tests/test_ionos_client.py::TestIONOSClient

# Test singolo metodo
pytest tests/test_dns_updater.py::TestDNSUpdater::test_update_dns_create_new_record
```

### Con coverage
```bash
pytest --cov=ionos_ddns --cov-report=html
```

### Test per categoria
```bash
# Solo test unitari (se marcati)
pytest -m unit

# Solo test di integrazione (se marcati)
pytest -m integration
```

## Installazione Dipendenze Test

```bash
# Con uv
uv pip install pytest pytest-mock responses

# Oppure installare tutte le dipendenze opzionali
uv pip install -e ".[test]"
```

## Configurazione

Il file `pytest.ini` contiene la configurazione base:
- Path dei test: `tests/`
- Pattern file: `test_*.py`
- Output: verbose con traceback breve

## Fixtures Disponibili

Definite in `conftest.py`:

- `mock_dns_config`: Configurazione DNS di test
- `mock_zone_data`: Dati zona DNS di esempio
- `mock_zones_list`: Lista zone DNS di test

## Mocking

I test utilizzano:
- **responses**: Mock delle chiamate HTTP alle API esterne
- **pytest-mock**: Mock degli oggetti Python interni
- **mocker**: Fixture per patch temporanei

## Best Practices

1. **Isolamento**: Ogni test è completamente isolato
2. **Mock HTTP**: Tutte le chiamate HTTP sono mockate (nessuna chiamata reale)
3. **Fast**: Test eseguiti in <1 secondo
4. **Deterministici**: Risultati consistenti
5. **Coverage**: Alta copertura del codice

## Continuous Integration

Per CI/CD, eseguire:

```bash
pytest --tb=short --strict-markers
```

## Debug Test Falliti

```bash
# Con più dettagli
pytest -vv

# Con traceback completo
pytest --tb=long

# Stoppa al primo fallimento
pytest -x

# Mostra stdout anche per test passati
pytest -s
```

## Aggiungere Nuovi Test

1. Creare file `test_<modulo>.py` in `tests/`
2. Definire classe `Test<NomeClasse>`
3. Creare metodi `test_<scenario>()`
4. Usare fixtures e mocking appropriati
5. Eseguire test per verifica

Esempio:
```python
class TestMyFeature:
    def test_my_scenario(self, mocker):
        # Arrange
        mock_obj = mocker.patch('module.function')

        # Act
        result = function_to_test()

        # Assert
        assert result == expected
        mock_obj.assert_called_once()
```
