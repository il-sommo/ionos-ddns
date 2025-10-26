# Guida alla Build dei Pacchetti

Questa guida spiega come costruire i pacchetti nativi per IONOS Dynamic DNS Updater su diverse distribuzioni Linux.

## Distribuzioni Supportate

- **Debian/Ubuntu**: Pacchetto `.deb` (testato su Ubuntu 24.04)
- **Alpine Linux**: Pacchetto `.apk` (testato su Alpine 3.22.2 x64)

Il Makefile rileva automaticamente la distribuzione e usa il sistema di packaging appropriato.

## Auto-Detection della Distribuzione

Il Makefile rileva automaticamente la tua distribuzione:

```bash
make detect-distro
```

Output esempio:
```
Distribuzione rilevata: ubuntu
```

Puoi usare i target generici che rilevano automaticamente la distro oppure i target specifici per ogni distribuzione.

---

## Build Rapida (Auto-Detection)

Per un build veloce su qualsiasi distribuzione supportata:

```bash
# 1. Installa dipendenze di build
make deps

# 2. Costruisci il pacchetto nativo
make build

# 3. Installa il pacchetto
make install
```

Il sistema rileverà automaticamente se sei su Debian/Ubuntu o Alpine e userà il metodo appropriato.

---

## Debian/Ubuntu - Build Pacchetto .deb

### Prerequisiti

Sistema operativo: Ubuntu 24.04 (Noble Numbat) o Debian equivalente

### Installazione Dipendenze

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
# Build del pacchetto .deb
make deb-build

# Oppure usa il target generico che rileva la distro
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

---

## Alpine Linux - Build Pacchetto .apk

### Prerequisiti

Sistema operativo: Alpine Linux 3.22 o superiore

### Installazione Dipendenze

Installa gli strumenti necessari per costruire pacchetti Alpine:

```bash
make apk-deps
```

Questo installerà:
- `alpine-sdk` (strumenti di build)
- Configurerà `abuild` con chiavi di firma
- Aggiungerà l'utente al gruppo `abuild`

**Nota**: Potrebbe essere necessario fare logout/login dopo l'installazione per rendere effettivo il gruppo `abuild`.

### Costruzione del Pacchetto

```bash
# Build del pacchetto .apk
make apk-build

# Il file .apk sarà creato in ~/packages/
find ~/packages -name "ionos-ddns-*.apk"
```

### Installazione del Pacchetto

```bash
# Usando il Makefile
make apk-install

# Oppure manualmente
sudo apk add --allow-untrusted ~/packages/*/ionos-ddns-*.apk
```

### Output della Build

Dopo la build, troverai in `~/packages/builder/x86_64/`:

- `ionos-ddns-0.1.0-r0.apk` - Pacchetto principale (~13 KB)
- `ionos-ddns-doc-0.1.0-r0.apk` - Documentazione (~6 KB)

### Verifica dell'Installazione

```bash
# Verifica che il comando sia disponibile
which ionos-ddns

# Verifica la versione
apk info ionos-ddns

# Verifica i file installati
apk info -L ionos-ddns
```

File installati:
- `/usr/bin/ionos-ddns` - Script principale
- `/usr/bin/ionos-ddns-setup-cron` - Helper per configurare cron
- `/etc/ionos-ddns/dns.json.example` - File di configurazione esempio
- `/usr/share/doc/ionos-ddns/README.md` - Documentazione

### Build con Docker (Consigliato per Testing)

Se non hai Alpine Linux installato, puoi usare Docker per costruire e testare il pacchetto:

```bash
# Costruisci il pacchetto in un container Alpine
sudo docker build -f Dockerfile.alpine -t ionos-ddns-alpine-build .

# Estrai i pacchetti costruiti
mkdir -p dist/alpine
sudo docker run --rm -v $(pwd)/dist/alpine:/output \
    ionos-ddns-alpine-build \
    sh -c "cp /home/builder/packages/builder/x86_64/ionos-ddns-*.apk /output/"

# Verifica i pacchetti estratti
ls -lh dist/alpine/

# Testa l'installazione in un container Alpine pulito
sudo docker run --rm -v $(pwd)/dist/alpine:/packages alpine:3.22 sh -c "
    apk add --no-cache python3 py3-requests dcron
    apk add --allow-untrusted /packages/ionos-ddns-0.1.0-r0.apk
    ionos-ddns --help
"
```

Oppure usa lo script helper:

```bash
# Build automatizzato con Docker
./docker-build-alpine.sh
```

Lo script eseguirà:
1. Build dell'immagine Docker
2. Costruzione del pacchetto APK
3. Estrazione del pacchetto in `dist/alpine/`
4. Verifica dell'installazione

---

## Troubleshooting

### Problema Connettività APT (Debian/Ubuntu)

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

### Errore di dipendenze durante l'installazione (Debian/Ubuntu)

```bash
sudo apt-get install -f -y
```

Questo comando installerà automaticamente tutte le dipendenze runtime necessarie:
- `python3` (>= 3.9)
- `python3-requests` (>= 2.31.0)
- `cron`

