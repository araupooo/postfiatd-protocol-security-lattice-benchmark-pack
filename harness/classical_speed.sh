#!/bin/sh
# classical_speed.sh — classical signature baseline on the same box, using
# the system OpenSSL speed test (no build needed). Appends unedited output
# to outputs/benchmark-classical.log. Single-threaded (-multi 0 default is
# single process; we pass no -multi flag).
set -eu
cd "$(dirname "$0")/.."
LOG="outputs/benchmark-classical.log"
mkdir -p outputs
{
    echo "=== classical signature baseline (OpenSSL speed) ==="
    echo "date_utc: $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
    echo "openssl: $(openssl version)"
    echo "command: openssl speed -elapsed -seconds 5 ed25519 ecdsap256"
    echo "note: Ed25519 is what postfiatd uses for Ed25519 keys"
    echo "      (external/ed25519-donna); ECDSA P-256 stands in for the"
    echo "      secp256k1 ECDSA path (same curve family, different curve)."
    echo "      secp256k1 itself is NOT measured here; see LIMITATIONS.md."
    echo ""
} > "$LOG"
openssl speed -elapsed -seconds 5 ed25519 ecdsap256 >> "$LOG" 2>&1
echo "date_utc_end: $(date -u '+%Y-%m-%dT%H:%M:%SZ')" >> "$LOG"
echo "wrote $LOG"
