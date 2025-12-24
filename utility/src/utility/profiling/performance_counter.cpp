#include <voltron/utility/profiling/performance_counter.h>
#include <iostream>

namespace voltron::utility::profiling {

PerformanceCounter& PerformanceCounter::instance() {
    static PerformanceCounter instance;
    return instance;
}

void PerformanceCounter::initialize() {
    enabled_ = true;
    std::cout << "[PerformanceCounter] Initialized\n";
}

void PerformanceCounter::shutdown() {
    enabled_ = false;
    std::cout << "[PerformanceCounter] Shutdown\n";
}

bool PerformanceCounter::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::profiling
