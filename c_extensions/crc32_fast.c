/**
 * High-performance CRC32 implementation in C.
 *
 * Provides a fast CRC32 checksum function callable from Python via ctypes.
 * Uses a lookup table for O(1) per-byte computation.
 *
 * Compile: gcc -shared -O2 -o libstorageops.so crc32_fast.c block_ops.c
 */

#include <stdint.h>
#include <stddef.h>

static uint32_t crc_table[256];
static int table_initialized = 0;

static void init_crc_table(void) {
    for (uint32_t i = 0; i < 256; i++) {
        uint32_t crc = i;
        for (int j = 0; j < 8; j++) {
            if (crc & 1)
                crc = (crc >> 1) ^ 0xEDB88320;
            else
                crc >>= 1;
        }
        crc_table[i] = crc;
    }
    table_initialized = 1;
}

/**
 * Compute CRC32 checksum of a buffer.
 *
 * @param data   Pointer to the data buffer
 * @param length Number of bytes in the buffer
 * @return       CRC32 checksum as uint32
 */
uint32_t fast_crc32(const uint8_t *data, size_t length) {
    if (!table_initialized)
        init_crc_table();

    uint32_t crc = 0xFFFFFFFF;
    for (size_t i = 0; i < length; i++) {
        uint8_t index = (crc ^ data[i]) & 0xFF;
        crc = (crc >> 8) ^ crc_table[index];
    }
    return crc ^ 0xFFFFFFFF;
}
