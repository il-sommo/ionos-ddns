# Guida alla Build del Pacchetto .deb

Questa guida spiega come costruire il pacchetto Debian per IONOS Dynamic DNS Updater su Ubuntu 24.04.

## Prerequisiti

Sistema operativo: Ubuntu 24.04 (Noble Numbat)

## Installazione Dipendenze

**IMPORTANTE**: Se riscontri problemi di connettività APT (timeout sulla porta 80), vedi la sezione [Troubleshooting - Problema Connettività APT](#problema-connettività-apt).

Installa gli strumenti necessari per costruire pacchetti Debian:

```bash
make deb-deps
```

Oppure manualmente:

```bash
sudo apt-get update
sudo apt-get install -y debhelper
```

**Nota**: Le dipendenze sono state semplificate. Solo `debhelper` è necessario per la build. Le altre dipendenze (`dh-python`, `python3-all`, `python3-setuptools`) non sono più richieste poiché il pacchetto installa uno script Python standalone.

## Costruzione del Pacchetto

### Metodo 1: Usando il Makefile (raccomandato)

```bash
# Build del pacchetto
make build

# Il file .deb sarà creato nella directory parent
ls -lh ../ionos-ddns_*.deb
```

### Metodo 2: Manualmente

```bash
# Dalla directory root del progetto
dpkg-buildpackage -us -uc -b
```

Opzioni usate:
- `-us`: Non firmare il file .changes
- `-uc`: Non firmare il file .deb
- `-b`: Costruisci solo il pacchetto binario

## Output della Build

Dopo la build, troverai nella directory parent:

- `ionos-ddns_0.1.0-1_all.deb` - Pacchetto Debian
- `ionos-ddns_0.1.0-1_amd64.buildinfo` - Informazioni di build
- `ionos-ddns_0.1.0-1_amd64.changes` - File di descrizione modifiche

## Installazione del Pacchetto

### Usando il Makefile

```bash
make install
```

### Manualmente

```bash
sudo dpkg -i ../ionos-ddns_0.1.0-1_all.deb
```

Se ci sono problemi con le dipendenze:

```bash
sudo apt-get install -f
```

## Verifica dell'Installazione

```bash
# Verifica che il comando sia disponibile
which ionos-ddns

# Verifica la versione
dpkg -l | grep ionos-ddns

# Verifica i file installati
dpkg -L ionos-ddns
```

File installati:
- `/usr/bin/ionos-ddns` - Script principale
- `/usr/bin/ionos-ddns-setup-cron` - Helper per configurare cron
- `/etc/ionos-ddns/dns.json.example` - File di configurazione esempio

## Pulizia

Per pulire i file generati dalla build:

```bash
make clean
```

Oppure manualmente:

```bash
dh_clean
rm -rf debian/ionos-ddns debian/.debhelper
```

## Troubleshooting

### Problema Connettività APT

**Errore**: `Could not connect to archive.ubuntu.com:80 - connection timed out`

**Causa**: La porta 80 (HTTP) è bloccata, tipicamente in ambienti container o con firewall restrittivi.

**Soluzione**: Configurare APT per usare HTTPS invece di HTTP:

```bash
# 1. Cambia i repository da HTTP a HTTPS
sudo sed -i 's|http://archive.ubuntu.com|https://archive.ubuntu.com|g' /etc/apt/sources.list
sudo sed -i 's|http://it.archive.ubuntu.com|https://archive.ubuntu.com|g' /etc/apt/sources.list

# 2. Aggiorna l'indice dei pacchetti
sudo apt-get update

# 3. Installa le dipendenze
sudo apt-get install -y debhelper
```

**Nota**: HTTPS funziona sulla porta 443 che è generalmente aperta anche in ambienti con firewall restrittivi.

### Errore: "debhelper compat level specified both in debian/compat and via build-dependency"

**Causa**: Livello di compatibilità debhelper specificato in due posti.

**Soluzione**: Il file `debian/compat` è obsoleto e non dovrebbe esistere. Il livello di compatibilità è già specificato in `debian/control` tramite `debhelper-compat (= 13)`.

```bash
rm debian/compat
```

### Errore: "dpkg-buildpackage: command not found"

Installa le dipendenze:
```bash
make deb-deps
```

### Errore durante la build

Pulisci e riprova:
```bash
make clean
make build
```

### Errore di dipendenze durante l'installazione

```bash
sudo apt-get install -f -y
```

Questo comando installerà automaticamente tutte le dipendenze runtime necessarie:
- `python3` (>= 3.9)
- `python3-requests` (>= 2.31.0)
- `cron`

## Modificare il Pacchetto

Se vuoi modificare il pacchetto:

1. Modifica i file in `debian/`
2. Aggiorna `debian/changelog` con le tue modifiche:
   ```bash
   dch -i
   ```
3. Ricostruisci il pacchetto:
   ```bash
   make build
   ```

## Struttura della Directory debian/

```
debian/
├── changelog       - Storia delle versioni (formato Debian)
├── control        - Metadata del pacchetto e dipendenze
├── install        - File da installare e destinazioni (opzionale)
├── postinst       - Script post-installazione
└── rules          - Script di build (Makefile)
```

**Nota**: Il file `debian/compat` è obsoleto in debhelper >= 13 e non dovrebbe essere usato. Il livello di compatibilità è specificato in `debian/control` tramite `Build-Depends: debhelper-compat (= 13)`.

### Dettagli dei File

- **changelog**: Traccia tutte le versioni e modifiche del pacchetto
- **control**: Specifica metadati, dipendenze di build e runtime
- **install**: File aggiuntivi da installare (non usato, l'installazione è gestita da `rules`)
- **postinst**: Script eseguito dopo l'installazione del pacchetto
- **rules**: Makefile che definisce come costruire e installare il pacchetto

## Testing del Pacchetto

Prima di distribuire il pacchetto, testalo:

```bash
# Installa
sudo dpkg -i ../ionos-ddns_*.deb

# Testa
ionos-ddns --help

# Configura
sudo cp /etc/ionos-ddns/dns.json.example /etc/ionos-ddns/dns.json
sudo nano /etc/ionos-ddns/dns.json

# Esegui test
ionos-ddns your-hostname.your-domain.com --config /etc/ionos-ddns/dns.json

# Disinstalla
sudo apt remove ionos-ddns
```

## Distribuzione

Il file `.deb` può essere distribuito e installato su qualsiasi sistema Ubuntu 24.04 con:

```bash
sudo dpkg -i ionos-ddns_0.1.0-1_all.deb
sudo apt-get install -f  # Se necessario
```

## Creazione Repository APT (Opzionale)

Per creare un repository APT personalizzato, consulta la documentazione Debian su `reprepro` o usa servizi come Packagecloud.
