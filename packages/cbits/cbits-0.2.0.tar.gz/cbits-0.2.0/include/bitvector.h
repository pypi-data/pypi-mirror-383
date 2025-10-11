/** @file include/bitvector.h
 * @brief Packed BitVector C-API declarations.
 *
 * This header decleares the BitVector C-API:
 * - creation, copy, free
 * - bit get/set/clear/flip operations
 * - rank and subvector-containment queries
 *
 * @author lambdaphoenix
 * @version 0.2.0
 * @copyright Copyright (c) 2025 lambdaphoenix
 */
#ifndef CBITS_BITVECTOR_H
#define CBITS_BITVECTOR_H

#include "compat.h"
#include <stdbool.h>

/**
 * @def BV_ALIGN
 * @brief Alignment in bytes for all BitVector allocations.
 */
#define BV_ALIGN 64
/**
 * @def BV_WORDS_SUPER_SHIFT
 * @brief Number of bits to shift a word index to compute a superblock
 * index.
 */
#define BV_WORDS_SUPER_SHIFT 3
/**
 * @def BV_WORDS_SUPER
 * @brief Number of 64-bit worde per superblock.
 */
#define BV_WORDS_SUPER (1u << BV_WORDS_SUPER_SHIFT)

/**
 * @brief Compute the word index for a given bit position.
 * @param pos bit index
 * @return Index of the 64-bit word containing that bit.
 */
static inline size_t
bv_word(const size_t pos)
{
    return pos >> 6;
}
/**
 * @brief Compute the bit offset within its 64-bit word.
 * @param pos bit index
 * @return Offset in [0...63] inside the 64-bit word.
 */
static inline size_t
bv_bit(const size_t pos)
{
    return pos & 63;
}

/**
 * @struct BitVector
 * @brief Packed array of bits with support for rank/select operations.
 *
 * Stores bits in an aligned array of 64-bit words, and maintains auxiliary
 * superblock and block rank tables for constant-time rank queries.
 */
typedef struct {
    uint64_t *data; /**< Aligned array of 64-bit words storing bits. */
    size_t n_bits;  /**< Total number of bits. */
    size_t n_words; /**< Number of 64-bit words allocated in @c data.*/
    size_t
        *super_rank; /**< Prefix-sum of popcounts at superblock granularity. */
    uint16_t *block_rank; /**< Prefix-sum of popcounts at block granularity. */
    bool rank_dirty; /**< Flag indicating that rank tables need rebuilding. */
} BitVector;

/**
 * @brief Mask off any excess bits in the last word of a BitVector.
 * @param bv Pointer to an allocated BitVector.
 * @since 0.1.2
 */
static inline void
bv_apply_tail_mask(BitVector *bv)
{
    if (!bv->n_words) {
        return;
    }
    unsigned tail = (unsigned) (bv->n_bits & 63);
    if (tail) {
        uint64_t mask = (UINT64_C(1) << tail) - 1;
        bv->data[bv->n_words - 1] &= mask;
    }
}

/**
 *  @brief Allocate a new BitVector with all bits cleared
 *  @param n_bits Number of bits
 *  @return Pointer to the new BitVector
 */
BitVector *
bv_new(size_t n_bits);
/**
 *  @brief Make a copy of an existing BitVector.
 *
 *  The copy shares no memory with the source; all bits and rank tables are
 *  reinitialized.
 *  @param src Pointer to the source BitVector
 *  @return Newly allocated BitVector copy, or @c NULL on failure.
 */
BitVector *
bv_copy(const BitVector *src);
/**
 *  @brief Free all memory associated with a BitVector
 *  @param bv Pointer to the BitVector to free
 */
void
bv_free(BitVector *bv);
/**
 *  @brief Get the bit value at a given position.
 *  @param bv Pointer to the BitVector
 *  @param pos Bit index
 *  @return @c 0 or @c 1 depending on the bit value
 */
