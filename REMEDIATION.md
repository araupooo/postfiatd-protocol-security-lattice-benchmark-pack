# Operator remediation (prioritised)

Ordered by risk reduction per unit of work. Items marked **[MEASURED]**
rest on numbers in this pack; **[SIMULATED]** rest on the burst model;
**[UNSUPPORTED]** could not be tested here and needs its own measurement
before it is relied on.

## P0 — Do now (no code changes)

### R-01 — Cap per-peer signature-verification work
**Addresses F-03, F-05 · [SIMULATED]**

A single peer can already force a verifier to spend 14.7 s of single-thread
verify time with 100,000 Ed25519 signatures (model B1); under SLH-DSA
that becomes 103.3 s. Before any PQ scheme is adopted, enforce a
per-peer, per-window budget on signature verifications (count, not just
bytes), with invalid signatures charged the same as valid ones, and shed
load (drop, then disconnect) when the budget is exceeded. The budget
should be set from measured verify rates on the operator's own hardware,
not from the numbers in this pack.

### R-02 — Log and alert on verify latency
**Addresses F-03, F-05 · [UNSUPPORTED — no postfiatd node was run]**

Record a histogram of per-signature verify time on the transaction and
validation paths, and alert when the 99th percentile or the queue depth
moves. Without this baseline, a burst (F-03) is invisible until the node
is already behind. This is observability work, not a protocol change.

## P1 — Before any PQ code lands

### R-03 — Run the liboqs KAT suite and interop vectors for ML-DSA-44
**Addresses F-01, F-05 · [UNSUPPORTED]**

This pack checked valid/tampered signatures and sizes, but did not run
Known Answer Tests. Before any integration, run the liboqs KAT suite for
ML-DSA-44/65/87 and cross-check against independent implementations
(e.g. the FIPS 204 test vectors). A wrong PQ implementation on the
consensus path is worse than no PQ implementation.

### R-04 — Measure the real secp256k1 baseline on validator hardware
**Addresses F-08 · [UNSUPPORTED]**

Benchmark libsecp256k1 verification (the code postfiatd actually runs)
on the hardware validators use, with the same harness shape as this
pack. The P-256/OpenSSL baseline here is a stand-in; migration sizing
decisions should use the real number.

## P2 — Migration design (when the work is scheduled)

### R-05 — Adopt a hybrid dual-signature transaction format, ML-DSA-44 first
**Addresses F-01, F-02, F-04 · [MEASURED]**

- New transactions carry two signatures: the existing classical
  signature (unchanged semantics) plus an ML-DSA-44 signature over the
  same signing hash. Both must verify; the classical check runs first so
  the PQ path is only reached for classically-valid transactions (bounds
  the DoS surface in R-01).
- ML-DSA-44, not ML-DSA-87: category 2, smallest signature (2,420 B),
  fastest verify measured here (26,163.3/s). ML-DSA-87 buys category 5 at
  1.9x the signature size and 2.3x slower verification for no ledger
  benefit today.
- Do not use SLH-DSA on the transaction path: 128s signs at 3.58/s and
  128f verifies at 968.2/s with a 17,088 B signature. Reserve SLH-DSA for
  offline, low-frequency signing (release signing, cold keys) where its
  minimal assumptions matter and its speed does not.

### R-06 — Treat validator-key migration as a separate track
**Addresses F-06 · [MEASURED — by source inspection]**

Validation signatures are secp256k1-only by assertion. Do not fold
validator-key migration into the transaction-key migration: it needs its
own format change, its own activation, and its own rollback plan, and a
mistake there breaks consensus rather than individual transactions.

### R-07 — Price signatures by size
**Addresses F-02 · [SIMULATED]**

A 2,420 B ML-DSA-44 signature is 37.8x an Ed25519 signature. If PQ
transactions ever share a fee market with classical ones, fees (or any
per-transaction size accounting) must reflect the bytes, or PQ
transactions will crowd out classical ones at the same fee. Model the
fee curve from the B3 bandwidth numbers before activation, not after.

## P3 — Later / ongoing

### R-08 — Re-measure on validator hardware and re-run this pack
**Addresses all findings · [MEASURED method, new data needed]**

This pack's numbers come from a shared-VM vCPU (AMD EPYC 9D25, ~1.5
shared CPUs). Re-run `sh harness/run_all.sh` on the hardware that will
actually verify signatures, and re-check the F-04 margin: if the
Ed25519/secp256k1 gap closes on faster hardware, the migration's
throughput case changes with it.
