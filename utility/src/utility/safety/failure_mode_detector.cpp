#include <voltron/utility/safety/failure_mode_detector.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::safety {

FailureModeDetector& FailureModeDetector::instance() {
    static FailureModeDetector instance;
    return instance;
}

void FailureModeDetector::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[FailureModeDetector] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void FailureModeDetector::shutdown() {
    enabled_ = false;
    std::cout << "[FailureModeDetector] Shutdown\n";
}

bool FailureModeDetector::isEnabled() const {
    return enabled_;
}

void FailureModeDetector::enable() {
    enabled_ = true;
}

void FailureModeDetector::disable() {
    enabled_ = false;
}

std::string FailureModeDetector::getStatus() const {
    std::ostringstream oss;
    oss << "FailureModeDetector - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void FailureModeDetector::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::safety
