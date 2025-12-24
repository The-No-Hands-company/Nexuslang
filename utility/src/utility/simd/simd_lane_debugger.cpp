#include <voltron/utility/simd/simd_lane_debugger.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::simd {

SimdLaneDebugger& SimdLaneDebugger::instance() {
    static SimdLaneDebugger instance;
    return instance;
}

void SimdLaneDebugger::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[SimdLaneDebugger] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void SimdLaneDebugger::shutdown() {
    enabled_ = false;
    std::cout << "[SimdLaneDebugger] Shutdown\n";
}

bool SimdLaneDebugger::isEnabled() const {
    return enabled_;
}

void SimdLaneDebugger::enable() {
    enabled_ = true;
}

void SimdLaneDebugger::disable() {
    enabled_ = false;
}

std::string SimdLaneDebugger::getStatus() const {
    std::ostringstream oss;
    oss << "SimdLaneDebugger - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void SimdLaneDebugger::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::simd
