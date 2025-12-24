#pragma once

#include <string>
#include <vector>

namespace voltron::utility::concurrency {

/**
 * @brief Track thread-local data lifecycle
 * 
 * TODO: Implement comprehensive thread_local_storage_debug functionality
 */
class ThreadLocalStorageDebug {
public:
    static ThreadLocalStorageDebug& instance();

    /**
     * @brief Initialize thread_local_storage_debug
     */
    void initialize();

    /**
     * @brief Shutdown thread_local_storage_debug
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    ThreadLocalStorageDebug() = default;
    ~ThreadLocalStorageDebug() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::concurrency
