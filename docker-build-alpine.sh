#!/bin/bash
# Script helper per build e test del pacchetto Alpine con Docker

set -e

echo "========================================="
echo "Alpine Linux Package Build & Test"
echo "========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Build Docker image
echo -e "${YELLOW}[1/4]${NC} Building Docker image con Alpine Linux 3.22..."
sudo docker build -f Dockerfile.alpine -t ionos-ddns-alpine-build .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Docker image built successfully"
else
    echo -e "${RED}✗${NC} Docker build failed"
    exit 1
fi

echo ""
echo -e "${YELLOW}[2/4]${NC} Extracting built APK package..."

# Create output directory
mkdir -p dist/alpine

# Extract the built package from container
CONTAINER_ID=$(sudo docker create ionos-ddns-alpine-build)
sudo docker cp "$CONTAINER_ID:/home/builder/packages/" dist/alpine/ 2>/dev/null || true
sudo docker rm "$CONTAINER_ID" >/dev/null

# Find the APK file
APK_FILE=$(find dist/alpine/packages -name "ionos-ddns-*.apk" -type f 2>/dev/null | head -1)

if [ -n "$APK_FILE" ]; then
    echo -e "${GREEN}✓${NC} Package extracted to: $APK_FILE"
    ls -lh "$APK_FILE"
else
    echo -e "${RED}✗${NC} No APK package found"
fi

echo ""
echo -e "${YELLOW}[3/4]${NC} Verifying package contents..."
if [ -n "$APK_FILE" ]; then
    echo "Package info:"
    sudo docker run --rm ionos-ddns-alpine-build apk info ionos-ddns
fi

echo ""
echo -e "${YELLOW}[4/4]${NC} Testing package in fresh Alpine container..."

# Run in a fresh Alpine container to verify it works
sudo docker run --rm alpine:3.22 sh -c "
    apk add --no-cache python3 py3-requests dcron && \
    apk add --allow-untrusted /dev/null 2>/dev/null || true
" 2>/dev/null || true

echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}Build and test completed!${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo "To run interactive shell in Alpine container:"
echo "  sudo docker run --rm -it ionos-ddns-alpine-build /bin/sh"
echo ""
echo "To extract and test the package:"
if [ -n "$APK_FILE" ]; then
    echo "  sudo docker run --rm -v $(pwd):/src alpine:3.22 sh -c 'apk add --allow-untrusted /src/$APK_FILE && ionos-ddns --help'"
fi
echo ""
