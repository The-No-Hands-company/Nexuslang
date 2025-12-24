#include <voltron/utility/memory/memory_sanitizer_wrapper.h>

#ifdef __has_feature
  #if __has_feature(address_sanitizer)
    #define VOLTRON_HAS_ASAN 1
    #include <sanitizer/asan_interface.h>
  #endif
  #if __has_feature(memory_sanitizer)
    #define VOLTRON_HAS_MSAN 1
    #include <sanitizer/msan_interface.h>
  #endif
  #if __has_feature(thread_sanitizer)
    #define VOLTRON_HAS_TSAN 1
  #endif
#endif

#if defined(__SANITIZE_ADDRESS__)
  #ifndef VOLTRON_HAS_ASAN
    #define VOLTRON_HAS_ASAN 1
    #include <sanitizer/asan_interface.h>
  #endif
#endif

namespace voltron::utility::memory {

void MemorySanitizerWrapper::poisonMemoryRegion(const void* addr, size_t size) {
#ifdef VOLTRON_HAS_ASAN
    ASAN_POISON_MEMORY_REGION(addr, size);
#else
    (void)addr;
    (void)size;
#endif
}

void MemorySanitizerWrapper::unpoisonMemoryRegion(const void* addr, size_t size) {
#ifdef VOLTRON_HAS_ASAN
    ASAN_UNPOISON_MEMORY_REGION(addr, size);
#else
    (void)addr;
    (void)size;
#endif
}

bool MemorySanitizerWrapper::isASanEnabled() {
#ifdef VOLTRON_HAS_ASAN
    return true;
#else
    return false;
#endif
}

bool MemorySanitizerWrapper::isMSanEnabled() {
#ifdef VOLTRON_HAS_MSAN
    return true;
#else
    return false;
#endif
}

bool MemorySanitizerWrapper::isTSanEnabled() {
#ifdef VOLTRON_HAS_TSAN
    return true;
#else
    return false;
#endif
}

bool MemorySanitizerWrapper::isUBSanEnabled() {
#ifdef __SANITIZE_UNDEFINED__
    return true;
#else
    return false;
#endif
}

void MemorySanitizerWrapper::markMemoryInitialized(const void* addr, size_t size) {
#ifdef VOLTRON_HAS_MSAN
    __msan_unpoison(addr, size);
#else
    (void)addr;
    (void)size;
#endif
}

void MemorySanitizerWrapper::markMemoryUninitialized(const void* addr, size_t size) {
#ifdef VOLTRON_HAS_MSAN
    __msan_allocated_memory(addr, size);
#else
    (void)addr;
    (void)size;
#endif
}

MemorySanitizerWrapper::PoisonGuard::PoisonGuard(const void* addr, size_t size)
    : addr_(addr), size_(size) {
    poisonMemoryRegion(addr_, size_);
}

MemorySanitizerWrapper::PoisonGuard::~PoisonGuard() {
    unpoisonMemoryRegion(addr_, size_);
}

} // namespace voltron::utility::memory
