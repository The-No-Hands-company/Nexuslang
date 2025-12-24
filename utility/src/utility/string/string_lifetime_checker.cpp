#include <voltron/utility/string/string_lifetime_checker.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::string {

StringLifetimeChecker& StringLifetimeChecker::instance() {
    static StringLifetimeChecker instance;
    return instance;
}

void StringLifetimeChecker::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[StringLifetimeChecker] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void StringLifetimeChecker::shutdown() {
    enabled_ = false;
    std::cout << "[StringLifetimeChecker] Shutdown\n";
}

bool StringLifetimeChecker::isEnabled() const {
    return enabled_;
}

void StringLifetimeChecker::enable() {
    enabled_ = true;
}

void StringLifetimeChecker::disable() {
    enabled_ = false;
}

std::string StringLifetimeChecker::getStatus() const {
    std::ostringstream oss;
    oss << "StringLifetimeChecker - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void StringLifetimeChecker::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::string
