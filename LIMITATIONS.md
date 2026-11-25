# Limitations

Honest limits of this pack. Anything listed here is a claim this pack
does **not** establish.

## Environment limits

- **Shared-VM vCPU.** All measurements ran on one thread of a shared VM
  (AMD EPYC 9D25, 4 logical CPUs visible, ~1.5 shared CPUs, 7.7 GiB RAM,
  Ubuntu 24.04.5, load average ~3.3 during the run). Clock speed is not
  pinned and neighbouring tenants add noise. Run-to-run variance observed:
  ML-DSA-44 verify was 25,983.9/s in the first run and 26,163.3/s in the
  second (~0.7%). Treat every rate as approximate to a few percent, and
  re-run on the target hardware before sizing anything (R-08).
- **Single thread only.** No multi-thread or multi-process measurement was
  made. The burst model's 2- and 4-thread columns assume linear scaling;
  real scaling under contention will be worse.
- **No postfiatd node was run.** No ledger, no consensus, no gossip, no
  close-time measurement. All ledger-level statements are arithmetic on
  measured rates (SIMULATED), not observations of postfiatd behaviour.

## Measurement limits

- **SLH-DSA measured under its SPHINCS+ name.** liboqs 0.14.0 registers
  the FIPS 205 parameter sets as `SPHINCS+-SHA2-128s-simple` and
  `SPHINCS+-SHA2-128f-simple` (the pre-standardisation names). The raw
  log records the true liboqs name; the display name `SLH-DSA-SHA2-128s`
  is used in this pack because the measured key/signature sizes
  (32/7,856 and 32/17,088 bytes) match FIPS 205 Table 2 exactly. FIPS 205
  made small changes relative to the SPHINCS+ submission, so these rates
  describe the liboqs SPHINCS+ implementation of the parameter sets, not
  a certified FIPS 205 implementation.
- **Classical baseline is a stand-in.** Ed25519 and ECDSA P-256 come from
  OpenSSL 3.0.13. postfiatd uses ed25519-donna for Ed25519 and
  libsecp256k1 for secp256k1 ECDSA — different implementations, and
  secp256k1 was not measured at all (F-08). The ML-DSA-vs-classical
  margin in F-04 is indicative, not a claim about postfiatd's own code.
- **Signing rates for ML-DSA are lower bounds.** The harness caps signing
  at 25 iterations; all three ML-DSA schemes hit the cap, so their
  reported sign rates understate the true rate. Only SLH-DSA-SHA2-128s
  signing (3.579/s) is a direct time-boxed measurement.
- **Message length fixed at 32 bytes.** All benchmarks sign/verify a
  32-byte message (the ledger's digest length). Longer messages add
  hashing cost that was not measured.
- **No KAT vectors executed.** Correctness rests on valid/tampered
  controls and the size cross-check, not on Known Answer Tests (K-09 gap).
- **Invalid-signature cost assumed, not measured.** The burst model
  charges invalid signatures at 1.0x a full verify.

## Scope limits

- **One revision pinned.** Everything about postfiatd refers to main HEAD
  `0085a1ff885d6a446369cf73a4430f75af22be55` (2026-10-10). A later commit can change any of it.
- **Source inspection only for postfiatd.** No postfiatd code was built,
  executed, or tested, and no postfiatd files are included in this pack.
- **Burst model parameters are assumptions.** 4 s ledger-close window,
  linear thread scaling, 64-byte Ed25519 signature baseline — all stated
  in `outputs/burst-model.log` and changeable in `harness/burst_model.py`.
- **Re-runs are re-measurements.** Logs carry timestamps and fresh
  ephemeral keys, so a re-run produces different bytes and different
  digests. `run_all.sh` regenerates `SHA256SUMS` after re-running; the
  manifest verifies the integrity of a given run's outputs, not
  byte-identical reproduction. Values should agree within normal variance
  on the same hardware.
