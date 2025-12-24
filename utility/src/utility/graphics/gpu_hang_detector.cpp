#include <voltron/utility/graphics/gpu_hang_detector.h>
#include <iostream>

namespace voltron::utility::graphics {

GpuHangDetector& GpuHangDetector::instance() {
    static GpuHangDetector instance;
    return instance;
}

void GpuHangDetector::initialize() {
    enabled_ = true;
    std::cout << "[GpuHangDetector] Initialized\n";
}

void GpuHangDetector::shutdown() {
    enabled_ = false;
    std::cout << "[GpuHangDetector] Shutdown\n";
}

bool GpuHangDetector::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::graphics