static inline int
bv_get(const BitVector *bv, const size_t pos)
{
    return (bv->data[bv_word(pos)] >> bv_bit(pos)) & 1;
}
/**
 *  @brief Set the bit at a given position (set to 1)
 *
 *  Marks the rank table dirty so it will be rebuilt on next rank query.
 *  @param bv Pointer to the BitVector
 *  @param pos Bit index
 */
static inline void
bv_set(BitVector *bv, const size_t pos)
{
    uint64_t mask = 1ULL << bv_bit(pos);
    bv->data[bv_word(pos)] |= mask;
    bv->rank_dirty = true;
}
/**
 *  @brief Clear the bit at a given position (set to 0)
 *
 *  Marks the rank table dirty so it will be rebuilt on next rank query.
 *  @param bv Pointer to the BitVector
 *  @param pos Bit index
 */
static inline void
bv_clear(BitVector *bv, const size_t pos)
{
    uint64_t mask = ~(1ULL << bv_bit(pos));
    bv->data[bv_word(pos)] &= mask;
    bv->rank_dirty = true;
}
/**
 *  @brief Toggle (flip) the bit at a given position
 *
 *  Marks the rank table dirty so it will be rebuilt on next rank query.
 *  @param bv Pointer to the BitVector
 *  @param pos Bit index
 */
static inline void
bv_flip(BitVector *bv, const size_t pos)
{
    uint64_t mask = 1ULL << bv_bit(pos);
    bv->data[bv_word(pos)] ^= mask;
    bv->rank_dirty = true;
}
/**
 *  @brief Set all bits in the half‑open range [start, start+len).
 *
 *  Marks the rank table dirty so it will be rebuilt on next rank query.
 *  @param bv Pointer to the BitVector
 *  @param start Start bit index
 *  @param len Number of bits to set
 *  @since 0.2.0
 */
void
bv_set_range(BitVector *bv, size_t start, size_t len);
/**
 *  @brief Clear all bits in the half‑open range [start, start+len).
 *
 *  Marks the rank table dirty so it will be rebuilt on next rank query.
 *  @param bv Pointer to the BitVector
 *  @param start Start bit index
 *  @param len Number of bits to clear
 *  @since 0.2.0
 */
void
bv_clear_range(BitVector *bv, size_t start, size_t len);
/**
 *  @brief Toggle (flip) all bits in the half‑open range [start, start+len).
 *
 *  Marks the rank table dirty so it will be rebuilt on next rank query.
 *  @param bv Pointer to the BitVector
 *  @param start Start bit index
 *  @param len Number of bits to flip
 *  @since 0.2.0
 */
void
bv_flip_range(BitVector *bv, size_t start, size_t len);
/**
 *  @brief Build or rebuild the rank tables for a BitVector.
 *
 *  This populates @c super_rank[] and @c block_rank[] to support O(1) rank
 * queries. After this call, @c bv->rank_dirty is cleared.
 *  @param bv Pointer to the BitVector whose tables to build
 */
void
bv_build_rank(BitVector *bv);
/**
 *  @brief Compute the rank (number of set bits) up to a position.
 *
 *  If the internal rank tables are dirty, they will be rebuilt.
 *  @param bv Pointer to the BitVector
 *  @param pos Bit index
 *  @return Number of bits set in range @c [0...pos]
 */
size_t
bv_rank(BitVector *bv, const size_t pos);
/**
 *  @brief Test equality of two BitVectors.
 *
 *  Only vectors with the same length can compare equal.
 *  @param a First BitVector
 *  @param b Second BitVector
 *  @return @c true if length and all words are identical, @c false otherwise
 */
bool
bv_equal(const BitVector *a, const BitVector *b);
/**
 *  @brief Check weather B appears as a contiguous sub-bitvector of A.
 *
 *  That is, whether there exists an offset i in A such that <tt> A[i..i+|B|-1]
 * == B[0..|B|-1] </tt>.
 *  @param a Haystack BitVector
 *  @param b Needle BitVector
 *  @return @c true if b is contained in a, @c false otherwise
 */
bool
bv_contains_subvector(const BitVector *a, const BitVector *b);

#endif /* CBITS_BITVECTOR_H */
