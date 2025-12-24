#include <voltron/utility/i18n/encoding_detector.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::i18n {

EncodingDetector& EncodingDetector::instance() {
    static EncodingDetector instance;
    return instance;
}

void EncodingDetector::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[EncodingDetector] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void EncodingDetector::shutdown() {
    enabled_ = false;
    std::cout << "[EncodingDetector] Shutdown\n";
}

bool EncodingDetector::isEnabled() const {
    return enabled_;
}

void EncodingDetector::enable() {
    enabled_ = true;
}

void EncodingDetector::disable() {
    enabled_ = false;
}

std::string EncodingDetector::getStatus() const {
    std::ostringstream oss;
    oss << "EncodingDetector - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void EncodingDetector::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::i18n
