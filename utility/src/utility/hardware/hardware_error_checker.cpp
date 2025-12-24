#include <voltron/utility/hardware/hardware_error_checker.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::hardware {

HardwareErrorChecker& HardwareErrorChecker::instance() {
    static HardwareErrorChecker instance;
    return instance;
}

void HardwareErrorChecker::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[HardwareErrorChecker] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void HardwareErrorChecker::shutdown() {
    enabled_ = false;
    std::cout << "[HardwareErrorChecker] Shutdown\n";
}

bool HardwareErrorChecker::isEnabled() const {
    return enabled_;
}

void HardwareErrorChecker::enable() {
    enabled_ = true;
}

void HardwareErrorChecker::disable() {
    enabled_ = false;
}

std::string HardwareErrorChecker::getStatus() const {
    std::ostringstream oss;
    oss << "HardwareErrorChecker - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void HardwareErrorChecker::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::hardware
