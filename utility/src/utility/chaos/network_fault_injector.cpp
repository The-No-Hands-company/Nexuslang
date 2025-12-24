#include <voltron/utility/chaos/network_fault_injector.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::chaos {

NetworkFaultInjector& NetworkFaultInjector::instance() {
    static NetworkFaultInjector instance;
    return instance;
}

void NetworkFaultInjector::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[NetworkFaultInjector] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void NetworkFaultInjector::shutdown() {
    enabled_ = false;
    std::cout << "[NetworkFaultInjector] Shutdown\n";
}

bool NetworkFaultInjector::isEnabled() const {
    return enabled_;
}

void NetworkFaultInjector::enable() {
    enabled_ = true;
}

void NetworkFaultInjector::disable() {
    enabled_ = false;
}

std::string NetworkFaultInjector::getStatus() const {
    std::ostringstream oss;
    oss << "NetworkFaultInjector - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void NetworkFaultInjector::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::chaos
