#include <voltron/utility/reversing/debugger_evasion_detector.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::reversing {

DebuggerEvasionDetector& DebuggerEvasionDetector::instance() {
    static DebuggerEvasionDetector instance;
    return instance;
}

void DebuggerEvasionDetector::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[DebuggerEvasionDetector] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void DebuggerEvasionDetector::shutdown() {
    enabled_ = false;
    std::cout << "[DebuggerEvasionDetector] Shutdown\n";
}

bool DebuggerEvasionDetector::isEnabled() const {
    return enabled_;
}

void DebuggerEvasionDetector::enable() {
    enabled_ = true;
}

void DebuggerEvasionDetector::disable() {
    enabled_ = false;
}

std::string DebuggerEvasionDetector::getStatus() const {
    std::ostringstream oss;
    oss << "DebuggerEvasionDetector - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void DebuggerEvasionDetector::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::reversing
