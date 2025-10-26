# Contributor: Fabrizio <fabrizio@example.com>
# Maintainer: Fabrizio <fabrizio@example.com>
pkgname=ionos-ddns
pkgver=0.2.0
pkgrel=0
pkgdesc="IONOS Dynamic DNS Updater - Automatic DNS record updates via IONOS API"
url="https://github.com/yourusername/ionos-ddns"
arch="noarch"
license="MIT"
depends="python3 py3-requests dcron"
makedepends=""
install="$pkgname.post-install"
subpackages="$pkgname-doc"
source="ionos_ddns.py
	ionos-ddns-setup-cron
	dns.json.example
	README.md
	"
builddir="$srcdir"
options="!check" # No test suite in minimal build

package() {
	# Install main script
	install -Dm755 "$builddir/ionos_ddns.py" \
		"$pkgdir/usr/bin/ionos-ddns"

	# Install cron setup helper
	install -Dm755 "$builddir/ionos-ddns-setup-cron" \
		"$pkgdir/usr/bin/ionos-ddns-setup-cron"

	# Install configuration example
	install -Dm644 "$builddir/dns.json.example" \
		"$pkgdir/etc/ionos-ddns/dns.json.example"

	# Install documentation
	install -Dm644 "$builddir/README.md" \
		"$pkgdir/usr/share/doc/$pkgname/README.md"
}

check() {
	# Optional: run tests if pytest is available
	# python3 -m pytest tests/ || true
	return 0
}

sha512sums="SKIP"
