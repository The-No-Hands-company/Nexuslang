#include <voltron/utility/profiling/profiler_integration.h>
#include <iostream>

namespace voltron::utility::profiling {

ProfilerIntegration& ProfilerIntegration::instance() {
    static ProfilerIntegration instance;
    return instance;
}

void ProfilerIntegration::initialize() {
    enabled_ = true;
    std::cout << "[ProfilerIntegration] Initialized\n";
}

void ProfilerIntegration::shutdown() {
    enabled_ = false;
    std::cout << "[ProfilerIntegration] Shutdown\n";
}

bool ProfilerIntegration::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::profiling
