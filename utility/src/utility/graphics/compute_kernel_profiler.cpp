#include <voltron/utility/graphics/compute_kernel_profiler.h>
#include <iostream>

namespace voltron::utility::graphics {

ComputeKernelProfiler& ComputeKernelProfiler::instance() {
    static ComputeKernelProfiler instance;
    return instance;
}

void ComputeKernelProfiler::initialize() {
    enabled_ = true;
    std::cout << "[ComputeKernelProfiler] Initialized\n";
}

void ComputeKernelProfiler::shutdown() {
    enabled_ = false;
    std::cout << "[ComputeKernelProfiler] Shutdown\n";
}

bool ComputeKernelProfiler::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::graphics
