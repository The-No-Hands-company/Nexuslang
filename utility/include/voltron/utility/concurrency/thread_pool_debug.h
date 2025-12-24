#pragma once

#include <string>
#include <vector>

namespace voltron::utility::concurrency {

/**
 * @brief Instrumented thread pool
 * 
 * TODO: Implement comprehensive thread_pool_debug functionality
 */
class ThreadPoolDebug {
public:
    static ThreadPoolDebug& instance();

    /**
     * @brief Initialize thread_pool_debug
     */
    void initialize();

    /**
     * @brief Shutdown thread_pool_debug
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    ThreadPoolDebug() = default;
    ~ThreadPoolDebug() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::concurrency
