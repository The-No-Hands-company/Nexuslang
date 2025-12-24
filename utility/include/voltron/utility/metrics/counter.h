#pragma once

#include <string>
#include <vector>

namespace voltron::utility::metrics {

/**
 * @brief Thread-safe counters
 * 
 * TODO: Implement comprehensive counter functionality
 */
class Counter {
public:
    static Counter& instance();

    /**
     * @brief Initialize counter
     */
    void initialize();

    /**
     * @brief Shutdown counter
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    Counter() = default;
    ~Counter() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::metrics
