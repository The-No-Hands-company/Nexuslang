#include <voltron/utility/orchestration/automated_remediation.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::orchestration {

AutomatedRemediation& AutomatedRemediation::instance() {
    static AutomatedRemediation instance;
    return instance;
}

void AutomatedRemediation::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[AutomatedRemediation] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void AutomatedRemediation::shutdown() {
    enabled_ = false;
    std::cout << "[AutomatedRemediation] Shutdown\n";
}

bool AutomatedRemediation::isEnabled() const {
    return enabled_;
}

void AutomatedRemediation::enable() {
    enabled_ = true;
}

void AutomatedRemediation::disable() {
    enabled_ = false;
}

std::string AutomatedRemediation::getStatus() const {
    std::ostringstream oss;
    oss << "AutomatedRemediation - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void AutomatedRemediation::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::orchestration
