#include <voltron/utility/simd/autovectorization_checker.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::simd {

AutovectorizationChecker& AutovectorizationChecker::instance() {
    static AutovectorizationChecker instance;
    return instance;
}

void AutovectorizationChecker::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[AutovectorizationChecker] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void AutovectorizationChecker::shutdown() {
    enabled_ = false;
    std::cout << "[AutovectorizationChecker] Shutdown\n";
}

bool AutovectorizationChecker::isEnabled() const {
    return enabled_;
}

void AutovectorizationChecker::enable() {
    enabled_ = true;
}

void AutovectorizationChecker::disable() {
    enabled_ = false;
}

std::string AutovectorizationChecker::getStatus() const {
    std::ostringstream oss;
    oss << "AutovectorizationChecker - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void AutovectorizationChecker::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::simd
