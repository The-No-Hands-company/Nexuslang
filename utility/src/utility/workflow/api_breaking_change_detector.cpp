#include <voltron/utility/workflow/api_breaking_change_detector.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::workflow {

ApiBreakingChangeDetector& ApiBreakingChangeDetector::instance() {
    static ApiBreakingChangeDetector instance;
    return instance;
}

void ApiBreakingChangeDetector::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[ApiBreakingChangeDetector] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void ApiBreakingChangeDetector::shutdown() {
    enabled_ = false;
    std::cout << "[ApiBreakingChangeDetector] Shutdown\n";
}

bool ApiBreakingChangeDetector::isEnabled() const {
    return enabled_;
}

void ApiBreakingChangeDetector::enable() {
    enabled_ = true;
}

void ApiBreakingChangeDetector::disable() {
    enabled_ = false;
}

std::string ApiBreakingChangeDetector::getStatus() const {
    std::ostringstream oss;
    oss << "ApiBreakingChangeDetector - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void ApiBreakingChangeDetector::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::workflow
