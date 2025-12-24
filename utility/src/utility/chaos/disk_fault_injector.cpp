#include <voltron/utility/chaos/disk_fault_injector.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::chaos {

DiskFaultInjector& DiskFaultInjector::instance() {
    static DiskFaultInjector instance;
    return instance;
}

void DiskFaultInjector::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[DiskFaultInjector] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void DiskFaultInjector::shutdown() {
    enabled_ = false;
    std::cout << "[DiskFaultInjector] Shutdown\n";
}

bool DiskFaultInjector::isEnabled() const {
    return enabled_;
}

void DiskFaultInjector::enable() {
    enabled_ = true;
}

void DiskFaultInjector::disable() {
    enabled_ = false;
}

std::string DiskFaultInjector::getStatus() const {
    std::ostringstream oss;
    oss << "DiskFaultInjector - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void DiskFaultInjector::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::chaos
