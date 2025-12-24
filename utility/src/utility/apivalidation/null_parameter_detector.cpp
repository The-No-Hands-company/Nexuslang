#include <voltron/utility/apivalidation/null_parameter_detector.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::apivalidation {

NullParameterDetector& NullParameterDetector::instance() {
    static NullParameterDetector instance;
    return instance;
}

void NullParameterDetector::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[NullParameterDetector] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void NullParameterDetector::shutdown() {
    enabled_ = false;
    std::cout << "[NullParameterDetector] Shutdown\n";
}

bool NullParameterDetector::isEnabled() const {
    return enabled_;
}

void NullParameterDetector::enable() {
    enabled_ = true;
}

void NullParameterDetector::disable() {
    enabled_ = false;
}

std::string NullParameterDetector::getStatus() const {
    std::ostringstream oss;
    oss << "NullParameterDetector - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void NullParameterDetector::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::apivalidation
