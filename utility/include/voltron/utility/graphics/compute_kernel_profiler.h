#pragma once

#include <string>
#include <vector>

namespace voltron::utility::graphics {

/**
 * @brief Profile compute shaders
 * 
 * TODO: Implement comprehensive compute_kernel_profiler functionality
 */
class ComputeKernelProfiler {
public:
    static ComputeKernelProfiler& instance();

    /**
     * @brief Initialize compute_kernel_profiler
     */
    void initialize();

    /**
     * @brief Shutdown compute_kernel_profiler
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    ComputeKernelProfiler() = default;
    ~ComputeKernelProfiler() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::graphics
