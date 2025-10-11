#include <stdio.h>
#include <stdint.h>

#ifndef AFFINE_H

// uint128_t is directly supported by the compiler
#if defined(UINT128_MAX)

static inline uint64_t mul_mod(uint64_t a, uint64_t b, uint64_t N) {
    return (uint64_t)((uint128_t)a * (uint128_t)b % (uint128_t)N);
}

// use GCC/Clang/... extension type
#elif defined(__SIZEOF_INT128__)

#ifndef __uint128_t
#define __uint128_t unsigned __int128
#endif

static inline uint64_t mul_mod(uint64_t a, uint64_t b, uint64_t N) {
    return (uint64_t)((__uint128_t)a * (__uint128_t)b % (__uint128_t)N);
}

// use intrinsics for x64 MSVC
#elif defined(_MSC_VER) && !defined(_M_ARM64)

#include <intrin.h>

static inline uint64_t mul_mod(uint64_t a, uint64_t b, uint64_t N) {
    uint64_t high, low, remainder;
    low = _umul128(a, b, &high);
    _udiv128(high, low, N, &remainder);
    return remainder;
}

#else

static inline uint64_t mul_mod(uint64_t a, uint64_t b, uint64_t N) {
    // Fallback using binary modular multiplication
    a %= N;
    b %= N;

    uint64_t result = 0;
    while (b) {
        if (b & 1) {
            // will not overflow since result, a < N
            result = (result + a) % N;
        }
        a = (a << 1) % N;
        b >>= 1;
    }
    return result;
}

#endif

// Note:
// The following must be true for affineCipherN functions to work correctly!
// - domain < 2^63
// - prime < domain, offset < domain
// - GCD(prime, domain) = 1
struct affineCipherParameters {
    uint64_t domain;
    uint64_t prime;
    uint64_t pre_offset;
    uint64_t post_offset;
};

static inline void fillAffineCipherParameters(
    struct affineCipherParameters * params,
    uint64_t domain,
    uint64_t prime,
    uint64_t pre_offset,
    uint64_t post_offset
) {
    params->domain = domain;
    params->prime = prime;
    params->pre_offset = pre_offset;
    params->post_offset = post_offset;
}

// IMPORTANT: Unless i < 2^63 nothing works here!
static inline uint64_t affineCipher(const struct affineCipherParameters * params, uint64_t i) {
    return (
        mul_mod(
            i + params->pre_offset,
            params->prime, params->domain
        ) + params->post_offset
    ) % params->domain;
}

#endif
