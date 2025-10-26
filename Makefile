.PHONY: help build install clean deb-deps

help:
	@echo "IONOS Dynamic DNS Updater - Makefile"
	@echo ""
	@echo "Target disponibili:"
	@echo "  make deb-deps  - Installa le dipendenze per la build del pacchetto .deb"
	@echo "  make build     - Costruisce il pacchetto .deb"
	@echo "  make install   - Installa il pacchetto .deb generato"
	@echo "  make clean     - Pulisce i file di build"
	@echo ""

deb-deps:
	@echo "Installazione dipendenze per la build del pacchetto Debian..."
	@echo ""
	@echo "NOTA: Se apt-get fallisce con timeout sulla porta 80, esegui prima:"
	@echo "  sudo sed -i 's|http://archive.ubuntu.com|https://archive.ubuntu.com|g' /etc/apt/sources.list"
	@echo ""
	sudo apt-get update
	sudo apt-get install -y debhelper

build:
	@echo "Costruzione del pacchetto .deb..."
	dpkg-buildpackage -us -uc -b
	@echo ""
	@echo "Pacchetto costruito con successo!"
	@echo "File .deb generato nella directory parent:"
	@ls -lh ../ionos-ddns_*.deb

install:
	@echo "Installazione del pacchetto..."
	sudo dpkg -i ../ionos-ddns_*.deb
	@echo ""
	@echo "Pacchetto installato con successo!"
	@echo "Vedi le istruzioni di configurazione sopra."

clean:
	@echo "Pulizia file di build..."
	dh_clean
	rm -rf debian/ionos-ddns debian/.debhelper debian/files debian/debhelper-build-stamp
	rm -f debian/*.substvars debian/*.log
	@echo "Pulizia completata."
