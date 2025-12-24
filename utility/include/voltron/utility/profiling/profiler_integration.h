#pragma once

#include <string>
#include <vector>

namespace voltron::utility::profiling {

/**
 * @brief Integration for Tracy/VTune/perf
 * 
 * TODO: Implement comprehensive profiler_integration functionality
 */
class ProfilerIntegration {
public:
    static ProfilerIntegration& instance();

    /**
     * @brief Initialize profiler_integration
     */
    void initialize();

    /**
     * @brief Shutdown profiler_integration
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    ProfilerIntegration() = default;
    ~ProfilerIntegration() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::profiling
