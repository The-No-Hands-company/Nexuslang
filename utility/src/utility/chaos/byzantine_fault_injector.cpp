#include <voltron/utility/chaos/byzantine_fault_injector.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::chaos {

ByzantineFaultInjector& ByzantineFaultInjector::instance() {
    static ByzantineFaultInjector instance;
    return instance;
}

void ByzantineFaultInjector::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[ByzantineFaultInjector] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void ByzantineFaultInjector::shutdown() {
    enabled_ = false;
    std::cout << "[ByzantineFaultInjector] Shutdown\n";
}

bool ByzantineFaultInjector::isEnabled() const {
    return enabled_;
}

void ByzantineFaultInjector::enable() {
    enabled_ = true;
}

void ByzantineFaultInjector::disable() {
    enabled_ = false;
}

std::string ByzantineFaultInjector::getStatus() const {
    std::ostringstream oss;
    oss << "ByzantineFaultInjector - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void ByzantineFaultInjector::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::chaos
