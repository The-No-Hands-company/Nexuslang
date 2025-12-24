#include <voltron/utility/binary/padding_detector.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::binary {

PaddingDetector& PaddingDetector::instance() {
    static PaddingDetector instance;
    return instance;
}

void PaddingDetector::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[PaddingDetector] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void PaddingDetector::shutdown() {
    enabled_ = false;
    std::cout << "[PaddingDetector] Shutdown\n";
}

bool PaddingDetector::isEnabled() const {
    return enabled_;
}

void PaddingDetector::enable() {
    enabled_ = true;
}

void PaddingDetector::disable() {
    enabled_ = false;
}

std::string PaddingDetector::getStatus() const {
    std::ostringstream oss;
    oss << "PaddingDetector - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void PaddingDetector::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::binary
