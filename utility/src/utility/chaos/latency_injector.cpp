#include <voltron/utility/chaos/latency_injector.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::chaos {

LatencyInjector& LatencyInjector::instance() {
    static LatencyInjector instance;
    return instance;
}

void LatencyInjector::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[LatencyInjector] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void LatencyInjector::shutdown() {
    enabled_ = false;
    std::cout << "[LatencyInjector] Shutdown\n";
}

bool LatencyInjector::isEnabled() const {
    return enabled_;
}

void LatencyInjector::enable() {
    enabled_ = true;
}

void LatencyInjector::disable() {
    enabled_ = false;
}

std::string LatencyInjector::getStatus() const {
    std::ostringstream oss;
    oss << "LatencyInjector - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void LatencyInjector::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::chaos
