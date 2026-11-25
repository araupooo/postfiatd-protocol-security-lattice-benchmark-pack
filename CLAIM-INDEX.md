# Claim-to-evidence index

Every measured or specification-derived claim in this pack, traced to its
script, raw output (file + line), digest entry, and primary source.
"Digest" means the file's entry in `SHA256SUMS` (full 64-hex digests in
that file; the manifest is regenerated on re-runs — see README.md
"Digests"). Line numbers refer to the committed raw logs.

## Measured claims (ML-DSA / SLH-DSA verification)

| ID | Claim | Script | Raw output (file:line) | Digest entry | Primary source |
|---|---|---|---|---|---|
| C-01 | ML-DSA-44 verifies at 26,163.257 ops/s (38.222 µs/op), single thread | `harness/bench_sig.c` via `harness/run_benchmarks.sh` | `outputs/benchmark-pq.log:22` (ops 130,817, line 20) | `outputs/benchmark-pq.log` | liboqs 0.14.0 (S-05); FIPS 204 (S-01) for the parameter set |
| C-02 | ML-DSA-44 sizes: pk 1,312 B, sig 2,420 B — match FIPS 204 Table 2 | `harness/bench_sig.c` (prints `length_*`); `harness/burst_model.py` aborts on mismatch | `outputs/benchmark-pq.log:14,16` | `outputs/benchmark-pq.log` | FIPS 204 Table 2 (S-01); cross-checked via RFC 9964 (S-03) |
| C-03 | ML-DSA-65 verifies at 16,779.197 ops/s (59.598 µs/op) | `harness/bench_sig.c` | `outputs/benchmark-pq.log:47` | `outputs/benchmark-pq.log` | liboqs 0.14.0 (S-05); FIPS 204 (S-01) |
| C-04 | ML-DSA-65 sizes: pk 1,952 B, sig 3,309 B — match FIPS 204 Table 2 | `harness/bench_sig.c`; `harness/burst_model.py` | `outputs/benchmark-pq.log:39,41` | `outputs/benchmark-pq.log` | FIPS 204 Table 2 (S-01) |
| C-05 | ML-DSA-87 verifies at 11,163.253 ops/s (89.580 µs/op) | `harness/bench_sig.c` | `outputs/benchmark-pq.log:72` | `outputs/benchmark-pq.log` | liboqs 0.14.0 (S-05); FIPS 204 (S-01) |
| C-06 | ML-DSA-87 sizes: pk 2,592 B, sig 4,627 B — match FIPS 204 Table 2 | `harness/bench_sig.c`; `harness/burst_model.py` | `outputs/benchmark-pq.log:64,66` | `outputs/benchmark-pq.log` | FIPS 204 Table 2 (S-01) |
| C-07 | SLH-DSA-SHA2-128s verifies at 2,461.518 ops/s (406.253 µs/op); signs at 3.579/s (279.378 ms/op) | `harness/bench_sig.c` (liboqs name `SPHINCS+-SHA2-128s-simple`) | `outputs/benchmark-pq.log:97,101` | `outputs/benchmark-pq.log` | liboqs 0.14.0 (S-05); FIPS 205 (S-02) |
| C-08 | SLH-DSA-SHA2-128s sizes: pk 32 B, sig 7,856 B — match FIPS 205 Table 2 | `harness/bench_sig.c`; `harness/burst_model.py` | `outputs/benchmark-pq.log:89,91` | `outputs/benchmark-pq.log` | FIPS 205 Table 2 (S-02) |
| C-09 | SLH-DSA-SHA2-128f verifies at 968.196 ops/s (1,032.849 µs/op); signs at 77.368/s | `harness/bench_sig.c` (liboqs name `SPHINCS+-SHA2-128f-simple`) | `outputs/benchmark-pq.log:121,125` | `outputs/benchmark-pq.log` | liboqs 0.14.0 (S-05); FIPS 205 (S-02) |
| C-10 | SLH-DSA-SHA2-128f sizes: pk 32 B, sig 17,088 B — match FIPS 205 Table 2 | `harness/bench_sig.c`; `harness/burst_model.py` | `outputs/benchmark-pq.log:113,115` | `outputs/benchmark-pq.log` | FIPS 205 Table 2 (S-02) |
| C-11 | Valid signatures verify; tampered signatures are rejected, for all 5 algorithms | `harness/bench_sig.c` controls | `outputs/benchmark-pq.log:18-19, 43-44, 68-69, 93-94, 117-118` | `outputs/benchmark-pq.log` | — (control, no external source) |
| C-12 | ML-DSA sign rates are lower bounds (25-iteration cap reached); SLH-DSA-128s sign rate is a direct measurement (18 ops, 5 s budget) | `harness/bench_sig.c` | `outputs/benchmark-pq.log:24-26, 49-51, 74-76, 99-101, 123-125` | `outputs/benchmark-pq.log` | — (harness behaviour) |

## Measured claims (classical baseline)

| ID | Claim | Script | Raw output (file:line) | Digest entry | Primary source |
|---|---|---|---|---|---|
| C-13 | Ed25519 verifies at 6,806.8 ops/s (OpenSSL 3.0.13, same box) | `harness/classical_speed.sh` (`openssl speed`) | `outputs/benchmark-classical.log:23` (also count line 14: 34,034 verifies in 5.00 s) | `outputs/benchmark-classical.log` | OpenSSL 3.0.13 (S-06) |
| C-14 | ECDSA P-256 verifies at 10,435.0 ops/s (OpenSSL 3.0.13, same box) | `harness/classical_speed.sh` | `outputs/benchmark-classical.log:21` (also count line 12: 52,175 verifies in 5.00 s) | `outputs/benchmark-classical.log` | OpenSSL 3.0.13 (S-06) |

