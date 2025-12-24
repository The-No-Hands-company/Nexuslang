#include <voltron/utility/apivalidation/version_compatibility_checker.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::apivalidation {

VersionCompatibilityChecker& VersionCompatibilityChecker::instance() {
    static VersionCompatibilityChecker instance;
    return instance;
}

void VersionCompatibilityChecker::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[VersionCompatibilityChecker] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void VersionCompatibilityChecker::shutdown() {
    enabled_ = false;
    std::cout << "[VersionCompatibilityChecker] Shutdown\n";
}

bool VersionCompatibilityChecker::isEnabled() const {
    return enabled_;
}

void VersionCompatibilityChecker::enable() {
    enabled_ = true;
}

void VersionCompatibilityChecker::disable() {
    enabled_ = false;
}

std::string VersionCompatibilityChecker::getStatus() const {
    std::ostringstream oss;
    oss << "VersionCompatibilityChecker - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void VersionCompatibilityChecker::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::apivalidation
