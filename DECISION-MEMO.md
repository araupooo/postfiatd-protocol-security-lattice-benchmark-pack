# Decision memo — hybrid classical / post-quantum migration

**Question:** how should postfiatd migrate transaction and validation
signatures toward quantum resistance, given the pinned revision
(`0085a1ff885d6a446369cf73a4430f75af22be55`, 2026-10-10) has no PQ support at all?

**Recommendation:** pursue a **hybrid dual-signature** migration with
**ML-DSA-44** as the PQ component for transactions, keep classical
signatures authoritative during a transition period, treat validator-key
migration as a separate later track, and do **not** put SLH-DSA on any
hot path.

## Options considered

### Option A — Hybrid dual-signature, ML-DSA-44 (RECOMMENDED)

New transactions carry the existing classical signature plus an ML-DSA-44
signature over the same signing hash; both must verify, classical first.

| Factor | Assessment |
|---|---|
| Security | Quantum-resistant once ML-DSA-44 is required; classical security retained throughout the transition. No flag day: old clients keep working until activation. |
| Verify cost | **[MEASURED]** ML-DSA-44 verifies at 26,163.3/s single-thread on this box — faster than the measured Ed25519 baseline (6,806.8/s). Throughput is not the blocker. |
| Size cost | **[MEASURED]** +2,420 B signature and +1,312 B public key per transaction (37.8x the Ed25519 signature). A 100,000-tx burst carries +224.7 MiB of signature bytes **[SIMULATED]**. This is the real price, and it must be priced into fees (R-07). |
| Risk | One new verify path on the consensus-critical funnel (`PublicKey.cpp` `verify`). Mitigated by KAT/interop testing (R-03) and classical-first ordering. |
| Effort | Format change (new key type, new signature field), verification plumbing in one function, activation mechanism, fee accounting. Significant but bounded. |

### Option B — Hybrid dual-signature, SLH-DSA-SHA2-128s

| Factor | Assessment |
|---|---|
| Security | Minimal assumptions (hash-based only) — the most conservative PQ choice. |
| Verify cost | **[MEASURED]** 2,461.5/s — 10.6x slower than ML-DSA-44, 2.8x slower than Ed25519. A 100,000-signature burst drains in 40.6 s single-thread **[SIMULATED]**. |
| Size cost | **[MEASURED]** 7,856 B signatures (122.8x Ed25519). |
| Signing cost | **[MEASURED]** 3.58 signatures/s (279 ms each). Any wallet or hot signer would stall. |
| Verdict | Reject for transactions. Keep SLH-DSA for offline, low-frequency signing (release signing, cold validator keys) where its assumptions matter and its speed does not. |

### Option C — Pure PQ flag day (no hybrid)

Replace classical signatures with ML-DSA-44 outright at an activation
point. Rejected: it orphans every existing key, breaks every existing
client at once, and removes the classical fallback if the PQ
implementation turns out to be faulty. There is no measured benefit over
Option A — the verify throughput is the same — and strictly more risk.

### Option D — Do nothing yet

Defer migration until a quantum threat is imminent. The honest case for
it: there is no large-scale quantum computer today, and the migration
costs real bandwidth and engineering. The case against it: the ledger's
signatures are long-lived public records — anything signed today can be
broken retrospectively once such a computer exists ("harvest now, decrypt
later" applies to signatures as well as encryption where long-term
non-repudiation matters). The recommendation is to **start Option A as
design and prototyping now** (format, KATs, testnet experiment) and let
activation wait for a governance decision — not to start nothing.

## What this memo does not decide

- **Activation mechanism and timeline.** No date or activation rule is
  proposed here; that is a governance decision, and this pack contains no
  data that would justify one.
- **Fee levels.** R-07 requires modelling from the B3 numbers; the exact
  curve is not set here.
- **Validator keys.** Option A covers transactions only. Validator-key
  migration (F-06) is a separate decision with its own memo.

## Evidence behind this memo

All throughput and size figures are **[MEASURED]** in
`outputs/benchmark-pq.log` and `outputs/benchmark-classical.log`; all
drain-time and bandwidth figures are **[SIMULATED]** in
`outputs/burst-model.log` from those measured inputs. The absence of PQ
code is **[MEASURED]** by source inspection (PINNED-REVISION.md). See
CLAIM-INDEX.md for the claim-by-claim trace.
