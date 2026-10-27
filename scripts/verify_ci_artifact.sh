#!/usr/bin/env bash
set -euo pipefail

ARTIFACT_DIR="build-artifacts"
ARTIFACT="$ARTIFACT_DIR/firmware-build-info.txt"
CHECKSUM="$ARTIFACT_DIR/firmware-build-info.sha256"

mkdir -p "$ARTIFACT_DIR"

echo "Step 1: Creating a demo-only firmware build-info artifact..."
cat > "$ARTIFACT" <<'ARTIFACT_EOF'
Project: FirmwareSigningDemo
Firmware-Version: 1.0.0
Platform: ARM64
Artifact-Type: DEMO-ONLY-NOT-REAL-FIRMWARE
Approval-Status: PENDING
ARTIFACT_EOF

echo "Step 2: Generating SHA-256 checksum..."
sha256sum "$ARTIFACT" > "$CHECKSUM"
cat "$CHECKSUM"

echo
echo "Step 3: Verifying artifact against its checksum..."
sha256sum --check "$CHECKSUM"

echo
echo "PASS: Demo artifact integrity verification succeeded."
