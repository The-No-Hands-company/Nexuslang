#include <voltron/utility/financial/rounding_error_detector.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::financial {

RoundingErrorDetector& RoundingErrorDetector::instance() {
    static RoundingErrorDetector instance;
    return instance;
}

void RoundingErrorDetector::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[RoundingErrorDetector] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void RoundingErrorDetector::shutdown() {
    enabled_ = false;
    std::cout << "[RoundingErrorDetector] Shutdown\n";
}

bool RoundingErrorDetector::isEnabled() const {
    return enabled_;
}

void RoundingErrorDetector::enable() {
    enabled_ = true;
}

void RoundingErrorDetector::disable() {
    enabled_ = false;
}

std::string RoundingErrorDetector::getStatus() const {
    std::ostringstream oss;
    oss << "RoundingErrorDetector - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void RoundingErrorDetector::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::financial
