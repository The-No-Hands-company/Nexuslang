#pragma once

#include <unordered_set>
#include <mutex>
#include <stdexcept>
#include <stacktrace>

namespace voltron::utility::memory {

/// @brief Detect double-free errors by tracking freed pointers
class DoubleFreeDetector {
public:
    static DoubleFreeDetector& instance();

    /// Record a pointer being freed
    void recordFree(void* ptr);

    /// Check if pointer was already freed (throws on double-free)
    void checkAndRecordFree(void* ptr);

    /// Clear tracking (useful for testing)
    void reset();

    /// Enable/disable detection
    void setEnabled(bool enabled);
    bool isEnabled() const;

private:
    DoubleFreeDetector() = default;

    DoubleFreeDetector(const DoubleFreeDetector&) = delete;
    DoubleFreeDetector& operator=(const DoubleFreeDetector&) = delete;

    mutable std::mutex mutex_;
    std::unordered_set<void*> freed_pointers_;
    bool enabled_ = true;
};

/// @brief RAII helper for scoped double-free detection
class DoubleFreeDetectionScope {
public:
    explicit DoubleFreeDetectionScope(bool enable);
    ~DoubleFreeDetectionScope();

private:
    bool previous_state_;
};

} // namespace voltron::utility::memory
