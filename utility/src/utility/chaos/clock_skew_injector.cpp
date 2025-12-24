#include <voltron/utility/chaos/clock_skew_injector.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::chaos {

ClockSkewInjector& ClockSkewInjector::instance() {
    static ClockSkewInjector instance;
    return instance;
}

void ClockSkewInjector::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[ClockSkewInjector] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void ClockSkewInjector::shutdown() {
    enabled_ = false;
    std::cout << "[ClockSkewInjector] Shutdown\n";
}

bool ClockSkewInjector::isEnabled() const {
    return enabled_;
}

void ClockSkewInjector::enable() {
    enabled_ = true;
}

void ClockSkewInjector::disable() {
    enabled_ = false;
}

std::string ClockSkewInjector::getStatus() const {
    std::ostringstream oss;
    oss << "ClockSkewInjector - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void ClockSkewInjector::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::chaos
