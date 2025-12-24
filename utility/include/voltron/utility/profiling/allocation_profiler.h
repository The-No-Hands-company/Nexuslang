#pragma once

#include <string>
#include <vector>

namespace voltron::utility::profiling {

/**
 * @brief Track allocation hotspots
 * 
 * TODO: Implement comprehensive allocation_profiler functionality
 */
class AllocationProfiler {
public:
    static AllocationProfiler& instance();

    /**
     * @brief Initialize allocation_profiler
     */
    void initialize();

    /**
     * @brief Shutdown allocation_profiler
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    AllocationProfiler() = default;
    ~AllocationProfiler() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::profiling
