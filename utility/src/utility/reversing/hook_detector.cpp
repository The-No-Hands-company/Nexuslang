#include <voltron/utility/reversing/hook_detector.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::reversing {

HookDetector& HookDetector::instance() {
    static HookDetector instance;
    return instance;
}

void HookDetector::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[HookDetector] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void HookDetector::shutdown() {
    enabled_ = false;
    std::cout << "[HookDetector] Shutdown\n";
}

bool HookDetector::isEnabled() const {
    return enabled_;
}

void HookDetector::enable() {
    enabled_ = true;
}

void HookDetector::disable() {
    enabled_ = false;
}

std::string HookDetector::getStatus() const {
    std::ostringstream oss;
    oss << "HookDetector - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void HookDetector::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::reversing
