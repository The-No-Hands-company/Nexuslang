#include <voltron/utility/hardware/actuator_monitor.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::hardware {

ActuatorMonitor& ActuatorMonitor::instance() {
    static ActuatorMonitor instance;
    return instance;
}

void ActuatorMonitor::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[ActuatorMonitor] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void ActuatorMonitor::shutdown() {
    enabled_ = false;
    std::cout << "[ActuatorMonitor] Shutdown\n";
}

bool ActuatorMonitor::isEnabled() const {
    return enabled_;
}

void ActuatorMonitor::enable() {
    enabled_ = true;
}

void ActuatorMonitor::disable() {
    enabled_ = false;
}

std::string ActuatorMonitor::getStatus() const {
    std::ostringstream oss;
    oss << "ActuatorMonitor - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void ActuatorMonitor::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::hardware
