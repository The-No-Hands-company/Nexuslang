#include <voltron/utility/simd/vectorization_profiler.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::simd {

VectorizationProfiler& VectorizationProfiler::instance() {
    static VectorizationProfiler instance;
    return instance;
}

void VectorizationProfiler::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[VectorizationProfiler] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void VectorizationProfiler::shutdown() {
    enabled_ = false;
    std::cout << "[VectorizationProfiler] Shutdown\n";
}

bool VectorizationProfiler::isEnabled() const {
    return enabled_;
}

void VectorizationProfiler::enable() {
    enabled_ = true;
}

void VectorizationProfiler::disable() {
    enabled_ = false;
}

std::string VectorizationProfiler::getStatus() const {
    std::ostringstream oss;
    oss << "VectorizationProfiler - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void VectorizationProfiler::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::simd
