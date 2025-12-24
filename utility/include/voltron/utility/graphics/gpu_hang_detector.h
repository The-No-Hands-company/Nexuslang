#pragma once

#include <string>
#include <vector>

namespace voltron::utility::graphics {

/**
 * @brief Detect GPU hangs/timeouts
 * 
 * TODO: Implement comprehensive gpu_hang_detector functionality
 */
class GpuHangDetector {
public:
    static GpuHangDetector& instance();

    /**
     * @brief Initialize gpu_hang_detector
     */
    void initialize();

    /**
     * @brief Shutdown gpu_hang_detector
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    GpuHangDetector() = default;
    ~GpuHangDetector() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::graphics
