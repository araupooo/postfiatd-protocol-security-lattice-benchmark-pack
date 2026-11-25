#!/usr/bin/env python3
"""burst_model.py — SIMULATED transaction-burst model.

Reads MEASURED verify throughput from outputs/benchmark-pq.log (liboqs)
and outputs/benchmark-classical.log (OpenSSL speed) and models how long a
crafted burst of signatures would take a single-threaded verifier to drain,
and how many signatures fit in one ledger-close window.

Everything in this file is SIMULATED: it is arithmetic on measured inputs,
not a measurement of postfiatd itself. No postfiatd node was run. The model,
its parameters, and its measured inputs are printed in the output log so a
reviewer can recompute every number from the raw logs.

Model
-----
drain_time_seconds = burst_size / verify_ops_per_sec        (single thread)
max_per_window     = verify_ops_per_sec * window_seconds
extra_bytes        = burst_size * (pq_sig_bytes - classical_sig_bytes)
                     (signature bytes only; excludes key and overhead)

Parameters (assumptions, not measurements)
------------------------------------------
WINDOW_SECONDS = 4.0   Assumed ledger-close interval. The XRP Ledger targets
                       a ~3-4 s close; 4 s is used as a round modelling
                       number only. Change it and re-run to test sensitivity.
THREADS = 1, 2, 4      Multi-thread columns assume linear scaling with
                       thread count. That scaling was NOT measured; it is an
                       upper bound (real scaling is worse under contention).
INVALID_COST = 1.0     An invalid signature is modelled as costing one full
                       verify operation. The cost of rejecting an invalid
                       ML-DSA/SLH-DSA signature was NOT measured separately.
CLASSICAL_SIG_BYTES = 64  Ed25519 signature size (64 bytes). secp256k1 DER
                       signatures vary (~70-72 bytes); 64 is the Ed25519
                       figure used for the comparison column.

Usage: python3 harness/burst_model.py
Writes outputs/burst-model.csv and outputs/burst-model.log.
Exits non-zero if any measured input cannot be parsed (no silent defaults).
"""
import csv
import re
import sys
from pathlib import Path

PACK = Path(__file__).resolve().parent.parent
PQ_LOG = PACK / "outputs" / "benchmark-pq.log"
CLASSICAL_LOG = PACK / "outputs" / "benchmark-classical.log"
CSV_OUT = PACK / "outputs" / "burst-model.csv"
LOG_OUT = PACK / "outputs" / "burst-model.log"

WINDOW_SECONDS = 4.0
BURST_SIZES = [1_000, 10_000, 100_000, 1_000_000]
THREADS = [1, 2, 4]
CLASSICAL_SIG_BYTES = 64

# FIPS 204 / FIPS 205 signature sizes in bytes (specification values,
# cross-checked against the liboqs-measured length_signature in the PQ log).
SIG_BYTES = {
    "ML-DSA-44": 2420,
    "ML-DSA-65": 3309,
    "ML-DSA-87": 4627,
    "SLH-DSA-SHA2-128s": 7856,
    "SLH-DSA-SHA2-128f": 17088,
}


def parse_pq_rates(text):
    """Return {alg: verify_ops_per_sec} parsed from benchmark-pq.log."""
    rates = {}
    current = None
    for line in text.splitlines():
        m = re.match(r"---\s+(\S+)\s+---", line)
        if m:
            current = m.group(1)
            continue
        m = re.match(r"verify_ops_per_sec:\s+([0-9.]+)", line)
        if m and current:
            rates[current] = float(m.group(1))
        m = re.match(r"length_signature:\s+(\d+)", line)
        if m and current:
            measured = int(m.group(1))
            expected = SIG_BYTES.get(current)
            if expected is not None and measured != expected:
                raise SystemExit(
                    f"FIPS size cross-check FAILED for {current}: "
                    f"liboqs reports {measured}, FIPS table says {expected}")
    missing = [a for a in SIG_BYTES if a not in rates]
    if missing:
        raise SystemExit(f"could not parse verify rates for: {missing}")
    return rates


def parse_classical_rates(text):
    """Return {'Ed25519': verify ops/s, 'ECDSA P-256': verify ops/s}.

    OpenSSL speed prints, for each algorithm, a summary row of the form:
        256 bits ecdsa (nistp256)   0.0000s   0.0001s  29223.2  10435.0
        253 bits EdDSA (Ed25519)   0.0001s   0.0001s  18219.8   6806.8
    Columns: sign time, verify time, sign/s, verify/s. The LAST number is
    verify ops/sec. (The earlier "Doing ... verify in 5.00s" lines give the
    same rates as counts / 5 s and agree with the table.)
    """
    rates = {}
    for line in text.splitlines():
        m = re.match(
            r"\s*253 bits EdDSA \(Ed25519\)\s+[0-9.]+s\s+[0-9.]+s\s+([0-9.]+)\s+([0-9.]+)",
            line)
        if m:
            rates["Ed25519"] = float(m.group(2))
            continue
        m = re.match(
            r"\s*256 bits ecdsa \(nistp256\)\s+[0-9.]+s\s+[0-9.]+s\s+([0-9.]+)\s+([0-9.]+)",
            line)
        if m:
            rates["ECDSA P-256"] = float(m.group(2))
    if "Ed25519" not in rates or "ECDSA P-256" not in rates:
        raise SystemExit(
            "could not parse classical verify rates from OpenSSL speed output; "
            f"got {rates}")
    return rates


