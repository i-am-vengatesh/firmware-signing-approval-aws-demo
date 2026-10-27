#!/usr/bin/env bash
set -euo pipefail

ARTIFACT_DIR="build-artifacts"
ARTIFACT_NAME="firmware-build-info.txt"
CHECKSUM_NAME="firmware-build-info.sha256"

mkdir -p "$ARTIFACT_DIR"

ARTIFACT="$ARTIFACT_DIR/$ARTIFACT_NAME"
CHECKSUM="$ARTIFACT_DIR/$CHECKSUM_NAME"

echo "Step 1: Creating demo-only build information..."
cat > "$ARTIFACT" <<'ARTIFACT_EOF'
Project: FirmwareSigningDemo
Firmware-Version: 1.0.0
Platform: ARM64
Artifact-Type: DEMO-ONLY-NOT-REAL-FIRMWARE
Approval-Status: PENDING
ARTIFACT_EOF

echo "Step 2: Generating SHA-256 checksum..."
(
    cd "$ARTIFACT_DIR"
    sha256sum "$ARTIFACT_NAME" > "$CHECKSUM_NAME"
)

echo "Step 3: Verifying original artifact..."
(
    cd "$ARTIFACT_DIR"
    sha256sum --check "$CHECKSUM_NAME"
)

echo "PASS: Original artifact integrity verification succeeded."
