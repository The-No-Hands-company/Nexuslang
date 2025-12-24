#include <voltron/utility/profiling/allocation_profiler.h>
#include <iostream>

namespace voltron::utility::profiling {

AllocationProfiler& AllocationProfiler::instance() {
    static AllocationProfiler instance;
    return instance;
}

void AllocationProfiler::initialize() {
    enabled_ = true;
    std::cout << "[AllocationProfiler] Initialized\n";
}

void AllocationProfiler::shutdown() {
    enabled_ = false;
    std::cout << "[AllocationProfiler] Shutdown\n";
}

bool AllocationProfiler::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::profiling
