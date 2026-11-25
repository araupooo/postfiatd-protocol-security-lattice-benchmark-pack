# Postfiatd Protocol Security and Lattice Benchmark Pack

Assessment of postfiatd main HEAD `0085a1ff885d6a446369cf73a4430f75af22be55`
(2026-10-10): ML-DSA and SLH-DSA signature-verification performance,
crafted transaction-burst behaviour, hybrid classical/post-quantum
migration options, and remediation for the highest-risk findings.

## Headline measured results (single thread, this box)

| Scheme | Verify ops/s | Verify µs/op | Signature | Public key |
|---|---|---|---|---|
| Ed25519 (OpenSSL baseline) | 6,806.8 | 146.9 | 64 B | 32 B |
| ECDSA P-256 (OpenSSL baseline) | 10,435.0 | 95.8 | ~70 B | 33 B* |
| ML-DSA-44 | 26,163.3 | 38.2 | 2,420 B | 1,312 B |
| ML-DSA-65 | 16,779.2 | 59.6 | 3,309 B | 1,952 B |
| ML-DSA-87 | 11,163.3 | 89.6 | 4,627 B | 2,592 B |
| SLH-DSA-SHA2-128s | 2,461.5 | 406.3 | 7,856 B | 32 B |
| SLH-DSA-SHA2-128f | 968.2 | 1,032.8 | 17,088 B | 32 B |

\* ECDSA P-256 signature size is DER-encoded and varies; the classical
comparison in the burst model uses the 64-byte Ed25519 figure.

Two results matter most. First, the pinned revision contains **no
post-quantum signature code at all** — the only key types are secp256k1
and Ed25519. Second, **ML-DSA verification is faster than the classical
baseline on this box**, while SLH-DSA is far slower and far larger: the
migration cost is signature size, not verify speed. The burst model
(SIMULATED) puts numbers on that: a crafted 100,000-signature burst
drains in 3.8 s under ML-DSA-44, 14.7 s under Ed25519, and 103.3 s under
SLH-DSA-SHA2-128f, single-threaded.

## Reproduce

One command, from the pack root:

```sh
sh harness/run_all.sh
```

It records the environment, builds liboqs 0.14.0 from source on first run
(a few minutes, network needed once for the clone), compiles the
benchmark, runs the ML-DSA/SLH-DSA benchmarks and the classical OpenSSL
baseline, runs the burst model, regenerates `SHA256SUMS`, and verifies
the digests. Exit 0 means the run passed. The committed reproduction log
is `outputs/reproduce.log`.

Requirements: `cc`, `cmake`, `git`, `python3`, `openssl` (3.0.x is fine),
a C compiler toolchain. No payment, no credentials, no account needed.

## Digests

`SHA256SUMS` lists the SHA-256 of every pack file (full 64-hex digests).
Verify at any time with:

```sh
sh harness/verify_digests.sh
```

Re-running `run_all.sh` produces new measurements, so it regenerates
`SHA256SUMS` at the end; the committed manifest covers the committed
outputs, the regenerated one covers the fresh run. Logs keep their
timestamps, so re-runs are re-measurements, not byte-identical
reproductions — values should agree within normal run-to-run variance on
the same hardware (see LIMITATIONS.md).

## Contents

| File | What it is |
|---|---|
| `PINNED-REVISION.md` | The pinned postfiatd revision, how the pin was verified, and the signature-verification code paths (file, line, blob SHA). |
| `SOURCES.md` | Primary sources: FIPS 204, FIPS 205, RFC 9964, postfiatd, liboqs, OpenSSL. |
| `CONTROLS.md` | Controls and how each was checked, including known control gaps. |
| `FINDINGS.md` | 8 ranked findings (2 High, 4 Medium, 2 Low), each labelled [MEASURED], [SIMULATED], or [UNSUPPORTED]. |
| `REMEDIATION.md` | Prioritised operator remediation (P0–P3). |
| `DECISION-MEMO.md` | Hybrid-migration decision memo: recommends dual-signature ML-DSA-44 for transactions; SLH-DSA offline only. |
| `CLAIM-INDEX.md` | Every claim traced to its script, raw output file + line, digest entry, and primary source. |
| `LIMITATIONS.md` | Honest limits: what this pack does not establish. |
| `harness/bench_sig.c` | C benchmark harness (liboqs API). |
| `harness/run_benchmarks.sh` | Builds liboqs if needed; runs the PQ benchmarks. |
| `harness/classical_speed.sh` | Classical baseline via `openssl speed`. |
| `harness/burst_model.py` | SIMULATED burst model (reads measured rates from the raw logs). |
| `harness/environment.sh` | Environment record. |
| `harness/run_all.sh` | The one reproduce command. |
| `harness/verify_digests.sh` | Digest verification (exit 0 = pass). |
| `outputs/` | Unedited raw logs, environment record, burst model outputs. |
| `SHA256SUMS` | SHA-256 manifest over all pack files. |

## Result classes

- **[MEASURED]** — produced by running the harness on this box, or by
  reading the pinned source. Traceable in CLAIM-INDEX.md.
- **[SIMULATED]** — arithmetic on measured inputs (the burst model). The
  model, parameters, and inputs are printed in `outputs/burst-model.log`.
- **[UNSUPPORTED]** — could not be tested here (e.g. secp256k1 baseline,
  postfiatd-internal PQ cost, KAT vectors). Listed in CLAIM-INDEX.md
  (U-01–U-06) and LIMITATIONS.md.

## Environment

Ubuntu 24.04.5, AMD EPYC 9D25, 4 logical CPUs (~1.5 shared), 7.7 GiB
RAM, OpenSSL 3.0.13, liboqs 0.14.0, gcc 13.3.0, cmake 3.28.3, Python
3.12.3. Full record in `outputs/environment.txt`.
