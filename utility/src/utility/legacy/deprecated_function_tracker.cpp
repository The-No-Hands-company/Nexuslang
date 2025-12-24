#include <voltron/utility/legacy/deprecated_function_tracker.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::legacy {

DeprecatedFunctionTracker& DeprecatedFunctionTracker::instance() {
    static DeprecatedFunctionTracker instance;
    return instance;
}

void DeprecatedFunctionTracker::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[DeprecatedFunctionTracker] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void DeprecatedFunctionTracker::shutdown() {
    enabled_ = false;
    std::cout << "[DeprecatedFunctionTracker] Shutdown\n";
}

bool DeprecatedFunctionTracker::isEnabled() const {
    return enabled_;
}

void DeprecatedFunctionTracker::enable() {
    enabled_ = true;
}

void DeprecatedFunctionTracker::disable() {
    enabled_ = false;
}

std::string DeprecatedFunctionTracker::getStatus() const {
    std::ostringstream oss;
    oss << "DeprecatedFunctionTracker - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void DeprecatedFunctionTracker::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::legacy
