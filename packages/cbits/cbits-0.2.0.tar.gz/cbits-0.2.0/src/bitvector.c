/**
 * @file src/bitvector.c
 * @brief Implementation of BitVector functions.
 *
 * This source file provides the C_API implementations for:
 * - bv_new, bv_copy, bv_free
 * - bv_build_rank, bv_rank
 * - bv_equal and bv_contains_subvector
 *
 * @see include/bitvector.h
 * @author lambdaphoenix
 * @version 0.2.0
 * @copyright Copyright (c) 2025 lambdaphoenix
 */

#include "bitvector.h"
#include <string.h>

/**
 * @brief Compute how many 64-bit words are needed to store a given number of
 * bits.
 *
 * Internally rounds up: any remainder bits occupy another full word.
 *
 * @param n_bits Number of bits to store.
 * @return Number of 64-bit words required.
 */
static inline size_t
words_for_bits(const size_t n_bits)
{
    return (n_bits + 63) >> 6;
}

BitVector *
bv_new(size_t n_bits)
{
    BitVector *bv = cbits_malloc_aligned(sizeof(BitVector), BV_ALIGN);
    if (!bv) {
        return NULL;
    }
    bv->n_bits = n_bits;
    bv->n_words = words_for_bits(n_bits);
    bv->rank_dirty = true;

    bv->data = cbits_malloc_aligned(bv->n_words * sizeof(uint64_t), BV_ALIGN);
    if (!bv->data) {
        cbits_free_aligned(bv);
        return NULL;
    }
    memset(bv->data, 0, bv->n_words * sizeof(uint64_t));

    size_t n_super =
        (bv->n_words + BV_WORDS_SUPER - 1) >> BV_WORDS_SUPER_SHIFT;
    bv->super_rank = cbits_malloc_aligned(n_super * sizeof(size_t), BV_ALIGN);
    if (!bv->super_rank) {
        cbits_free_aligned(bv->data);
        cbits_free_aligned(bv);
        return NULL;
    }
    bv->block_rank =
        cbits_malloc_aligned(bv->n_words * sizeof(uint16_t), BV_ALIGN);
    if (!bv->block_rank) {
        cbits_free_aligned(bv->super_rank);
        cbits_free_aligned(bv->data);
        cbits_free_aligned(bv);
        return NULL;
    }
    return bv;
}

BitVector *
bv_copy(const BitVector *src)
{
    BitVector *dst = bv_new(src->n_bits);
    if (!dst) {
        return NULL;
    }

    memcpy(dst->data, src->data, src->n_words * sizeof(uint64_t));
    bv_apply_tail_mask(dst);
    return dst;
}

void
bv_free(BitVector *bv)
{
    cbits_free_aligned(bv->block_rank);
    cbits_free_aligned(bv->super_rank);
    cbits_free_aligned(bv->data);
    cbits_free_aligned(bv);
}

void
bv_set_range(BitVector *bv, size_t start, size_t len)
{
    if (len == 0) {
        return;
    }
    size_t end = start + len;
    size_t w_start = start >> 6;
    size_t w_end = (end - 1) >> 6;
    unsigned off_start = start & 63;
    unsigned off_end = end & 63;

    if (w_start == w_end) {
        unsigned span = (unsigned) (end - start);
        uint64_t mask = (span == 64)
                            ? UINT64_MAX
                            : ((UINT64_C(1) << span) - 1) << off_start;
        bv->data[w_start] |= mask;
    }
    else {
        bv->data[w_start] |= ~0ULL << off_start;
        for (size_t w = w_start + 1; w < w_end; ++w) {
            bv->data[w] = ~0ULL;
        }
        if (off_end) {
            bv->data[w_end] |= (UINT64_C(1) << off_end) - 1;
        }
        else {
            bv->data[w_end] = ~0ULL;
        }
    }
    bv_apply_tail_mask(bv);
    bv->rank_dirty = true;
}

void
bv_clear_range(BitVector *bv, size_t start, size_t len)
{
    if (len == 0) {
        return;
    }
    size_t end = start + len;
    size_t w_start = start >> 6;
    size_t w_end = (end - 1) >> 6;
    unsigned off_start = start & 63;
    unsigned off_end = end & 63;

    if (w_start == w_end) {
        unsigned span = (unsigned) (end - start);
        uint64_t mask = (span == 64)
                            ? UINT64_MAX
                            : ((UINT64_C(1) << span) - 1) << off_start;
        bv->data[w_start] &= ~mask;
    }
    else {
        bv->data[w_start] |= ~0ULL << off_start;
        for (size_t w = w_start + 1; w < w_end; ++w) {
            bv->data[w] = 0ULL;
        }
        if (off_end) {
            bv->data[w_end] &= ~((UINT64_C(1) << off_end) - 1);
        }
        else {
            bv->data[w_end] = 0ULL;
        }
    }
    bv->rank_dirty = true;
}

void
bv_flip_range(BitVector *bv, size_t start, size_t len)
{
    if (len == 0) {
        return;
    }
    size_t end = start + len;
    size_t w_start = start >> 6;
    size_t w_end = (end - 1) >> 6;
    unsigned off_start = start & 63;
    unsigned off_end = end & 63;

    if (w_start == w_end) {
        unsigned span = (unsigned) (end - start);
        uint64_t mask = (span == 64)
                            ? UINT64_MAX
                            : ((UINT64_C(1) << span) - 1) << off_start;
        bv->data[w_start] ^= mask;
    }
    else {
        bv->data[w_start] ^= ~0ULL << off_start;
        for (size_t w = w_start + 1; w < w_end; ++w) {
            bv->data[w] ^= ~0ULL;
        }
        if (off_end) {
            bv->data[w_end] ^= (UINT64_C(1) << off_end) - 1;
        }
        else {
            bv->data[w_end] ^= ~0ULL;
        }
    }
    bv_apply_tail_mask(bv);
    bv->rank_dirty = true;
}

