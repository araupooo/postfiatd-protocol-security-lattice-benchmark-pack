#!/bin/sh
# run_benchmarks.sh — build liboqs (if needed), compile bench_sig, run the
# ML-DSA / SLH-DSA verification benchmarks, append unedited output to
# outputs/benchmark-pq.log. Single-threaded; total runtime a few minutes.
set -eu
cd "$(dirname "$0")/.."
PACK_DIR="$(pwd)"
LIBOQS_SRC="${LIBOQS_SRC:-$PACK_DIR/.deps/liboqs}"
LIBOQS_BUILD="${LIBOQS_BUILD_DIR:-$LIBOQS_SRC/build}"
LOG="outputs/benchmark-pq.log"

if [ ! -f "$LIBOQS_BUILD/lib/liboqs.a" ]; then
    echo "liboqs not built yet; cloning tag 0.14.0 and building (one-time, a few minutes)..."
    if [ ! -d "$LIBOQS_SRC" ]; then
        git clone --depth 1 --branch 0.14.0 https://github.com/open-quantum-safe/liboqs.git "$LIBOQS_SRC"
    fi
    cmake -S "$LIBOQS_SRC" -B "$LIBOQS_BUILD" -DOQS_BUILD_ONLY_LIB=ON -DCMAKE_BUILD_TYPE=Release -DOQS_DIST_BUILD=OFF
    cmake --build "$LIBOQS_BUILD" -j 2
fi
echo "liboqs library: $LIBOQS_BUILD/lib/liboqs.a"

mkdir -p outputs
cc -O2 -I"$LIBOQS_SRC/src" -I"$LIBOQS_BUILD/include" \
    harness/bench_sig.c -L"$LIBOQS_BUILD/lib" -loqs -lcrypto -o harness/bench_sig
echo "bench_sig built: $(./harness/bench_sig 2>&1 | head -1 || true)"

{
    echo "=== pq-signature benchmark run ==="
    echo "date_utc: $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
    echo "liboqs: 0.14.0 (open-quantum-safe/liboqs, tag 0.14.0)"
    echo "message: fixed 32-byte vector (256-bit digest length, mirrors postfiatd sha512Half)"
    echo "threads: 1"
    echo "verify_budget_sec: 5"
    echo "sign_budget_sec: 5 (capped at 25 sign iterations per algorithm)"
    echo ""
} > "$LOG"

# liboqs 0.14.0 does not register the FIPS 205 names (SLH-DSA-SHA2-128s);
# the same parameter sets are registered under their SPHINCS+ names.
# "DISPLAY|LIBOQS-NAME" pairs; the raw log keeps the true liboqs name.
for pair in "ML-DSA-44|ML-DSA-44" "ML-DSA-65|ML-DSA-65" "ML-DSA-87|ML-DSA-87" \
            "SLH-DSA-SHA2-128s|SPHINCS+-SHA2-128s-simple" "SLH-DSA-SHA2-128f|SPHINCS+-SHA2-128f-simple"; do
    display="${pair%%|*}"
    alg="${pair#*|}"
    echo "--- $display ---" >> "$LOG"
    echo "liboqs_algorithm_name: $alg" >> "$LOG"
    ./harness/bench_sig "$alg" 5 5 >> "$LOG" 2>&1 || {
        echo "result: BENCHMARK_FAILED for $display ($alg)" >> "$LOG"
        echo "FAILED: $display ($alg) (see $LOG)"
    }
    echo "" >> "$LOG"
done
echo "date_utc_end: $(date -u '+%Y-%m-%dT%H:%M:%SZ')" >> "$LOG"
echo "wrote $LOG"
