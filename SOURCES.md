# Primary sources

Every specification-derived claim in this pack traces to one of these
sources. Secondary summaries were used only to locate the primary text;
where a secondary source and the primary text disagreed, the primary text
wins (none did for the figures used here).

## Standards

| # | Source | What was taken from it |
|---|---|---|
| S-01 | NIST FIPS 204, Module-Lattice-Based Digital Signature Standard, 13 Aug 2024 — https://csrc.nist.gov/pubs/fips/204/final | ML-DSA parameter sets ML-DSA-44/65/87, NIST security categories 2/3/5, and Table 2 sizes: public key 1,312 / 1,952 / 2,592 bytes; signature 2,420 / 3,309 / 4,627 bytes. |
| S-02 | NIST FIPS 205, Stateless Hash-Based Digital Signature Standard, 13 Aug 2024 — https://csrc.nist.gov/pubs/fips/205/final | SLH-DSA, 12 parameter sets (SHA2/SHAKE × 128/192/256 × s/f), Table 2 sizes: public key 32/48/64 bytes; signatures 7,856 / 17,088 / 16,224 / 35,664 / 29,792 / 49,856 bytes. |
| S-03 | IETF RFC 9964, ML-DSA for JOSE and COSE, May 2026 — https://datatracker.ietf.org/doc/rfc9964/ | Independent restatement of the FIPS 204 Table 2 sizes (Section 5, Table 1); used as the cross-check for S-01. Sizes agree byte-for-byte. |

## Software under assessment

| # | Source | What was taken from it |
|---|---|---|
| S-04 | postfiatd, `postfiatorg/postfiatd`, main HEAD `0085a1ff885d6a446369cf73a4430f75af22be55` (2026-10-10) — https://github.com/postfiatorg/postfiatd | Signature-verification code paths and the absence of any PQ signature code; file paths, line numbers, and blob SHAs in PINNED-REVISION.md. |
| S-05 | liboqs 0.14.0, open-quantum-safe/liboqs, tag 0.14.0 — https://github.com/open-quantum-safe/liboqs | Reference implementation used for all ML-DSA/SLH-DSA measurements. `OQS_VERSION` 0.14.0 confirmed in the build (CMakeLists.txt lines 44–46) and printed by the harness (`liboqs_version:` line in the raw log). |
| S-06 | OpenSSL 3.0.13 (system package, Ubuntu 24.04.5) — `openssl version` | Classical baseline (`openssl speed`); no ML-DSA support in 3.0.x, which is why liboqs was used for the PQ schemes. |

## Size cross-check (specification vs implementation)

The harness prints `length_signature` / `length_public_key` as reported by
liboqs for each algorithm, and `harness/burst_model.py` refuses to run if
any measured size disagrees with the FIPS table value in S-01/S-02. The
cross-check passed for all five measured algorithms; see the raw log
(`outputs/benchmark-pq.log`) and CLAIM-INDEX.md (C-02).
