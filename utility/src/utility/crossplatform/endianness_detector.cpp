#include <voltron/utility/crossplatform/endianness_detector.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::crossplatform {

EndiannessDetector& EndiannessDetector::instance() {
    static EndiannessDetector instance;
    return instance;
}

void EndiannessDetector::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[EndiannessDetector] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void EndiannessDetector::shutdown() {
    enabled_ = false;
    std::cout << "[EndiannessDetector] Shutdown\n";
}

bool EndiannessDetector::isEnabled() const {
    return enabled_;
}

void EndiannessDetector::enable() {
    enabled_ = true;
}

void EndiannessDetector::disable() {
    enabled_ = false;
}

std::string EndiannessDetector::getStatus() const {
    std::ostringstream oss;
    oss << "EndiannessDetector - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void EndiannessDetector::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::crossplatform
