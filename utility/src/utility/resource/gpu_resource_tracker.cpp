#include <voltron/utility/resource/gpu_resource_tracker.h>
#include <iostream>

namespace voltron::utility::resource {

GpuResourceTracker& GpuResourceTracker::instance() {
    static GpuResourceTracker instance;
    return instance;
}

void GpuResourceTracker::initialize() {
    enabled_ = true;
    std::cout << "[GpuResourceTracker] Initialized\n";
}

void GpuResourceTracker::shutdown() {
    enabled_ = false;
    std::cout << "[GpuResourceTracker] Shutdown\n";
}

bool GpuResourceTracker::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::resource
