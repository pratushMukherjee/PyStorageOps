/**
 * Low-level block operations in C for performance-critical paths.
 *
 * Provides fast block copy, compare, and zero-fill operations
 * callable from Python via ctypes.
 */

#include <stdint.h>
#include <stddef.h>
#include <string.h>

/**
 * Fast block copy with optional XOR (for RAID parity computation).
 *
 * If xor_mode is non-zero, XORs src into dst instead of copying.
 *
 * @param dst       Destination buffer
 * @param src       Source buffer
 * @param length    Number of bytes
 * @param xor_mode  If non-zero, XOR src into dst
 */
void block_copy(uint8_t *dst, const uint8_t *src, size_t length, int xor_mode) {
    if (xor_mode) {
        /* Process 8 bytes at a time for better throughput */
        size_t i = 0;
        size_t aligned = length & ~(size_t)7;
        for (; i < aligned; i += 8) {
            *(uint64_t *)(dst + i) ^= *(const uint64_t *)(src + i);
        }
        for (; i < length; i++) {
            dst[i] ^= src[i];
        }
    } else {
        memcpy(dst, src, length);
    }
}

/**
 * Compare two blocks byte-by-byte.
 *
 * @param a      First buffer
 * @param b      Second buffer
 * @param length Number of bytes to compare
 * @return       0 if identical, byte offset of first difference + 1
 */
size_t block_compare(const uint8_t *a, const uint8_t *b, size_t length) {
    for (size_t i = 0; i < length; i++) {
        if (a[i] != b[i])
            return i + 1;
    }
    return 0;
}

/**
 * Zero-fill a block.
 *
 * @param dst    Buffer to zero
 * @param length Number of bytes
 */
void block_zero(uint8_t *dst, size_t length) {
    memset(dst, 0, length);
}

/**
 * Fill a block with a repeating byte pattern (useful for testing).
 *
 * @param dst     Buffer to fill
 * @param pattern Byte value to fill with
 * @param length  Number of bytes
 */
void block_fill(uint8_t *dst, uint8_t pattern, size_t length) {
    memset(dst, pattern, length);
}
