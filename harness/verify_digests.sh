#!/bin/sh
# verify_digests.sh — verify SHA256SUMS against the pack files.
# Exits 0 only if every listed file matches its recorded digest.
# Usage: sh harness/verify_digests.sh   (run from the pack root)
set -eu
cd "$(dirname "$0")/.."
if [ ! -f SHA256SUMS ]; then
    echo "SHA256SUMS missing" >&2
    exit 1
fi
sha256sum -c SHA256SUMS
