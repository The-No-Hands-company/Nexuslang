#include <voltron/utility/specialized/automotive_can_bus_monitor.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::specialized {

AutomotiveCanBusMonitor& AutomotiveCanBusMonitor::instance() {
    static AutomotiveCanBusMonitor instance;
    return instance;
}

void AutomotiveCanBusMonitor::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[AutomotiveCanBusMonitor] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void AutomotiveCanBusMonitor::shutdown() {
    enabled_ = false;
    std::cout << "[AutomotiveCanBusMonitor] Shutdown\n";
}

bool AutomotiveCanBusMonitor::isEnabled() const {
    return enabled_;
}

void AutomotiveCanBusMonitor::enable() {
    enabled_ = true;
}

void AutomotiveCanBusMonitor::disable() {
    enabled_ = false;
}

std::string AutomotiveCanBusMonitor::getStatus() const {
    std::ostringstream oss;
    oss << "AutomotiveCanBusMonitor - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void AutomotiveCanBusMonitor::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::specialized
