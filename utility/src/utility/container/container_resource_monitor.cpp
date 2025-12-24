#include <voltron/utility/container/container_resource_monitor.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::container {

ContainerResourceMonitor& ContainerResourceMonitor::instance() {
    static ContainerResourceMonitor instance;
    return instance;
}

void ContainerResourceMonitor::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[ContainerResourceMonitor] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void ContainerResourceMonitor::shutdown() {
    enabled_ = false;
    std::cout << "[ContainerResourceMonitor] Shutdown\n";
}

bool ContainerResourceMonitor::isEnabled() const {
    return enabled_;
}

void ContainerResourceMonitor::enable() {
    enabled_ = true;
}

void ContainerResourceMonitor::disable() {
    enabled_ = false;
}

std::string ContainerResourceMonitor::getStatus() const {
    std::ostringstream oss;
    oss << "ContainerResourceMonitor - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void ContainerResourceMonitor::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::container
