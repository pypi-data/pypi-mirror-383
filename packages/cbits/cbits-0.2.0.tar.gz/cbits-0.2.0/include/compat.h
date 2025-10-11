/**
 * @file include/compat.h
 * @brief Cross-platform aligned allocators, popcount, prefetch.
 *
 * Provides wrappers for:
 * - posix_memalign or _aligned_malloc/free
 * - cache prefetch instructions
 * - optimized 64-bit popcount and block-level popcount
 *
 * @author lambdaphoenix
 * @version 0.2.0
 * @copyright Copyright (c) 2025 lambdaphoenix
 */
#ifndef CBITS_COMPAT_H
#define CBITS_COMPAT_H

#include <stdint.h>
#include <stddef.h>
#include <stdlib.h>

#if defined(__x86_64__) || defined(_M_X64)
    #if defined(_MSC_VER)
        #include <immintrin.h>
    #else
        #include <x86intrin.h>
    #endif
#endif

#ifdef _MSC_VER
    #ifdef _M_IX86
        #pragma intrinsic(__popcnt)
    #elif defined(_M_X64) || defined(_M_AMD64)
        #pragma intrinsic(__popcnt)
        #pragma intrinsic(__popcnt64)
    #endif
#endif

/* Aligned malloc / free */
#if defined(_MSC_VER)
    #include <malloc.h>
    #include <errno.h>

static inline int
posix_memalign(void **memptr, size_t alignment, size_t size)
{
    void *p = _aligned_malloc(size, alignment);
    if (!p) {
        return ENOMEM;
    }
    *memptr = p;
    return 0;
}

/**
 * @brief Free aligned memory.
 *
 * On MSVC uses _aligned_free, otherwise standard free.
 *
 * @param ptr Pointer returned by cbits_malloc_aligned.
 */
static inline void
cbits_free_aligned(void *ptr)
{
    _aligned_free(ptr);
}
#else

/**
 * @brief Free aligned memory.
 *
 * On MSVC uses _aligned_free, otherwise standard free.
 *
 * @param ptr Pointer returned by cbits_malloc_aligned.
 */
static inline void
cbits_free_aligned(void *ptr)
{
    free(ptr);
}
#endif

/**
 * @brief Allocate aligned memory.
 *
 * Uses posix_memalign on POSIX, or _aligned_malloc on MSVC.
 *
 * @param size  Number of bytes to allocate.
 * @param align Desired alignment in bytes (must be power of two).
 * @return Pointer to aligned memory, or NULL if allocation failed.
 */
static inline void *
cbits_malloc_aligned(size_t size, size_t align)
{
    void *p = NULL;
    if (posix_memalign(&p, align, size) != 0) {
        return NULL;
    }
    return p;
}

/* Prefetch */

/**
 * @brief Prefetch a cache line at ptr into L1.
 *
 * @param ptr Address to prefetch.
 */
static inline void
cbits_prefetch(const void *ptr)
{
#if defined(_MSC_VER) && defined(_M_X64)
    #include <xmmintrin.h>
    _mm_prefetch((const char *) ptr, _MM_HINT_T0);
#elif defined(__GNUC__) || defined(__clang__)
    __builtin_prefetch(ptr, 0, 1);
#else
    (void) ptr; /* no-op */
#endif
}

/* Popcount */

/**
 * @brief Count bits set in a 64-bit word.
 *
 * @param ptr Pointer to the uint64_t to count bits in.
 * @return Number of set bits in *ptr.
 */
static inline uint64_t
cbits_popcount64(uint64_t x)
{
#if defined(_MSC_VER)
    #if defined(_M_IX86) || defined(_M_ARM)
    return (uint64_t) __popcnt((uint32_t) x) +
           (uint64_t) __popcnt((uint32_t) (x >> 32));
    #else
    return (uint64_t) __popcnt64(x);
    #endif
#else
    return (uint64_t) __builtin_popcountll(x);
#endif
}

/**
 * @brief Dispatch pointer for block popcount.
 *
 * Initially set to @ref cbits_popcount_block_fallback, and overwritten
 * during module initialization by @ref init_cpu_dispatch to point to
 * the best available implementation.
 */
extern uint64_t (*cbits_popcount_block_ptr)(const uint64_t *ptr);

/**
 * @brief Fallback popcount block implementation.
 *
 * Processes in 64-bit chunks, summing up cbits_popcount64 for each of
 * 8 words. Used when no vector instructions are available.
 *
 * @param ptr Pointer to at least 8 uint64_t words.
 * @return Total popcount of the 8 words.
 */
uint64_t
cbits_popcount_block_fallback(const uint64_t *ptr);

#if defined(__x86_64__) || defined(_M_X64)
/**
 * @brief AVX2 popcount block implementation (256-bit).
 *
 * Loads two 256-bit vectors, stores to temporary array, and sums
 * popcounts of each 64-bit element.
 *
 * Only used when targeting AVX2.
 *
 * @param ptr Pointer to at least 8 uint64_t words.
 * @return Total popcount of the 8 words.
 */
uint64_t
cbits_popcount_block_avx2(const uint64_t *ptr);

/**
 * @brief AVX-512VPOPCNTDQ popcount block implementation (512-bit).
 *
 * Loads one 512-bit vector, applies _mm512_popcnt_epi64, then reduces
 * with _mm512_reduce_add_epi64.
 *
 * Only used when targeting AVX-512VPOPCNTDQ.
 *
 * @param ptr Pointer to at least 8 uint64_t words.
 * @return Total popcount of the 8 words.
 */
uint64_t
cbits_popcount_block_avx512(const uint64_t *ptr);
#endif

/**
 * @brief Inline wrapper that calls the current dispatch pointer.
 *
 * @param ptr Pointer to 8 contiguous uint64_t words.
 * @return Total popcount as computed by the best available impl.
 */
static inline uint64_t
cbits_popcount_block(const uint64_t *ptr)
{
    return cbits_popcount_block_ptr(ptr);
}
/**
 * @brief Constructor to initialize popcount dispatch pointer.
 *
 * At program start, this function checks CPU support for AVX-512VPOPCNTDQ
 * and AVX2 via __builtin_cpu_supports, then updates
 * cbits_popcount_block_ptr accordingly.
 *
 * @param void
 */
void
init_cpu_dispatch(void);

#endif /* CBITS_COMPAT_H */
