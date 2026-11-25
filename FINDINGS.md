# Ranked findings

Severity scale: **Critical** = exploitable now or blocks a migration;
**High** = material risk or cost that must be addressed before any
migration; **Medium** = measurable cost or risk with a known mitigation;
**Low** = minor or informational. Each finding states its evidence class:
**[MEASURED]**, **[SIMULATED]**, or **[UNSUPPORTED]** (a claim that could
not be tested here — see LIMITATIONS.md).

## F-01 — High — No post-quantum signature support in the pinned revision

**[MEASURED — by source inspection]**

The pinned postfiatd revision (`0085a1ff885d6a446369cf73a4430f75af22be55`, 2026-10-10) contains no
ML-DSA, SLH-DSA, or other post-quantum signature code. A search of `src/`,
`include/`, and `docs/` for `ML-DSA`, `MLDSA`, `SLH-DSA`, `SLHDSA`,
`Dilithium`, `SPHINCS`, `liboqs`, and `oqs` returns zero matches. The only
key types are secp256k1 and Ed25519 (`include/xrpl/protocol/KeyType.h`,
lines 28–31), and all verification funnels through one function,
`verify` in `src/libxrpl/protocol/PublicKey.cpp` (lines 289–321), which
dispatches to libsecp256k1 ECDSA or ed25519-donna. Both schemes are
broken by a large-scale quantum computer (Shor's algorithm), so the
ledger's transaction and validation signatures have no quantum-resistant
path today. All PQ numbers in this pack are therefore measured on liboqs,
not on postfiatd code.

## F-02 — High — Signature-size blowup dominates the migration cost

**[MEASURED — sizes; SIMULATED — bandwidth]**

| Scheme | Signature | vs Ed25519 (64 B) |
|---|---|---|
| Ed25519 (current) | 64 B | 1.0x |
| ML-DSA-44 | 2,420 B | 37.8x |
| ML-DSA-65 | 3,309 B | 51.7x |
| ML-DSA-87 | 4,627 B | 72.3x |
| SLH-DSA-SHA2-128s | 7,856 B | 122.8x |
| SLH-DSA-SHA2-128f | 17,088 B | 267.0x |

Sizes are FIPS 204 Table 2 / FIPS 205 Table 2 values, confirmed against
liboqs (`length_signature` in the raw log). Public keys grow too: ML-DSA-44
needs 1,312 B where an Ed25519 key needs 32 B. In the burst model, a
100,000-transaction burst carries 224.7 MiB of extra signature bytes under
ML-DSA-44 and 1,623.5 MiB under SLH-DSA-SHA2-128f, versus Ed25519
(`outputs/burst-model.log`, section B3). Ledger size, gossip bandwidth,
and storage grow with every signed transaction; this — not verify speed —
is the binding cost of a PQ migration.

## F-03 — Medium — SLH-DSA verification is the burst bottleneck

**[MEASURED — rates; SIMULATED — drain times]**

Single-thread verify throughput on this box: SLH-DSA-SHA2-128s 2,461.5/s,
SLH-DSA-SHA2-128f 968.2/s — against Ed25519 at 6,806.8/s. Modelled drain
time for a crafted 100,000-signature burst, single thread: 40.6 s (128s)
and 103.3 s (128f), versus 14.7 s for Ed25519 and 3.8 s for ML-DSA-44
(`outputs/burst-model.log`, B1). A peer flooding invalid or valid
SLH-DSA signatures would hold a verifier busy ~7x longer than an Ed25519
flood of the same size. SLH-DSA signing is worse still: 128s signs at
3.58/s (279 ms per signature) — unusable on any hot signing path.

## F-04 — Medium — ML-DSA verification is faster than the classical baseline here

**[MEASURED — with a caveat]**

ML-DSA-44 verifies at 26,163.3/s, ML-DSA-65 at 16,779.2/s, ML-DSA-87 at
11,163.3/s — all faster than the measured Ed25519 baseline (6,806.8/s)
and ECDSA P-256 (10,435.0/s) on the same box. A 100,000-signature burst
drains in 3.8 s under ML-DSA-44 versus 14.7 s under Ed25519 (SIMULATED).
Caveat: the classical baseline is OpenSSL's Ed25519, while postfiatd uses
ed25519-donna — different implementations, so the gap is indicative, not
a claim about postfiatd's own verify path. Even so, the result refutes the
default assumption that PQ verification is necessarily slower: for
ML-DSA, throughput is not the blocker; size is (F-02).

## F-05 — Medium — One verification entry point: easy to extend, single point of failure

**[MEASURED — by source inspection]**

Every transaction signature check (`STTx::checkSign`,
`src/libxrpl/protocol/STTx.cpp` lines 259, 282, 433, 532) and every
validation signature check (`STValidation::isValid`,
`src/libxrpl/protocol/STValidation.cpp` line 136) funnels through
`verify` / `verifyDigest` in `PublicKey.cpp`. That is good for a
migration — one place to add a hybrid path — and bad for risk: a bug in a
new PQ verify path would sit on the consensus-critical path for every
transaction and validation. Any PQ addition needs the same canonicality
discipline the current code already applies (ECDSA canonicality checks in
`verifyDigest`, Ed25519 canonicality check at `PublicKey.cpp` line 304).

## F-06 — Medium — Validator validation signatures are secp256k1-only

**[MEASURED — by source inspection]**

`STValidation::isValid` asserts the signer key is secp256k1
(`STValidation.cpp` line 123, `XRPL_ASSERT` lines 127–129) and verifies with `verifyDigest`
(line 136) only. Validator identity keys cannot migrate to Ed25519, let alone to a
PQ scheme, without a validation-format change — a separate migration from
transaction signatures, on the consensus-critical path, with no fallback
if the new format is mishandled. Migration planning must treat
transaction keys and validator keys as two tracks.

## F-07 — Low — SLH-DSA 'f' is faster to sign but slower to verify

**[MEASURED]**

SLH-DSA-SHA2-128f signs 21.6x faster than 128s (77.4/s vs 3.58/s) but
verifies 2.5x slower (968.2/s vs 2,461.5/s), while carrying a 2.2x larger
signature (17,088 B vs 7,856 B). The 'f' tuning optimises the signer's
cost; a ledger verifier pays the verification cost on every transaction
it receives. Picking 'f' because it sounds "fast" would buy slower
verification and more bandwidth. For any ledger-facing use, 's' dominates
'f'; in practice neither belongs on the hot path (see the decision memo).

## F-08 — Low — No secp256k1 baseline was measured

**[UNSUPPORTED]**

The classical baseline covers ECDSA P-256 and Ed25519 via OpenSSL.
postfiatd's secp256k1 path uses libsecp256k1, which was not benchmarked,
so the comparison between ML-DSA and the ledger's actual dominant
signature scheme is incomplete. libsecp256k1 is generally faster than
OpenSSL's P-256 implementation, so the classical side of the comparison
is likely understated. This weakens F-04's margin but does not change its
direction for ML-DSA-44 (26,163/s vs a P-256 baseline of 10,435/s).

## Finding counts by severity

| Severity | Count |
|---|---|
| Critical | 0 |
| High | 2 (F-01, F-02) |
| Medium | 4 (F-03, F-04, F-05, F-06) |
| Low | 2 (F-07, F-08) |
| Total | 8 |
