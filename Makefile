.PHONY: help build install clean deb-deps apk-deps apk-build apk-install detect-distro

# Auto-detect distribution
DISTRO := $(shell if [ -f /etc/os-release ]; then . /etc/os-release && echo $$ID; else echo "unknown"; fi)

help:
	@echo "IONOS Dynamic DNS Updater - Makefile"
	@echo ""
	@echo "Distribuzione rilevata: $(DISTRO)"
	@echo ""
	@echo "=== Target generici (auto-detection) ==="
	@echo "  make deps      - Installa dipendenze per la build (rileva distro)"
	@echo "  make build     - Costruisce il pacchetto nativo (rileva distro)"
	@echo "  make install   - Installa il pacchetto generato (rileva distro)"
	@echo "  make clean     - Pulisce i file di build"
	@echo ""
	@echo "=== Target Debian/Ubuntu specifici ==="
	@echo "  make deb-deps  - Installa dipendenze per build .deb"
	@echo "  make deb-build - Costruisce pacchetto .deb"
	@echo "  make deb-install - Installa pacchetto .deb"
	@echo ""
	@echo "=== Target Alpine Linux specifici ==="
	@echo "  make apk-deps  - Installa dipendenze per build .apk"
	@echo "  make apk-build - Costruisce pacchetto .apk"
	@echo "  make apk-install - Installa pacchetto .apk"
	@echo ""

detect-distro:
	@echo "Distribuzione rilevata: $(DISTRO)"

# Generic targets that auto-detect distribution
deps:
ifeq ($(DISTRO),alpine)
	@$(MAKE) apk-deps
else ifeq ($(DISTRO),debian)
	@$(MAKE) deb-deps
else ifeq ($(DISTRO),ubuntu)
	@$(MAKE) deb-deps
else
	@echo "ERRORE: Distribuzione '$(DISTRO)' non supportata"
	@echo "Distribuzioni supportate: Debian, Ubuntu, Alpine Linux"
	@exit 1
endif

build:
ifeq ($(DISTRO),alpine)
	@$(MAKE) apk-build
else ifeq ($(DISTRO),debian)
	@$(MAKE) deb-build
else ifeq ($(DISTRO),ubuntu)
	@$(MAKE) deb-build
else
	@echo "ERRORE: Distribuzione '$(DISTRO)' non supportata"
	@exit 1
endif

install:
ifeq ($(DISTRO),alpine)
	@$(MAKE) apk-install
else ifeq ($(DISTRO),debian)
	@$(MAKE) deb-install
else ifeq ($(DISTRO),ubuntu)
	@$(MAKE) deb-install
else
	@echo "ERRORE: Distribuzione '$(DISTRO)' non supportata"
	@exit 1
endif

# ========================================
# Debian/Ubuntu specific targets
# ========================================
deb-deps:
	@echo "Installazione dipendenze per la build del pacchetto Debian..."
	@echo ""
	@echo "NOTA: Se apt-get fallisce con timeout sulla porta 80, esegui prima:"
	@echo "  sudo sed -i 's|http://archive.ubuntu.com|https://archive.ubuntu.com|g' /etc/apt/sources.list"
	@echo ""
	sudo apt-get update
	sudo apt-get install -y debhelper

deb-build:
	@echo "Costruzione del pacchetto .deb..."
	dpkg-buildpackage -us -uc -b
	@echo ""
	@echo "Pacchetto costruito con successo!"
	@echo "File .deb generato nella directory parent:"
	@ls -lh ../ionos-ddns_*.deb

deb-install:
	@echo "Installazione del pacchetto Debian..."
	sudo dpkg -i ../ionos-ddns_*.deb
	@echo ""
	@echo "Pacchetto installato con successo!"
	@echo "Vedi le istruzioni di configurazione sopra."

# ========================================
# Alpine Linux specific targets
# ========================================
apk-deps:
	@echo "Installazione dipendenze per la build del pacchetto Alpine..."
	@echo ""
	sudo apk add --no-cache alpine-sdk
	@echo ""
	@echo "Configurazione utente per abuild..."
	@if ! id -nG | grep -qw abuild; then \
		sudo addgroup $$USER abuild; \
		echo "Utente aggiunto al gruppo 'abuild'"; \
		echo "NOTA: Potrebbe essere necessario fare logout/login"; \
	fi
	@if [ ! -f ~/.abuild/abuild.conf ]; then \
		mkdir -p ~/.abuild; \
		echo "PACKAGER_PRIVKEY=\"~/.abuild/$$USER.rsa\"" > ~/.abuild/abuild.conf; \
		abuild-keygen -a -i -n; \
		echo "Chiavi abuild generate in ~/.abuild/"; \
	fi

apk-build:
	@echo "Costruzione del pacchetto .apk per Alpine Linux..."
	@echo ""
	@if [ ! -f APKBUILD ]; then \
		echo "ERRORE: File APKBUILD non trovato!"; \
		exit 1; \
	fi
	@echo "Generazione checksum..."
	abuild checksum
	@echo ""
	@echo "Build del pacchetto..."
	abuild -rK
	@echo ""
	@echo "Pacchetto costruito con successo!"
	@echo "File .apk disponibili in ~/packages/"
	@find ~/packages -name "ionos-ddns-*.apk" -type f 2>/dev/null || true

apk-install:
	@echo "Installazione del pacchetto Alpine..."
	@APK_FILE=$$(find ~/packages -name "ionos-ddns-*.apk" -type f 2>/dev/null | head -1); \
	if [ -z "$$APK_FILE" ]; then \
		echo "ERRORE: Nessun pacchetto .apk trovato in ~/packages/"; \
		echo "Esegui prima 'make apk-build'"; \
		exit 1; \
	fi; \
	echo "Installazione di $$APK_FILE..."; \
	sudo apk add --allow-untrusted "$$APK_FILE"
	@echo ""
	@echo "Pacchetto installato con successo!"

# ========================================
# Generic clean target
# ========================================
clean:
	@echo "Pulizia file di build..."
	@# Debian cleanup
	@if [ -d debian ]; then \
		dh_clean 2>/dev/null || true; \
		rm -rf debian/ionos-ddns debian/.debhelper debian/files debian/debhelper-build-stamp; \
		rm -f debian/*.substvars debian/*.log; \
	fi
	@# Alpine cleanup
	@if [ -f APKBUILD ]; then \
		abuild clean 2>/dev/null || true; \
		rm -f .APKINDEX.* *.tar.gz; \
	fi
	@# Generic cleanup
	rm -rf __pycache__ *.pyc .pytest_cache
	@echo "Pulizia completata."
