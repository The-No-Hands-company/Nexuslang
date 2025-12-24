#include <voltron/utility/safety/safety_invariant_checker.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::safety {

SafetyInvariantChecker& SafetyInvariantChecker::instance() {
    static SafetyInvariantChecker instance;
    return instance;
}

void SafetyInvariantChecker::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[SafetyInvariantChecker] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void SafetyInvariantChecker::shutdown() {
    enabled_ = false;
    std::cout << "[SafetyInvariantChecker] Shutdown\n";
}

bool SafetyInvariantChecker::isEnabled() const {
    return enabled_;
}

void SafetyInvariantChecker::enable() {
    enabled_ = true;
}

void SafetyInvariantChecker::disable() {
    enabled_ = false;
}

std::string SafetyInvariantChecker::getStatus() const {
    std::ostringstream oss;
    oss << "SafetyInvariantChecker - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void SafetyInvariantChecker::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::safety
