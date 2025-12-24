#pragma once

#include <cstddef>
#include <cstdint>

/**
 * @brief Wrapper for AddressSanitizer (ASan) and MemorySanitizer (MSan) integration
 * 
 * Provides manual poisoning and unpoisoning of memory regions,
 * allowing fine-grained control over sanitizer behavior.
 */

namespace voltron::utility::memory {

class MemorySanitizerWrapper {
public:
    /**
     * @brief Mark memory region as poisoned (inaccessible)
     */
    static void poisonMemoryRegion(const void* addr, size_t size);

    /**
     * @brief Mark memory region as unpoisoned (accessible)
     */
    static void unpoisonMemoryRegion(const void* addr, size_t size);

    /**
     * @brief Check if AddressSanitizer is enabled
     */
    static bool isASanEnabled();

    /**
     * @brief Check if MemorySanitizer is enabled
     */
    static bool isMSanEnabled();

    /**
     * @brief Check if ThreadSanitizer is enabled
     */
    static bool isTSanEnabled();

    /**
     * @brief Check if UndefinedBehaviorSanitizer is enabled
     */
    static bool isUBSanEnabled();

    /**
     * @brief Mark memory as initialized for MSan
     */
    static void markMemoryInitialized(const void* addr, size_t size);

    /**
     * @brief Mark memory as uninitialized for MSan
     */
    static void markMemoryUninitialized(const void* addr, size_t size);

    /**
     * @brief RAII guard for poisoning memory regions
     */
    class PoisonGuard {
    public:
        PoisonGuard(const void* addr, size_t size);
        ~PoisonGuard();
        
        PoisonGuard(const PoisonGuard&) = delete;
        PoisonGuard& operator=(const PoisonGuard&) = delete;

    private:
        const void* addr_;
        size_t size_;
    };
};

} // namespace voltron::utility::memory
