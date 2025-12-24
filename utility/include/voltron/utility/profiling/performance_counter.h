#pragma once

#include <string>
#include <vector>

namespace voltron::utility::profiling {

/**
 * @brief CPU cycle counters and metrics
 * 
 * TODO: Implement comprehensive performance_counter functionality
 */
class PerformanceCounter {
public:
    static PerformanceCounter& instance();

    /**
     * @brief Initialize performance_counter
     */
    void initialize();

    /**
     * @brief Shutdown performance_counter
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    PerformanceCounter() = default;
    ~PerformanceCounter() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::profiling
