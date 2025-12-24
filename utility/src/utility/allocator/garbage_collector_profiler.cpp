#include <voltron/utility/allocator/garbage_collector_profiler.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::allocator {

GarbageCollectorProfiler& GarbageCollectorProfiler::instance() {
    static GarbageCollectorProfiler instance;
    return instance;
}

void GarbageCollectorProfiler::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[GarbageCollectorProfiler] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void GarbageCollectorProfiler::shutdown() {
    enabled_ = false;
    std::cout << "[GarbageCollectorProfiler] Shutdown\n";
}

bool GarbageCollectorProfiler::isEnabled() const {
    return enabled_;
}

void GarbageCollectorProfiler::enable() {
    enabled_ = true;
}

void GarbageCollectorProfiler::disable() {
    enabled_ = false;
}

std::string GarbageCollectorProfiler::getStatus() const {
    std::ostringstream oss;
    oss << "GarbageCollectorProfiler - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void GarbageCollectorProfiler::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::allocator
