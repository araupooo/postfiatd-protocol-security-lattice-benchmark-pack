/* bench_sig.c — signature verification benchmark harness.
 *
 * Measures key generation, signing, and verification throughput for the
 * post-quantum signature schemes named in FIPS 204 (ML-DSA) and FIPS 205
 * (SLH-DSA) using liboqs 0.14.0, on one thread, with a fixed 32-byte
 * message (the same length as the 256-bit signing digest postfiatd verifies
 * via sha512Half in src/libxrpl/protocol/PublicKey.cpp).
 *
 * Output is plain text, one line per measurement, plus a correctness
 * section: a valid signature must verify, and a tampered signature must
 * fail. No timestamps are printed inside the measurement lines; the driver
 * script records start/end times in the log header/footer instead, so the
 * measurement block is stable across runs.
 *
 * Build: cc -O2 -I<liboqs-src>/src -I<liboqs-build>/include bench_sig.c \
 *          -L<liboqs-build>/lib -loqs -lcrypto -o bench_sig
 *   (liboqs built with -DOQS_BUILD_ONLY_LIB=ON; link order matters.)
 *
 * Usage: ./bench_sig <alg-name> [verify-seconds] [sign-seconds]
 *   verify-seconds / sign-seconds default to 5. Signing of the slowest
 *   scheme is additionally capped at 25 iterations so a run stays short.
 */
#include <oqs/oqs.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

static double now_sec(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec + (double)ts.tv_nsec / 1e9;
}

int main(int argc, char **argv)
{
    if (argc < 2) {
        fprintf(stderr, "usage: %s <alg> [verify-seconds] [sign-seconds]\n", argv[0]);
        return 2;
    }
    const char *alg_name = argv[1];
    double verify_budget = argc > 2 ? atof(argv[2]) : 5.0;
    double sign_budget = argc > 3 ? atof(argv[3]) : 5.0;
    if (verify_budget <= 0) verify_budget = 5.0;
    if (sign_budget <= 0) sign_budget = 5.0;

    printf("liboqs_version: %s\n", OQS_VERSION_TEXT);
    printf("algorithm: %s\n", alg_name);

    OQS_SIG *sig = OQS_SIG_new(alg_name);
    if (sig == NULL) {
        printf("result: ALGORITHM_NOT_ENABLED\n");
        return 1;
    }
    printf("claimed_nist_level: %d\n", sig->claimed_nist_level);
    printf("length_public_key: %zu\n", sig->length_public_key);
    printf("length_secret_key: %zu\n", sig->length_secret_key);
    printf("length_signature: %zu\n", sig->length_signature);

    uint8_t *pk = malloc(sig->length_public_key);
    uint8_t *sk = malloc(sig->length_secret_key);
    uint8_t *signature = malloc(sig->length_signature);
    size_t sig_len = 0;
    /* Fixed 32-byte message: mirrors the 256-bit digest length verified by
     * postfiatd (sha512Half). Content is a fixed, non-secret test vector. */
    static const uint8_t message[32] = {
        0x50, 0x4f, 0x53, 0x54, 0x46, 0x49, 0x41, 0x54, 0x2d, 0x62, 0x65, 0x6e, 0x63, 0x68, 0x2d, 0x6d,
        0x73, 0x67, 0x2d, 0x33, 0x32, 0x2d, 0x62, 0x79, 0x74, 0x65, 0x2d, 0x76, 0x65, 0x63, 0x74, 0x6f
    };
    if (!pk || !sk || !signature) {
        printf("result: ALLOCATION_FAILED\n");
        return 1;
    }

    if (OQS_SIG_keypair(sig, pk, sk) != OQS_SUCCESS) {
        printf("result: KEYPAIR_FAILED\n");
        return 1;
    }
    if (OQS_SIG_sign(sig, signature, &sig_len, message, sizeof(message), sk) != OQS_SUCCESS) {
        printf("result: SIGN_FAILED\n");
        return 1;
    }
    printf("signature_len_produced: %zu\n", sig_len);
    if (sig_len != sig->length_signature) {
        printf("result: SIGNATURE_LENGTH_MISMATCH\n");
        return 1;
    }

    /* Correctness controls (run before timing). */
    OQS_STATUS rc = OQS_SIG_verify(sig, message, sizeof(message), signature, sig_len, pk);
    printf("control_valid_signature_verifies: %s\n", rc == OQS_SUCCESS ? "PASS" : "FAIL");
    if (rc != OQS_SUCCESS) {
        printf("result: VALID_SIGNATURE_REJECTED\n");
        return 1;
    }
    signature[0] ^= 0x01; /* tamper one byte */
    rc = OQS_SIG_verify(sig, message, sizeof(message), signature, sig_len, pk);
    printf("control_tampered_signature_rejected: %s\n", rc != OQS_SUCCESS ? "PASS" : "FAIL");
    if (rc == OQS_SUCCESS) {
        printf("result: TAMPERED_SIGNATURE_ACCEPTED\n");
        return 1;
    }
    signature[0] ^= 0x01; /* restore */

    /* Verification throughput: loop until the time budget is spent. */
    {
        size_t ops = 0;
        double start = now_sec();
        double end;
        do {
            if (OQS_SIG_verify(sig, message, sizeof(message), signature, sig_len, pk) != OQS_SUCCESS) {
                printf("result: VERIFY_FAILED_DURING_TIMING\n");
                return 1;
            }
            ops++;
            end = now_sec();
        } while (end - start < verify_budget);
        double elapsed = end - start;
        printf("verify_ops: %zu\n", ops);
        printf("verify_seconds: %.6f\n", elapsed);
        printf("verify_ops_per_sec: %.3f\n", (double)ops / elapsed);
        printf("verify_usec_per_op: %.3f\n", elapsed * 1e6 / (double)ops);
    }

    /* Signing throughput: time-boxed, capped at 25 iterations so the
     * slowest scheme (SLH-DSA 's' variants) keeps the run short. */
    {
        size_t ops = 0;
        double start = now_sec();
        double end;
        do {
            size_t out_len = 0;
            if (OQS_SIG_sign(sig, signature, &out_len, message, sizeof(message), sk) != OQS_SUCCESS) {
                printf("result: SIGN_FAILED_DURING_TIMING\n");
                return 1;
            }
            ops++;
            end = now_sec();
        } while (end - start < sign_budget && ops < 25);
        double elapsed = end - start;
        printf("sign_ops: %zu\n", ops);
        printf("sign_seconds: %.6f\n", elapsed);
        printf("sign_ops_per_sec: %.3f\n", (double)ops / elapsed);
        printf("sign_usec_per_op: %.3f\n", elapsed * 1e6 / (double)ops);
        if (ops >= 25)
            printf("sign_note: iteration cap of 25 reached; rate is a lower bound\n");
    }

    /* Key-generation throughput: 10 fresh keypairs (fast for these schemes). */
    {
        size_t ops = 0;
        double start = now_sec();
        for (ops = 0; ops < 10; ops++) {
            if (OQS_SIG_keypair(sig, pk, sk) != OQS_SUCCESS) {
                printf("result: KEYPAIR_FAILED_DURING_TIMING\n");
                return 1;
            }
        }
        double elapsed = now_sec() - start;
        printf("keypair_ops: %zu\n", ops);
        printf("keypair_seconds: %.6f\n", elapsed);
        printf("keypair_ops_per_sec: %.3f\n", (double)ops / elapsed);
    }

    printf("result: OK\n");
    OQS_SIG_free(sig);
    free(pk);
    free(sk);
    free(signature);
    return 0;
}