### Errori Alpine Linux

#### Errore: "ERROR: ionos-ddns: UNTRUSTED signature"

**Soluzione**: Usa `--allow-untrusted` durante l'installazione:

```bash
sudo apk add --allow-untrusted ~/packages/*/ionos-ddns-*.apk
```

Oppure installa la chiave pubblica:

```bash
sudo cp ~/.abuild/*.rsa.pub /etc/apk/keys/
sudo apk add ~/packages/*/ionos-ddns-*.apk
```

#### Errore: "abuild: command not found"

Installa le dipendenze:

```bash
make apk-deps
```

#### Errore: "Permission denied" durante abuild

Assicurati di essere nel gruppo `abuild`:

```bash
sudo addgroup $USER abuild
# Logout e login necessari
```

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

## Struttura del Progetto

### File di Packaging

```
.
├── debian/                              # Debian/Ubuntu packaging
│   ├── changelog                        # Storia versioni (formato Debian)
│   ├── control                          # Metadata e dipendenze
│   ├── postinst                         # Script post-installazione
│   └── rules                            # Script di build (Makefile)
│
├── APKBUILD                             # Alpine Linux package definition
├── ionos-ddns.post-install              # Alpine post-install script
│
├── Dockerfile.alpine                    # Docker per build Alpine
├── docker-build-alpine.sh               # Script helper build Docker
│
├── Makefile                             # Build system con auto-detection
├── BUILDING.md                          # Questa guida
└── README.md                            # Documentazione principale
```

### Dettagli dei File Debian

- **debian/changelog**: Traccia tutte le versioni e modifiche del pacchetto
- **debian/control**: Specifica metadati, dipendenze di build e runtime
- **debian/postinst**: Script eseguito dopo l'installazione del pacchetto
- **debian/rules**: Makefile che definisce come costruire e installare il pacchetto

**Nota**: Il file `debian/compat` è obsoleto in debhelper >= 13 e non dovrebbe essere usato. Il livello di compatibilità è specificato in `debian/control` tramite `Build-Depends: debhelper-compat (= 13)`.

### Dettagli dei File Alpine

- **APKBUILD**: File principale di definizione del pacchetto Alpine (simile a Debian control + rules)
- **ionos-ddns.post-install**: Script eseguito dopo l'installazione (equivalente a debian/postinst)
- **Dockerfile.alpine**: Ambiente di build Docker per Alpine Linux
- **docker-build-alpine.sh**: Script automatizzato per build e test con Docker

## Testing del Pacchetto

### Testing Debian/Ubuntu

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

### Testing Alpine Linux

```bash
# Installa
sudo apk add --allow-untrusted ~/packages/*/ionos-ddns-*.apk

# Testa
ionos-ddns --help

# Configura
sudo cp /etc/ionos-ddns/dns.json.example /etc/ionos-ddns/dns.json
sudo vi /etc/ionos-ddns/dns.json

# Esegui test
ionos-ddns your-hostname.your-domain.com --config /etc/ionos-ddns/dns.json

# Disinstalla
sudo apk del ionos-ddns
```

## Distribuzione

### Debian/Ubuntu

Il file `.deb` può essere distribuito e installato su qualsiasi sistema Ubuntu 24.04/Debian con:

```bash
sudo dpkg -i ionos-ddns_0.1.0-1_all.deb
sudo apt-get install -f  # Se necessario
```

### Alpine Linux

Il file `.apk` può essere distribuito e installato su Alpine Linux 3.22+ con:

```bash
sudo apk add --allow-untrusted ionos-ddns-0.1.0-r0.apk
```

### Creazione Repository

#### Repository APT (Debian/Ubuntu)

Per creare un repository APT personalizzato, consulta:
- Documentazione Debian su `reprepro`
- Servizi cloud come Packagecloud, Cloudsmith

#### Repository APK (Alpine)

Per creare un repository APK:

```bash
# Genera index firmato
apk index -o APKINDEX.tar.gz ~/packages/builder/x86_64/*.apk
abuild-sign -k ~/.abuild/*.rsa APKINDEX.tar.gz

# Pubblica su server HTTP/S
# Gli utenti aggiungeranno: echo "http://your-repo/path" | sudo tee -a /etc/apk/repositories
```

## Comparazione Pacchetti

| Caratteristica | Debian (.deb) | Alpine (.apk) |
|----------------|---------------|---------------|
| **Dimensione pacchetto** | ~5 KB | ~13 KB |
| **Dipendenze totali** | ~15 MB | ~15 MB |
| **Tool di build** | debhelper, dpkg | alpine-sdk, abuild |
| **Formato compressione** | gzip/xz | gzip |
| **Sistema init** | systemd | OpenRC |
| **Cron daemon** | cron | dcron |
| **Firma pacchetto** | GPG (opzionale) | RSA (integrata) |
| **Repository** | APT | APK |

Entrambi i pacchetti installano gli stessi file e offrono la stessa funzionalità.
