# Pinned postfiatd revision

## Revision pinned

| Field | Value |
|---|---|
| Repository | https://github.com/postfiatorg/postfiatd |
| Branch | main |
| HEAD commit | `0085a1ff885d6a446369cf73a4430f75af22be55` |
| Commit date | 2026-10-10T16:53:26Z |
| Commit subject | Merge pull request #50 from postfiatorg/hotfix/upstream-hardening-1.0.9 — 1.0.9: backport the upstream 3.4.1 payment engine overflow fix |
| Repo description (GitHub API) | "Decentralized cryptocurrency blockchain daemon implementing the XRP Ledger protocol in C++" (a fork of the XRP Ledger daemon) |

## How the pin was verified

1. Local clone (`git clone --depth 1 https://github.com/postfiatorg/postfiatd.git`)
   reported HEAD `0085a1ff885d6a446369cf73a4430f75af22be55`.
2. GitHub API `GET /repos/postfiatorg/postfiatd/commits?per_page=1&sha=main`
   returned the same SHA and the same commit date. The two agree.
3. Blob SHA + size for each cited source file were checked with
   `GET /repos/postfiatorg/postfiatd/contents/<path>?ref=<pinned SHA>`
   and are listed in SOURCES.md. A blob SHA is content-addressed: it
   identifies the exact file bytes, independent of any line-number rendering.

No postfiatd code was executed, built, or run for this pack. Inspection was
read-only (file viewing and text search on the local checkout, plus the
GitHub API). No postfiatd source files are copied into this pack; files are
cited by path, line number, and blob SHA only.

## Why this revision

The assessment names no specific revision, so the latest `main` HEAD at
build time (2026-11-25) was pinned and documented here. Any later commit
changes the assessed code; re-run the pack against a new pin if the revision
moves.

## Signature-verification code in the pinned revision

All line numbers below were verified with `grep -n` on the local checkout
of the pinned commit — not from any web rendering.

| File (blob SHA, size) | Lines | What it does |
|---|---|---|
| `src/libxrpl/protocol/PublicKey.cpp` (`54b50c80ef104b89a0dc7f357ca7d9a3e3edaab7`, 9,547 B) | 232–287 `verifyDigest`; 289–321 `verify` | The single signature-verification entry point. `verify` dispatches on key type: secp256k1 goes to `verifyDigest` (libsecp256k1 `secp256k1_ecdsa_verify`, lines 275, 281); Ed25519 goes to `ed25519_sign_open` (line 311) after a canonicality check. |
| `include/xrpl/protocol/KeyType.h` (`810e3e6fdf49a2cb73449b3a387ad5ea525c2bba`, 1,795 B) | 28–31 | `enum class KeyType { secp256k1 = 0, ed25519 = 1 }` — the only two key types the ledger recognises. |
| `src/libxrpl/protocol/STTx.cpp` (`ddbe294e47b4e4f4b7ac8d055ba8de99f7377568`, 26,021 B) | 259, 282 `checkSign`; 433, 532 `verify(...)` | Transaction signature checking calls `verify` for the single signature and for each counter-signature. |
| `src/libxrpl/protocol/STValidation.cpp` (`d2cb0586f261e9e06fa31f0da9c3fdc28cfc62ca`, 5,493 B) | 136 `verifyDigest` | Validator validation signatures are verified with the same secp256k1 digest path. |
| `external/ed25519-donna/ed25519.h` (`dc86675cd184116b41fca51c615082c2a9cb8ae3`, 960 B) | 17 | Declaration of `ed25519_sign_open` (vendored ed25519-donna). |

## What is NOT in the pinned revision (finding, not omission)

A case-insensitive search of `src/`, `include/`, and `docs/` for
`ML-DSA`, `MLDSA`, `SLH-DSA`, `SLHDSA`, `Dilithium`, `SPHINCS`, `liboqs`,
and `oqs` returned **zero matches**. The pinned revision contains no
post-quantum signature code, no ML-DSA/SLH-DSA implementation, and no
hybrid-signature path. Every ML-DSA/SLH-DSA number in this pack is therefore
measured on liboqs 0.14.0 (an external reference implementation), **not**
on postfiatd code — see FINDINGS.md (F-01) and LIMITATIONS.md. The burst
model in `outputs/burst-model.log` is explicitly labelled SIMULATED.
