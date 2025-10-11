from libc.stdint cimport *

cdef extern from "_affine_cipher.h":
    struct affineCipherParameters:
        uint64_t domain
        uint64_t prime
        uint64_t pre_offset
        uint64_t post_offset

    cdef uint64_t affineCipher(affineCipherParameters * param, uint64_t i) noexcept

    cdef void fillAffineCipherParameters(
        affineCipherParameters * params,
        uint64_t domain,
        uint64_t prime,
        uint64_t pre_offset,
        uint64_t post_offset
    ) noexcept
