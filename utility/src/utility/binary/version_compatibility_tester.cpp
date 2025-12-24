#include <voltron/utility/binary/version_compatibility_tester.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::binary {

VersionCompatibilityTester& VersionCompatibilityTester::instance() {
    static VersionCompatibilityTester instance;
    return instance;
}

void VersionCompatibilityTester::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[VersionCompatibilityTester] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void VersionCompatibilityTester::shutdown() {
    enabled_ = false;
    std::cout << "[VersionCompatibilityTester] Shutdown\n";
}

bool VersionCompatibilityTester::isEnabled() const {
    return enabled_;
}

void VersionCompatibilityTester::enable() {
    enabled_ = true;
}

void VersionCompatibilityTester::disable() {
    enabled_ = false;
}

std::string VersionCompatibilityTester::getStatus() const {
    std::ostringstream oss;
    oss << "VersionCompatibilityTester - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void VersionCompatibilityTester::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::binary