def main():
    pq_text = PQ_LOG.read_text()
    classical_text = CLASSICAL_LOG.read_text()
    pq_rates = parse_pq_rates(pq_text)
    classical_rates = parse_classical_rates(classical_text)

    all_rates = {}
    all_rates.update(classical_rates)
    all_rates.update(pq_rates)

    lines = []
    lines.append("=== transaction-burst model (SIMULATED) ===")
    lines.append("status: SIMULATED — arithmetic on measured inputs, not a postfiatd measurement")
    lines.append(f"window_seconds_assumed: {WINDOW_SECONDS}")
    lines.append("threads_modelled: 1, 2, 4 (linear scaling assumed, NOT measured)")
    lines.append("invalid_signature_cost_modelled: 1.0 x one full verify (NOT measured separately)")
    lines.append(f"classical_signature_bytes_assumed: {CLASSICAL_SIG_BYTES} (Ed25519)")
    lines.append("measured_inputs:")
    lines.append(f"  pq_log: {PQ_LOG.name}")
    lines.append(f"  classical_log: {CLASSICAL_LOG.name}")
    for alg, rate in all_rates.items():
        lines.append(f"  measured_verify_ops_per_sec[{alg}]: {rate:.3f}")
    lines.append("")
    lines.append("--- B1: single-thread drain time (seconds) for a burst of N signatures ---")
    lines.append("burst_size | " + " | ".join(f"{a}" for a in all_rates))
    for n in BURST_SIZES:
        cells = " | ".join(f"{n / all_rates[a]:.2f}" for a in all_rates)
        lines.append(f"{n} | {cells}")
    lines.append("")
    lines.append(f"--- B2: max signatures verifiable in one {WINDOW_SECONDS:.0f} s window (single thread) ---")
    for alg, rate in all_rates.items():
        lines.append(f"  {alg}: {rate * WINDOW_SECONDS:.1f}")
    lines.append("")
    lines.append("--- B3: extra signature bytes vs Ed25519 for a burst of N tx (MiB) ---")
    for alg, sig_bytes in SIG_BYTES.items():
        extra = sig_bytes - CLASSICAL_SIG_BYTES
        cells = " | ".join(f"{n * extra / 1048576:.2f}" for n in BURST_SIZES)
        lines.append(f"  {alg} (+{extra} B/sig): {cells}")
    lines.append("")
    lines.append("--- B4: drain time (seconds) for a 100,000-signature burst by thread count (linear-scaling model) ---")
    for alg, rate in all_rates.items():
        cells = " | ".join(f"{100000 / (rate * t):.2f}" for t in THREADS)
        lines.append(f"  {alg}: {cells}  (threads 1 | 2 | 4)")
    lines.append("")
    lines.append("--- B5: burst headroom — how many x the current classical rate each PQ scheme costs ---")
    base = classical_rates["Ed25519"]
    for alg in SIG_BYTES:
        lines.append(f"  {alg}: verify is {base / pq_rates[alg]:.1f}x slower than Ed25519; "
                     f"drain time {pq_rates[alg] and base / pq_rates[alg]:.1f}x longer")
    lines.append("")
    lines.append("recompute: drain_time = burst_size / verify_ops_per_sec; "
                 "all inputs above are copied from the raw logs named here.")

    LOG_OUT.write_text("\n".join(lines) + "\n")

    with open(CSV_OUT, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["scenario", "algorithm", "burst_size", "threads",
                    "verify_ops_per_sec_measured", "drain_time_seconds",
                    "max_per_4s_window", "extra_sig_bytes_vs_ed25519"])
        for alg, rate in all_rates.items():
            for n in BURST_SIZES:
                extra = SIG_BYTES.get(alg, CLASSICAL_SIG_BYTES) - CLASSICAL_SIG_BYTES
                w.writerow(["B1_drain_single_thread", alg, n, 1, f"{rate:.3f}",
                            f"{n / rate:.3f}", f"{rate * WINDOW_SECONDS:.1f}", extra])
            for t in THREADS:
                w.writerow(["B4_drain_100k_by_threads", alg, 100000, t, f"{rate:.3f}",
                            f"{100000 / (rate * t):.3f}", "", ""])
    print(f"wrote {CSV_OUT}")
    print(f"wrote {LOG_OUT}")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
