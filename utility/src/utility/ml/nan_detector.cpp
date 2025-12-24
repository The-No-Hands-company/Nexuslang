#include <voltron/utility/ml/nan_detector.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::ml {

NanDetector& NanDetector::instance() {
    static NanDetector instance;
    return instance;
}

void NanDetector::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[NanDetector] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void NanDetector::shutdown() {
    enabled_ = false;
    std::cout << "[NanDetector] Shutdown\n";
}

bool NanDetector::isEnabled() const {
    return enabled_;
}

void NanDetector::enable() {
    enabled_ = true;
}

void NanDetector::disable() {
    enabled_ = false;
}

std::string NanDetector::getStatus() const {
    std::ostringstream oss;
    oss << "NanDetector - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void NanDetector::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::ml
