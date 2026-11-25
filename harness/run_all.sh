#!/bin/sh
# run_all.sh — THE one README command. Re-runs the whole pack from a fresh
# clone: environment record, PQ benchmarks, classical baseline, burst model,
# then regenerates the SHA-256 manifest and verifies it. Exit 0 = pass.
#
#   sh harness/run_all.sh
#
# Notes:
# - Builds liboqs 0.14.0 from source on first run (a few minutes, network
#   needed once for the clone). Re-runs reuse .deps/liboqs.
# - Re-running produces NEW measurements, so SHA256SUMS is regenerated at
#   the end; the committed manifest covers the committed outputs, the
#   regenerated one covers the fresh run. See README.md ("Digests").
# - Logs keep their timestamps; re-runs are re-measurements, not
#   byte-identical reproductions. Values should agree within normal
#   run-to-run variance on the same hardware (see LIMITATIONS.md).
set -eu
cd "$(dirname "$0")/.."

sh harness/environment.sh outputs/environment.txt
sh harness/run_benchmarks.sh
sh harness/classical_speed.sh
python3 harness/burst_model.py

# Regenerate the manifest over the fresh outputs, then verify it.
# SHA256SUMS itself and reproduce.log are excluded from the manifest.
find . -type f \
  -not -path './.deps/*' \
  -not -path './.git/*' \
  -not -name 'SHA256SUMS' \
  -not -name 'reproduce.log' \
  -not -name 'bench_sig' \
  -not -name '*.pyc' \
  | LC_ALL=C sort | xargs sha256sum > SHA256SUMS

sh harness/verify_digests.sh
echo "run_all.sh: PASS (exit 0)"
