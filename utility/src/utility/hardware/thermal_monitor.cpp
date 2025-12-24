#include <voltron/utility/hardware/thermal_monitor.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::hardware {

ThermalMonitor& ThermalMonitor::instance() {
    static ThermalMonitor instance;
    return instance;
}

void ThermalMonitor::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[ThermalMonitor] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void ThermalMonitor::shutdown() {
    enabled_ = false;
    std::cout << "[ThermalMonitor] Shutdown\n";
}

bool ThermalMonitor::isEnabled() const {
    return enabled_;
}

void ThermalMonitor::enable() {
    enabled_ = true;
}

void ThermalMonitor::disable() {
    enabled_ = false;
}

std::string ThermalMonitor::getStatus() const {
    std::ostringstream oss;
    oss << "ThermalMonitor - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void ThermalMonitor::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::hardware
