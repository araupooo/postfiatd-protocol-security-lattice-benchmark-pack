# Controls

What was controlled, and how each control was checked. A control that
failed would have stopped the run; all controls passed unless noted.

| # | Control | How it was checked | Result |
|---|---|---|---|
| K-01 | Valid signatures verify | `bench_sig.c` signs a fixed 32-byte message, then verifies the produced signature; must return success. | PASS for all 5 algorithms (`control_valid_signature_verifies: PASS`, benchmark-pq.log lines 18, 43, 68, 93, 117) |
| K-02 | Tampered signatures are rejected | The same signature with one byte flipped must fail verification. | PASS for all 5 algorithms (`control_tampered_signature_rejected: PASS`, lines 19, 44, 69, 94, 118) |
| K-03 | Measured sizes match the standards | `length_public_key` / `length_signature` reported by liboqs are compared against the FIPS 204 Table 2 / FIPS 205 Table 2 values in `burst_model.py`; a mismatch aborts the model run. | PASS for all 5 algorithms (ML-DSA-44 pk 1312/sig 2420; ML-DSA-65 1952/3309; ML-DSA-87 2592/4627; SLH-DSA-SHA2-128s pk 32/sig 7856; SLH-DSA-SHA2-128f pk 32/sig 17088) |
| K-04 | Same box, same conditions for PQ and classical | Classical baseline (`openssl speed`) and PQ benchmarks ran on the same VM, same day, single-threaded, back to back. | Done; environment in `outputs/environment.txt` |
| K-05 | Message length matches the ledger's digest length | Benchmark message is a fixed 32-byte vector — the same length as the 256-bit `sha512Half` digest postfiatd verifies. | By construction in `harness/bench_sig.c` |
| K-06 | Pinned revision is the one cited | Local clone HEAD and GitHub API HEAD agree; blob SHA + size verified per file via the API. | Done; see PINNED-REVISION.md |
| K-07 | No postfiatd code executed | Inspection was read-only (file viewing + text search + GitHub API). No postfiatd binary, script, or test was run. | By construction; see PINNED-REVISION.md |
| K-08 | Digests cover every pack file | `SHA256SUMS` is generated over all pack files except itself and `reproduce.log`; `verify_digests.sh` must exit 0. | Verified in the fresh-clone check; see `outputs/reproduce.log` |
| K-09 | Fresh-clone reproduction | The pack was copied to a clean directory and `sh harness/run_all.sh` was run there; exit 0 required. | Done; see `outputs/reproduce.log` |

## Known control gaps (honest)

- **No KAT (Known Answer Test) vectors were run.** liboqs ships KATs, but
  this pack did not execute them; correctness rests on K-01/K-02 plus the
  size cross-check (K-03). Running the liboqs KAT suite is listed as
  follow-up work in REMEDIATION.md (R-06).
- **No secp256k1 baseline was measured.** The classical baseline uses
  ECDSA P-256 and Ed25519 from OpenSSL; postfiatd's secp256k1 path uses
  libsecp256k1, which was not benchmarked. See LIMITATIONS.md.
- **Invalid-signature verify cost was not measured.** The burst model
  assumes an invalid signature costs one full verify (B-model parameter
  `INVALID_COST = 1.0`). That assumption is stated in the model output,
  not hidden.
- **Single-threaded only.** No multi-thread scaling was measured; the
  2- and 4-thread columns in the burst model assume linear scaling and are
  labelled as such.
