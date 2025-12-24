#include <voltron/utility/workflow/backwards_compatibility_tester.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::workflow {

BackwardsCompatibilityTester& BackwardsCompatibilityTester::instance() {
    static BackwardsCompatibilityTester instance;
    return instance;
}

void BackwardsCompatibilityTester::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[BackwardsCompatibilityTester] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void BackwardsCompatibilityTester::shutdown() {
    enabled_ = false;
    std::cout << "[BackwardsCompatibilityTester] Shutdown\n";
}

bool BackwardsCompatibilityTester::isEnabled() const {
    return enabled_;
}

void BackwardsCompatibilityTester::enable() {
    enabled_ = true;
}

void BackwardsCompatibilityTester::disable() {
    enabled_ = false;
}

std::string BackwardsCompatibilityTester::getStatus() const {
    std::ostringstream oss;
    oss << "BackwardsCompatibilityTester - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void BackwardsCompatibilityTester::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::workflow