void
bv_build_rank(BitVector *bv)
{
    size_t super_total = 0;
    const size_t n_words = bv->n_words;
    const size_t n_super =
        (n_words + BV_WORDS_SUPER - 1) >> BV_WORDS_SUPER_SHIFT;

    for (size_t i = 0; i < n_super; ++i) {
        const size_t base = i << BV_WORDS_SUPER_SHIFT;
        const size_t end =
            base + BV_WORDS_SUPER < n_words ? base + BV_WORDS_SUPER : n_words;

        bv->super_rank[i] = super_total;
        if (end - base == BV_WORDS_SUPER) {
            super_total += cbits_popcount_block(&bv->data[base]);
        }
        else {
            size_t w = base;
            for (; w + 3 < end; w += 4) {
                cbits_prefetch(&bv->data[w + 16]);

                super_total += cbits_popcount64(bv->data[w]);
                super_total += cbits_popcount64(bv->data[w + 1]);
                super_total += cbits_popcount64(bv->data[w + 2]);
                super_total += cbits_popcount64(bv->data[w + 3]);
            }
            for (; w < end; ++w) {
                super_total += cbits_popcount64(bv->data[w]);
            }
        }

        size_t acc = 0;
        size_t w = base;
        for (; w + 3 < end; w += 4) {
            bv->block_rank[w] = (uint16_t) acc;
            acc += cbits_popcount64(bv->data[w]);
            bv->block_rank[w + 1] = (uint16_t) acc;
            acc += cbits_popcount64(bv->data[w + 1]);
            bv->block_rank[w + 2] = (uint16_t) acc;
            acc += cbits_popcount64(bv->data[w + 2]);
            bv->block_rank[w + 3] = (uint16_t) acc;
            acc += cbits_popcount64(bv->data[w + 3]);
        }
        for (; w < end; ++w) {
            bv->block_rank[w] = (uint16_t) acc;
            acc += cbits_popcount64(bv->data[w]);
        }
    }
    bv->rank_dirty = false;
}

size_t
bv_rank(BitVector *bv, const size_t pos)
{
    if (bv->rank_dirty) {
        bv_build_rank(bv);
    }
    size_t w = pos >> 6;
    size_t off = pos & 63;
    size_t s = bv->super_rank[w >> BV_WORDS_SUPER_SHIFT];
    size_t b = bv->block_rank[w];
    uint64_t mask = (1ULL << (off + 1)) - 1;
    uint64_t part = bv->data[w] & mask;
    return s + b + (size_t) cbits_popcount64(part);
}

bool
bv_equal(const BitVector *a, const BitVector *b)
{
    if (a->n_bits != b->n_bits) {
        return false;
    }

    for (size_t i = 0; i < a->n_words; ++i) {
        if (a->data[i] != b->data[i]) {
            return false;
        }
    }
    return true;
}

bool
bv_contains_subvector(const BitVector *A, const BitVector *B)
{
    if (B->n_bits == 0) {
        return true;
    }
    if (B->n_bits > A->n_bits) {
        return false;
    }

    const size_t max_pos = A->n_bits - B->n_bits;
    const unsigned B_tail = (unsigned) (B->n_bits & 63);
    const uint64_t tail_mask = B_tail ? ((1ULL << B_tail) - 1) : UINT64_MAX;

    if (B->n_bits <= 64) {
        uint64_t needle = B->data[0] & tail_mask;
        for (size_t pos = 0; pos <= max_pos; ++pos) {
            size_t w_off = pos >> 6;
            unsigned b_off = pos & 63;

            uint64_t lo = A->data[w_off];
            uint64_t hi = (w_off + 1 < A->n_words) ? A->data[w_off + 1] : 0ULL;
            uint64_t window = (lo >> b_off) | (hi << (64 - b_off));

            if ((window & tail_mask) == needle) {
                return true;
            }
        }
        return false;
    }

    const size_t B_words = B->n_words;
    for (size_t pos = 0; pos <= max_pos; ++pos) {
        const size_t w_off = pos >> 6;
        const unsigned b_off = pos & 63;

        {
            uint64_t lo = A->data[w_off];
            uint64_t hi = (w_off + 1 < A->n_words) ? A->data[w_off + 1] : 0ULL;
            uint64_t aw0 = (lo >> b_off) | (hi << (64 - b_off));
            uint64_t mask0 = (B_words == 1) ? tail_mask : UINT64_MAX;
            if ((aw0 & mask0) != (B->data[0] & mask0)) {
                continue;
            }
        }

        bool match = true;
        for (size_t j = 1; j < B_words; ++j) {
            uint64_t lo = A->data[w_off + j];
            uint64_t hi =
                (w_off + j + 1 < A->n_words) ? A->data[w_off + j + 1] : 0ULL;
            uint64_t wordA = (lo >> b_off) | (hi << (64 - b_off));
            uint64_t mask = (B_words == j + 1) ? tail_mask : UINT64_MAX;

            if ((wordA & mask) != (B->data[j] & mask)) {
                match = false;
                break;
            }
        }
        if (match) {
            return true;
        }
    }
    return false;
}
