#include <voltron/utility/reversing/anti_tamper_checker.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::reversing {

AntiTamperChecker& AntiTamperChecker::instance() {
    static AntiTamperChecker instance;
    return instance;
}

void AntiTamperChecker::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[AntiTamperChecker] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void AntiTamperChecker::shutdown() {
    enabled_ = false;
    std::cout << "[AntiTamperChecker] Shutdown\n";
}

bool AntiTamperChecker::isEnabled() const {
    return enabled_;
}

void AntiTamperChecker::enable() {
    enabled_ = true;
}

void AntiTamperChecker::disable() {
    enabled_ = false;
}

std::string AntiTamperChecker::getStatus() const {
    std::ostringstream oss;
    oss << "AntiTamperChecker - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void AntiTamperChecker::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::reversing
