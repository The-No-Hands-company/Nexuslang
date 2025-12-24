#include <voltron/utility/reversing/code_cave_detector.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::reversing {

CodeCaveDetector& CodeCaveDetector::instance() {
    static CodeCaveDetector instance;
    return instance;
}

void CodeCaveDetector::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[CodeCaveDetector] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void CodeCaveDetector::shutdown() {
    enabled_ = false;
    std::cout << "[CodeCaveDetector] Shutdown\n";
}

bool CodeCaveDetector::isEnabled() const {
    return enabled_;
}

void CodeCaveDetector::enable() {
    enabled_ = true;
}

void CodeCaveDetector::disable() {
    enabled_ = false;
}

std::string CodeCaveDetector::getStatus() const {
    std::ostringstream oss;
    oss << "CodeCaveDetector - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void CodeCaveDetector::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::reversing
