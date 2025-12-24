#include <voltron/utility/chaos/random_crash_injector.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::chaos {

RandomCrashInjector& RandomCrashInjector::instance() {
    static RandomCrashInjector instance;
    return instance;
}

void RandomCrashInjector::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[RandomCrashInjector] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void RandomCrashInjector::shutdown() {
    enabled_ = false;
    std::cout << "[RandomCrashInjector] Shutdown\n";
}

bool RandomCrashInjector::isEnabled() const {
    return enabled_;
}

void RandomCrashInjector::enable() {
    enabled_ = true;
}

void RandomCrashInjector::disable() {
    enabled_ = false;
}

std::string RandomCrashInjector::getStatus() const {
    std::ostringstream oss;
    oss << "RandomCrashInjector - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void RandomCrashInjector::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::chaos