## Measured claims (source inspection of the pinned revision)

| ID | Claim | Method | Evidence | Digest entry | Primary source |
|---|---|---|---|---|---|
| C-15 | postfiatd's only key types are secp256k1 and Ed25519 | `grep -n` on local checkout of pinned commit | `include/xrpl/protocol/KeyType.h` lines 28–31; blob SHA `810e3e6fdf49a2cb73449b3a387ad5ea525c2bba` | — (cited file is in postfiatd, not this pack) | postfiatd `0085a1ff885d6a446369cf73a4430f75af22be55` (S-04) |
| C-16 | All signature verification funnels through `verify`/`verifyDigest` in `PublicKey.cpp` | `grep -n` on local checkout | `src/libxrpl/protocol/PublicKey.cpp` lines 239 (`verifyDigest`), 289 (`verify`), 275/281 (secp256k1 verify), 304 (Ed25519 canonicality), 311 (`ed25519_sign_open`); blob SHA `54b50c80ef104b89a0dc7f357ca7d9a3e3edaab7` | — | postfiatd `0085a1ff885d6a446369cf73a4430f75af22be55` (S-04) |
| C-17 | Transaction signatures are checked in `STTx::checkSign` via `verify` | `grep -n` on local checkout | `src/libxrpl/protocol/STTx.cpp` lines 259, 282, 433, 532; blob SHA `ddbe294e47b4e4f4b7ac8d055ba8de99f7377568` | — | postfiatd `0085a1ff885d6a446369cf73a4430f75af22be55` (S-04) |
| C-18 | Validation signatures are secp256k1-only | `grep -n` on local checkout | `src/libxrpl/protocol/STValidation.cpp` lines 123, 127–129, 136; blob SHA `d2cb0586f261e9e06fa31f0da9c3fdc28cfc62ca` | — | postfiatd `0085a1ff885d6a446369cf73a4430f75af22be55` (S-04) |
| C-19 | The pinned revision contains no ML-DSA/SLH-DSA code (zero matches for 8 search terms across `src/`, `include/`, `docs/`) | `grep -rln` on local checkout | PINNED-REVISION.md ("What is NOT in the pinned revision") | — | postfiatd `0085a1ff885d6a446369cf73a4430f75af22be55` (S-04) |
| C-20 | Pinned HEAD `0085a1ff885d6a446369cf73a4430f75af22be55` (2026-10-10) agrees between local clone and GitHub API | `git rev-parse HEAD` + GitHub API commits endpoint | PINNED-REVISION.md ("How the pin was verified") | — | GitHub API, `postfiatorg/postfiatd` (S-04) |

## Simulated claims (burst model)

| ID | Claim | Script | Raw output | Digest entry | Measured inputs |
|---|---|---|---|---|---|
| C-21 | 100,000-signature burst drains in 3.82 s (ML-DSA-44) / 14.69 s (Ed25519) / 103.28 s (SLH-DSA-SHA2-128f), single thread | `harness/burst_model.py` | `outputs/burst-model.log:22` (B1); `outputs/burst-model.csv` rows `B1_drain_single_thread` | `outputs/burst-model.log`, `outputs/burst-model.csv` | C-01, C-07, C-09, C-13 |
| C-22 | Max signatures per 4 s window, single thread: ML-DSA-44 104,653.0; Ed25519 27,227.2; SLH-DSA-SHA2-128f 3,872.8 | `harness/burst_model.py` | `outputs/burst-model.log:25-32` (B2) | `outputs/burst-model.log` | C-01, C-09, C-13 |
| C-23 | Extra signature bytes vs Ed25519 for 100,000 tx: ML-DSA-44 +224.69 MiB; SLH-DSA-SHA2-128f +1,623.54 MiB | `harness/burst_model.py` | `outputs/burst-model.log:35-39` (B3) | `outputs/burst-model.log` | C-02, C-10, C-13 (64 B Ed25519 sig assumed) |
| C-24 | 100,000-signature burst by thread count (linear-scaling model): ML-DSA-44 3.82 / 1.91 / 0.96 s at 1 / 2 / 4 threads | `harness/burst_model.py` | `outputs/burst-model.log:41-48` (B4) | `outputs/burst-model.log` | C-01 et al.; linear scaling assumed, NOT measured |

## Unsupported claims (explicitly not established by this pack)

| ID | Claim | Why it is unsupported |
|---|---|---|
| U-01 | postfiatd's own secp256k1 verify throughput | libsecp256k1 was not benchmarked; the classical baseline uses OpenSSL P-256/Ed25519 (F-08). |
| U-02 | Post-quantum verification cost inside postfiatd | No PQ code exists in the pinned revision; all PQ rates are liboqs rates on this box (F-01). |
| U-03 | Multi-thread scaling of verification | Only single-thread rates were measured; B4 assumes linear scaling (C-24). |
| U-04 | Cost of rejecting an invalid PQ signature | Not measured separately; the model assumes 1.0x a full verify. |
| U-05 | Ledger-level effects (close time, gossip, storage) of PQ signatures | No postfiatd node was run; only arithmetic on measured rates and sizes (B1–B4). |
| U-06 | liboqs KAT correctness | KAT vectors were not executed; correctness rests on controls K-01–K-03. |
